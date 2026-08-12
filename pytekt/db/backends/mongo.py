"""MongoDB backend (optional: pip install pytekt[db])."""

from __future__ import annotations

import json
import re
import threading
from typing import Any, Dict, Iterator, List, Optional

from ..base import Connection
from ..document import DocumentCollection
from ..errors import ConnectionError, QueryError
from ..pool import ClientHolder
from ..types import Filter, parse_filters


def _require_pymongo():
    try:
        import pymongo  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "MongoDB support requires pymongo. Install with: pip install pytekt[db]"
        ) from e


def _safe_collection(name: str) -> str:
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise QueryError(f"Invalid collection name: {name!r}")
    return name


def _mongo_filter(filters: List[Filter]) -> Dict[str, Any]:
    q: Dict[str, Any] = {}
    for f in filters:
        if f.op == "eq":
            q[f.field] = f.value
        elif f.op == "ne":
            q[f.field] = {"$ne": f.value}
        elif f.op == "gt":
            q[f.field] = {"$gt": f.value}
        elif f.op == "gte":
            q[f.field] = {"$gte": f.value}
        elif f.op == "lt":
            q[f.field] = {"$lt": f.value}
        elif f.op == "lte":
            q[f.field] = {"$lte": f.value}
        elif f.op == "in":
            q[f.field] = {"$in": list(f.value)}
        elif f.op == "nin":
            q[f.field] = {"$nin": list(f.value)}
        elif f.op == "contains":
            q[f.field] = {"$regex": re.escape(str(f.value)), "$options": "i"}
        elif f.op == "startswith":
            q[f.field] = {"$regex": f"^{re.escape(str(f.value))}"}
        elif f.op == "regex":
            q[f.field] = {"$regex": f.value}
        elif f.op == "exists":
            q[f.field] = {"$exists": bool(f.value)}
        else:
            q[f.field] = f.value
    return q


class MongoCollection(DocumentCollection):
    def __init__(self, connection: "MongoConnection", name: str) -> None:
        super().__init__(connection, _safe_collection(name))

    def _col(self):
        return self._conn._db[self.name]

    def insert(self, document: Dict[str, Any]) -> Any:
        result = self._col().insert_one(dict(document))
        return result.inserted_id

    def insert_many(self, documents: List[Dict[str, Any]]) -> List[Any]:
        result = self._col().insert_many([dict(d) for d in documents])
        return list(result.inserted_ids)

    def find(self, **filters: Any) -> List[Dict[str, Any]]:
        limit = filters.pop("_limit", None)
        q = _mongo_filter(parse_filters(filters))
        cursor = self._col().find(q)
        if limit is not None:
            cursor = cursor.limit(int(limit))
        return [self._conn._normalize_doc(d) for d in cursor]

    def update(self, query: Dict[str, Any], patch: Dict[str, Any]) -> int:
        q = _mongo_filter(parse_filters(query))
        result = self._col().update_many(q, {"$set": patch})
        return int(result.modified_count)

    def delete(self, **filters: Any) -> int:
        q = _mongo_filter(parse_filters(filters))
        result = self._col().delete_many(q)
        return int(result.deleted_count)

    def count(self, **filters: Any) -> int:
        q = _mongo_filter(parse_filters(filters))
        return int(self._col().count_documents(q))

    def watch(self, *, pipeline: Optional[List[Dict[str, Any]]] = None) -> Iterator[Dict[str, Any]]:
        """Change stream on this collection."""
        kwargs: Dict[str, Any] = {}
        if pipeline:
            kwargs["pipeline"] = pipeline
        with self._col().watch(**kwargs) as stream:
            for change in stream:
                yield dict(change)


class MongoConnection(Connection):
    engine = "mongodb"

    def __init__(self, cfg: Dict[str, Any]) -> None:
        _require_pymongo()
        import pymongo

        super().__init__()
        self._cfg = cfg
        self._holder = ClientHolder()
        uri = cfg.get("uri") or cfg.get("url")
        if not uri:
            host = cfg.get("host", "localhost")
            port = int(cfg.get("port") or 27017)
            user = cfg.get("username") or cfg.get("user")
            password = cfg.get("password")
            if user:
                uri = f"mongodb://{user}:{password}@{host}:{port}"
            else:
                uri = f"mongodb://{host}:{port}"
        db_name = cfg.get("database") or cfg.get("db") or "pytekt"

        def factory():
            client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
            return client[db_name]

        self._db = self._holder.get_or_create(factory)
        self._client = self._db.client

    def _normalize_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(doc)
        if "_id" in out:
            out["id"] = str(out.pop("_id"))
        return out

    def collection(self, name: str) -> MongoCollection:
        return MongoCollection(self, name)

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
        q = _mongo_filter(filters)
        pipeline: List[Dict[str, Any]] = [{"$match": q}]
        if order_by:
            pipeline.append({"$sort": {order_by: -1 if order_desc else 1}})
        if offset:
            pipeline.append({"$skip": int(offset)})
        if limit is not None:
            pipeline.append({"$limit": int(limit)})
        if columns:
            pipeline.append({"$project": {c: 1 for c in columns}})
        return [self._normalize_doc(d) for d in self._db[table].aggregate(pipeline)]

    def execute_count(self, table: str, *, filters: List[Filter]) -> int:
        return int(self._db[table].count_documents(_mongo_filter(filters)))

    def close(self) -> None:
        self._holder.close()


def connect_mongo(cfg: Dict[str, Any]) -> MongoConnection:
    return MongoConnection(cfg)
