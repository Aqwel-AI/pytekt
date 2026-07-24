"""SQLite-backed key-value store."""

from __future__ import annotations

import json
import sqlite3
import threading
from typing import Any, Dict, Iterator, List, Optional


class KeyValueStore:
    """
    Persistent key-value store backed by SQLite.

    Supports string keys and JSON-serializable values, plus namespaces
    for logical grouping.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.
    table : str
        Table name (allows multiple logical stores in one DB).
    """

    def __init__(self, db_path: str = ".aion_kv.db", table: str = "kv") -> None:
        self._db_path = db_path
        self._table = table
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, timeout=5)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {self._table} "
                "(key TEXT PRIMARY KEY, value TEXT NOT NULL, namespace TEXT DEFAULT '')"
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{self._table}_ns ON {self._table}(namespace)"
            )

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    f"SELECT value FROM {self._table} WHERE key = ?", (key,)
                ).fetchone()
        if row is None:
            return default
        return json.loads(row[0])

    def set(self, key: str, value: Any, *, namespace: str = "") -> None:
        val_json = json.dumps(value, default=str)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    f"INSERT OR REPLACE INTO {self._table} (key, value, namespace) VALUES (?, ?, ?)",
                    (key, val_json, namespace),
                )

    def delete(self, key: str) -> bool:
        with self._lock:
            with self._connect() as conn:
                cursor = conn.execute(
                    f"DELETE FROM {self._table} WHERE key = ?", (key,)
                )
                return cursor.rowcount > 0

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def keys(self, *, namespace: Optional[str] = None) -> List[str]:
        with self._lock:
            with self._connect() as conn:
                if namespace is not None:
                    rows = conn.execute(
                        f"SELECT key FROM {self._table} WHERE namespace = ?",
                        (namespace,),
                    ).fetchall()
                else:
                    rows = conn.execute(f"SELECT key FROM {self._table}").fetchall()
        return [r[0] for r in rows]

    def values(self, *, namespace: Optional[str] = None) -> List[Any]:
        with self._lock:
            with self._connect() as conn:
                if namespace is not None:
                    rows = conn.execute(
                        f"SELECT value FROM {self._table} WHERE namespace = ?",
                        (namespace,),
                    ).fetchall()
                else:
                    rows = conn.execute(f"SELECT value FROM {self._table}").fetchall()
        return [json.loads(r[0]) for r in rows]

    def items(self, *, namespace: Optional[str] = None) -> List[tuple]:
        with self._lock:
            with self._connect() as conn:
                if namespace is not None:
                    rows = conn.execute(
                        f"SELECT key, value FROM {self._table} WHERE namespace = ?",
                        (namespace,),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        f"SELECT key, value FROM {self._table}"
                    ).fetchall()
        return [(r[0], json.loads(r[1])) for r in rows]

    def clear(self, *, namespace: Optional[str] = None) -> int:
        with self._lock:
            with self._connect() as conn:
                if namespace is not None:
                    c = conn.execute(
                        f"DELETE FROM {self._table} WHERE namespace = ?", (namespace,)
                    )
                else:
                    c = conn.execute(f"DELETE FROM {self._table}")
                return c.rowcount

    def size(self, *, namespace: Optional[str] = None) -> int:
        with self._lock:
            with self._connect() as conn:
                if namespace is not None:
                    row = conn.execute(
                        f"SELECT COUNT(*) FROM {self._table} WHERE namespace = ?",
                        (namespace,),
                    ).fetchone()
                else:
                    row = conn.execute(f"SELECT COUNT(*) FROM {self._table}").fetchone()
        return row[0] if row else 0

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __getitem__(self, key: str) -> Any:
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        if not self.delete(key):
            raise KeyError(key)

    def __len__(self) -> int:
        return self.size()
