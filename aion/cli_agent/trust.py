"""Deferred workspace trust prompt (asked before coding, not at startup)."""

from __future__ import annotations

from typing import Optional

from . import ui
from .session_prefs import save_trust, saved_trust

if False:  # TYPE_CHECKING
    from .connect import AgentConnector


def prompt_workspace_trust(workspace_root: str) -> Optional[bool]:
    """Ask once for file access. Returns True/False, or None on cancel."""
    try:
        return ui.get_yes_no(
            f"Allow file access in {workspace_root}?",
            default=True,
        )
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def ensure_trust_for_coding(connector: "AgentConnector") -> bool:
    """Prompt once before coding; remembered in ~/.aion.yaml."""
    if connector.trust_confirmed:
        return True

    if saved_trust(connector.cfg):
        connector.apply_trust(True)
        connector.trust_confirmed = True
        return True

    result = prompt_workspace_trust(connector.workspace_root)
    if result is None:
        return False

    connector.apply_trust(result)
    connector.trust_confirmed = True
    save_trust(connector.cfg, trusted=result)
    return True
