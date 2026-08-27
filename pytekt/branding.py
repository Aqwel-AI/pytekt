"""
PyTekt CLI Branding & Terminal Styling Helper.
Provides reusable brand palette constants, interactive platform selection menu,
green progress loading animation matching install_splash.py, bordered metadata box,
step-by-step task sequence with Matrix Green checkmarks, and automatic no-TTY plain-text fallback.
"""

from __future__ import annotations

import os
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union


# ==============================================================================
# 1. Official PyTekt Terminal Brand Palette
# ==============================================================================

class Palette:
    """Hex color codes matching PyTekt brand specification."""
    ELECTRIC_BLUE = "#3D8BFD"  # Primary accents, command names
    MATRIX_GREEN  = "#3ECF8E"  # Progress bar fill and success checkmarks (✓)
    NEON_CYAN     = "#22D3EE"  # Highlight strokes, animated typing/streaming
    COSMIC_PURPLE = "#C084FC"  # Reserved for anything AI-related (bots.ai)
    CYBER_PINK    = "#F472B6"  # Single highlight moment (final "ready" tag)
    CRISP_WHITE   = "#E7EDF4"  # Body text and terminal chrome
    DARK_VOID     = "#0A0E14"  # Background
    MUTED_SLATE   = "#8B9CB3"  # Secondary labels, file paths, timestamps
    BORDER_SLATE  = "#2D3A4D"  # Box-drawing borders (┌─┐, └─┘)
    AMBER         = "#F5A524"  # Warnings (missing compiler, optional deps)
    RED           = "#F14C4C"  # Errors


SPINNER_FRAMES: Sequence[str] = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")


# ==============================================================================
# 2. Environment & Terminal Detection
# ==============================================================================

def is_interactive(stream: Any = None) -> bool:
    """Return True if stdout is a valid interactive TTY that supports color."""
    target = stream or sys.stdout
    if os.environ.get("NO_COLOR") or os.environ.get("PYTEKT_NO_ANIMATION"):
        return False
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS") or os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    return hasattr(target, "isatty") and target.isatty()


def check_for_keypress() -> bool:
    """Non-blocking check on sys.stdin to see if user pressed any key to skip animation."""
    if not (hasattr(sys.stdin, "isatty") and sys.stdin.isatty()):
        return False
    try:
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if r:
            try:
                sys.stdin.read(1)
            except Exception:
                pass
            return True
    except Exception:
        pass
    return False


def detect_compiler() -> str:
    """Detect local C++ compiler version for C++ core compilation."""
    for cmd in ("clang++", "g++", "c++"):
        p = shutil.which(cmd)
        if p:
            try:
                out = subprocess.check_output(
                    [cmd, "--version"], text=True, stderr=subprocess.STDOUT, timeout=0.8
                )
                first_line = out.splitlines()[0]
                if "clang" in first_line.lower():
                    return first_line.split("(")[0].strip()
                elif "gcc" in first_line.lower() or "g++" in first_line.lower():
                    return first_line.split(")")[0].replace("(", "").strip()
                return first_line[:28].strip()
            except Exception:
                return f"{cmd} (detected)"
    return "None (pure-Python fallback)"


def get_rich_console(stream: Any = None) -> Optional[Any]:
    """Get rich Console instance if rich is available."""
    try:
        from rich.console import Console
        return Console(file=stream or sys.stdout, highlight=False)
    except ImportError:
        return None


# ASCII / Unicode Block Logo
LOGO_LINES: Sequence[str] = (
    "██████╗  ██╗   ██╗████████╗███████╗██╗  ██╗████████╗",
    "██╔══██╗ ╚██╗ ██╔╝╚══██╔══╝██╔════╝██║ ██╔╝╚══██╔══╝",
    "██████╔╝  ╚████╔╝    ██║   █████╗  █████═╝    ██║   ",
    "██╔═══╝    ╚██╔╝     ██║   ██╔══╝  ██╔═██╗    ██║   ",
    "██║         ██║      ██║   ███████╗██║  ██╗   ██║   ",
    "╚═╝         ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   ",
)


def print_banner(
    console: Optional[Any] = None,
    animated: bool = True,
    sweep_duration: float = 0.65,
    stream: Any = None,
) -> None:
    """Draw PyTekt logo marque (used when full banner is requested)."""
    target_stream = stream or sys.stdout
    interactive = is_interactive(target_stream) and animated

    if not interactive:
        target_stream.write("\n".join(LOGO_LINES) + "\n\n")
        target_stream.flush()
        return

    rich_console = console or get_rich_console(target_stream)
    if rich_console is None:
        target_stream.write("\n".join(LOGO_LINES) + "\n\n")
        target_stream.flush()
        return

    from rich.text import Text
    final_text = Text("\n".join(LOGO_LINES) + "\n", style=Palette.ELECTRIC_BLUE)
    rich_console.print(final_text)


# ==============================================================================
# ==============================================================================
# 3. Interactive Keyboard Navigation (Arrow Keys & Multi-select Spacebar)
# ==============================================================================

