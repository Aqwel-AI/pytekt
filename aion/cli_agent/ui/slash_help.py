"""Slash-command help shown when the user types ``/`` or ``/partial``."""

from __future__ import annotations

from typing import List, Tuple

from .style import accent, accent_muted, bold, dim

# (command, args hint, description)
SLASH_COMMANDS: List[Tuple[str, str, str]] = [
    ("connect", "<provider> [model]", "Connect (e.g. /connect ollama)"),
    ("reconnect", "<provider>", "New API key + connect"),
    ("disconnect", "[name]", "Stop current AI or named provider/model"),
    ("models", "", "Refresh dashboard"),
    ("init", "", "Create AION.md in this folder"),
    ("idle", "[minutes|off]", "Auto-disconnect after idle (0 = never)"),
    ("help", "", "Show all commands"),
    ("usage", "", "Open usage dashboard in browser"),
    ("quit", "", "Exit agent"),
]


def print_slash_help(prefix: str = "") -> None:
    """List commands matching *prefix* (empty = show all)."""
    p = prefix.lower().strip()
    matches = [
        (cmd, args_hint, desc)
        for cmd, args_hint, desc in SLASH_COMMANDS
        if not p or cmd.startswith(p) or p in cmd
    ]
    print()
    print(accent("  / commands"))
    print(dim("  " + "─" * 40))
    if not matches:
        print(dim(f"  No commands match {accent('/' + prefix)}"))
        print(dim("  Type /help or ? for the full list."))
    else:
        for cmd, args_hint, desc in matches:
            line = accent(f"/{cmd}")
            if args_hint:
                line += accent_muted(f" {args_hint}")
            print(f"  {line:36} {dim(desc)}")
    print(dim("  Tip: type a full command, e.g. /connect ollama"))
    print()
