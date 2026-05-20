"""ANSI colors and icons for the agent CLI."""

from __future__ import annotations

import os
import re
import sys

# Aion brand green (user-specified)
AION_BRAND_HEX = "#12B981"
AION_RGB = (18, 185, 129)
AION_RGB_BRIGHT = (32, 210, 150)
AION_RGB_DIM = (12, 130, 92)
AION_RGB_MUTED = (90, 150, 125)

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")

COLOR = (
    hasattr(sys.stdout, "isatty")
    and sys.stdout.isatty()
    and not os.environ.get("NO_COLOR")
)


def visible_len(text: str) -> int:
    return len(_ANSI_RE.sub("", text or ""))


def pad_visible(text: str, width: int) -> str:
    """Pad/truncate to visible width (ANSI-safe)."""
    s = text or ""
    n = visible_len(s)
    if n > width:
        plain = _ANSI_RE.sub("", s)
        return plain[:width]
    if n < width:
        return s + " " * (width - n)
    return s


def c(code: str, text: str) -> str:
    if not COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def _truecolor(r: int, g: int, b: int, text: str) -> str:
    return c(f"38;2;{r};{g};{b}", text)


def bold(t: str) -> str:
    return c("1", t)


def primary(t: str) -> str:
    """Main dashboard text (white)."""
    return c("97", t)


def dim(t: str) -> str:
    return c("2", t)


def italic(t: str) -> str:
    return c("3", t)


def cyan(t: str) -> str:
    return c("36", t)


def yellow(t: str) -> str:
    return c("33", t)


def magenta(t: str) -> str:
    return c("35", t)


def red(t: str) -> str:
    return c("31", t)


def blue(t: str) -> str:
    return c("34", t)


def accent(t: str) -> str:
    """Primary brand color #12B981."""
    return _truecolor(*AION_RGB, t)


def accent_bright(t: str) -> str:
    """Lighter brand for highlights and animation."""
    return _truecolor(*AION_RGB_BRIGHT, t)


def accent_dim(t: str) -> str:
    """Darker brand for borders and idle states."""
    return _truecolor(*AION_RGB_DIM, t)


def accent_muted(t: str) -> str:
    """Muted green for hints and secondary labels."""
    return _truecolor(*AION_RGB_MUTED, t)


def green(t: str) -> str:
    """Alias to brand green (same as accent)."""
    return accent(t)


def terracotta(t: str) -> str:
    """Legacy warm accent — maps to brand green."""
    return accent(t)


# Icons
ICON_AGENT = ""
ICON_USER = "👤"
ICON_THINK = "🧠"
ICON_TOOL = "🔧"
ICON_SUCCESS = "✨"
ICON_ERROR = "❌"
ICON_CONFIG = "⚙️"
ICON_EXIT = "👋"
ICON_RESET = "🧹"
ICON_INFO = "ℹ️"
ICON_GLOBE = "🌐"
ICON_GOOGLE = "🇬"
ICON_AUTH = "🔐"
ICON_OLLAMA = "🦙"
ICON_TRUST = "🛡️"
ICON_CODE = "💻"
ICON_WARNING = "⚠️"
ICON_LOGOUT = "🚪"
ICON_OFFLINE = "📴"
ICON_CHAT = "💬"

PROVIDER_ICONS = {
    "openai": "🟢",
    "deepseek": "🐋",
    "gemini": "🔵",
    "google": "🔵",
    "anthropic": "🟠",
    "claude": "🟠",
    "ollama": ICON_OLLAMA,
    "openai_compatible": "🔌",
    "compatible": "🔌",
}
