"""Persistent chat history store for conversation threads."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ChatThread:
    """A conversation thread with message history."""

    id: str
    title: str = ""
    messages: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0


class ChatHistoryStore:
    """
    SQLite-backed store for persisting chat threads.

    Each thread has an id, title, ordered messages, and metadata.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.
    """

    def __init__(self, db_path: str = ".aion_chat_history.db") -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, timeout=5)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS threads "
                "(id TEXT PRIMARY KEY, title TEXT, metadata TEXT, "
                "created_at REAL, updated_at REAL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS messages "
                "(id INTEGER PRIMARY KEY AUTOINCREMENT, thread_id TEXT NOT NULL, "
                "role TEXT NOT NULL, content TEXT NOT NULL, metadata TEXT, "
                "created_at REAL, "
                "FOREIGN KEY(thread_id) REFERENCES threads(id))"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_msg_thread ON messages(thread_id)"
            )

    def create_thread(
        self, *, title: str = "", metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new thread and return its id."""
        thread_id = uuid.uuid4().hex[:12]
        now = time.time()
        meta_json = json.dumps(metadata or {}, default=str)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO threads (id, title, metadata, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (thread_id, title, meta_json, now, now),
                )
        return thread_id

    def add_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a message to a thread."""
        now = time.time()
        meta_json = json.dumps(metadata or {}, default=str)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO messages (thread_id, role, content, metadata, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (thread_id, role, content, meta_json, now),
                )
                conn.execute(
                    "UPDATE threads SET updated_at = ? WHERE id = ?", (now, thread_id)
                )

    def get_thread(self, thread_id: str) -> Optional[ChatThread]:
        """Load a thread with all its messages."""
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT id, title, metadata, created_at, updated_at "
                    "FROM threads WHERE id = ?",
                    (thread_id,),
                ).fetchone()
                if row is None:
                    return None
                msgs = conn.execute(
                    "SELECT role, content, metadata FROM messages "
                    "WHERE thread_id = ? ORDER BY id",
                    (thread_id,),
                ).fetchall()

        messages = []
        for role, content, meta_json in msgs:
            msg: Dict[str, Any] = {"role": role, "content": content}
            if meta_json:
                meta = json.loads(meta_json)
                if meta:
                    msg["metadata"] = meta
            messages.append(msg)

        return ChatThread(
            id=row[0],
            title=row[1],
            messages=messages,
            metadata=json.loads(row[2]) if row[2] else {},
            created_at=row[3],
            updated_at=row[4],
        )

    def list_threads(self, *, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List threads sorted by most recently updated."""
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT id, title, metadata, created_at, updated_at "
                    "FROM threads ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()
        return [
            {
                "id": r[0],
                "title": r[1],
                "metadata": json.loads(r[2]) if r[2] else {},
                "created_at": r[3],
                "updated_at": r[4],
            }
            for r in rows
        ]

    def delete_thread(self, thread_id: str) -> bool:
        with self._lock:
            with self._connect() as conn:
                conn.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
                c = conn.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
                return c.rowcount > 0

    def get_messages(
        self, thread_id: str, *, limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Get messages for a thread, optionally limited to the last *limit*."""
        with self._lock:
            with self._connect() as conn:
                if limit is not None:
                    rows = conn.execute(
                        "SELECT role, content FROM ("
                        "  SELECT role, content, id FROM messages "
                        "  WHERE thread_id = ? ORDER BY id DESC LIMIT ?"
                        ") ORDER BY id",
                        (thread_id, limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT role, content FROM messages "
                        "WHERE thread_id = ? ORDER BY id",
                        (thread_id,),
                    ).fetchall()
        return [{"role": r[0], "content": r[1]} for r in rows]

    def search_threads(self, query: str) -> List[Dict[str, Any]]:
        """Search threads by title or message content."""
        pattern = f"%{query}%"
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT DISTINCT t.id, t.title, t.metadata, t.created_at, t.updated_at "
                    "FROM threads t LEFT JOIN messages m ON t.id = m.thread_id "
                    "WHERE t.title LIKE ? OR m.content LIKE ? "
                    "ORDER BY t.updated_at DESC",
                    (pattern, pattern),
                ).fetchall()
        return [
            {
                "id": r[0],
                "title": r[1],
                "metadata": json.loads(r[2]) if r[2] else {},
                "created_at": r[3],
                "updated_at": r[4],
            }
            for r in rows
        ]

    def clear(self) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute("DELETE FROM messages")
                conn.execute("DELETE FROM threads")
