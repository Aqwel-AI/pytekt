"""Backward-compatible entry for ``aion auth`` (see :mod:`aion.cli_agent.auth`)."""

from .cli_agent import auth_main

__all__ = ["auth_main"]
