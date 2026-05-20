"""Cyberpunk glitch intro — one animation: corrupt AION logo → lock-in."""

from __future__ import annotations

import os
import random
import sys
import time
from typing import List

from .style import accent, bold

AION_LOGO_LINES: List[str] = [
    "     █████╗ ██╗ ██████╗ ███╗   ██╗",
    "    ██╔══██╗██║██╔═══██╗████╗  ██║",
    "    ███████║██║██║   ██║██╔██╗ ██║",
    "    ██╔══██║██║██║   ██║██║╚██╗██║",
    "    ██║  ██║██║╚██████╔╝██║ ╚████║",
    "    ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝",
]

_GLITCH_CHARS = "░▒▓█▀▄▌▐─│"


def _animations_enabled() -> bool:
    if os.environ.get("NO_COLOR") or os.environ.get("AION_NO_SPLASH"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _corrupt_line(line: str, intensity: float) -> str:
    if intensity <= 0:
        return line
    out: List[str] = []
    for ch in line:
        if ch == " ":
            out.append(" ")
        elif random.random() < intensity:
            out.append(random.choice(_GLITCH_CHARS))
        else:
            out.append(ch)
    return "".join(out)


def _print_logo_static(*, indent: str = "  ") -> None:
    for line in AION_LOGO_LINES:
        print(indent + accent(bold(line)))
    print()


def show_aion_glitch_intro(*, duration: float = 2.0, indent: str = "  ") -> None:
    """Corrupt AION logo flicker, then stable logo."""
    if not _animations_enabled():
        _print_logo_static(indent=indent)
        return

    logo = AION_LOGO_LINES
    height = len(logo)
    random.seed()

    try:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
    except Exception:
        pass

    start = time.time()
    frame = 0

    # Main animation — corrupted logo flicker
    while time.time() - start < duration:
        intensity = max(0.05, 0.9 - (time.time() - start) / duration)
        if frame > 0:
            sys.stdout.write(f"\033[{height}A")
        for line in logo:
            corrupted = _corrupt_line(line, intensity * 0.5)
            sys.stdout.write(indent + accent(corrupted) + "\n")
        sys.stdout.flush()
        frame += 1
        time.sleep(0.06)

    # Final frame — clean logo (no extra flash/scan/noise)
    sys.stdout.write(f"\033[{height}A")
    for line in logo:
        sys.stdout.write(indent + accent(bold(line)) + "\n")
    sys.stdout.flush()

    try:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    except Exception:
        pass
    print()
