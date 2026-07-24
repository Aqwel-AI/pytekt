"""Shared terminal theme settings for the Aion CLI and installer."""

from __future__ import annotations

import os
import sys
from typing import Dict, Optional


THEME_NAMES = ("cyberpunk", "minimal", "monochrome")

# Keep the original Aion colors as the cyberpunk default. Minimal reduces the
# palette to white/gray, while monochrome disables ANSI styling entirely.
_THEME_CODES: Dict[str, Dict[str, str]] = {
    "cyberpunk": {},
    "minimal": {
        "92": "37",
        "36": "37",
        "96": "37",
        "33": "37",
        "42;30": "7;30",
    },
    "monochrome": {},
}


def configured_theme() -> str:
    """Read the configured theme without making config a hard dependency."""
    try:
        from .user_config import get_config

        value = get_config().get("theme", "cyberpunk")
        if isinstance(value, dict):
            value = value.get("name", "cyberpunk")
        value = str(value).lower()
        return value if value in THEME_NAMES else "cyberpunk"
    except Exception:
        return "cyberpunk"


def is_monochrome(theme: Optional[str] = None) -> bool:
    return (theme or configured_theme()) == "monochrome"


def ansi_code(code: str, theme: Optional[str] = None) -> str:
    """Map a base ANSI code to the selected theme's equivalent."""
    selected = theme or configured_theme()
    return _THEME_CODES.get(selected, {}).get(code, code)


def supports_color(theme: Optional[str] = None) -> bool:
    """Return whether styled output should be used for the current terminal."""
    return (
        not os.environ.get("NO_COLOR")
        and not is_monochrome(theme)
        and hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
    )
