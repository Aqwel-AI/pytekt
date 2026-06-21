"""Slash-command help shown when the user types ``/`` or ``/partial``."""

from __future__ import annotations

from typing import List, Tuple

from .style import accent, accent_muted, bold, dim

# (command, args hint, description)
SLASH_COMMANDS: List[Tuple[str, str, str]] = [
    ("mode", "[plain|agent|debug|plan|review|test]", "Interaction mode"),
    ("connect", "[provider] [model]", "Connect to a provider"),
    ("reconnect", "[model]", "Reconnect to saved provider"),
    ("disconnect", "[provider] [keys]", "Go offline; add keys to remove API key"),
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
    print(dim("  Tip: @file @folder @git in messages attach context"))
    print()
