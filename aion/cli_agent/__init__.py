"""
Interactive CLI agent for Aion (``aion agent``).

This package intentionally keeps imports lightweight. The interactive app,
auth flow, and config commands are loaded lazily so importing
``aion.cli_agent`` does not pull the full terminal runtime into unrelated
modules.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "api_main",
    "auth_main",
    "config_command",
    "run_agent_command",
]


def api_main(*args: Any, **kwargs: Any) -> Any:
    """Lazy entry point for ``aion api`` commands."""
    from .api import api_main as _api_main

    return _api_main(*args, **kwargs)


def auth_main(*args: Any, **kwargs: Any) -> Any:
    """Lazy entry point for ``aion auth`` commands."""
    from .auth import auth_main as _auth_main

    return _auth_main(*args, **kwargs)


def config_command(*args: Any, **kwargs: Any) -> Any:
    """Lazy entry point for config commands."""
    from .config import config_command as _config_command

    return _config_command(*args, **kwargs)


def run_agent_command(*args: Any, **kwargs: Any) -> Any:
    """Lazy entry point for the terminal agent."""
    from .app import run_agent_command as _run_agent_command

    return _run_agent_command(*args, **kwargs)
