"""Screen control and the single agent startup animation."""

from __future__ import annotations

import os
import sys

from .glitch import AION_LOGO_LINES, show_aion_glitch_intro
from .style import accent, accent_bright, accent_muted, bold, dim

AION_LOGO = "\n".join(AION_LOGO_LINES)


def _animations_enabled() -> bool:
    if os.environ.get("NO_COLOR") or os.environ.get("AION_NO_SPLASH"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_logo() -> None:
    for line in AION_LOGO_LINES:
        print(accent(bold(line)))


def run_agent_intro(*, version: str = "0.2.0") -> None:
    """Only the cyberpunk glitch logo, then dashboard."""
    clear_screen()
    print()
    show_aion_glitch_intro(duration=2.0)


def print_header(*, version: str = "0.2.0") -> None:
    clear_screen()
    print_logo()
    print()


def show_spinner(text: str, duration: float = 1.0) -> None:
    """No spinner animation — kept for API compatibility."""
    return


def show_aion_boot(*, duration: float = 2.6) -> None:
    """Removed — use show_aion_glitch_intro only."""
    return


def show_aion_loading(*, duration: float = 2.6) -> None:
    return


def show_loading_animation(*, duration: float = 2.6) -> None:
    return


def print_agent_tagline(*, version: str = "0.2.0") -> None:
    print()


def divider(width: int = 60) -> str:
    return dim("  " + "─" * width)


def type_text(text: str, *, delay: float = 0.02) -> None:
    print(text)
