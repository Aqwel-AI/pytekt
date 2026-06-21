"""Append-only agent audit log."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_AUDIT_PATH = Path.home() / ".aion" / "agent_audit.jsonl"


def _ensure_parent() -> None:
    _AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)


def log_action(
    *,
    action: str,
    path: Optional[str] = None,
    command: Optional[str] = None,
    provider: Optional[str] = None,
    session_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    _ensure_parent()
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "path": path,
        "command": command,
        "provider": provider,
        "session_id": session_id,
    }
    if extra:
        entry.update(extra)
    with _AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_recent(n: int = 20) -> List[Dict[str, Any]]:
    if not _AUDIT_PATH.is_file():
        return []
    lines = _AUDIT_PATH.read_text(encoding="utf-8").splitlines()
    out: List[Dict[str, Any]] = []
    for line in lines[-n:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def format_recent(n: int = 20) -> str:
    entries = read_recent(n)
    if not entries:
        return "No audit entries."
    lines = []
    for e in entries:
        ts = e.get("ts", "?")[:19]
        action = e.get("action", "?")
        detail = e.get("path") or e.get("command") or ""
        lines.append(f"{ts} {action} {detail}")
    return "\n".join(lines)
