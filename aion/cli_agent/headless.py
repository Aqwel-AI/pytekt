"""Headless non-interactive agent runner for CI."""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

from .config import get_config
from .connect import AgentConnector
from .mentions import expand_mentions
from .session_prefs import saved_model, saved_provider, saved_workspace_roots
from .tools import build_tool_registry, tools_schema
from . import ui


def run_headless_agent(
    *,
    task: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    yes: bool = False,
    workspace: Optional[str] = None,
) -> int:
    """Run a single task non-interactively. Exit 0 on success, 1 on failure."""
    workspace_root = workspace or os.getcwd()
    cfg = get_config()
    session = ui.AgentSession(
        mode="offline",
        is_trusted=True,
        interaction_mode="agent",
    )
    connector = AgentConnector(
        cfg=cfg,
        registry=build_tool_registry(workspace_root=workspace_root, is_trusted=True),
        tools_schema=tools_schema(is_trusted=True),
        session=session,
        is_trusted=True,
        workspace_root=workspace_root,
    )
    connector.apply_trust(True)
    connector.tool_middleware.auto_approve = yes

    prov = provider or saved_provider(cfg) or "ollama"
    mod = model or saved_model(cfg)
    if not connector.connect(prov=prov, mod=mod, quiet=True):
        print(json.dumps({"ok": False, "error": "connect failed"}))
        return 1

    if not connector.agent:
        print(json.dumps({"ok": False, "error": "no agent"}))
        return 1

    try:
        enriched, _ = expand_mentions(
            task,
            workspace_root,
            pinned_paths=[],
            extra_roots=saved_workspace_roots(cfg),
        )
        response = connector.chat(enriched)
        print(json.dumps({"ok": True, "response": response}))
        return 0
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 1
