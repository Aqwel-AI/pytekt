"""Sync usage JSONL and experiment tracker data into a database."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from ..base import Connection
from .bulk import bulk_upsert


def sync_usage(
    conn: Connection,
    *,
    path: Optional[str] = None,
    table: str = "usage_events",
) -> int:
    """Import ``~/.pytekt/usage/events.jsonl`` into a collection/table."""
    from ...usage.store import UsageStore, default_store_path

    store = UsageStore(path or default_store_path())
    events = store.read_all()
    if not events:
        return 0
    for i, ev in enumerate(events):
        ev.setdefault("id", i + 1)
    return bulk_upsert(conn, table, events, key_field="id")


def sync_tracker(
    conn: Connection,
    *,
    root: str = ".aion_runs",
    table: str = "experiments",
) -> int:
    """Import experiment tracker run folders into a collection/table."""
    if not os.path.isdir(root):
        return 0
    rows: list[Dict[str, Any]] = []
    for name in os.listdir(root):
        run_dir = os.path.join(root, name)
        meta_path = os.path.join(run_dir, "meta.json")
        if not os.path.isfile(meta_path):
            continue
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        meta["id"] = name
        metrics_path = os.path.join(run_dir, "metrics.json")
        if os.path.isfile(metrics_path):
            with open(metrics_path, encoding="utf-8") as f:
                meta["metrics"] = json.load(f)
        rows.append(meta)
    if not rows:
        return 0
    return bulk_upsert(conn, table, rows, key_field="id")
