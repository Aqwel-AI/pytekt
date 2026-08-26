"""
PyTekt Bots — High-Performance Native-Core Bot Framework for Python.

Blazingly fast event dispatch, token-bucket rate limiting, FSM, and in-process
session caches backed by C++ (with pure-Python fallbacks), plus seamless
1-line LLM integration with PyTekt's AI stack.
"""

from __future__ import annotations

from ._core import (
    AntiSpam,
    Cache,
    Dispatcher,
    FSM,
    Metrics,
    RateLimiter,
    UniversalEvent,
    WebhookServer,
    _IS_NATIVE,
)
from .ai import AI
from .base import Bot, Context
from .discord import DiscordBot
from .telegram import TelegramBot

__all__ = [
    "AI",
    "AntiSpam",
    "Bot",
    "Cache",
    "Context",
    "DiscordBot",
    "Dispatcher",
    "FSM",
    "Metrics",
    "RateLimiter",
    "TelegramBot",
    "UniversalEvent",
    "WebhookServer",
    "_IS_NATIVE",
]
