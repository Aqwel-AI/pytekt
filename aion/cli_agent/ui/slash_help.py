"""Slash-command help shown when the user types ``/`` or ``/partial``."""

from __future__ import annotations

from ..command_vocab import SLASH_COMMANDS, suggest_slash
from .style import accent, accent_muted, bold, dim


def print_slash_help(prefix: str = "") -> None:
    """List commands matching *prefix* (empty = show all)."""
    p = prefix.lower().strip()
    if p:
        matched_names = set(suggest_slash(p, limit=50))
        matches = [
            (cmd, args_hint, desc)
            for cmd, args_hint, desc in SLASH_COMMANDS
            if cmd in matched_names
        ]
    else:
        matches = list(SLASH_COMMANDS)
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
