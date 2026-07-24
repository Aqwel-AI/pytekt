"""MySQL backend (optional: pip install aqwel-aion[db])."""

from __future__ import annotations

import threading
from typing import Any, Dict, Tuple

from ..errors import ConnectionError
from ..pool import ThreadLocalPool
from ..retry import with_retry
from ..schema import sql_type_mysql
from .sql_base import SqlConnection


def _require_pymysql():
    try:
        import pymysql  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "MySQL support requires PyMySQL. Install with: pip install aqwel-aion[db]"
        ) from e


class MysqlConnection(SqlConnection):
    engine = "mysql"
    placeholder = "%s"

    def __init__(self, cfg: Dict[str, Any]) -> None:
        _require_pymysql()
        import pymysql
        import pymysql.cursors

        self._cfg = cfg
        self._lock = threading.Lock()

        def factory():
            return pymysql.connect(
                host=cfg.get("host", "localhost"),
                port=int(cfg.get("port") or 3306),
                user=cfg.get("username") or cfg.get("user") or "root",
                password=cfg.get("password") or "",
                database=cfg.get("database") or cfg.get("db"),
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
            )

        self._pool = ThreadLocalPool(factory)
        super().__init__(
            type_fn=sql_type_mysql,
            execute_fn=self._run_execute,
            executemany_fn=self._run_executemany,
            lock=self._lock,
        )

    def _run_execute(self, sql: str, params: Tuple[Any, ...]):
        sql = sql.replace("?", "%s")
        return with_retry(lambda: self._pool.get().cursor().execute(sql, params or None))

    def _run_executemany(self, sql: str, params_list: list):
        sql = sql.replace("?", "%s")
        return with_retry(lambda: self._pool.get().cursor().executemany(sql, params_list))

    def _fetchall(self, sql: str, params: Tuple[Any, ...]):
        sql = sql.replace("?", "%s")
        with self._lock:
            cur = self._pool.get().cursor()
            cur.execute(sql, params or None)
            return list(cur.fetchall())

    def close(self) -> None:
        self._pool.close()


def connect_mysql(cfg: Dict[str, Any]) -> MysqlConnection:
    if not cfg.get("database") and not cfg.get("db"):
        raise ConnectionError("MySQL requires 'database' in connection config")
    return MysqlConnection(cfg)
