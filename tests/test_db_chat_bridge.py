"""Tests for chat bridge and agent DB integration helpers."""

import os
import tempfile

from aion.db.chat_bridge import ChatBridge
from aion.db.settings import get_db_connection, default_db_url
from aion.store import ChatHistoryStore


def test_chat_bridge_save_thread():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "chat.db")
        bridge = ChatBridge(ChatHistoryStore(path))
        tid = bridge.save_thread(
            [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}],
            title="Test",
        )
        thread = bridge.get_thread(tid)
        assert thread is not None
        assert len(thread.messages) == 2


def test_sqlite_conn_chat_property():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "app.db")
        conn = get_db_connection(url=f"sqlite:///{path}")
        tid = conn.chat.save_thread(
            [{"role": "user", "content": "ping"}],
            title="sqlite",
        )
        assert tid
        conn.close()


def test_default_db_url():
    assert default_db_url().startswith("sqlite:///")
