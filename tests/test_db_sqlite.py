"""Tests for pytekt.db SQLite backend."""

import os
import tempfile

import pytekt.db as db
from pytekt.store import KeyValueStore


def test_connect_and_dict_api():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")
        conn = db.connect(f"sqlite:///{path}")
        conn.users.insert({"name": "Alice", "score": 10})
        conn.users.insert({"name": "Bob", "score": 5})
        rows = conn.users.find(name="Alice")
        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"
        assert conn.users.count() == 2
        conn.users.update({"name": "Bob"}, {"score": 7})
        bob = conn.users.find_one(name="Bob")
        assert bob is not None
        assert bob["score"] == 7
        conn.close()


def test_query_builder():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "q.db")
        conn = db.connect(f"sqlite:///{path}")
        conn.users.insert({"name": "A", "age": 30})
        conn.users.insert({"name": "B", "age": 20})
        rows = (
            conn.table("users")
            .where(conn.col.age > 25)
            .select("name", "age")
            .order_by("age", desc=True)
            .all()
        )
        assert len(rows) == 1
        assert rows[0]["name"] == "A"
        conn.close()


def test_store_compat():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "kv.db")
        conn = db.connect(f"sqlite:///{path}")
        conn.kv.set("k1", {"x": 1})
        assert conn.kv.get("k1") == {"x": 1}
        kv = KeyValueStore(path)
        kv.set("k2", {"y": 2})
        assert kv.get("k2") == {"y": 2}
        conn.close()


def test_agent_memory():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "agent.db")
        conn = db.connect(f"sqlite:///{path}")
        mem = db.agent_memory(conn, thread_id="t1")
        mem.append("user", "hi")
        mem.append("assistant", "hello")
        msgs = mem.load_messages()
        assert len(msgs) == 2
        assert msgs[0]["role"] == "user"
        conn.close()


def test_hybrid_search():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "hyb.db")
        conn = db.connect(f"sqlite:///{path}")
        conn.docs.insert({
            "content": "transformer training guide",
            "embedding": [1.0, 0.0, 0.0],
            "source": "paper",
        })
        conn.docs.insert({
            "content": "cooking recipes",
            "embedding": [0.0, 1.0, 0.0],
            "source": "blog",
        })
        hits = conn.docs.hybrid_search(
            text="transformer",
            vector=[1.0, 0.0, 0.0],
            filter={"source": "paper"},
            top_k=5,
        )
        assert len(hits) >= 1
        assert "transformer" in hits[0]["content"]
        conn.close()


def test_bulk_upsert():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "bulk.db")
        conn = db.connect(f"sqlite:///{path}")
        n = db.bulk_upsert(conn, "items", [{"id": 1, "v": 1}, {"id": 2, "v": 2}])
        assert n == 2
        n2 = db.bulk_upsert(conn, "items", [{"id": 1, "v": 9}])
        assert n2 == 1
        one = conn.items.find_one(id=1)
        assert one is not None
        assert one["v"] == 9
        conn.close()


def test_supported_engines():
    engines = db.supported_engines()
    assert "sqlite" in engines
    assert "mongodb" in engines
