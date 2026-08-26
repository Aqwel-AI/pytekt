"""
PyTekt Bots Core: Event Dispatch, Rate Limiting, FSM, Cache, Webhook Server, AntiSpam, Metrics.
Tries native C++ compiled pybind11 module first, falling back to pure-Python reference implementation.
"""

from __future__ import annotations

import sys
from typing import Any

_IS_NATIVE = False

# Try importing the compiled C++ extension
try:
    from ._native_core import (  # type: ignore[import-not-found]
        AntiSpam,
        Cache,
        Dispatcher,
        FSM,
        Metrics,
        RateLimiter,
        UniversalEvent,
        WebhookServer,
    )
    _IS_NATIVE = True
except (ImportError, ModuleNotFoundError):
    try:
        from pytekt.bots._native_core import (  # type: ignore[import-not-found]
            AntiSpam,
            Cache,
            Dispatcher,
            FSM,
            Metrics,
            RateLimiter,
            UniversalEvent,
            WebhookServer,
        )
        _IS_NATIVE = True
    except (ImportError, ModuleNotFoundError):
        try:
            from pytekt._bots_core import (  # type: ignore[import-not-found]
                AntiSpam,
                Cache,
                Dispatcher,
                FSM,
                Metrics,
                RateLimiter,
                UniversalEvent,
                WebhookServer,
            )
            _IS_NATIVE = True
        except (ImportError, ModuleNotFoundError):
            from .._core_fallback import (
                AntiSpam,
                Cache,
                Dispatcher,
                FSM,
                Metrics,
                RateLimiter,
                UniversalEvent,
                WebhookServer,
            )
            _IS_NATIVE = False

__all__ = [
    "AntiSpam",
    "Cache",
    "Dispatcher",
    "FSM",
    "Metrics",
    "RateLimiter",
    "UniversalEvent",
    "WebhookServer",
    "_IS_NATIVE",
]
