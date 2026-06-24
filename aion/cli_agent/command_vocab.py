"""Shared slash-command vocabulary for CLI autocomplete and web suggestions."""

from __future__ import annotations

import difflib
from typing import List, Tuple

# (command, args hint, description)
SLASH_COMMANDS: List[Tuple[str, str, str]] = [
    ("mode", "[plain|agent|debug|plan|review|test]", "Interaction mode"),
    ("connect", "[provider] [model]", "Connect to a provider"),
    ("reconnect", "[model]", "Reconnect to saved provider"),
    ("disconnect", "[forget|keys]", "Go offline; forget clears saved connection"),
    ("status", "", "Show session status"),
    ("reset", "", "Clear conversation memory"),
    ("pin", "<path>", "Pin path to every turn"),
    ("unpin", "[path]", "Remove pin (or all)"),
    ("pins", "", "List pinned paths"),
    ("undo", "", "Restore last file snapshot"),
    ("audit", "", "Show recent audit log"),
    ("tools", "[on|off]", "Force tool use on/off"),
    ("root", "add <path>", "Add workspace root"),
    ("approve", "", "Execute pending plan"),
    ("research", "<query>", "Read-only subagent research"),
    ("commit", "[message]", "Git commit"),
    ("branch", "<name>", "Create/switch branch"),
    ("pr-summary", "", "Generate PR summary from git"),
    ("models", "", "Refresh dashboard"),
    ("init", "", "Create AION.md in this folder"),
    ("idle", "[minutes|off]", "Auto-disconnect after idle (0 = never)"),
    ("help", "", "Show all commands"),
    ("usage", "", "Open usage dashboard in browser"),
    ("web", "", "Open agent web UI in browser"),
    ("db", "status|sync|memory", "Database status, sync usage/tracker, memory"),
    ("sky", "[tonight|moon|log|web]", "Moon phase, visible stars, or web dashboard"),
    ("quit", "", "Exit agent"),
]

_CONNECT_PROVIDERS = ("ollama", "nvidia", "nim")


def slash_command_names() -> List[str]:
    return [cmd for cmd, _, _ in SLASH_COMMANDS]


def connect_provider_names() -> List[str]:
    return list(_CONNECT_PROVIDERS)


def suggest_slash(partial: str, *, limit: int = 12) -> List[str]:
    """Return slash command names matching *partial* (without leading ``/``)."""
    p = partial.lower().strip()
    names = slash_command_names()
    if not p:
        return names[:limit]
    direct = [n for n in names if n.startswith(p)]
    fuzzy = difflib.get_close_matches(p, names, n=limit, cutoff=0.4)
    merged = direct + [n for n in fuzzy if n not in direct]
    return merged[:limit]


def suggest_connect_args(partial: str, *, limit: int = 8) -> List[str]:
    """Suggest provider names after ``/connect ``."""
    p = partial.lower().strip()
    names = connect_provider_names()
    if not p:
        return names[:limit]
    direct = [n for n in names if n.startswith(p)]
    fuzzy = difflib.get_close_matches(p, names, n=limit, cutoff=0.4)
    merged = direct + [n for n in fuzzy if n not in direct]
    return merged[:limit]


def complete_slash_line(line: str) -> List[str]:
    """
    Return full-line completion candidates for readline.

    Examples: ``/con`` → ``/connect``; ``/connect nv`` → ``/connect nvidia``.
    """
    if not line.startswith("/"):
        return []
    body = line[1:]
    if " " not in body:
        partial = body
        return [f"/{name}" for name in suggest_slash(partial)]
    cmd, _, rest = body.partition(" ")
    if cmd.lower() == "connect":
        partial = rest.strip()
        if not partial or " " not in partial:
            token = partial.split()[0] if partial else ""
            return [f"/connect {name}" for name in suggest_connect_args(token)]
    return []