def read_single_key(
    stream: Any = None,
    key_reader: Optional[Callable[[], str]] = None,
    prompt_text: str = "",
) -> str:
    """
    Read a single key event (up, down, space, enter, digits, etc.).
    Supports terminal raw mode on real TTYs (Unix / macOS & Windows), line input fallbacks, and mock key readers.
    """
    if key_reader is not None:
        try:
            raw_val = key_reader()
        except StopIteration:
            return "enter"
        if raw_val == " ":
            return "space"
        val = str(raw_val).strip().lower()
        if val in ("escape", "esc", "q", "quit", "cancel", "exit") or val == "\x1b":
            return "escape"
        if val in ("ctrl_c", "ctrl-c", "\x03", "\x04"):
            return "ctrl_c"
        if val in ("up", "u", "k", "w", "top", "arrowup", "up arrow", "↑") or "\x1b[a" in val or "\x1boa" in val:
            return "up"
        if val in ("down", "d", "j", "s", "bottom", "arrowdown", "down arrow", "↓") or "\x1b[b" in val or "\x1bob" in val:
            return "down"
        if val in ("space", "toggle", "t", "prabel", "p", "x", "check"):
            return "space"
        if val in ("enter", "return", "ok", "done", "confirm", ""):
            return "enter"
        if val in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            return val
        return val

    target = stream if stream is not None else sys.stdin
    is_real_tty = hasattr(target, "fileno") and hasattr(target, "isatty") and target.isatty()

    if not is_real_tty:
        try:
            line = input(prompt_text or "")
        except (EOFError, KeyboardInterrupt, StopIteration):
            return "ctrl_c"
        if line == " ":
            return "space"
        val = line.strip().lower()
        if val in ("escape", "esc", "q", "quit", "cancel", "exit") or val == "\x1b":
            return "escape"
        if val in ("ctrl_c", "ctrl-c", "\x03", "\x04"):
            return "ctrl_c"
        if val in ("up", "u", "k", "w", "top", "arrowup", "up arrow", "↑") or "\x1b[a" in val or "\x1boa" in val:
            return "up"
        if val in ("down", "d", "j", "s", "bottom", "arrowdown", "down arrow", "↓") or "\x1b[b" in val or "\x1bob" in val:
            return "down"
        if val in ("space", "toggle", "t", "prabel", "p", "x", "check"):
            return "space"
        if val in ("enter", "return", "ok", "done", "confirm", ""):
            return "enter"
        if val in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            return val
        return val or "enter"

    # Try Windows console raw key reading if on Windows
    if sys.platform == "win32":
        try:
            import msvcrt
            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):
                ch2 = msvcrt.getwch()
                if ch2 in ("H", "I", "G"):  # Up arrow, Page Up, Home
                    return "up"
                elif ch2 in ("P", "Q", "O"):  # Down arrow, Page Down, End
                    return "down"
                elif ch2 == "M":
                    return "right"
                elif ch2 == "K":
                    return "left"
                return "escape"
            elif ch in ("\r", "\n"):
                return "enter"
            elif ch == " ":
                return "space"
            elif ch in ("k", "K", "w", "W"):
                return "up"
            elif ch in ("j", "J", "s", "S"):
                return "down"
            elif ch in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                return ch
            elif ch in ("\x03", "\x04"):
                return "ctrl_c"
            elif ch in ("\x1b", "q", "Q"):
                return "escape"
            return ch
        except ImportError:
            pass

    # POSIX termios / tty raw key reading
    import termios
    import tty
    import select

    fd = target.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        # Read raw byte directly from fd without Python TextIOWrapper buffering
        raw_b = os.read(fd, 1)
        if not raw_b:
            return "enter"
        ch = raw_b.decode("utf-8", errors="ignore")
        if ch in ("\x03", "\x04"):
            return "ctrl_c"
        if ch in ("q", "Q"):
            return "escape"
        if ch == "\x1b":
            # Check if there are further bytes in the escape sequence
            r, _, _ = select.select([fd], [], [], 0.05)
            if not r:
                return "escape"
            seq_b = os.read(fd, 16)
            seq = seq_b.decode("utf-8", errors="ignore")
            if seq in ("[A", "OA", "[1;2A", "[1;5A", "[a") or seq.startswith(("[A", "OA", "[5~", "[1~", "[H", "OH", "[Z")):
                return "up"
            elif seq in ("[B", "OB", "[1;2B", "[1;5B", "[b") or seq.startswith(("[B", "OB", "[6~", "[4~", "[F", "OF")):
                return "down"
            elif seq in ("[C", "OC") or seq.startswith(("[C", "OC")):
                return "right"
            elif seq in ("[D", "OD") or seq.startswith(("[D", "OD")):
                return "left"
            return "escape"
        elif ch in ("\r", "\n"):
            return "enter"
        elif ch == " ":
            return "space"
        elif ch in ("k", "K", "w", "W"):
            return "up"
        elif ch in ("j", "J", "s", "S"):
            return "down"
        elif ch in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            return ch
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class WizardCancelled(KeyboardInterrupt):
    """Raised when the user cancels an interactive wizard with Esc or Ctrl+C."""
    def __init__(self, message: str = "✖ Bot creation cancelled.") -> None:
        super().__init__(message)
        self.message = message


def print_cancellation_message(
    stream: Any = None,
    console: Any = None,
    message: str = "✖ Bot creation cancelled.",
) -> None:
    """Print red cancellation text when user aborts with Esc or Ctrl+C."""
    target_stream = stream or sys.stdout
    rich_console = console or get_rich_console(target_stream)
    if rich_console and is_interactive(target_stream):
        from rich.text import Text
        rich_console.print(Text(f"\n{message}", style=f"bold {Palette.RED}"))
    else:
        target_stream.write(f"\n\033[1;91m{message}\033[0m\n")
        target_stream.flush()


def handle_cancellation(
    stream: Any = None,
    console: Any = None,
    message: str = "✖ Bot creation cancelled.",
) -> None:
    """Print red cancellation notice and raise WizardCancelled."""
    print_cancellation_message(stream=stream, console=console, message=message)
    raise WizardCancelled(message)


