"""Schema inference and lite table creation."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Set, Tuple


def _value_type(value: Any) -> str:
    if value is None:
        return "text"
    if isinstance(value, bool):
        return "integer"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "real"
    if isinstance(value, (dict, list)):
        return "json"
    return "text"


def infer_columns(document: Dict[str, Any]) -> Dict[str, str]:
    """Infer SQL column types from a sample document."""
    cols: Dict[str, str] = {"id": "integer"}
    for key, value in document.items():
        if key == "id":
            continue
        cols[key] = _value_type(value)
    return cols


def merge_columns(
    existing: Dict[str, str],
    document: Dict[str, Any],
) -> Dict[str, str]:
    merged = dict(existing)
    for key, value in document.items():
        if key == "id":
            continue
        new_t = _value_type(value)
        if key not in merged:
            merged[key] = new_t
        elif merged[key] != new_t and merged[key] != "json":
            merged[key] = "json"
    return merged


def sql_type_sqlite(col_type: str) -> str:
    return {
        "integer": "INTEGER",
        "real": "REAL",
        "text": "TEXT",
        "json": "TEXT",
    }.get(col_type, "TEXT")


def sql_type_mysql(col_type: str) -> str:
    return {
        "integer": "BIGINT",
        "real": "DOUBLE",
        "text": "TEXT",
        "json": "JSON",
    }.get(col_type, "TEXT")


def sql_type_postgres(col_type: str) -> str:
    return {
        "integer": "BIGINT",
        "real": "DOUBLE PRECISION",
        "text": "TEXT",
        "json": "JSONB",
    }.get(col_type, "TEXT")


def serialize_value(value: Any, *, engine: str) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    return value


def deserialize_row(row: Dict[str, Any], json_columns: Set[str]) -> Dict[str, Any]:
    out = dict(row)
    for col in json_columns:
        if col in out and isinstance(out[col], str):
            try:
                out[col] = json.loads(out[col])
            except (json.JSONDecodeError, TypeError):
                pass
    return out
