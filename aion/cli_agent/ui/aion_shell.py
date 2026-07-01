"""Aion agent dashboard shell and input prompt."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from ..constants import (
    COMING_SOON_PROVIDERS,
    CONNECTABLE_PROVIDERS,
    DISPLAY_PROVIDERS,
    PROVIDER_ENV_VARS,
)
from .input import aion_input_prompt, configure_input
from .status import format_session_summary
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
    (pid, label, PROVIDER_ENV_VARS.get(pid)) for pid, label in DISPLAY_PROVIDERS
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


def _provider_has_credentials(provider_id: str, cfg: Dict[str, Any], env_var: Optional[str]) -> bool:
    if provider_id == "ollama":
        return _ollama_available()
    if env_var and os.environ.get(env_var):
        return True
    if provider_id in CONNECTABLE_PROVIDERS:
        from ...providers.keys import resolve_api_key

        return bool(resolve_api_key(provider_id, cfg))
    return False


def _provider_status(cfg: Dict[str, Any], session: Any, provider_id: str, env_var: Optional[str]) -> str:
    if provider_id in COMING_SOON_PROVIDERS:
        return accent_muted("◎ coming soon")
    if session.connected and session.provider == provider_id:
        return accent_bright("● active")
    if provider_id == "ollama":
        if _ollama_available():
            return accent("● local")
        return dim("○ offline")
    if _provider_has_credentials(provider_id, cfg, env_var):
        return accent("● ready")
    return dim("○ no key")


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

    summary = format_session_summary(session)
    summary_lines = summary.split("\n")
    session_line = summary_lines[0] if summary_lines else accent_muted("○ Not connected")
    mode_line = summary_lines[1] if len(summary_lines) > 1 else ""

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
    print(_split(f"  {session_line}", dim("  /connect ollama")))
    if mode_line:
        print(_split(f"  {mode_line.strip()}", dim("  /mode agent|plain|debug")))
    print(_split(dim(f"  {cwd}"), dim("  @file @folder @git")))
    print(_split("", dim("  /init → AION.md")))
    print(_rule())
    print(_line(accent_muted("  PROVIDERS")))
    for _pid, label, env_var in API_PROVIDERS:
        st = _provider_status(cfg, session, _pid, env_var)
        print(_line(_provider_row(label, st)))
    print(_rule())
    print(_line(accent_muted("  ACTIVITY")))
    activity_text = session.activity.format_dashboard(5) if hasattr(session, "activity") else "No recent activity"
    for act_line in activity_text.split("\n"):
        print(_line(dim(act_line) if act_line.startswith("  ") else dim(f"  {act_line}")))
    print(accent("└" + "─" * INNER + "┘"))
    print()


def print_input_area(*, connected: bool) -> None:
    hint = "Describe a task or edit · use @path" if connected else "/connect ollama or nvidia"
    print(dim(f"  {hint}"))
    if connected:
        print(dim("  /mode · / for commands  ·  /disconnect to go offline"))
    else:
        print(dim("  /connect ollama  ·  /connect nvidia  ·  type / for command help"))


def print_shortcuts() -> None:
    print()
    print(accent_bright("  Commands"))
    print(dim("  ─────────────────────────────────────"))
    for cmd, desc in (
        ("/", "List slash commands (or /partial to filter)"),
        ("/mode", "plain | agent | debug"),
        ("/connect", "Pick from installed Ollama models"),
        ("/connect ollama", "Connect to Ollama"),
        ("/connect nvidia", "Connect to NVIDIA NIM (API key required)"),
        ("/connect <model>", "Connect to a specific model"),
        ("/disconnect [name]", "Go offline (add 'keys' to remove API key)"),
        ("/jobs", "Show runtime jobs"),
        ("/artifacts", "Show created/edited artifacts"),
        ("/trace", "Show runtime event trace"),
        ("/session", "Show persisted runtime session"),
        ("/resume", "Resume latest saved workspace session"),
        ("/diff", "Show staged diff preview"),
        ("/revert", "Rollback current edit batch"),
        ("/validate", "Run current batch validation"),
        ("/safety", "Set safety mode"),
        ("/role", "Set specialist role"),
        ("/bg-test", "Run project tests in background"),
        ("/status", "Show session status"),
        ("/reset", "Clear conversation memory"),
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


__all__ = [
    "aion_input_prompt",
    "configure_input",
    "print_aion_dashboard",
    "print_input_area",
    "print_shortcuts",
    "write_aion_md",
]
