"""Agent conversation memory backed by any pytekt.db connection."""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from ..base import Connection


class AgentMemoryStore:
    """Persist agent chat threads to a collection (default ``agent_threads``)."""

    def __init__(
        self,
        conn: Connection,
        thread_id: Optional[str] = None,
        *,
        collection: str = "agent_threads",
    ) -> None:
        self._conn = conn
        self._coll = conn.collection(collection)
        self.thread_id = thread_id or uuid.uuid4().hex[:12]
        self._ensure_thread()

    def _ensure_thread(self) -> None:
        if not self._coll.find_one(thread_id=self.thread_id):
            self._coll.insert({
                "thread_id": self.thread_id,
                "messages": [],
                "created_at": time.time(),
                "updated_at": time.time(),
            })

    def load_messages(self) -> List[Dict[str, str]]:
        row = self._coll.find_one(thread_id=self.thread_id)
        if not row:
            return []
        msgs = row.get("messages", [])
        return list(msgs) if isinstance(msgs, list) else []

    def save_messages(self, messages: List[Dict[str, str]]) -> None:
        self._coll.update(
            {"thread_id": self.thread_id},
            {"messages": messages, "updated_at": time.time()},
        )

    def append(self, role: str, content: str) -> None:
        msgs = self.load_messages()
        msgs.append({"role": role, "content": content})
        self.save_messages(msgs)

    def clear(self) -> None:
        self.save_messages([])


def agent_memory(
    conn: Connection,
    thread_id: Optional[str] = None,
    **kwargs: Any,
) -> AgentMemoryStore:
    """Create an :class:`AgentMemoryStore` for the given connection."""
    return AgentMemoryStore(conn, thread_id, **kwargs)
