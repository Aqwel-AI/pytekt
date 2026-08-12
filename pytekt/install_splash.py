"""
Animated install success screen for PyTekt.

Shown after ``pip install pytekt`` (setuptools hook) and via ``aion welcome``.
Uses ANSI colors when stdout is a TTY; falls back to plain text in CI.
"""

from __future__ import annotations

import os
import random
import sys
import time
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


def _package_version() -> str:
    try:
        from importlib.metadata import version as pkg_version

        return pkg_version("pytekt")
    except Exception:
        pass
    try:
        from pytekt import __version__

        return __version__
    except Exception:
        return "0.2.0"


def _state_dir() -> Path:
    return Path.home() / ".aion"


def _splash_marker(version: str) -> Path:
    return _state_dir() / f".splash_shown_{version}"


def mark_install_splash_shown(version: Optional[str] = None) -> None:
    """Record that the install/upgrade splash was shown for this version."""
    version = version or _package_version()
    try:
        _state_dir().mkdir(parents=True, exist_ok=True)
        _splash_marker(version).touch()
    except Exception:
        pass


def should_show_install_splash() -> bool:
    """True once per installed/updated version on an interactive TTY."""
    if os.environ.get("PYTEKT_NO_SPLASH"):
        return False
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return False
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    if not (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()):
        return False
    return not _splash_marker(_package_version()).exists()


def maybe_show_install_splash() -> None:
    """
    Show the Aion install animation once after install or upgrade.

    Called from setuptools install hooks and from the ``aion`` CLI on first use
    of a new version (modern pip wheel installs skip setuptools ``install``).
    """
    if not should_show_install_splash():
        return
    version = _package_version()
    mark_install_splash_shown(version)
    try:
        show_install_splash(animated=True, version=version)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# ANSI styling
# ---------------------------------------------------------------------------

