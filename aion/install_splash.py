"""
Animated install success screen for Aqwel-Aion.

Shown after ``pip install aqwel-aion`` (setuptools hook) and via ``aion welcome``.
Uses ANSI colors when stdout is a TTY; falls back to plain text in CI.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Iterable, List, Optional, Sequence, Tuple

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


# ---------------------------------------------------------------------------
# Big ASCII art
# ---------------------------------------------------------------------------

LOGO = r"""
     █████╗ ██╗ ██████╗ ███╗   ██╗
    ██╔══██╗██║██╔═══██╗████╗  ██║
    ███████║██║██║   ██║██╔██╗ ██║
    ██╔══██║██║██║   ██║██║╚██╗██║
    ██║  ██║██║╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
"""

# (display_name, internal_module) — shown big during install animation
INSTALL_SECTIONS: Sequence[Tuple[str, Sequence[Tuple[str, str]]]] = (
    ("Core", (
        ("MATHS", "maths"),
        ("ALGORITHMS", "algorithms"),
        ("VISUALIZATION", "visualization"),
    )),
    ("Core ML", (
        ("PREPROCESSING", "preprocessing"),
        ("MODELS", "models"),
        ("METRICS", "metrics"),
        ("HYPEROPT", "hyperopt"),
    )),
    ("Data", (
        ("DATA", "data"),
        ("DATASETS", "datasets"),
        ("TOKENIZER", "tokenizer"),
        ("PIPELINE", "pipeline"),
    )),
    ("LLM & agents", (
        ("PROVIDERS", "providers"),
        ("TOOLS", "tools"),
        ("RAG", "rag"),
        ("AGENTS", "agents"),
        ("LLM EVAL", "llm_eval"),
    )),
    ("Infra & UI", (
        ("DB", "db"),
        ("CACHE", "cache"),
        ("STORE", "store"),
        ("TRACKER", "tracker"),
        ("SERVE", "serve"),
        ("UI", "ui"),
        ("HUB", "hub"),
    )),
    ("Science", (
        ("COSMOS", "cosmos"),
    )),
    ("Former & more", (
        ("FORMER", "former"),
        ("STRUCTURES", "structures"),
        ("EMBED", "embed"),
        ("VISION", "vision"),
    )),
)


def _big_letters(text: str, *, color_on: bool) -> str:
    """Spaced uppercase label (reads large in the terminal)."""
    spaced = "  ".join(text.upper())
    return bold(spaced, on=color_on)


def _progress_bar(step: int, total: int, width: int = 28, *, color_on: bool) -> str:
    filled = int(width * step / max(total, 1))
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * step / max(total, 1))
    return dim(f"[{bar}] {pct:3d}%", on=color_on)


def _write_line(text: str = "", *, flush: bool = True) -> None:
    sys.stdout.write(text + "\n")
    if flush:
        sys.stdout.flush()


def _show_logo_glitch(*, color_on: bool) -> None:
    """Same cyberpunk glitch intro as ``aion agent``."""
    try:
        from aion.cli_agent.ui.glitch import show_aion_glitch_intro

        show_aion_glitch_intro(duration=2.0, indent="")
        return
    except Exception:
        pass
    for line in LOGO.rstrip("\n").split("\n"):
        _write_line(cyan(line, on=color_on))
    _write_line()


def _show_static_modules(*, color_on: bool) -> None:
    for section, modules in INSTALL_SECTIONS:
        _write_line(bold(f"  {section}", on=color_on))
        for display, mod in modules:
            _write_line(f"    ✓ {_big_letters(display, color_on=False)}  ({mod})")


def _show_quick_module_reveal(*, color_on: bool, delay: float) -> None:
    """Fast staggered checklist after the glitch intro."""
    all_modules: List[Tuple[str, str, str]] = []
    for section, modules in INSTALL_SECTIONS:
        for display, mod in modules:
            all_modules.append((section, display, mod))

    total = len(all_modules)
    for idx, (section, display, mod) in enumerate(all_modules, start=1):
        if idx == 1 or all_modules[idx - 2][0] != section:
            _write_line()
            _write_line(bold(f"  ── {section} ──", on=color_on))
        _write_line(_progress_bar(idx, total, color_on=color_on), flush=True)
        label = _big_letters(display, color_on=color_on)
        check = green(" ✓", on=color_on)
        mod_txt = dim(f" ({mod})", on=color_on)
        _write_line(f"  ▸ {label}{check}{mod_txt}")
        time.sleep(delay)


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
        _show_logo_glitch(color_on=color_on)
    else:
        for line in LOGO.rstrip("\n").split("\n"):
            _write_line(cyan(line, on=color_on))
        _write_line()

    _write_line(bold(f"  Aqwel-Aion  v{version}", on=color_on))
    _write_line(dim("  Complete AI Research & Development Library", on=color_on))
    _write_line()

    if not use_anim:
        _write_line(green("  Installation complete!", on=color_on))
        _write_line()
        _show_static_modules(color_on=color_on)
        _write_footer(color_on)
        return

    _write_line(green(bold("  ✓ Installation complete", on=color_on), on=color_on))
    _write_line()
    _show_quick_module_reveal(color_on=color_on, delay=delay)
    _write_line()
    _write_line(green(bold("  ✓ ALL MODULES INSTALLED", on=color_on), on=color_on))
    _write_footer(color_on)


def _write_footer(color_on: bool) -> None:
    _write_line()
    _write_line(dim("  Quick start:", on=color_on))
    _write_line("    python -c \"import aion; print(aion.__version__)\"")
    _write_line("    aion agent          # terminal coding agent (Ollama)")
    _write_line("    aion start          # open Aion Hub")
    _write_line("    aion welcome        # replay this install animation")
    _write_line(dim("  Skip animation: AION_NO_SPLASH=1 pip install aqwel-aion", on=color_on))
    _write_line(dim("  https://aqwelai.xyz/", on=color_on))
    _write_line()


def show_install_splash_if_requested() -> None:
    """Called from CLI when user runs ``aion welcome``."""
    show_install_splash(animated=True)
