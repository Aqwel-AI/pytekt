"""Query builder for SQL and document backends."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .errors import NotFoundError
from .types import Filter

if TYPE_CHECKING:
    from .base import Connection


class Query:
    """Fluent query: ``conn.table('users').where(...).select(...).all()``."""

    def __init__(self, connection: "Connection", table: str) -> None:
        self._conn = connection
        self._table = table
        self._filters: List[Filter] = []
        self._columns: Optional[List[str]] = None
        self._order_by: Optional[str] = None
        self._order_desc = False
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None

    def where(self, expr: Filter) -> "Query":
        self._filters.append(expr)
        return self

    def select(self, *columns: str) -> "Query":
        self._columns = list(columns) if columns else None
        return self

    def order_by(self, column: str, *, desc: bool = False) -> "Query":
        self._order_by = column
        self._order_desc = desc
        return self

    def limit(self, n: int) -> "Query":
        self._limit = n
        return self

    def offset(self, n: int) -> "Query":
        self._offset = n
        return self

    def all(self) -> List[Dict[str, Any]]:
        return self._conn.execute_query(
            self._table,
            filters=self._filters,
            columns=self._columns,
            order_by=self._order_by,
            order_desc=self._order_desc,
            limit=self._limit,
            offset=self._offset,
        )

    def one(self) -> Dict[str, Any]:
        rows = self.limit(1).all()
        if not rows:
            raise NotFoundError(f"No row in {self._table!r} matching query")
        return rows[0]

    def count(self) -> int:
        return self._conn.execute_count(self._table, filters=self._filters)

    def first(self) -> Optional[Dict[str, Any]]:
        rows = self.limit(1).all()
        return rows[0] if rows else None

    def to_df(self):
        """Export results as a pandas DataFrame (requires pandas)."""
        from .pandas_bridge import rows_to_dataframe

        return rows_to_dataframe(self.all())
