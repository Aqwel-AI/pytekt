"""Backward-compatible entry for ``aion api`` (see :mod:`aion.cli_agent.api`)."""

from .cli_agent import api_main

__all__ = ["api_main"]
