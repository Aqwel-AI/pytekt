"""Fast bulk insert and upsert."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from ..base import Connection


def bulk_insert(
    conn: Connection,
    table: str,
    documents: Sequence[Dict[str, Any]],
    *,
    batch_size: int = 500,
) -> int:
    """Insert many documents in batches."""
    coll = conn.collection(table)
    total = 0
    batch: List[Dict[str, Any]] = []
    for doc in documents:
        batch.append(dict(doc))
        if len(batch) >= batch_size:
            coll.insert_many(batch)
            total += len(batch)
            batch = []
    if batch:
        coll.insert_many(batch)
        total += len(batch)
    return total


def bulk_upsert(
    conn: Connection,
    table: str,
    documents: Sequence[Dict[str, Any]],
    *,
    key_field: str = "id",
    batch_size: int = 500,
) -> int:
    """
    Upsert documents by *key_field*.

    SQL backends update when key exists; Mongo uses replace; Redis overwrites key.
    """
    coll = conn.collection(table)
    total = 0
    for doc in documents:
        d = dict(doc)
        key_val = d.get(key_field)
        if key_val is None:
            coll.insert(d)
        else:
            existing = coll.find_one(**{key_field: key_val})
            if existing:
                coll.update({key_field: key_val}, d)
            else:
                coll.insert(d)
        total += 1
        if total % batch_size == 0:
            pass
    return total
