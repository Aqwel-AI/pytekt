"""Backward-compatible entry for ``aion agent`` (see :mod:`aion.cli_agent`)."""

from .cli_agent import config_command, run_agent_command

__all__ = ["config_command", "run_agent_command"]
