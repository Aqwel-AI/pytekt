"""Connection and collection base types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional

from .types import ColProxy, Filter, parse_filters


class Collection(ABC):
    """Dict-style document collection API."""

    def __init__(self, connection: "Connection", name: str) -> None:
        self._conn = connection
        self.name = name

    def hybrid_search(self, **kwargs: Any) -> List[Dict[str, Any]]:
        from .features.hybrid import hybrid_search

        return hybrid_search(self._conn, self.name, **kwargs)

    @abstractmethod
    def insert(self, document: Dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def insert_many(self, documents: List[Dict[str, Any]]) -> List[Any]:
        ...

    @abstractmethod
    def find(self, **filters: Any) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def find_one(self, **filters: Any) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    def update(self, query: Dict[str, Any], patch: Dict[str, Any]) -> int:
        ...

    @abstractmethod
    def delete(self, **filters: Any) -> int:
        ...

    @abstractmethod
    def count(self, **filters: Any) -> int:
        ...

    def _filters(self, **kwargs: Any) -> List[Filter]:
        return parse_filters(kwargs)


class QueryBackend(ABC):
    """Methods query builder delegates to."""

    @abstractmethod
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
        ...

    @abstractmethod
    def execute_count(self, table: str, *, filters: List[Filter]) -> int:
        ...


class Connection(QueryBackend):
    """Database connection with collection and query-builder access."""

    engine: str = "unknown"

    def __init__(self) -> None:
        self.col = ColProxy()

    @abstractmethod
    def collection(self, name: str) -> Collection:
        ...

    def table(self, name: str) -> "Query":
        from .query import Query

        return Query(self, name)

    def __getattr__(self, name: str) -> Collection:
        if name.startswith("_") or name in ("col", "table", "collection", "engine"):
            raise AttributeError(name)
        return self.collection(name)

    def close(self) -> None:
        """Close underlying connections (override in backends)."""

    def __enter__(self) -> "Connection":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
