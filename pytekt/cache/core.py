"""Cache protocol and concrete implementations (memory + SQLite)."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from typing import Any, Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class Cache(Protocol):
    """Minimal cache interface."""

    def get(self, key: str) -> Optional[Any]: ...
    def set(self, key: str, value: Any, *, ttl: Optional[int] = None) -> None: ...
    def delete(self, key: str) -> bool: ...
    def clear(self) -> None: ...
    def has(self, key: str) -> bool: ...


class MemoryCache:
    """Thread-safe in-memory cache with optional per-key TTL."""

    def __init__(self, *, default_ttl: Optional[int] = None, max_size: int = 10_000) -> None:
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._lock = threading.Lock()

    def _is_expired(self, key: str) -> bool:
        exp = self._expiry.get(key)
        if exp is None:
            return False
        return time.time() > exp

    def _evict_expired(self) -> None:
        now = time.time()
        expired = [k for k, exp in self._expiry.items() if now > exp]
        for k in expired:
            self._store.pop(k, None)
            self._expiry.pop(k, None)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._store or self._is_expired(key):
                self._store.pop(key, None)
                self._expiry.pop(key, None)
                return None
            return self._store[key]

    def set(self, key: str, value: Any, *, ttl: Optional[int] = None) -> None:
        with self._lock:
            if len(self._store) >= self._max_size:
                self._evict_expired()
                if len(self._store) >= self._max_size:
                    oldest = next(iter(self._store))
                    self._store.pop(oldest)
                    self._expiry.pop(oldest, None)
            self._store[key] = value
            t = ttl if ttl is not None else self._default_ttl
            if t is not None:
                self._expiry[key] = time.time() + t

    def delete(self, key: str) -> bool:
        with self._lock:
            removed = key in self._store
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return removed

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self._expiry.clear()

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def size(self) -> int:
        with self._lock:
            self._evict_expired()
            return len(self._store)

    def keys(self):
        with self._lock:
            self._evict_expired()
            return list(self._store.keys())


class DiskCache:
    """SQLite-backed persistent cache with optional TTL."""

    def __init__(self, db_path: str = ".aion_cache.db", *, default_ttl: Optional[int] = None) -> None:
        self._db_path = db_path
        self._default_ttl = default_ttl
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, timeout=5)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS cache "
                "(key TEXT PRIMARY KEY, value TEXT NOT NULL, expires_at REAL)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires ON cache(expires_at)")

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
                ).fetchone()
            if row is None:
                return None
            value_json, expires_at = row
            if expires_at is not None and time.time() > expires_at:
                self.delete(key)
                return None
            return json.loads(value_json)

    def set(self, key: str, value: Any, *, ttl: Optional[int] = None) -> None:
        t = ttl if ttl is not None else self._default_ttl
        expires_at = (time.time() + t) if t is not None else None
        value_json = json.dumps(value, default=str)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                    (key, value_json, expires_at),
                )

    def delete(self, key: str) -> bool:
        with self._lock:
            with self._connect() as conn:
                cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return cursor.rowcount > 0

    def clear(self) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute("DELETE FROM cache")

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def size(self) -> int:
        with self._lock:
            with self._connect() as conn:
                self._purge_expired(conn)
                row = conn.execute("SELECT COUNT(*) FROM cache").fetchone()
                return row[0] if row else 0

    def _purge_expired(self, conn: sqlite3.Connection) -> None:
        conn.execute("DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at < ?", (time.time(),))

    def purge_expired(self) -> int:
        """Remove all expired entries and return the count deleted."""
        with self._lock:
            with self._connect() as conn:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                    (time.time(),),
                )
                return cursor.rowcount


def make_cache_key(*args: Any, **kwargs: Any) -> str:
    """Create a deterministic hash key from arbitrary arguments."""
    raw = json.dumps({"a": args, "k": kwargs}, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()
