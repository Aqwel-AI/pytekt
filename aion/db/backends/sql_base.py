"""Shared SQL document store logic."""

from __future__ import annotations

import json
import re
import threading
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from ..base import Connection, QueryBackend
from ..document import DocumentCollection
from ..errors import DuplicateKeyError, QueryError
from ..schema import (
    deserialize_row,
    infer_columns,
    merge_columns,
    serialize_value,
)
from ..types import Filter, compile_sql_filters, parse_filters


def _safe_table(name: str) -> str:
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise QueryError(f"Invalid table name: {name!r}")
    return name


class SqlCollection(DocumentCollection):
    def __init__(
        self,
        connection: "SqlConnection",
        name: str,
    ) -> None:
        super().__init__(connection, name)
        self._table = _safe_table(name)

    def insert(self, document: Dict[str, Any]) -> Any:
        return self._conn._insert(self._table, document)

    def insert_many(self, documents: List[Dict[str, Any]]) -> List[Any]:
        return [self.insert(doc) for doc in documents]

    def find(self, **filters: Any) -> List[Dict[str, Any]]:
        limit = filters.pop("_limit", None)
        parsed = parse_filters(filters)
        return self._conn.execute_query(
            self._table,
            filters=parsed,
            limit=limit,
        )

    def update(self, query: Dict[str, Any], patch: Dict[str, Any]) -> int:
        return self._conn._update(self._table, query, patch)

    def delete(self, **filters: Any) -> int:
        return self._conn._delete(self._table, parse_filters(filters))

    def count(self, **filters: Any) -> int:
        return self._conn.execute_count(self._table, filters=parse_filters(filters))


class SqlConnection(Connection, QueryBackend):
    """Base for SQLite, MySQL, PostgreSQL."""

    param_style = "?"
    placeholder = "?"

    def __init__(
        self,
        *,
        type_fn: Callable[[str], str],
        execute_fn: Callable[[str, Tuple[Any, ...]], Any],
        executemany_fn: Callable[[str, List[Tuple[Any, ...]]], Any],
        lock: threading.Lock,
    ) -> None:
        super().__init__()
        self._type_fn = type_fn
        self._execute = execute_fn
        self._executemany = executemany_fn
        self._lock = lock
        self._schemas: Dict[str, Dict[str, str]] = {}
        self._json_cols: Dict[str, Set[str]] = {}

    def collection(self, name: str) -> SqlCollection:
        return SqlCollection(self, name)

    def _ensure_table(self, table: str, document: Dict[str, Any]) -> None:
        table = _safe_table(table)
        with self._lock:
            if table not in self._schemas:
                self._schemas[table] = infer_columns(document)
                cols = self._schemas[table]
                json_cols = {k for k, t in cols.items() if t == "json"}
                self._json_cols[table] = json_cols
                col_defs = ", ".join(
                    f"{k} {self._type_fn(t)}" + (" PRIMARY KEY AUTOINCREMENT" if k == "id" else "")
                    for k, t in cols.items()
                )
                sql = f"CREATE TABLE IF NOT EXISTS {table} ({col_defs})"
                self._execute(sql, ())
            else:
                merged = merge_columns(self._schemas[table], document)
                new_json = {k for k, t in merged.items() if t == "json"}
                for col, typ in merged.items():
                    if col not in self._schemas[table]:
                        self._execute(
                            f"ALTER TABLE {table} ADD COLUMN {col} {self._type_fn(typ)}",
                            (),
                        )
                self._schemas[table] = merged
                self._json_cols[table] = self._json_cols.get(table, set()) | new_json

    def _insert(self, table: str, document: Dict[str, Any]) -> Any:
        self._ensure_table(table, document)
        doc = dict(document)
        if doc.get("id") is None:
            doc.pop("id", None)
        cols = list(doc.keys())
        json_cols = self._json_cols.get(table, set())
        values = [serialize_value(doc[k], engine=self.engine) for k in cols]
        ph = ", ".join([self.placeholder] * len(cols))
        col_names = ", ".join(cols)
        sql = f"INSERT INTO {table} ({col_names}) VALUES ({ph})"
        with self._lock:
            cur = self._execute(sql, tuple(values))
            if "id" in self._schemas.get(table, {}):
                return getattr(cur, "lastrowid", None)
        return None

    def _update(self, table: str, query: Dict[str, Any], patch: Dict[str, Any]) -> int:
        filters = parse_filters(query)
        where, params = compile_sql_filters(filters, json_columns=tuple(self._json_cols.get(table, ())))
        if not patch:
            return 0
        sets = []
        values: List[Any] = []
        for k, v in patch.items():
            sets.append(f"{k} = {self.placeholder}")
            values.append(serialize_value(v, engine=self.engine))
        sql = f"UPDATE {table} SET {', '.join(sets)}"
        if where:
            sql += f" WHERE {where}"
        with self._lock:
            cur = self._execute(sql, tuple(values + params))
            return int(getattr(cur, "rowcount", 0) or 0)

    def _delete(self, table: str, filters: List[Filter]) -> int:
        where, params = compile_sql_filters(filters, json_columns=tuple(self._json_cols.get(table, ())))
        sql = f"DELETE FROM {table}"
        if where:
            sql += f" WHERE {where}"
        with self._lock:
            cur = self._execute(sql, tuple(params))
            return int(getattr(cur, "rowcount", 0) or 0)

    def execute_query(
        self,
        table: str,
        *,
        filters: List[Filter],
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        table = _safe_table(table)
        if table not in self._schemas:
            return []
        where, params = compile_sql_filters(filters, json_columns=tuple(self._json_cols.get(table, ())))
        cols = ", ".join(columns) if columns else "*"
        sql = f"SELECT {cols} FROM {table}"
        if where:
            sql += f" WHERE {where}"
        if order_by:
            sql += f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'}"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        if offset is not None:
            sql += f" OFFSET {int(offset)}"
        with self._lock:
            rows = self._fetchall(sql, tuple(params))
        json_cols = self._json_cols.get(table, set())
        return [deserialize_row(r, json_cols) for r in rows]

    def execute_count(self, table: str, *, filters: List[Filter]) -> int:
        table = _safe_table(table)
        if table not in self._schemas:
            return 0
        where, params = compile_sql_filters(filters, json_columns=tuple(self._json_cols.get(table, ())))
        sql = f"SELECT COUNT(*) AS c FROM {table}"
        if where:
            sql += f" WHERE {where}"
        with self._lock:
            rows = self._fetchall(sql, tuple(params))
        return int(rows[0]["c"]) if rows else 0

    def _fetchall(self, sql: str, params: Tuple[Any, ...]) -> List[Dict[str, Any]]:
        cur = self._execute(sql, params)
        if hasattr(cur, "fetchall"):
            raw = cur.fetchall()
            if raw and isinstance(raw[0], dict):
                return list(raw)
            if hasattr(cur, "description") and cur.description:
                keys = [d[0] for d in cur.description]
                return [dict(zip(keys, row)) for row in raw]
        return []
