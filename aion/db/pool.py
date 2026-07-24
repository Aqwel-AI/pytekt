"""Thread-local connection pooling for SQL backends."""

from __future__ import annotations

import threading
from typing import Any, Callable, Dict, Optional


class ThreadLocalPool:
    """Reuse one connection per thread."""

    def __init__(self, factory: Callable[[], Any]) -> None:
        self._factory = factory
        self._local = threading.local()

    def get(self) -> Any:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = self._factory()
            self._local.conn = conn
        return conn

    def close(self) -> None:
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
            self._local.conn = None


class ClientHolder:
    """Singleton client holder for MongoDB / Redis."""

    def __init__(self) -> None:
        self._client: Any = None
        self._lock = threading.Lock()

    def get_or_create(self, factory: Callable[[], Any]) -> Any:
        with self._lock:
            if self._client is None:
                self._client = factory()
            return self._client

    def close(self) -> None:
        with self._lock:
            if self._client is not None:
                try:
                    self._client.close()
                except Exception:
                    pass
                self._client = None
