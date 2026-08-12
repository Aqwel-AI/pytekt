"""Pipeline steps for database read/write."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..pipeline.core import Step
from .base import Connection
from .features.bulk import bulk_upsert


class DbReadStep(Step):
    """Load rows from a table/collection into pipeline data."""

    name = "db_read"

    def __init__(
        self,
        conn: Connection,
        table: str,
        *,
        filters: Optional[Dict[str, Any]] = None,
        as_key: str = "rows",
    ) -> None:
        self.conn = conn
        self.table = table
        self.filters = filters or {}
        self.as_key = as_key

    def run(self, data: Any, ctx: Dict[str, Any]) -> Any:
        rows = self.conn.collection(self.table).find(**self.filters)
        if isinstance(data, dict):
            out = dict(data)
            out[self.as_key] = rows
            return out
        ctx[self.as_key] = rows
        return data


class DbWriteStep(Step):
    """Insert pipeline documents into a table/collection."""

    name = "db_write"

    def __init__(
        self,
        conn: Connection,
        table: str,
        *,
        data_key: str = "rows",
    ) -> None:
        self.conn = conn
        self.table = table
        self.data_key = data_key

    def run(self, data: Any, ctx: Dict[str, Any]) -> Any:
        rows: List[Dict[str, Any]]
        if isinstance(data, dict) and self.data_key in data:
            rows = list(data[self.data_key])
        elif self.data_key in ctx:
            rows = list(ctx[self.data_key])
        elif isinstance(data, list):
            rows = data
        else:
            rows = [data] if isinstance(data, dict) else []
        self.conn.collection(self.table).insert_many(rows)
        return data


class DbUpsertStep(Step):
    """Bulk upsert documents from pipeline data."""

    name = "db_upsert"

    def __init__(
        self,
        conn: Connection,
        table: str,
        *,
        data_key: str = "rows",
        key_field: str = "id",
    ) -> None:
        self.conn = conn
        self.table = table
        self.data_key = data_key
        self.key_field = key_field

    def run(self, data: Any, ctx: Dict[str, Any]) -> Any:
        if isinstance(data, dict) and self.data_key in data:
            rows = list(data[self.data_key])
        elif self.data_key in ctx:
            rows = list(ctx[self.data_key])
        elif isinstance(data, list):
            rows = data
        else:
            rows = []
        bulk_upsert(self.conn, self.table, rows, key_field=self.key_field)
        return data