def interactive_select(
    title: str,
    prompt: str,
    options: Sequence[Tuple[str, str, str, bool]],
    default_idx: int = 0,
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> str:
    """
    Interactive single-choice menu navigable with keyboard arrows (up/down), W/S keys, and Enter.
    """
    target_stream = stream or sys.stdout
    is_tty = is_interactive(target_stream) if interactive is None else interactive
    default_key = options[default_idx][0] if options else ""

    if not is_tty:
        return default_key

    console = get_rich_console(target_stream)
    current_idx = default_idx
    notice = ""

    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live

    def render_panel() -> Panel:
        t = Text()
        t.append(f"{prompt}\n\n", style=f"bold {Palette.CRISP_WHITE}")
        for i, (key, label, desc, enabled) in enumerate(options):
            is_cursor = (i == current_idx)
            pointer = "❯ " if is_cursor else "  "
            if enabled:
                radio = "◉ " if is_cursor else "○ "
                l_style = f"bold {Palette.MATRIX_GREEN}" if is_cursor else Palette.CRISP_WHITE
                t.append(pointer, style=f"bold {Palette.NEON_CYAN}" if is_cursor else "")
                t.append(radio, style=f"bold {Palette.MATRIX_GREEN}")
                t.append(f"{label:<12} ", style=l_style)
                t.append(f"({desc})\n", style=f"bold {Palette.MATRIX_GREEN}")
            else:
                radio = "○ "
                t.append(pointer, style=f"bold {Palette.MUTED_SLATE}" if is_cursor else "")
                t.append(radio, style=Palette.MUTED_SLATE)
                t.append(f"{label:<12} ", style=Palette.MUTED_SLATE)
                t.append(f"({desc})\n", style=f"dim {Palette.MUTED_SLATE}")

        if notice:
            t.append(f"\n{notice}\n", style=f"bold {Palette.AMBER}")

        t.append("\n↑/↓: navigate  •  enter: select  •  esc/ctrl+c: cancel", style=Palette.MUTED_SLATE)
        return Panel(
            t,
            border_style=Palette.BORDER_SLATE,
            padding=(0, 2),
            title=f"[{Palette.MATRIX_GREEN}]{title}[/{Palette.MATRIX_GREEN}]",
            title_align="left",
        )

    is_real_tty = (
        key_reader is None
        and hasattr(sys.stdin, "fileno")
        and hasattr(sys.stdin, "isatty")
        and sys.stdin.isatty()
        and hasattr(target_stream, "isatty")
        and target_stream.isatty()
    )

    if console and is_real_tty:
        with Live(render_panel(), console=console, auto_refresh=False) as live:
            while True:
                try:
                    k = read_single_key(stream=sys.stdin)
                except (KeyboardInterrupt, EOFError):
                    live.stop()
                    handle_cancellation(stream=target_stream, console=console)

                if k in ("escape", "esc", "ctrl_c", "q"):
                    live.stop()
                    handle_cancellation(stream=target_stream, console=console)
                elif k in ("up", "w", "k"):
                    current_idx = (current_idx - 1) % len(options)
                    notice = ""
                    live.update(render_panel(), refresh=True)
                elif k in ("down", "s", "j"):
                    current_idx = (current_idx + 1) % len(options)
                    notice = ""
                    live.update(render_panel(), refresh=True)
                elif k.isdigit():
                    idx = int(k) - 1
                    if 0 <= idx < len(options):
                        current_idx = idx
                        opt_key, label, _, enabled = options[current_idx]
                        if not enabled:
                            notice = f"⚠️  {label} is coming soon! Only Telegram is currently active."
                            live.update(render_panel(), refresh=True)
                        else:
                            return opt_key
                elif k in ("enter", "space"):
                    opt_key, label, _, enabled = options[current_idx]
                    if not enabled:
                        notice = f"⚠️  {label} is coming soon! Only Telegram is currently active."
                        live.update(render_panel(), refresh=True)
                    else:
                        return opt_key
    else:
        while True:
            if console:
                console.print(render_panel())
            else:
                target_stream.write(f"\n{title}:\n")
                for i, (k, l, d, e) in enumerate(options, 1):
                    status = f"({d})"
                    target_stream.write(f"  [{i}] {l:<10} {status}\n")
                if notice:
                    target_stream.write(f"  {notice}\n")
                target_stream.flush()

            try:
                k = read_single_key(stream=None, key_reader=key_reader, prompt_text="  Choose option [1]: ")
            except (KeyboardInterrupt, EOFError):
                handle_cancellation(stream=target_stream, console=console)

            if k in ("escape", "esc", "ctrl_c", "q"):
                handle_cancellation(stream=target_stream, console=console)
            elif k in ("up", "w", "k"):
                current_idx = (current_idx - 1) % len(options)
                notice = ""
            elif k in ("down", "s", "j"):
                current_idx = (current_idx + 1) % len(options)
                notice = ""
            elif k.isdigit():
                idx = int(k) - 1
                if 0 <= idx < len(options):
                    current_idx = idx
                    opt_key, label, _, enabled = options[current_idx]
                    if not enabled:
                        notice = f"⚠️  {label} is coming soon! Only Telegram is currently active."
                    else:
                        return opt_key
            elif k in ("enter", "space"):
                opt_key, label, _, enabled = options[current_idx]
                if not enabled:
                    notice = f"⚠️  {label} is coming soon! Only Telegram is currently active."
                else:
                    return opt_key
            else:
                matched = False
                for idx, (opt_k, opt_lbl, _, enabled) in enumerate(options):
                    if k == opt_k or k == opt_lbl.lower() or opt_lbl.lower().startswith(k):
                        if not enabled:
                            notice = f"⚠️  {opt_lbl} is coming soon! Only Telegram is currently active."
                        else:
                            return opt_k
                        matched = True
                        break
                if not matched and k in ("yes", "y", "true", "with") and len(options) == 2:
                    return options[1][0]
                if not matched and k in ("no", "n", "false", "without") and len(options) == 2:
                    return options[0][0]
                if not matched and not is_real_tty:
                    return options[current_idx][0]


def interactive_multiselect(
    title: str,
    prompt: str,
    options: Sequence[Tuple[str, str, str, bool]],
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> Dict[str, bool]:
    """
    Interactive multi-select menu navigable with keyboard arrows (up/down),
    toggled with Spacebar ("prabel"), and confirmed with Enter.
    """
    target_stream = stream or sys.stdout
    is_tty = is_interactive(target_stream) if interactive is None else interactive
    selected = {k: default for k, _, _, default in options}
    current_idx = 0

    if not is_tty:
        return selected

    console = get_rich_console(target_stream)

    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live

    def render_panel() -> Panel:
        t = Text()
        t.append(f"{prompt}\n\n", style=f"bold {Palette.CRISP_WHITE}")
        for i, (key, label, desc, _) in enumerate(options):
            is_cursor = (i == current_idx)
            checked = selected[key]
            pointer = "❯ " if is_cursor else "  "
            box = "[✔] " if checked else "[ ] "

            p_style = f"bold {Palette.NEON_CYAN}" if is_cursor else ""
            b_style = f"bold {Palette.MATRIX_GREEN}" if checked else Palette.BORDER_SLATE
            if is_cursor:
                l_style = f"bold {Palette.MATRIX_GREEN}" if checked else f"bold {Palette.CRISP_WHITE}"
            else:
                l_style = Palette.MATRIX_GREEN if checked else Palette.MUTED_SLATE

            t.append(pointer, style=p_style)
            t.append(box, style=b_style)
            t.append(f"{label:<26} ", style=l_style)
            t.append(f"({desc})\n", style="dim #8B9CB3")

        t.append("\n↑/↓: navigate  •  space: toggle  •  enter: confirm  •  esc/ctrl+c: cancel", style=Palette.MUTED_SLATE)
        return Panel(
            t,
            border_style=Palette.BORDER_SLATE,
            padding=(0, 2),
            title=f"[{Palette.MATRIX_GREEN}]{title}[/{Palette.MATRIX_GREEN}]",
            title_align="left",
        )

    is_real_tty = (
        key_reader is None
        and hasattr(sys.stdin, "fileno")
        and hasattr(sys.stdin, "isatty")
        and sys.stdin.isatty()
        and hasattr(target_stream, "isatty")
        and target_stream.isatty()
    )

    if console and is_real_tty:
        with Live(render_panel(), console=console, auto_refresh=False) as live:
            while True:
                try:
                    k = read_single_key(stream=sys.stdin)
                except (KeyboardInterrupt, EOFError):
                    live.stop()
                    handle_cancellation(stream=target_stream, console=console)

                if k in ("escape", "esc", "ctrl_c", "q"):
                    live.stop()
                    handle_cancellation(stream=target_stream, console=console)
                elif k in ("up", "w", "k"):
                    current_idx = (current_idx - 1) % len(options)
                    live.update(render_panel(), refresh=True)
                elif k in ("down", "s", "j"):
                    current_idx = (current_idx + 1) % len(options)
                    live.update(render_panel(), refresh=True)
                elif k in ("space", "prabel", "toggle"):
                    opt_key = options[current_idx][0]
                    selected[opt_key] = not selected[opt_key]
                    live.update(render_panel(), refresh=True)
                elif k in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                    idx = int(k) - 1
                    if 0 <= idx < len(options):
                        current_idx = idx
                        opt_key = options[idx][0]
                        selected[opt_key] = not selected[opt_key]
                        live.update(render_panel(), refresh=True)
                elif k == "enter":
                    break
    else:
        if console:
            console.print(render_panel())
        while True:
            try:
                k = read_single_key(stream=None, key_reader=key_reader, prompt_text="  Choose features [enter to confirm]: ")
            except (KeyboardInterrupt, EOFError):
                handle_cancellation(stream=target_stream, console=console)

            if k in ("escape", "esc", "ctrl_c", "q"):
                handle_cancellation(stream=target_stream, console=console)
            elif k in ("up", "w", "k"):
                current_idx = (current_idx - 1) % len(options)
            elif k in ("down", "s", "j"):
                current_idx = (current_idx + 1) % len(options)
            elif k in ("space", "prabel", "toggle"):
                opt_key = options[current_idx][0]
                selected[opt_key] = not selected[opt_key]
            elif "," in k or " " in k:
                for part in k.replace(",", " ").split():
                    if part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < len(options):
                            opt_key = options[idx][0]
                            selected[opt_key] = not selected[opt_key]
                break
            elif k.isdigit():
                idx = int(k) - 1
                if 0 <= idx < len(options):
                    current_idx = idx
                    opt_key = options[idx][0]
                    selected[opt_key] = not selected[opt_key]
            elif k == "enter":
                break
            else:
                break

    return selected


def select_platform_interactive(
    default: str = "telegram",
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> str:
    """
    Prompt user to select bot platform with keyboard arrow keys (top and bottom buttons)
    and Enter. Discord and Slack are visible but cannot be chosen.
    """
    options = [
        ("telegram", "Telegram", "Ready", True),
        ("discord", "Discord", "coming soon", False),
        ("slack", "Slack", "coming soon", False),
    ]
    return interactive_select(
        title="Bot Platform Selection",
        prompt="Select target bot platform:",
        options=options,
        default_idx=0,
        stream=stream,
        interactive=interactive,
        key_reader=key_reader,
    )


def select_features_multiselect(
    default_ai: bool = False,
    default_db: bool = False,
    default_roles: bool = False,
    default_i18n: bool = False,
    default_scheduler: bool = False,
    default_payments: bool = False,
    default_ui: bool = False,
    default_minimal: bool = False,
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> Dict[str, bool]:
    """
    Multi-select prompt for bot features & configuration.
    Users can navigate with Up/Down arrow keys (top and bottom keyboard buttons),
    toggle any combination with Space ("prabel"), and submit with Enter.
    """
    options = [
        ("with_ai", "AI Assistant Layer", "bots.ai - LLM tools, memory, /ask", default_ai),
        ("with_db", "Database Persistence", "pytekt.db - SQLite storage & /stats", default_db),
        ("with_roles", "Role-Based Access (RBAC)", "Admin/Mod commands & permissions", default_roles),
        ("with_i18n", "Internationalization (i18n)", "Multi-language /lang switcher & locales", default_i18n),
        ("with_scheduler", "Background Scheduler", "Cron jobs & recurring periodic tasks", default_scheduler),
        ("with_payments", "Payments & Subscriptions", "Telegram Stars, Crypto & invoice handlers", default_payments),
        ("with_ui", "Interactive UI Components", "Pagination catalogs, wizards & cards", default_ui),
        ("minimal", "Minimal Single-File", "Single-file main.py layout", default_minimal),
    ]
    return interactive_multiselect(
        title="Bot Features & Configuration",
        prompt="Select bot features (Space to toggle, Enter to confirm):",
        options=options,
        stream=stream,
        interactive=interactive,
        key_reader=key_reader,
    )


def select_ai_interactive(
    default: bool = False,
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> bool:
    """Prompt user to choose AI assistant integration (bots.ai)."""
    options = [
        ("no_ai", "Without AI", "Fast rule-based dispatch (Default)", True),
        ("with_ai", "With AI", "LLM memory, tool calling, /ask command", True),
    ]
    res = interactive_select(
        title="AI Configuration",
        prompt="Include PyTekt AI Assistant layer (bots.ai)?",
        options=options,
        default_idx=1 if default else 0,
        stream=stream,
        interactive=interactive,
        key_reader=key_reader,
    )
    return res == "with_ai"


def select_db_interactive(
    default: bool = False,
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> bool:
    """Prompt user to choose persistence/database layer (pytekt.db)."""
    options = [
        ("no_db", "In-Memory", "Fast in-process state & FSM (Default)", True),
        ("with_db", "SQLite DB", "Persistent user tracking & /stats", True),
    ]
    res = interactive_select(
        title="Database Configuration",
        prompt="Include persistent storage (pytekt.db)?",
        options=options,
        default_idx=1 if default else 0,
        stream=stream,
        interactive=interactive,
        key_reader=key_reader,
    )
    return res == "with_db"


def select_layout_interactive(
    default: bool = False,
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> bool:
    """Prompt user to choose project architecture layout (modular vs minimal)."""
    options = [
        ("modular", "Modular Professional", "bot/handlers, config, middlewares (Default)", True),
        ("minimal", "Minimal Single-file", "Compact starter: main.py", True),
    ]
    res = interactive_select(
        title="Project Architecture",
        prompt="Choose project architecture layout:",
        options=options,
        default_idx=1 if default else 0,
        stream=stream,
        interactive=interactive,
        key_reader=key_reader,
    )
    return res == "minimal"


def select_template_interactive(
    platform: str,
    default_template: str = "echo",
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> str:
    """Prompt user to select a starter template or 'none' for custom features."""
    from .bots.templates import list_templates
    templates = list_templates(platform=platform)
    options = [
        ("none", "None (Custom Features)", "Select individual features manually (like in the past)", True),
    ]
    for t in templates:
        options.append((t.id, t.name, t.description, True))

    default_idx = 1
    for i, opt in enumerate(options):
        if opt[0] == default_template:
            default_idx = i
            break

    return interactive_select(
        title="Starter Bot Templates",
        prompt="Select a starter template or 'None' for custom features:",
        options=options,
        default_idx=default_idx,
        stream=stream,
        interactive=interactive,
        key_reader=key_reader,
    )


def select_scaffold_mode_interactive(
    default: str = "auto",
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> str:
    """Prompt user whether to auto-generate project files or output manual setup instructions."""
    options = [
        ("auto", "Auto-Generate Full Project", "Scaffold files & tests automatically (Default)", True),
        ("manual", "Manual Setup Instructions", "Print copy-paste-ready files & code blocks", True),
    ]
    return interactive_select(
        title="Project Setup Mode",
        prompt="Choose how to setup your bot:",
        options=options,
        default_idx=0 if default == "auto" else 1,
        stream=stream,
        interactive=interactive,
        key_reader=key_reader,
    )


def prompt_scaffold_wizard(
    name: str,
    platform: Optional[str] = None,
    template: Optional[str] = None,
    scaffold_mode: Optional[str] = None,
    skip_prompts: bool = False,
    with_ai: Optional[bool] = None,
    with_db: Optional[bool] = None,
    with_roles: Optional[bool] = None,
    with_i18n: Optional[bool] = None,
    with_scheduler: Optional[bool] = None,
    with_payments: Optional[bool] = None,
    with_ui: Optional[bool] = None,
    minimal: Optional[bool] = None,
    stream: Any = None,
    interactive: Optional[bool] = None,
    key_reader: Optional[Callable[[], str]] = None,
) -> Dict[str, Any]:
    """Interactively prompt for platform, starter template, and generation mode."""
    plat = platform
    if not plat or plat in ("discord", "slack"):
        plat = select_platform_interactive(default="telegram", stream=stream, interactive=interactive, key_reader=key_reader)

    # 1. Template selection
    if skip_prompts:
        chosen_template = template or "echo"
        chosen_mode = scaffold_mode or "auto"
    else:
        if template is None:
            chosen_template = select_template_interactive(
                platform=plat,
                default_template="echo",
                stream=stream,
                interactive=interactive,
                key_reader=key_reader,
            )
        else:
            chosen_template = template

    # When user chooses 'none' (or 'custom'), present the feature multi-select prompt "like in the past"
    if str(chosen_template).lower() in ("none", "custom", "scratch", "no"):
        manifest = None
        all_features_specified = (
            with_ai is not None
            and with_db is not None
            and with_roles is not None
            and with_i18n is not None
            and with_scheduler is not None
            and with_payments is not None
            and with_ui is not None
            and minimal is not None
        )
        if not all_features_specified and not skip_prompts:
            features = select_features_multiselect(
                default_ai=with_ai or False,
                default_db=with_db or False,
                default_roles=with_roles or False,
                default_i18n=with_i18n or False,
                default_scheduler=with_scheduler or False,
                default_payments=with_payments or False,
                default_ui=with_ui or False,
                default_minimal=minimal or False,
                stream=stream,
                interactive=interactive,
                key_reader=key_reader,
            )
            ai_flag = features["with_ai"] if with_ai is None else with_ai
            db_flag = features["with_db"] if with_db is None else with_db
            roles_flag = features["with_roles"] if with_roles is None else with_roles
            i18n_flag = features["with_i18n"] if with_i18n is None else with_i18n
            sched_flag = features["with_scheduler"] if with_scheduler is None else with_scheduler
            pay_flag = features["with_payments"] if with_payments is None else with_payments
            ui_flag = features["with_ui"] if with_ui is None else with_ui
            min_flag = features["minimal"] if minimal is None else minimal
        else:
            ai_flag = with_ai if with_ai is not None else False
            db_flag = with_db if with_db is not None else False
            roles_flag = with_roles if with_roles is not None else False
            i18n_flag = with_i18n if with_i18n is not None else False
            sched_flag = with_scheduler if with_scheduler is not None else False
            pay_flag = with_payments if with_payments is not None else False
            ui_flag = with_ui if with_ui is not None else False
            min_flag = minimal if minimal is not None else False

        chosen_mode = scaffold_mode or "auto"

        return {
            "platform": plat,
            "template": None,
            "manifest": None,
            "scaffold_mode": chosen_mode,
            "with_ai": ai_flag,
            "with_db": db_flag,
            "with_roles": roles_flag,
            "with_i18n": i18n_flag,
            "with_scheduler": sched_flag,
            "with_payments": pay_flag,
            "with_ui": ui_flag,
            "minimal": min_flag,
        }
    else:
        from .bots.templates import get_template
        manifest = get_template(chosen_template, platform=plat)

        # Feature flags: CLI flags take precedence, else manifest defaults
        ai_flag = with_ai if with_ai is not None else (manifest.with_ai if manifest else False)
        db_flag = with_db if with_db is not None else (manifest.with_db if manifest else False)
        roles_flag = with_roles if with_roles is not None else (manifest.with_roles if manifest else False)
        i18n_flag = with_i18n if with_i18n is not None else (manifest.with_i18n if manifest else False)
        sched_flag = with_scheduler if with_scheduler is not None else (manifest.with_scheduler if manifest else False)
        pay_flag = with_payments if with_payments is not None else (manifest.with_payments if manifest else False)
        ui_flag = with_ui if with_ui is not None else (manifest.with_ui if manifest else False)
        min_flag = minimal if minimal is not None else (manifest.minimal if manifest else False)

        chosen_mode = scaffold_mode or "auto"

        return {
            "platform": plat,
            "template": chosen_template,
            "manifest": manifest,
            "scaffold_mode": chosen_mode,
            "with_ai": ai_flag,
            "with_db": db_flag,
            "with_roles": roles_flag,
            "with_i18n": i18n_flag,
            "with_scheduler": sched_flag,
            "with_payments": pay_flag,
            "with_ui": ui_flag,
            "minimal": min_flag,
        }


# ==============================================================================
# 4. Green Progress Bar Loading Animation
# ==============================================================================

def format_green_progress_line(step: int, total: int = 100, width: int = 28, color_on: bool = True) -> str:
    """Format progress line matching install_splash.py Matrix Green styling."""
    filled = int(width * step / max(total, 1))
    bar = ("█" * filled) + ("░" * (width - filled))
    label = f"{step:3d}%"

    if step < 25:
        phase = "resolve"
        status = "preparing package graph"
    elif step < 55:
        phase = "scaffold"
        status = "generating bot handlers"
    elif step < 80:
        phase = "configure"
        status = "writing environment & dependencies"
    elif step < 100:
        phase = "verify"
        status = "validating C++ core runtime"
    else:
        phase = "complete"
        status = "system ready"

    if color_on:
        p_str = f"\033[92m{phase.ljust(9)}\033[0m"
        b_str = f"\033[92m[{bar}]\033[0m"
        pct_str = f"\033[92m{label}\033[0m"
        s_str = f"\033[2m{status}\033[0m"
        return f"  {p_str} {b_str} {pct_str}  {s_str}"
    else:
        return f"  {phase.ljust(9)} [{bar}] {label}  {status}"


def run_green_loading_animation(
    duration: float = 0.75,
    stream: Any = None,
    animated: bool = True,
) -> None:
    """Run Matrix Green progress bar loading animation without PyTekt wordmark."""
    target_stream = stream or sys.stdout
    color_on = is_interactive(target_stream) and animated

    if not color_on:
        target_stream.write(format_green_progress_line(100, 100, color_on=False) + "\n\n")
        target_stream.flush()
        return

    total = 100
    steps = [6, 18, 35, 52, 68, 82, 92, 98, 100]
    delay = duration / float(len(steps))

    target_stream.write(format_green_progress_line(1, total, color_on=True) + "\n")
    target_stream.flush()

    for st in steps:
        if check_for_keypress():
            break
        target_stream.write("\033[1A\r")
        target_stream.write(format_green_progress_line(st, total, color_on=True) + "\n")
        target_stream.flush()
        time.sleep(delay)

    target_stream.write("\n")
    target_stream.flush()


# ==============================================================================
# 5. Bordered Metadata Box
# ==============================================================================

def print_metadata_box(
    name: str,
    platform: str,
    target_path: Path,
    include_ai: bool = False,
    include_db: bool = False,
    include_roles: bool = False,
    include_i18n: bool = False,
    include_scheduler: bool = False,
    include_payments: bool = False,
    include_ui: bool = False,
    minimal: bool = False,
    compiler: Optional[str] = None,
    console: Optional[Any] = None,
    stream: Any = None,
) -> None:
    """Print bordered box with project metadata using Matrix Green styling."""
    target_stream = stream or sys.stdout
    comp = compiler or detect_compiler()
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    plat_str = platform.capitalize()

    features_list = []
    if include_ai:
        features_list.append("AI")
    if include_db:
        features_list.append("DB")
    if include_roles:
        features_list.append("RBAC")
    if include_i18n:
        features_list.append("i18n")
    if include_scheduler:
        features_list.append("Cron")
    if include_payments:
        features_list.append("Pay")
    if include_ui:
        features_list.append("UI")
    if not features_list:
        features_list.append("Core")
    features_str = ", ".join(features_list)

    # 1. Non-interactive / Plain-text Fallback
    if not is_interactive(target_stream):
        box = [
            "┌" + "─" * 58 + "┐",
            f"│  Project   : {name:<43}│",
            f"│  Platform  : {plat_str:<43}│",
            f"│  Features  : {features_str:<43}│",
            f"│  Python    : {py_ver:<43}│",
            f"│  Core      : {comp:<43}│",
            f"│  Location  : {str(target_path):<43}│",
            "└" + "─" * 58 + "┘",
        ]
        target_stream.write("\n".join(box) + "\n\n")
        target_stream.flush()
        return

    # 2. Rich Box
    rich_console = console or get_rich_console(target_stream)
    if rich_console is None:
        return

    from rich.panel import Panel
    from rich.table import Table

    table = Table.grid(padding=(0, 2))
    table.add_column(style=Palette.MUTED_SLATE, justify="right")
    table.add_column(style=f"bold {Palette.CRISP_WHITE}")

    table.add_row("Project", name)
    table.add_row("Platform", f"[{Palette.MATRIX_GREEN}]{plat_str}[/{Palette.MATRIX_GREEN}]")
    feat_color = Palette.COSMIC_PURPLE if include_ai else Palette.MATRIX_GREEN
    table.add_row("Features", f"[{feat_color}]{features_str}[/{feat_color}]")
    table.add_row("Python", py_ver)
    table.add_row("Core", comp)
    table.add_row("Location", str(target_path))

    panel = Panel(
        table,
        border_style=Palette.BORDER_SLATE,
        padding=(1, 2),
        title=f"[{Palette.MATRIX_GREEN}]Bot Project Configuration[/{Palette.MATRIX_GREEN}]",
        title_align="left",
    )
    rich_console.print(panel)
    rich_console.print("")


# ==============================================================================
# 6. Step-by-Step Task Sequence with Matrix Green Checkmarks
# ==============================================================================

class StepTask:
    """A task in the scaffolding sequence."""
    def __init__(
        self,
        key: str,
        label: str,
        action: Optional[Callable[[], Any]] = None,
        is_ai: bool = False,
        is_warning: bool = False,
    ) -> None:
        self.key = key
        self.label = label
        self.action = action
        self.is_ai = is_ai
        self.is_warning = is_warning
        self.completed = False


def run_task_sequence(
    tasks: Sequence[StepTask],
    console: Optional[Any] = None,
    animated: bool = True,
    step_duration: float = 0.18,
    stream: Any = None,
) -> None:
    """
    Execute tasks sequentially, animating transition from pending to Matrix Green ✓.
    Degrades to clean plain text when not interactive.
    """
    target_stream = stream or sys.stdout
    interactive = is_interactive(target_stream) and animated

    # 1. Plain text fallback
    if not interactive:
        for t in tasks:
            if t.action:
                t.action()
            t.completed = True
            if t.is_ai:
                prefix = "✦"
            elif t.is_warning:
                prefix = "⚠"
            else:
                prefix = "✓"
            target_stream.write(f"  {prefix} {t.label}\n")
        target_stream.write("\n")
        target_stream.flush()
        return

    # 2. Interactive Rich Animated Sequence
    rich_console = console or get_rich_console(target_stream)
    if rich_console is None:
        return

    from rich.table import Table
    from rich.text import Text

    spinner_idx = 0
    skip_animation = False

    for current_idx, current_task in enumerate(tasks):
        # Execute action
        if current_task.action:
            current_task.action()

        if not skip_animation:
            sub_steps = 4
            for s in range(sub_steps):
                if check_for_keypress():
                    skip_animation = True
                    break

                table = Table.grid(padding=(0, 1))
                table.add_column(width=4)
                table.add_column()

                for idx, t in enumerate(tasks):
                    if idx < current_idx:
                        # Completed
                        if t.is_ai:
                            icon = Text(" ✦ ", style=f"bold {Palette.COSMIC_PURPLE}")
                            lbl = Text(t.label, style=Palette.COSMIC_PURPLE)
                        elif t.is_warning:
                            icon = Text(" ⚠ ", style=f"bold {Palette.AMBER}")
                            lbl = Text(t.label, style=Palette.AMBER)
                        else:
                            icon = Text(" ✓ ", style=f"bold {Palette.MATRIX_GREEN}")
                            lbl = Text(t.label, style=Palette.CRISP_WHITE)
                    elif idx == current_idx:
                        # In progress
                        frame = SPINNER_FRAMES[(spinner_idx + s) % len(SPINNER_FRAMES)]
                        icon = Text(f" {frame} ", style=f"bold {Palette.MATRIX_GREEN}")
                        lbl = Text(t.label, style=f"bold {Palette.CRISP_WHITE}")
                    else:
                        # Pending
                        icon = Text(" ○ ", style=Palette.BORDER_SLATE)
                        lbl = Text(t.label, style=Palette.MUTED_SLATE)

                    table.add_row(icon, lbl)

                sys.stdout.write(f"\033[{len(tasks)}A\r" if current_idx > 0 or s > 0 else "")
                rich_console.print(table)
                time.sleep(step_duration / float(sub_steps))
                spinner_idx += 1

        current_task.completed = True

    # Final static render of completed checklist
    sys.stdout.write(f"\033[{len(tasks)}A\r" if not skip_animation else "")
    final_table = Table.grid(padding=(0, 1))
    final_table.add_column(width=4)
    final_table.add_column()
    for t in tasks:
        if t.is_ai:
            icon = Text(" ✦ ", style=f"bold {Palette.COSMIC_PURPLE}")
            lbl = Text(t.label, style=f"bold {Palette.COSMIC_PURPLE}")
        elif t.is_warning:
            icon = Text(" ⚠ ", style=f"bold {Palette.AMBER}")
            lbl = Text(t.label, style=Palette.AMBER)
        else:
            icon = Text(" ✓ ", style=f"bold {Palette.MATRIX_GREEN}")
            lbl = Text(t.label, style=Palette.CRISP_WHITE)
        final_table.add_row(icon, lbl)

    rich_console.print(final_table)
    rich_console.print("")


# ==============================================================================
# 7. Closing Banner
# ==============================================================================

def print_closing_banner(
    project_dir: Path,
    run_cmd: str = "python main.py",
    console: Optional[Any] = None,
    stream: Any = None,
) -> None:
    """Print closing banner with Cyber Pink highlight and Matrix Green run command."""
    target_stream = stream or sys.stdout

    # 1. Non-interactive / Plain-text Fallback
    if not is_interactive(target_stream):
        target_stream.write(f"Bot ready → {run_cmd}\n")
        target_stream.write(f"Next steps:\n")
        target_stream.write(f"  cd {project_dir.name}\n")
        target_stream.write(f"  cp .env.example .env   # (add your bot token)\n")
        target_stream.write(f"  {run_cmd}\n")
        target_stream.flush()
        return

    # 2. Rich Formatted Output
    rich_console = console or get_rich_console(target_stream)
    if rich_console is None:
        return

    from rich.text import Text

    line = Text()
    line.append("Bot ready ", style=f"bold {Palette.CYBER_PINK}")
    line.append("→ ", style=f"bold {Palette.CRISP_WHITE}")
    line.append(run_cmd, style=f"bold {Palette.MATRIX_GREEN}")
    rich_console.print(line)

    rich_console.print(f"\n[{Palette.MUTED_SLATE}]Next steps:[/{Palette.MUTED_SLATE}]")
    rich_console.print(f"  [{Palette.MATRIX_GREEN}]cd[/{Palette.MATRIX_GREEN}] {project_dir.name}")
    rich_console.print(f"  [{Palette.MATRIX_GREEN}]cp[/{Palette.MATRIX_GREEN}] .env.example .env   [{Palette.MUTED_SLATE}]# (add your bot token)[/{Palette.MUTED_SLATE}]")
    rich_console.print(f"  [{Palette.MATRIX_GREEN}]{run_cmd}[/{Palette.MATRIX_GREEN}]         [{Palette.MUTED_SLATE}]# (or: pytekt bots dev main.py)[/{Palette.MUTED_SLATE}]\n")


from contextlib import contextmanager


@contextmanager
def spinner(label: str, console: Optional[Any] = None, stream: Any = None):
    """
    Context manager showing spinner while a task runs, then green checkmark upon completion.
    Degrades to clean plain text if not an interactive TTY.
    """
    target_stream = stream or sys.stdout
    if not is_interactive(target_stream):
        target_stream.write(f"  ... {label}\n")
        target_stream.flush()
        try:
            yield
        finally:
            target_stream.write(f"  ✓ {label}\n")
            target_stream.flush()
        return

    rich_console = console or get_rich_console(target_stream)
    if rich_console:
        from rich.status import Status
        with Status(f"[{Palette.CRISP_WHITE}]{label}[/{Palette.CRISP_WHITE}]", console=rich_console, spinner_style=Palette.MATRIX_GREEN):
            yield
        rich_console.print(f"  [{Palette.MATRIX_GREEN}]✓[/{Palette.MATRIX_GREEN}] [{Palette.CRISP_WHITE}]{label}[/{Palette.CRISP_WHITE}]")
    else:
        try:
            yield
        finally:
            target_stream.write(f"  ✓ {label}\n")
            target_stream.flush()


# ==============================================================================
# 8. Coordinated Bot Scaffolding Loading Animation Runner
# ==============================================================================

def animate_bot_scaffold(
    name: str,
    platform: str,
    target_dir: Optional[Path] = None,
    template: Optional[str] = None,
    scaffold_mode: str = "auto",
    manifest: Optional[Any] = None,
    include_ai: bool = False,
    include_db: bool = False,
    include_roles: bool = False,
    include_i18n: bool = False,
    include_scheduler: bool = False,
    include_payments: bool = False,
    include_ui: bool = False,
    minimal: bool = False,
    animated: bool = True,
    stream: Any = None,
) -> Path:
    """
    Run branded loading animation (without PyTekt wordmark) and generate bot project skeleton
    or output manual setup instructions.
    Uses Matrix Green styling from install_splash.py.
    Returns path to created project.
    """
    from .bots.scaffold import generate_project

    clean_name = name.strip()
    slug = clean_name.lower().replace(" ", "_").replace("-", "_")
    base_dir = (target_dir or Path.cwd()) / slug
    console = get_rich_console(stream)

    try:
        # 1. Bordered Metadata Box
        print_metadata_box(
            name=clean_name,
            platform=platform,
            target_path=base_dir,
            include_ai=include_ai,
            include_db=include_db,
            include_roles=include_roles,
            include_i18n=include_i18n,
            include_scheduler=include_scheduler,
            include_payments=include_payments,
            include_ui=include_ui,
            minimal=minimal,
            console=console,
            stream=stream,
        )

        # 2. Green Progress Bar Loading Animation (~0.7s)
        run_green_loading_animation(duration=0.75, stream=stream, animated=animated)

        # 3. Handle Manual Setup Mode with Step Tasks Checklist
        if scaffold_mode == "manual":
            manual_guide_container: List[str] = []

            def _do_manual():
                with spinner(f"Generating {template or 'bot'} manual setup instructions...", console=console, stream=stream):
                    from .bots.templates import generate_manual_setup, get_template
                    m = manifest or (get_template(template, platform=platform) if template else None)
                    g = generate_manual_setup(
                        manifest=m,
                        project_name=clean_name,
                        platform=platform,
                        template=template,
                        with_ai=include_ai,
                        with_db=include_db,
                        with_roles=include_roles,
                        with_i18n=include_i18n,
                        with_scheduler=include_scheduler,
                        with_payments=include_payments,
                        with_ui=include_ui,
                        minimal=minimal,
                    )
                    manual_guide_container.append(g)

            tasks = [
                StepTask("dirs", "Analyzing target bot architecture & credentials schema"),
                StepTask("code", f"Synthesizing {platform.capitalize()} source components", action=_do_manual),
            ]
            if include_ai:
                tasks.append(
                    StepTask("ai", "Configuring ai/ (bots.ai assistant, default tools & prompts)", is_ai=True)
                )
            if include_db:
                tasks.append(
                    StepTask("db", "Configuring db/ (pytekt.db persistence, operations & schemas)")
                )
            if include_roles:
                tasks.append(
                    StepTask("roles", "Configuring roles/ (RBAC permissions & admin commands)")
                )
            if include_i18n:
                tasks.append(
                    StepTask("i18n", "Configuring locales/ (en, ru, es translation files & /lang)")
                )
            if include_scheduler:
                tasks.append(
                    StepTask("scheduler", "Configuring scheduler/ (cron tasks & periodic intervals)")
                )
            if include_payments:
                tasks.append(
                    StepTask("payments", "Configuring payments/ (Telegram Stars & digital checkout)")
                )
            if include_ui:
                tasks.append(
                    StepTask("ui", "Configuring ui_components/ (pagination, survey wizards & cards)")
                )
            tasks.extend([
                StepTask("env", "Writing .env.example credentials template"),
                StepTask("deps", "Configuring packaging and dependencies (pyproject.toml, requirements.txt)"),
                StepTask("tests", "Preparing in-memory test suite"),
                StepTask("core", "Validating C++ dispatch core & native event loop"),
            ])

            run_task_sequence(tasks, console=console, animated=animated, stream=stream)

            target_stream = stream or sys.stdout
            target_stream.write("\n" + manual_guide_container[0] + "\n")
            target_stream.flush()
            return base_dir

        # 4. Auto-Generate Step Tasks Checklist with Matrix Green ✓
        created_path: List[Path] = []

        def _do_scaffold():
            with spinner(f"Writing {clean_name} project files...", console=console, stream=stream):
                p = generate_project(
                    name=clean_name,
                    platform=platform,
                    target_dir=target_dir,
                    template=template,
                    include_ai=include_ai,
                    include_db=include_db,
                    include_roles=include_roles,
                    include_i18n=include_i18n,
                    include_scheduler=include_scheduler,
                    include_payments=include_payments,
                    include_ui=include_ui,
                    minimal=minimal,
                )
                created_path.append(p)

        if minimal:
            tasks = [
                StepTask("dirs", "Creating project root & configuration"),
                StepTask("code", f"Scaffolding single-file {platform.capitalize()} bot (main.py)", action=_do_scaffold),
            ]
            if include_ai:
                tasks.append(
                    StepTask("ai", "Configuring ai/ (bots.ai assistant, default tools & prompts)", is_ai=True)
                )
            if include_db:
                tasks.append(
                    StepTask("db", "Configuring db/ (pytekt.db persistence, operations & schemas)")
                )
            if include_roles:
                tasks.append(
                    StepTask("roles", "Configuring roles/ (RBAC permissions & admin commands)")
                )
            if include_i18n:
                tasks.append(
                    StepTask("i18n", "Configuring locales/ (en, ru, es translation files & /lang)")
                )
            if include_scheduler:
                tasks.append(
                    StepTask("scheduler", "Configuring scheduler/ (cron tasks & periodic intervals)")
                )
            if include_payments:
                tasks.append(
                    StepTask("payments", "Configuring payments/ (Telegram Stars & digital checkout)")
                )
            if include_ui:
                tasks.append(
                    StepTask("ui", "Configuring ui_components/ (pagination, survey wizards & cards)")
                )
            tasks.extend([
                StepTask("env", "Writing .env.example credentials template"),
                StepTask("deps", "Configuring packaging and dependencies (pyproject.toml, requirements.txt)"),
                StepTask("tests", "Setting up in-memory test suite (tests/test_bot.py)"),
                StepTask("core", "Validating C++ dispatch core & native event loop"),
            ])
        else:
            tasks = [
                StepTask("dirs", "Creating modular structure (bot/, handlers/, middlewares/, utils/)"),
                StepTask("config", "Writing bot/config.py (typed settings loaded from .env)"),
                StepTask("handlers", f"Scaffolding {platform.capitalize()} handlers (commands.py, messages.py, callbacks.py)", action=_do_scaffold),
            ]
            if include_ai:
                tasks.append(
                    StepTask("ai", "Configuring bot/ai/setup.py (AI assistant & @ai.tool registrations)", is_ai=True)
                )
            if include_db:
                tasks.append(
                    StepTask("db", "Configuring bot/models/ & bot/db/ (pytekt.db persistence & operations)")
                )
            if include_roles:
                tasks.append(
                    StepTask("roles", "Configuring bot/roles/ (RBAC permissions, @admin_only & /ban)")
                )
            if include_i18n:
                tasks.append(
                    StepTask("i18n", "Configuring bot/locales/ (i18n translator, JSON locales & /lang)")
                )
            if include_scheduler:
                tasks.append(
                    StepTask("scheduler", "Configuring bot/scheduler/ (in-process cron & interval tasks)")
                )
            if include_payments:
                tasks.append(
                    StepTask("payments", "Configuring bot/payments/ (Telegram Stars & crypto invoices)")
                )
            if include_ui:
                tasks.append(
                    StepTask("ui", "Configuring bot/ui_components/ (Paginators, surveys & modals)")
                )
            tasks.extend([
                StepTask("middlewares", "Configuring bot/middlewares/ & bot/utils/"),
                StepTask("main", "Creating bot/main.py application entry point"),
                StepTask("tests", "Setting up in-memory pytest suite (tests/test_handlers.py)"),
                StepTask("meta", "Generating .env.example, .gitignore, SECURITY.md & pyproject.toml"),
                StepTask("readme", "Writing dynamically tailored README.md"),
            ])

        run_task_sequence(tasks, console=console, animated=animated, stream=stream)

        # 4. Closing Banner
        dest = created_path[0] if created_path else base_dir
        run_cmd = "python main.py" if minimal else "python -m bot.main"
        print_closing_banner(project_dir=dest, run_cmd=run_cmd, console=console, stream=stream)

        return dest
    except (KeyboardInterrupt, WizardCancelled):
        handle_cancellation(stream=stream, console=console)
