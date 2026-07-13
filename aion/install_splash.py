"""
Animated install success screen for Aqwel-Aion.

Shown after ``pip install aqwel-aion`` (setuptools hook) and via ``aion welcome``.
Uses ANSI colors when stdout is a TTY; falls back to plain text in CI.
"""

from __future__ import annotations

import os
import re
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple


def _package_version() -> str:
    try:
        from aion import __version__

        return __version__
    except Exception:
        return "0.2.0"


# ---------------------------------------------------------------------------
# ANSI styling
# ---------------------------------------------------------------------------

def _supports_color() -> bool:
    if os.environ.get("NO_COLOR") or os.environ.get("AION_NO_SPLASH"):
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


def green(t: str, *, on: bool) -> str:
    return _c("32", t, enabled=on)


def dim(t: str, *, on: bool) -> str:
    return _c("2", t, enabled=on)


def white(t: str, *, on: bool) -> str:
    return _c("97", t, enabled=on)


def accent(t: str, *, on: bool) -> str:
    return _c("92", t, enabled=on)


# ---------------------------------------------------------------------------
# Pixel logo data
# ---------------------------------------------------------------------------

LOGO = r"""
     █████╗ ██╗ ██████╗ ███╗   ██╗
    ██╔══██╗██║██╔═══██╗████╗  ██║
    ███████║██║██║   ██║██╔██╗ ██║
    ██╔══██║██║██║   ██║██║╚██╗██║
    ██║  ██║██║╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
"""

PIXEL_PALETTE: Dict[str, Tuple[int, int, int]] = {
    "W": (245, 247, 250),
    "C": (72, 235, 213),
    "T": (31, 196, 174),
    "D": (20, 28, 35),
}

PIXEL_LOGO: Sequence[str] = (
    "                                            ",
    "                                            ",
    "                                            ",
    "                                            ",
    "                                            ",
    "                                            ",
    "                   W                        ",
    "                  WW                        ",
    "                  WW  CCCCCC                ",
    "                W WWW      CCC              ",
    "               WW WWW        CCC            ",
    "              WW W WWW  W     CCC           ",
    "             WW  WWWWWWW W      CC          ",
    "            WWW   WWWWWWWWW     CC          ",
    "            WWW   WWWWWWWWWW     CC         ",
    "            WWW    WWWWWWWWWW     C         ",
    "            WWW     WWWWWWWWWW    CC        ",
    "          C WWWW WWWWWWWWWWTTWW   CC        ",
    "          CTWWWW  WWWWWWWWWWTTW    C        ",
    "          CC WWWW   WWWWWWWWWDWW   CC       ",
    "          CCC WWWW   WWWWWWWWWWWWW CC       ",
    "           CCC WWWWW  WWWWWDDWWWWD CC       ",
    "          CCCCC WWWW  WWWDDDDDDWW  CC       ",
    "          CTCCCCTWWWW WWWDD  WW    C        ",
    "          CC CCCCCTWWWWWWT        CC        ",
    "           CCCCCCCCTWWWWWD        CC        ",
    "           CCCCCCCCCCWWWWWT       CC        ",
    "            TCCCCCCCCWDDWWW      CC         ",
    "            WTCCCCCTCCDTWWWW     CC         ",
    "            WWWCCCCCTC DWWWW    CC          ",
    "             WWWWWCCCCDDWWWW   CC           ",
    "              WWWWWCCCDDWWW   CC            ",
    "               WWWWWTCDTWWW CCC             ",
    "                 WWWCTDWWWCCCC              ",
    "                   WW TWDTCC                ",
    "                    WTW                     ",
    "                                            ",
    "                                            ",
    "                                            ",
    "                                            ",
    "                                            ",
    "                                            ",
    "                                            ",
    "                                            ",
)

INFO_ROWS: Sequence[Tuple[str, str]] = (
    ("name", "Aqwel-Aion"),
    ("author", "Aksel Aghajanyan"),
    ("company", "Aqwel AI Team"),
    ("package", "aqwel-aion"),
    ("license", "Apache-2.0"),
    ("surface", "Python library + terminal agent"),
    ("python", ">=3.8"),
    ("docs", "aqwelai.xyz"),
)

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def _write_line(text: str = "", *, flush: bool = True) -> None:
    sys.stdout.write(text + "\n")
    if flush:
        sys.stdout.flush()


