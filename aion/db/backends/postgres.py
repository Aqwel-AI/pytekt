"""PostgreSQL backend (optional: pip install aqwel-aion[db])."""

from __future__ import annotations

import threading
from typing import Any, Dict, Tuple

from ..errors import ConnectionError
from ..pool import ThreadLocalPool
from ..retry import with_retry
from ..schema import sql_type_postgres
from .sql_base import SqlConnection


def _require_psycopg():
    try:
        import psycopg  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "PostgreSQL support requires psycopg. Install with: pip install aqwel-aion[db]"
        ) from e


class PostgresConnection(SqlConnection):
    engine = "postgresql"
    placeholder = "%s"

    def __init__(self, cfg: Dict[str, Any]) -> None:
        _require_psycopg()
        import psycopg
        from psycopg.rows import dict_row

        self._cfg = cfg
        self._lock = threading.Lock()
        dsn = cfg.get("dsn") or cfg.get("url")
        if not dsn:
            host = cfg.get("host", "localhost")
            port = int(cfg.get("port") or 5432)
            user = cfg.get("username") or cfg.get("user") or "postgres"
            password = cfg.get("password") or ""
            database = cfg.get("database") or cfg.get("db") or "postgres"
            dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        def factory():
            return psycopg.connect(dsn, row_factory=dict_row, autocommit=True)

        self._pool = ThreadLocalPool(factory)
        super().__init__(
            type_fn=sql_type_postgres,
            execute_fn=self._run_execute,
            executemany_fn=self._run_executemany,
            lock=self._lock,
        )

    def _adapt_sql(self, sql: str) -> str:
        sql = sql.replace("?", "%s")
        if "AUTOINCREMENT" in sql:
            sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        return sql

    def _run_execute(self, sql: str, params: Tuple[Any, ...]):
        sql = self._adapt_sql(sql)
        def _go():
            cur = self._pool.get().cursor()
            cur.execute(sql, params or None)
            return cur
        return with_retry(_go)

    def _run_executemany(self, sql: str, params_list: list):
        sql = self._adapt_sql(sql)
        return with_retry(lambda: self._pool.get().cursor().executemany(sql, params_list))

    def _fetchall(self, sql: str, params: Tuple[Any, ...]):
        sql = self._adapt_sql(sql)
        with self._lock:
            cur = self._pool.get().cursor()
            cur.execute(sql, params or None)
            return list(cur.fetchall())

    def close(self) -> None:
        self._pool.close()


def connect_postgres(cfg: Dict[str, Any]) -> PostgresConnection:
    return PostgresConnection(cfg)
