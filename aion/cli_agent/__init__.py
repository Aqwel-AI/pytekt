"""
Interactive CLI agent for Aion (``aion agent``).

Layout
------
app
    Entry point and main chat loop.
connect
    Provider connection (cloud, Ollama).
commands
    In-session slash commands (/help, /mode, …).
config
    ``~/.aion.yaml`` load/save and ``aion config``.
constants
    Mode labels and default models.
tools
    Tool registry setup and OpenAI-style schemas.
ui
    Terminal styling, menus, status bar, help.
api / auth
    ``aion api`` and ``aion auth`` subcommands.
"""

from __future__ import annotations

from .api import api_main
from .app import run_agent_command
from .auth import auth_main
from .config import config_command

__all__ = [
    "api_main",
    "auth_main",
    "config_command",
    "run_agent_command",
]
