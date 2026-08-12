"""Filter operators and field descriptors for :mod:`aion.db`."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

OP_SUFFIXES = {
    "eq": "eq",
    "ne": "ne",
    "gt": "gt",
    "gte": "gte",
    "lt": "lt",
    "lte": "lte",
    "in": "in",
    "nin": "nin",
    "contains": "contains",
    "startswith": "startswith",
    "regex": "regex",
    "exists": "exists",
}


@dataclass(frozen=True)
class Filter:
    field: str
    op: str
    value: Any


@dataclass(frozen=True)
class ColumnRef:
    """Used in query builder: ``conn.col.age > 25``."""

    name: str

    def _filter(self, op: str, value: Any) -> Filter:
        return Filter(self.name, op, value)

    def __eq__(self, other: object) -> Filter:
        return self._filter("eq", other)

    def __ne__(self, other: object) -> Filter:
        return self._filter("ne", other)

    def __gt__(self, other: object) -> Filter:
        return self._filter("gt", other)

    def __ge__(self, other: object) -> Filter:
        return self._filter("gte", other)

    def __lt__(self, other: object) -> Filter:
        return self._filter("lt", other)

    def __le__(self, other: object) -> Filter:
        return self._filter("lte", other)


class ColProxy:
    """Attribute access yields :class:`ColumnRef` (``conn.col.age``)."""

    def __getattr__(self, name: str) -> ColumnRef:
        return ColumnRef(name)

    def __getitem__(self, name: str) -> ColumnRef:
        return ColumnRef(name)


def parse_filters(kwargs: Dict[str, Any]) -> List[Filter]:
    """Parse ``name__gte=5`` style kwargs into :class:`Filter` list."""
    filters: List[Filter] = []
    for key, value in kwargs.items():
        if "__" in key:
            field, suffix = key.rsplit("__", 1)
            op = OP_SUFFIXES.get(suffix)
            if op is None:
                field = key
                op = "eq"
        else:
            field, op = key, "eq"
        filters.append(Filter(field, op, value))
    return filters


def compile_sql_filters(
    filters: List[Filter],
    *,
    json_columns: Tuple[str, ...] = (),
) -> Tuple[str, List[Any]]:
    """Compile filters to SQL WHERE clause and parameters."""
    if not filters:
        return "", []
    parts: List[str] = []
    params: List[Any] = []
    for f in filters:
        col = f.field
        if f.op == "eq":
            parts.append(f"{col} = ?")
            params.append(f.value)
        elif f.op == "ne":
            parts.append(f"{col} != ?")
            params.append(f.value)
        elif f.op == "gt":
            parts.append(f"{col} > ?")
            params.append(f.value)
        elif f.op == "gte":
            parts.append(f"{col} >= ?")
            params.append(f.value)
        elif f.op == "lt":
            parts.append(f"{col} < ?")
            params.append(f.value)
        elif f.op == "lte":
            parts.append(f"{col} <= ?")
            params.append(f.value)
        elif f.op == "in":
            vals = list(f.value)
            if not vals:
                parts.append("0 = 1")
            else:
                parts.append(f"{col} IN ({','.join('?' * len(vals))})")
                params.extend(vals)
        elif f.op == "nin":
            vals = list(f.value)
            if not vals:
                parts.append("1 = 1")
            else:
                parts.append(f"{col} NOT IN ({','.join('?' * len(vals))})")
                params.extend(vals)
        elif f.op == "contains":
            if col in json_columns:
                parts.append(f"{col} LIKE ?")
                params.append(f"%{f.value}%")
            else:
                parts.append(f"{col} LIKE ?")
                params.append(f"%{f.value}%")
        elif f.op == "startswith":
            parts.append(f"{col} LIKE ?")
            params.append(f"{f.value}%")
        elif f.op == "regex":
            parts.append(f"{col} REGEXP ?")
            params.append(f.value if isinstance(f.value, str) else re.escape(str(f.value)))
        elif f.op == "exists":
            if f.value:
                parts.append(f"{col} IS NOT NULL")
            else:
                parts.append(f"{col} IS NULL")
        else:
            parts.append(f"{col} = ?")
            params.append(f.value)
    return " AND ".join(parts), params
