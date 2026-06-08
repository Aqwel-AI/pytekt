"""Aion agent dashboard shell and input prompt."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from ..constants import AGENT_PROVIDER, DISPLAY_PROVIDERS
from .style import (
    accent,
    accent_bright,
    accent_muted,
    bold,
    dim,
    pad_visible,
    primary,
)

API_PROVIDERS: List[Tuple[str, str, Optional[str]]] = [
    (pid, label, None) for pid, label in DISPLAY_PROVIDERS
]

BOX_WIDTH = 74
INNER = BOX_WIDTH - 2
COL_W = (INNER - 3) // 2  # " " + left + " │ " + right + " "


def _line(content: str = "") -> str:
    return accent("│") + pad_visible(content, INNER) + accent("│")


def _split(left: str, right: str) -> str:
    return accent("│ ") + pad_visible(left, COL_W) + accent(" │ ") + pad_visible(right, COL_W) + accent(" │")


def _rule() -> str:
    return accent("├" + "─" * INNER + "┤")


def _ollama_available() -> bool:
    try:
        from ...providers.ollama import OllamaProvider

        return bool(OllamaProvider.list_models())
    except Exception:
        return False


def _provider_status(cfg: Dict[str, Any], session: Any, provider_id: str, env_var: Optional[str]) -> str:
    del cfg, env_var
    if provider_id != AGENT_PROVIDER:
        return accent_muted("◎ coming soon")
    if session.connected and session.provider == provider_id:
        return accent_bright("● active")
    if _ollama_available():
        return accent("● local")
    return dim("○ offline")


def _provider_row(label: str, status: str) -> str:
    width = INNER - 4
    dots_len = max(2, width - len(label) - 12)
    dots = dim("." * dots_len)
    return f"  {label} {dots} {status}"


def print_aion_dashboard(
    *,
    cfg: Dict[str, Any],
    session: Any,
    version: str,
    workspace: str,
    user_name: Optional[str] = None,
) -> None:
    name = (user_name or os.environ.get("USER", "Developer")).split("@")[0]
    if name and name[0].islower():
        name = name[0].upper() + name[1:]

    cwd = workspace.replace(os.path.expanduser("~"), "~")
    if len(cwd) > INNER - 6:
        cwd = "…" + cwd[-(INNER - 7) :]

    if session.connected and session.provider:
        prov = session.provider.replace("_", " ").title()
        model = session.model or ""
        session_txt = accent_bright(f"● {prov}") + (accent_muted(f" · {model}") if model else "")
    else:
        session_txt = accent_muted("○ Not connected")

    title = primary(bold("AION")) + dim(" · ") + accent_muted("Coding Agent")

    print()
    print(accent("┌" + "─" * INNER + "┐"))
    print(_split(title, accent_muted(f"v{version}")))
    print(_rule())
    print(_line(primary(f"  Welcome, {name}")))
    try:
        from ..context_info import get_agent_context

        ctx = get_agent_context()
        print(_line(accent_muted(f"  {ctx['line_short']}")))
    except Exception:
        pass
    print(_line(""))
    print(_split(accent_muted("SESSION"), accent_muted("QUICK START")))
    print(_split(f"  {session_txt}", dim("  /connect ollama")))
    print(_split(dim(f"  {cwd}"), dim("  /init → AION.md")))
    print(_split("", dim("  Ask in plain language")))
    print(_rule())
    print(_line(accent_muted("  PROVIDERS")))
    for _pid, label, env_var in API_PROVIDERS:
        st = _provider_status(cfg, session, _pid, env_var)
        print(_line(_provider_row(label, st)))
    print(_rule())
    print(_line(accent_muted("  ACTIVITY")))
    print(_line(dim("  No recent activity")))
    print(accent("└" + "─" * INNER + "┘"))
    print()


def print_input_area(*, connected: bool) -> None:
    hint = "Describe a task or edit" if connected else "/connect ollama"
    print(f"{accent(bold('You'))} {dim('»')} {accent_muted(hint)}")
    if connected:
        print(dim("  / for commands  ·  /disconnect to go offline"))
    else:
        print(dim("  /connect ollama  ·  type / for command help"))


def aion_input_prompt() -> str:
    return input(f"{accent(bold('You'))} {dim('» ')}").strip()


def print_shortcuts() -> None:
    print()
    print(accent_bright("  Commands"))
    print(dim("  ─────────────────────────────────────"))
    for cmd, desc in (
        ("/", "List slash commands (or /partial to filter)"),
        ("/connect", "Pick from installed Ollama models"),
        ("/connect <model>", "Connect to a specific Ollama model"),
        ("/disconnect [name]", "Go offline"),
        ("/idle off", "Keep connection after restart (default)"),
        ("/idle 30", "Auto-disconnect after 30 min idle"),
        ("quit", "Exit agent"),
    ):
        print(f"  {accent(cmd):22} {dim(desc)}")
    print()


def write_aion_md(workspace: str) -> str:
    path = os.path.join(workspace, "AION.md")
    if os.path.exists(path):
        return f"{path} already exists."
    content = """# AION.md — instructions for the Aion agent

## Project
Describe your stack and conventions.

## Commands
- Tests: pytest

## Rules
- Small focused changes; run tests when possible.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Created {path}"
