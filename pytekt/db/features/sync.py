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
    """Import JSONL usage events into a collection/table."""
    events_path = path or os.path.expanduser("~/.pytekt/usage/events.jsonl")
    if not os.path.isfile(events_path):
        return 0
    events = []
    with open(events_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                ev.setdefault("id", i)
                events.append(ev)
            except Exception:
                continue
    if not events:
        return 0
    return bulk_upsert(conn, table, events, key_field="id")


def sync_tracker(
    conn: Connection,
    *,
    root: str = ".pytekt_runs",
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
