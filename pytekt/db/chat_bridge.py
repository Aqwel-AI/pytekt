"""Bridge :mod:`aion.store` chat history to :mod:`aion.db` SQLite connections."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..store.chat_history import ChatHistoryStore, ChatThread


class ChatBridge:
    """Wraps :class:`ChatHistoryStore` with a unified ``save_thread`` API."""

    def __init__(self, store: ChatHistoryStore) -> None:
        self._store = store

    def create_thread(self, *, title: str = "", metadata: Optional[Dict[str, Any]] = None) -> str:
        return self._store.create_thread(title=title, metadata=metadata)

    def save_thread(
        self,
        messages: List[Dict[str, str]],
        *,
        thread_id: Optional[str] = None,
        title: str = "",
    ) -> str:
        """
        Persist a full message list.

        Creates a new thread when *thread_id* is missing or unknown.
        """
        tid = thread_id
        if tid and self._store.get_thread(tid):
            pass
        else:
            tid = self._store.create_thread(title=title or "Agent session")
        for msg in messages:
            self._store.add_message(tid, msg.get("role", "user"), msg.get("content", ""))
        return tid

    def add_message(self, thread_id: str, role: str, content: str, **kwargs: Any) -> None:
        self._store.add_message(thread_id, role, content, **kwargs)

    def get_thread(self, thread_id: str) -> Optional[ChatThread]:
        return self._store.get_thread(thread_id)

    def list_threads(self, *, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        return self._store.list_threads(limit=limit, offset=offset)

    def delete_thread(self, thread_id: str) -> bool:
        return self._store.delete_thread(thread_id)

    def search(self, query: str, *, limit: int = 20) -> List[Dict[str, Any]]:
        return self._store.search(query, limit=limit)
