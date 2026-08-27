"""
Base UI component classes and color utilities for cross-platform bot interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


# Color palette for Discord embeds and rich visual styling
COLORS: Dict[str, int] = {
    "default": 0x5865F2,
    "primary": 0x5865F2,  # Blurple
    "secondary": 0x4F545C,
    "success": 0x57F287,  # Green
    "warning": 0xFEE75C,  # Yellow
    "danger": 0xED4245,   # Red
    "info": 0x3498DB,     # Blue
    "dark": 0x2C2F33,
    "purple": 0x9B59B6,
    "gold": 0xF1C40F,
    "orange": 0xE67E22,
}


def parse_color(color: Union[int, str, None]) -> int:
    """Parse color into standard RGB integer."""
    if color is None:
        return COLORS["default"]
    if isinstance(color, int):
        return color
    if isinstance(color, str):
        c = color.lower().strip()
        if c in COLORS:
            return COLORS[c]
        if c.startswith("#"):
            try:
                return int(c[1:], 16)
            except ValueError:
                return COLORS["default"]
        if c.startswith("0x"):
            try:
                return int(c, 16)
            except ValueError:
                return COLORS["default"]
    return COLORS["default"]



class UIComponent(ABC):
    """Abstract base class for all declarative UI components."""

    @abstractmethod
    def to_telegram(self) -> Dict[str, Any]:
        """Compile component into Telegram Bot API payload."""
        raise NotImplementedError

    @abstractmethod
    def to_discord(self) -> Dict[str, Any]:
        """Compile component into Discord REST/Gateway payload."""
        raise NotImplementedError

    def compile(self, platform: str) -> Dict[str, Any]:
        """Compile component to target platform payload."""
        plat = platform.lower().strip()
        if plat == "telegram":
            return self.to_telegram()
        elif plat == "discord":
            return self.to_discord()
        else:
            # Fallback to Telegram-like representation
            return self.to_telegram()
