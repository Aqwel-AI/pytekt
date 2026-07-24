"""
Persistent storage: key-value store, vector store, and chat history.

All stores use SQLite for zero-dependency persistence.

Examples
--------
>>> from aion.store import KeyValueStore
>>> kv = KeyValueStore("app.db")
>>> kv.set("user:1", {"name": "Alice"})
>>> kv.get("user:1")
{'name': 'Alice'}
"""

from .kv import KeyValueStore
from .vector import PersistentVectorStore
from .chat_history import ChatHistoryStore, ChatThread

__all__ = [
    "ChatHistoryStore",
    "ChatThread",
    "KeyValueStore",
    "PersistentVectorStore",
]
