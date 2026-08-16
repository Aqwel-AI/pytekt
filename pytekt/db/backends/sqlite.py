"""SQLite backend — zero extra dependencies."""

from __future__ import annotations

import sqlite3
import threading
from typing import Any, Tuple
from urllib.parse import unquote, urlparse

from ..schema import sql_type_sqlite
from .sql_base import SqlConnection


class SqliteConnection(SqlConnection):
    engine = "sqlite"

    def __init__(self, db_path: str = ":memory:") -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        super().__init__(
            type_fn=sql_type_sqlite,
            execute_fn=self._run_execute,
            executemany_fn=self._run_executemany,
            lock=self._lock,
        )
        self._kv = None
        self._chat = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path, timeout=5, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _run_execute(self, sql: str, params: Tuple[Any, ...]) -> sqlite3.Cursor:
        conn = self._get_conn()
        cur = conn.execute(sql, params)
        conn.commit()
        return cur

    def _run_executemany(self, sql: str, params_list: list) -> sqlite3.Cursor:
        conn = self._get_conn()
        cur = conn.executemany(sql, params_list)
        conn.commit()
        return cur

    @property
    def kv(self):
        """Key-value store (:mod:`pytekt.store`)."""
        if self._kv is None:
            from ...store import KeyValueStore

            path = self._db_path if self._db_path != ":memory:" else ".pytekt_kv.db"
            self._kv = KeyValueStore(path)
        return self._kv

    @property
    def chat(self):
        """Chat history (:mod:`pytekt.store`) with ``save_thread`` helper."""
        if self._chat is None:
            from ...store import ChatHistoryStore
            from ..chat_bridge import ChatBridge

            path = self._db_path if self._db_path != ":memory:" else ".pytekt_chat.db"
            self._chat = ChatBridge(ChatHistoryStore(path))
        return self._chat

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None


def connect_sqlite(url_or_path: str) -> SqliteConnection:
    if url_or_path.startswith("sqlite:"):
        parsed = urlparse(url_or_path)
        path = unquote(parsed.path or parsed.netloc or "")
        if path.startswith("/") and len(path) > 2 and path[2] == ":":
            path = path[1:]
        elif path.startswith("/"):
            path = path[1:] if path != "/:memory:" else ":memory:"
        if not path or path == "/":
            path = ":memory:"
        return SqliteConnection(path)
    return SqliteConnection(url_or_path)
