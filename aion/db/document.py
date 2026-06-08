"""Concrete collection mixin helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import Collection


class DocumentCollection(Collection):
    """Shared helpers for SQL-backed collections."""

    def find_one(self, **filters: Any) -> Optional[Dict[str, Any]]:
        rows = self.find(**{**filters, "_limit": 1})  # type: ignore[arg-type]
        return rows[0] if rows else None
