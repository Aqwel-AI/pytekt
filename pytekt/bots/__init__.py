"""
PyTekt Bots — High-Performance Native-Core Bot Framework for Python.

Blazingly fast event dispatch, token-bucket rate limiting, FSM, and in-process
session caches backed by C++ (with pure-Python fallbacks), plus seamless
1-line LLM integration with PyTekt's AI stack, declarative cross-platform UI,
durable database persistence, RBAC permissions, i18n, scheduling, and payments.
"""

from __future__ import annotations

from . import payments, ui
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
from .extension import Extension, ExtensionManager
from .i18n import I18nManager
from .payments import (
    Invoice,
    LabeledPrice,
    NotSupportedError,
    PreCheckoutQuery,
    SuccessfulPayment,
)
from .persistence import BotDB
from .roles import RoleRegistry, admin_only, requires_role
from .scheduler import ScheduledJob, Scheduler
from .telegram import TelegramBot
from .testing import BotTestClient, TestResponse
from .ui import (
    Button,
    Card,
    Keyboard,
    Modal,
    ModalField,
    Wizard,
    WizardStep,
)

__all__ = [
    "AI",
    "AntiSpam",
    "Bot",
    "BotDB",
    "BotTestClient",
    "Button",
    "Cache",
    "Card",
    "Context",
    "DiscordBot",
    "Dispatcher",
    "Extension",
    "ExtensionManager",
    "FSM",
    "I18nManager",
    "Invoice",
    "Keyboard",
    "LabeledPrice",
    "Metrics",
    "Modal",
    "ModalField",
    "NotSupportedError",
    "PreCheckoutQuery",
    "RateLimiter",
    "RoleRegistry",
    "ScheduledJob",
    "Scheduler",
    "SuccessfulPayment",
    "TelegramBot",
    "TestResponse",
    "UniversalEvent",
    "WebhookServer",
    "Wizard",
    "WizardStep",
    "_IS_NATIVE",
    "admin_only",
    "payments",
    "requires_role",
    "ui",
]