def _supports_color() -> bool:
    if os.environ.get("NO_COLOR") or os.environ.get("PYTEKT_NO_SPLASH"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(code: str, text: str, *, enabled: bool) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(t: str, *, on: bool) -> str:
    return _c("1", t, enabled=on)


def cyan(t: str, *, on: bool) -> str:
    return _c("36", t, enabled=on)


def dim(t: str, *, on: bool) -> str:
    return _c("2", t, enabled=on)


def white(t: str, *, on: bool) -> str:
    return _c("97", t, enabled=on)


def accent(t: str, *, on: bool) -> str:
    return _c("92", t, enabled=on)


# ---------------------------------------------------------------------------
# AION wordmark
# ---------------------------------------------------------------------------

LOGO = r"""
     █████╗ ██╗ ██████╗ ███╗   ██╗
    ██╔══██╗██║██╔═══██╗████╗  ██║
    ███████║██║██║   ██║██╔██╗ ██║
    ██╔══██║██║██║   ██║██║╚██╗██║
    ██║  ██║██║╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
"""

INFO_ROWS: Sequence[Tuple[str, str]] = (
    ("name", "PyTekt"),
    ("author", "Aksel Aghajanyan"),
    ("company", "Aqwel AI Team"),
    ("package", "pytekt"),
    ("license", "Apache-2.0"),
    ("surface", "Python research library"),
    ("python", ">=3.8"),
    ("docs", "aqwelai.xyz"),
)

_GLITCH_CHARS = "░▒▓█▀▄▌▐─│"
AION_LOGO_LINES: Sequence[str] = tuple(
    line for line in LOGO.strip("\n").split("\n") if line.strip() or line
)


def _write_line(text: str = "", *, flush: bool = True) -> None:
    sys.stdout.write(text + "\n")
    if flush:
        sys.stdout.flush()


def _progress_line(step: int, total: int, *, color_on: bool, width: int = 26) -> str:
    filled = int(width * step / max(total, 1))
    bar = ("#" * filled) + ("." * (width - filled))
    label = f"{step:3d}%"
    if step < 25:
        phase = "resolve"
        status = "preparing package graph"
    elif step < 55:
        phase = "fetch"
        status = "syncing runtime assets"
    elif step < 85:
        phase = "install"
        status = "writing Aion components"
    elif step < 100:
        phase = "finalize"
        status = "validating install state"
    else:
        phase = "complete"
        status = "system ready"
    phase_txt = accent(phase.ljust(8), on=color_on)
    bar_txt = white(f"[{bar}]", on=color_on)
    pct_txt = accent(label, on=color_on)
    status_txt = dim(status, on=color_on)
    return f"  {phase_txt} {bar_txt} {pct_txt}  {status_txt}"


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


def _show_pytekt_glitch_intro(*, color_on: bool, duration: float = 1.6) -> None:
    """Corrupt AION logo flicker, then lock in the clean wordmark."""
    indent = "  "
    logo = list(AION_LOGO_LINES)
    height = len(logo)

    if not color_on:
        for line in logo:
            _write_line(indent + line)
        _write_line()
        return

    try:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
    except Exception:
        pass

    random.seed()
    start = time.time()
    frame = 0
    while time.time() - start < duration:
        intensity = max(0.05, 0.9 - (time.time() - start) / duration)
        if frame > 0:
            sys.stdout.write(f"\033[{height}A")
        for line in logo:
            corrupted = _corrupt_line(line, intensity * 0.5)
            sys.stdout.write(indent + accent(bold(corrupted, on=True), on=True) + "\n")
        sys.stdout.flush()
        frame += 1
        time.sleep(0.055)

    sys.stdout.write(f"\033[{height}A")
    for line in logo:
        sys.stdout.write(indent + accent(bold(line, on=True), on=True) + "\n")
    sys.stdout.flush()

    try:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    except Exception:
        pass
    _write_line()


def _show_intro(*, color_on: bool) -> None:
    _show_pytekt_glitch_intro(color_on=color_on)


def _info_panel_lines(version: str, *, color_on: bool) -> List[str]:
    rows = [
        white(bold("PyTekt", on=color_on), on=color_on),
        dim("Matrix install profile", on=color_on),
        cyan("────────────────────────────", on=color_on),
        f"{dim('status ', on=color_on)} {accent(':: installed', on=color_on)}",
        f"{dim('version', on=color_on)} {white(version, on=color_on)}",
    ]
    for key, value in INFO_ROWS:
        rows.append(f"{dim(key.ljust(7), on=color_on)} {white(value, on=color_on)}")
    rows.extend(
        [
            cyan("────────────────────────────", on=color_on),
            f"{dim('tagline ', on=color_on)} {white('Complete AI Research & Development Library', on=color_on)}",
        ]
    )
    return rows


def _write_info_profile(version: str, *, color_on: bool) -> None:
    for line in _info_panel_lines(version, color_on=color_on):
        _write_line("  " + line)


def _show_progress(*, color_on: bool, animated: bool) -> None:
    total = 100
    if not animated:
        _write_line(_progress_line(total, total, color_on=color_on))
        return

    _write_line(_progress_line(1, total, color_on=color_on))
    for step in range(2, total + 1):
        sys.stdout.write("\033[1A\r")
        _write_line(_progress_line(step, total, color_on=color_on))
        if step < 15:
            time.sleep(0.012)
        elif step < 50:
            time.sleep(0.008)
        elif step < 85:
            time.sleep(0.005)
        else:
            time.sleep(0.01)

def show_install_splash(
    *,
    animated: bool = True,
    delay: float = 0.04,
    version: Optional[str] = None,
) -> None:
    """
    Print the full install celebration screen.

    Parameters
    ----------
    animated:
        If False or stdout is not a TTY, print a static summary instead.
    delay:
        Seconds between module lines (animated mode only).
    """
    version = version or _package_version()
    color_on = _supports_color()
    use_anim = animated and color_on

    _write_line()
    _show_intro(color_on=color_on)
    _write_info_profile(version, color_on=color_on)
    _write_line()
    _show_progress(color_on=color_on, animated=use_anim)
    _write_line()
    _write_line(accent(bold("  ✓ Installation complete", on=color_on), on=color_on))
    _write_line()
    mark_install_splash_shown(version)


def show_install_splash_if_requested() -> None:
    """Called from CLI when user runs ``aion welcome``."""
    show_install_splash(animated=True)
