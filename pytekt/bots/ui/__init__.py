"""
PyTekt Bots Declarative Cross-Platform UI Module.

Write UI components once; compile down to native Telegram, Discord, and future platforms:
- Keyboard: Interactive buttons and WebApp launcher buttons.
- Card: Rich media cards (Discord Embeds / Telegram formatted photos).
- Modal: Interactive popup input forms (Discord Modals / Telegram ForceReply prompts).
- Wizard: Multi-step interactive guided flows with in-place message edits.
"""

from __future__ import annotations

from .card import Card
from .components import COLORS, UIComponent, parse_color
from .keyboard import Button, Keyboard
from .modal import Modal, ModalField
from .wizard import Wizard, WizardStep

__all__ = [
    "Button",
    "Card",
    "COLORS",
    "Keyboard",
    "Modal",
    "ModalField",
    "UIComponent",
    "Wizard",
    "WizardStep",
    "parse_color",
]
