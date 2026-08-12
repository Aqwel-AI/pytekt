"""
Unified database layer for PyTekt.

Pythonic dict API and query builder across SQLite, MySQL, PostgreSQL,
MongoDB, and Redis.

Examples
--------
>>> import pytekt.db as db
>>> conn = db.connect("sqlite://./app.db")
>>> conn.users.insert({"name": "Alice", "score": 10})
>>> conn.users.find(name="Alice")
[{'id': 1, 'name': 'Alice', 'score': 10}]
"""

from .base import Collection, Connection
from .cached import cached
from .errors import (
    ConnectionError,
    DbError,
    DuplicateKeyError,
    NotFoundError,
    QueryError,
)
from .factory import connect, create_db, supported_engines
from .settings import db_url_from_config, get_db_connection
from .features import (
    AgentMemoryStore,
    agent_memory,
    bulk_insert,
    bulk_upsert,
    hybrid_search,
    sync_tracker,
    sync_usage,
)
from .pipeline import DbReadStep, DbUpsertStep, DbWriteStep
from .query import Query
from .types import ColProxy, ColumnRef, Filter

__all__ = [
    "AgentMemoryStore",
    "Collection",
    "ColumnRef",
    "ColProxy",
    "Connection",
    "ConnectionError",
    "DbError",
    "DbReadStep",
    "DbUpsertStep",
    "DbWriteStep",
    "DuplicateKeyError",
    "Filter",
    "NotFoundError",
    "Query",
    "QueryError",
    "agent_memory",
    "bulk_insert",
    "bulk_upsert",
    "cached",
    "connect",
    "create_db",
    "db_url_from_config",
    "get_db_connection",
    "hybrid_search",
    "supported_engines",
    "sync_tracker",
    "sync_usage",
]
