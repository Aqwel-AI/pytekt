"""Modern terminal theme helpers for the agent UI."""

from __future__ import annotations

from .style import accent, accent_bright, accent_muted, bold, cyan, dim, green, red, yellow


def status_chip(label: str, value: str, *, tone: str = "neutral") -> str:
    """Render one compact status chip."""
    colors = {
        "neutral": accent_muted,
        "good": green,
        "warn": yellow,
        "error": red,
        "active": accent_bright,
        "info": cyan,
    }
    color = colors.get(tone, accent_muted)
    return f"{dim('[')}{accent(label)} {color(value)}{dim(']')}"


def section_title(title: str) -> str:
    """Render one modern section header."""
    return bold(accent_bright(title))
