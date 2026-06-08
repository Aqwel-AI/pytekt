"""Agent slash commands for :mod:`aion.db`."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..db.features.agent import AgentMemoryStore
from ..db.settings import db_url_from_config, get_db_connection
from ..db import sync_tracker, sync_usage
from . import ui


def handle_db_command(args: str, *, cfg: Dict[str, Any], memory: Optional[AgentMemoryStore]) -> None:
    """
    Handle ``/db`` subcommands: status, sync usage, sync tracker, memory.
    """
    parts = args.split(maxsplit=1)
    sub = (parts[0].lower() if parts else "status").strip()
    rest = parts[1] if len(parts) > 1 else ""

    if sub in ("status", "?"):
        url = db_url_from_config(cfg)
        ui.info_print(f"Database: {ui.cyan(url)}")
        try:
            conn = get_db_connection(cfg)
            ui.info_print(f"Engine: {ui.bold(conn.engine)} · OK")
            conn.close()
        except Exception as e:
            ui.error_print(f"Connection failed: {e}")
        if memory:
            ui.info_print(f"Agent thread: {ui.accent_muted(memory.thread_id)}")
        return

    if sub == "sync":
        target = rest.lower() if rest else "all"
        try:
            conn = get_db_connection(cfg)
            try:
                if target in ("usage", "all"):
                    n = sync_usage(conn)
                    ui.success_print(f"Synced {ui.bold(str(n))} usage events.")
                if target in ("tracker", "all"):
                    n = sync_tracker(conn)
                    ui.success_print(f"Synced {ui.bold(str(n))} experiment runs.")
                if target not in ("usage", "tracker", "all"):
                    ui.error_print("Usage: /db sync usage | tracker | all")
            finally:
                conn.close()
        except Exception as e:
            ui.error_print(str(e))
        return

    if sub == "memory":
        if not memory:
            ui.error_print("Agent memory not initialized.")
            return
        if rest == "clear":
            memory.clear()
            ui.success_print("Cleared agent memory for this thread.")
            return
        msgs = memory.load_messages()
        ui.info_print(f"Thread {ui.bold(memory.thread_id)} · {len(msgs)} messages")
        return

    ui.error_print(
        f"Unknown /db command {ui.bold(sub)}. "
        f"Try {ui.cyan('/db status')}, {ui.cyan('/db sync all')}, {ui.cyan('/db memory')}."
    )
