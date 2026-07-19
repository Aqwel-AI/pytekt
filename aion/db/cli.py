"""``aion db`` — sync, status, and quick demos."""

from __future__ import annotations

import argparse
from typing import Optional

from . import connect, supported_engines, sync_tracker, sync_usage
from .settings import db_url_from_config, get_db_connection


def _print(msg: str) -> None:
    print(msg)


def db_status(cfg: dict, *, url: Optional[str] = None) -> None:
    target = url or db_url_from_config(cfg)
    _print(f"  URL: {target}")
    _print(f"  Engines: {', '.join(supported_engines())}")
    try:
        conn = get_db_connection(cfg, url=url)
        _print(f"  Connected: {conn.engine}")
        conn.close()
    except Exception as e:
        _print(f"  Connection failed: {e}")


def db_sync_usage(cfg: dict, *, url: Optional[str] = None, table: str = "usage_events") -> int:
    conn = get_db_connection(cfg, url=url)
    try:
        return sync_usage(conn, table=table)
    finally:
        conn.close()


def db_sync_tracker(
    cfg: dict,
    *,
    url: Optional[str] = None,
    root: str = ".aion_runs",
    table: str = "experiments",
) -> int:
    conn = get_db_connection(cfg, url=url)
    try:
        return sync_tracker(conn, root=root, table=table)
    finally:
        conn.close()


def db_demo() -> None:
    conn = connect("sqlite:///:memory:")
    conn.users.insert({"name": "Alice", "score": 10})
    rows = conn.users.find(name="Alice")
    _print(f"  demo ok — {rows}")
    conn.close()


def db_main(args: argparse.Namespace) -> None:
    from ..user_config import get_config

    cfg = get_config()
    action = getattr(args, "db_action", None) or "status"

    if action in (None, "status"):
        db_status(cfg, url=getattr(args, "url", None))
        return

    if action == "sync-usage":
        n = db_sync_usage(cfg, url=getattr(args, "url", None), table=getattr(args, "table", "usage_events"))
        _print(f"  Synced {n} usage events.")
        return

    if action == "sync-tracker":
        n = db_sync_tracker(
            cfg,
            url=getattr(args, "url", None),
            root=getattr(args, "root", ".aion_runs"),
            table=getattr(args, "table", "experiments"),
        )
        _print(f"  Synced {n} experiment runs.")
        return

    if action == "demo":
        db_demo()
        return

    _print("  Unknown db action. Try: aion db status | sync-usage | sync-tracker | demo")
