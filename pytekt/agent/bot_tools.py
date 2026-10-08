"""
Bot Architect & Scaffolding Tools for PyTekt Agent.
Integrates PyTekt Bots framework for autonomous bot generation and testing.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional


def scaffold_bot_project(
    name: str,
    platform: str = "telegram",
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Scaffold a new PyTekt Bot project for Telegram, Discord, or Slack.
    """
    valid_platforms = ("telegram", "discord", "slack")
    p_lower = platform.lower()
    if p_lower not in valid_platforms:
        return {"error": f"Invalid platform '{platform}'. Choose from: {valid_platforms}"}

    target_base = Path(output_dir or os.getcwd())
    try:
        from ..bots.scaffold import generate_project
        res_dir = generate_project(name=name, platform=p_lower, target_dir=target_base)
        return {
            "status": "success",
            "project_name": name,
            "platform": p_lower,
            "directory": str(res_dir),
            "files_created": [
                os.path.relpath(os.path.join(r, f), str(res_dir))
                for r, _, files in os.walk(str(res_dir))
                for f in files
            ],
        }
    except Exception as e:
        return {"error": f"Failed to scaffold bot: {e}"}


def test_bot_in_memory(handler_file: str) -> Dict[str, Any]:
    """
    Load a bot module and verify it in-memory with BotTestClient.
    """
    if not os.path.isfile(handler_file):
        return {"error": f"File not found: {handler_file}"}

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dynamic_bot_mod", handler_file)
        if not spec or not spec.loader:
            return {"error": "Could not load module specification"}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Look for bot instance
        bot_instance = None
        for attr in dir(mod):
            val = getattr(mod, attr)
            if hasattr(val, "handle_event") and hasattr(val, "dispatcher"):
                bot_instance = val
                break

        if not bot_instance:
            return {"error": "No Bot instance found in the specified file"}

        from ..bots.testing import BotTestClient
        client = BotTestClient(bot_instance)
        # Test sending /start
        resp = client.send_message("/start")
        return {
            "status": "success",
            "bot_platform": bot_instance.platform,
            "test_command": "/start",
            "response": resp.text if resp else "No response",
        }
    except Exception as e:
        return {"error": f"In-memory bot test failed: {e}"}