def _write_lines(lines: Sequence[str], *, delay: float = 0.0) -> None:
    for line in lines:
        _write_line(line)
        if delay > 0:
            time.sleep(delay)


def _visible_len(text: str) -> int:
    return len(ANSI_RE.sub("", text))


def _pad_visible(text: str, width: int) -> str:
    return text + (" " * max(0, width - _visible_len(text)))


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


def _rgb_fg(rgb: Tuple[int, int, int], text: str, *, enabled: bool) -> str:
    if not enabled:
        return text
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def _rgb_bg(rgb: Tuple[int, int, int], text: str, *, enabled: bool) -> str:
    if not enabled:
        return text
    r, g, b = rgb
    return f"\033[48;2;{r};{g};{b}m{text}\033[0m"


def _render_logo_row(top: str, bottom: str, *, color_on: bool) -> str:
    cells: List[str] = []
    for upper, lower in zip(top, bottom):
        upper_rgb = PIXEL_PALETTE.get(upper)
        lower_rgb = PIXEL_PALETTE.get(lower)
        if upper_rgb and lower_rgb:
            cells.append(_rgb_bg(lower_rgb, _rgb_fg(upper_rgb, "▀", enabled=color_on), enabled=color_on))
        elif upper_rgb:
            cells.append(_rgb_fg(upper_rgb, "▀", enabled=color_on))
        elif lower_rgb:
            cells.append(_rgb_fg(lower_rgb, "▄", enabled=color_on))
        else:
            cells.append(" ")
    return "".join(cells)


def _logo_lines(*, color_on: bool) -> List[str]:
    if not color_on:
        return [line for line in LOGO.rstrip("\n").split("\n") if line]
    rows: List[str] = []
    for idx in range(0, len(PIXEL_LOGO), 2):
        rows.append(_render_logo_row(PIXEL_LOGO[idx], PIXEL_LOGO[idx + 1], color_on=color_on))
    return rows


def _show_logo_intro(*, color_on: bool) -> None:
    logo_lines = _logo_lines(color_on=color_on)
    if not color_on:
        _write_lines(logo_lines)
        _write_line()
        return

    try:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
    except Exception:
        pass

    blank = " " * max((len(line) for line in logo_lines), default=0)
    for _ in logo_lines:
        _write_line(blank)

    for idx, line in enumerate(logo_lines):
        sys.stdout.write(f"\033[{len(logo_lines) - idx}A")
        for _ in range(idx):
            sys.stdout.write("\033[B")
        sys.stdout.write("\r" + line + "\n")
        for _ in range(idx):
            sys.stdout.write("\033[A")
        sys.stdout.flush()
        time.sleep(0.035)

    _write_line()

    try:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    except Exception:
        pass


def _show_intro(*, color_on: bool) -> None:
    _show_logo_intro(color_on=color_on)


def _info_panel_lines(version: str, *, color_on: bool) -> List[str]:
    rows = [
        white(bold("Aqwel-Aion", on=color_on), on=color_on),
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


def _render_side_by_side(left: Sequence[str], right: Sequence[str], *, gap: int = 4) -> List[str]:
    left_width = max((_visible_len(line) for line in left), default=0)
    height = max(len(left), len(right))
    rows: List[str] = []
    for idx in range(height):
        left_line = left[idx] if idx < len(left) else ""
        right_line = right[idx] if idx < len(right) else ""
        rows.append(f"{_pad_visible(left_line, left_width)}{' ' * gap}{right_line}".rstrip())
    return rows


def _write_logo_profile(version: str, *, color_on: bool) -> None:
    left = _logo_lines(color_on=color_on)
    right = _info_panel_lines(version, color_on=color_on)
    _write_lines(_render_side_by_side(left, right))


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
    if use_anim:
        _show_intro(color_on=color_on)
    else:
        _write_logo_profile(version, color_on=color_on)
        _write_line()

    if use_anim:
        _write_logo_profile(version, color_on=color_on)
        _write_line()
        _show_progress(color_on=color_on, animated=True)
        _write_line()
    else:
        _show_progress(color_on=color_on, animated=False)
        _write_line()

    _write_line(accent(bold("  ✓ Installation complete", on=color_on), on=color_on))
    _write_line()


def show_install_splash_if_requested() -> None:
    """Called from CLI when user runs ``aion welcome``."""
    show_install_splash(animated=True)
