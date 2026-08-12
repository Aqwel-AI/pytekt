"""Redis backend (optional: pip install pytekt[db])."""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, Optional

from ..base import Connection
from ..document import DocumentCollection
from ..errors import QueryError
from ..pool import ClientHolder
from ..types import Filter, parse_filters


def _require_redis():
    try:
        import redis  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "Redis support requires redis-py. Install with: pip install pytekt[db]"
        ) from e


def _safe_name(name: str) -> str:
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise QueryError(f"Invalid collection name: {name!r}")
    return name


class RedisCollection(DocumentCollection):
    def __init__(self, connection: "RedisConnection", name: str) -> None:
        super().__init__(connection, _safe_name(name))

    def _prefix(self) -> str:
        return f"pytekt:{self.name}:"

    def _load(self, key: str) -> Optional[Dict[str, Any]]:
        raw = self._conn._client.get(key)
        if raw is None:
            return None
        doc = json.loads(raw)
        doc["_key"] = key
        return doc

    def _all_docs(self) -> List[Dict[str, Any]]:
        prefix = self._prefix()
        docs = []
        for key in self._conn._client.scan_iter(match=prefix + "*"):
            k = key.decode() if isinstance(key, bytes) else key
            doc = self._load(k)
            if doc:
                docs.append(doc)
        return docs

    def _match(self, doc: Dict[str, Any], filters: List[Filter]) -> bool:
        for f in filters:
            val = doc.get(f.field)
            if f.op == "eq" and val != f.value:
                return False
            if f.op == "ne" and val == f.value:
                return False
            if f.op == "gt" and not (val is not None and val > f.value):
                return False
            if f.op == "gte" and not (val is not None and val >= f.value):
                return False
            if f.op == "lt" and not (val is not None and val < f.value):
                return False
            if f.op == "lte" and not (val is not None and val <= f.value):
                return False
            if f.op == "contains" and not (val is not None and str(f.value) in str(val)):
                return False
        return True

    def insert(self, document: Dict[str, Any]) -> Any:
        doc = dict(document)
        doc_id = str(doc.pop("id", None) or uuid.uuid4().hex[:12])
        key = self._prefix() + doc_id
        doc["id"] = doc_id
        ttl = doc.pop("_ttl", None)
        payload = json.dumps(doc, default=str)
        if ttl:
            self._conn._client.setex(key, int(ttl), payload)
        else:
            self._conn._client.set(key, payload)
        return doc_id

    def insert_many(self, documents: List[Dict[str, Any]]) -> List[Any]:
        return [self.insert(d) for d in documents]

    def find(self, **filters: Any) -> List[Dict[str, Any]]:
        limit = filters.pop("_limit", None)
        parsed = parse_filters(filters)
        rows = [d for d in self._all_docs() if self._match(d, parsed)]
        if limit is not None:
            rows = rows[: int(limit)]
        return rows

    def update(self, query: Dict[str, Any], patch: Dict[str, Any]) -> int:
        n = 0
        for doc in self.find(**query):
            key = doc.pop("_key", None)
            if not key:
                continue
            doc.update(patch)
            self._conn._client.set(key, json.dumps(doc, default=str))
            n += 1
        return n

    def delete(self, **filters: Any) -> int:
        n = 0
        for doc in self.find(**filters):
            key = doc.get("_key")
            if key and self._conn._client.delete(key):
                n += 1
        return n

    def count(self, **filters: Any) -> int:
        return len(self.find(**filters))

    def set(self, key: str, value: Any, *, ttl: Optional[int] = None) -> None:
        payload = json.dumps(value, default=str)
        full = self._prefix() + key
        if ttl:
            self._conn._client.setex(full, ttl, payload)
        else:
            self._conn._client.set(full, payload)

    def get(self, key: str, default: Any = None) -> Any:
        raw = self._conn._client.get(self._prefix() + key)
        if raw is None:
            return default
        return json.loads(raw)


class RedisConnection(Connection):
    engine = "redis"

    def __init__(self, cfg: Dict[str, Any]) -> None:
        _require_redis()
        import redis

        super().__init__()
        host = cfg.get("host", "localhost")
        port = int(cfg.get("port") or 6379)
        db = int(cfg.get("database") or cfg.get("db") or 0)
        password = cfg.get("password")
        self._holder = ClientHolder()

        def factory():
            return redis.Redis(host=host, port=port, db=db, password=password, decode_responses=False)

        self._client = self._holder.get_or_create(factory)

    def collection(self, name: str) -> RedisCollection:
        return RedisCollection(self, name)

    def execute_query(
        self,
        table: str,
        *,
        filters: List[Filter],
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        coll = self.collection(table)
        kwargs = {f.field if f.op == "eq" else f"{f.field}__{f.op}": f.value for f in filters}
        rows = coll.find(**kwargs)
        if order_by:
            rows.sort(key=lambda r: r.get(order_by), reverse=order_desc)
        if offset:
            rows = rows[int(offset) :]
        if limit is not None:
            rows = rows[: int(limit)]
        if columns:
            rows = [{c: r.get(c) for c in columns} for r in rows]
        return rows

    def execute_count(self, table: str, *, filters: List[Filter]) -> int:
        kwargs = {f.field if f.op == "eq" else f"{f.field}__{f.op}": f.value for f in filters}
        return self.collection(table).count(**kwargs)

    def close(self) -> None:
        self._holder.close()


def connect_redis(cfg: Dict[str, Any]) -> RedisConnection:
    return RedisConnection(cfg)
