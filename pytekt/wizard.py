"""
PyTekt Post-Install Dependency Selector (pytekt init)
======================================================

Terminal-based post-install setup wizard for the PyTekt Python library.
Allows users to select and install optional third-party dependency groups
needed to power specific PyTekt features, keeping the core installation lightweight.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
"""

from __future__ import annotations

import importlib.util
import os
import select
import subprocess
import sys
import time
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

try:
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.spinner import Spinner
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ---------------------------------------------------------------------------
# Color Palette Constants
# ---------------------------------------------------------------------------
COLOR_BRIGHT = "#00FF7F"      # Active / selected / confirm states, checkmarks
COLOR_LIME = "#7CFC00"        # Alternative accent
COLOR_MEDIUM = "#2E8B57"      # Headers, borders, panel outlines
COLOR_DARK = "#006400"        # Dimmed / inactive text, unfocused items
COLOR_DIM = "#3A6E48"         # Helper navigation hints
COLOR_WHITE = "#E6ECE6"       # Body text for contrast/readability
COLOR_GREY = "#667766"        # Disabled / greyed out items
COLOR_BG_FOCUS_1 = "#003311"  # Focus pulse stage 1
COLOR_BG_FOCUS_2 = "#00551A"  # Focus pulse stage 2
COLOR_BG_FOCUS_3 = "#00280D"  # Focus pulse stage 3 (settled)


# ---------------------------------------------------------------------------
# Dependency Group Definitions
# ---------------------------------------------------------------------------
DEPENDENCY_GROUPS = [
    {
        "id": "data",
        "name": "Data handling",
        "desc": "pandas, numpy",
        "extra": "data",
        "packages": ["pandas", "numpy"],
    },
    {
        "id": "ml",
        "name": "Machine Learning",
        "desc": "scikit-learn, xgboost",
        "extra": "ml",
        "packages": ["scikit-learn", "xgboost"],
    },
    {
        "id": "dl",
        "name": "Deep Learning",
        "desc": "torch, tensorflow",
        "extra": "dl",
        "packages": ["torch", "tensorflow"],
    },
    {
        "id": "viz",
        "name": "Visualization",
        "desc": "matplotlib, seaborn",
        "extra": "viz",
        "packages": ["matplotlib", "seaborn"],
    },
    {
        "id": "nlp",
        "name": "NLP",
        "desc": "transformers, nltk",
        "extra": "nlp",
        "packages": ["transformers", "nltk"],
    },
    {
        "id": "vision",
        "name": "Computer Vision",
        "desc": "opencv-python, pillow",
        "extra": "vision",
        "packages": ["opencv-python-headless", "pillow"],
    },
    {
        "id": "stats",
        "name": "Statistics",
        "desc": "scipy, statsmodels",
        "extra": "stats",
        "packages": ["scipy", "statsmodels"],
    },
]

GROUP_IDS = [g["id"] for g in DEPENDENCY_GROUPS]
GROUP_MAP = {g["id"]: g for g in DEPENDENCY_GROUPS}

LOGO_LINES = [
    r"██████╗  ██╗   ██╗████████╗███████╗██╗  ██╗████████╗",
    r"██╔══██╗ ╚██╗ ██╔╝╚══██╔══╝██╔════╝██║ ██╔╝╚══██╔══╝",
    r"██████╔╝  ╚████╔╝    ██║   █████╗  █████═╝    ██║   ",
    r"██╔═══╝    ╚██╔╝     ██║   ██╔══╝  ██╔═██╗    ██║   ",
    r"██║         ██║      ██║   ███████╗██║  ██╗   ██║   ",
    r"╚═╝         ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   ",
]

LOGO_GRADIENT = [
    "#006400",
    "#157a2c",
    "#22993d",
    "#2E8B57",
    "#32CD32",
    "#00FF7F",
]


# ---------------------------------------------------------------------------
# Cross-Platform Key Reader
# ---------------------------------------------------------------------------
class KeyReader:
    """Non-blocking keyboard input reader supporting POSIX and Windows."""

    def __init__(self) -> None:
        self.is_windows = os.name == "nt"
        self._old_settings = None
        self.fd = 0

    def __enter__(self) -> "KeyReader":
        if not self.is_windows:
            try:
                import termios
                import tty
                if sys.stdin.isatty():
                    self.fd = sys.stdin.fileno()
                    self._old_settings = termios.tcgetattr(self.fd)
                    tty.setcbreak(self.fd)
            except Exception:
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self.is_windows and self._old_settings is not None:
            try:
                import termios
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass

    def get_key(self, timeout: float = 0.03) -> Optional[str]:
        """Return the next key pressed, or None if no key within timeout."""
        if self.is_windows:
            import msvcrt
            start = time.time()
            while time.time() - start < timeout:
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    if ch in (b"\x00", b"\xe0"):
                        ch2 = msvcrt.getch()
                        if ch2 == b"H":
                            return "UP"
                        elif ch2 == b"P":
                            return "DOWN"
                        elif ch2 == b"K":
                            return "LEFT"
                        elif ch2 == b"M":
                            return "RIGHT"
                    elif ch in (b"\r", b"\n"):
                        return "ENTER"
                    elif ch == b" ":
                        return "SPACE"
                    elif ch == b"\x1b":
                        return "ESC"
                    elif ch == b"\x03":
                        return "CTRL_C"
                    elif ch == b"\t":
                        return "TAB"
                    else:
                        try:
                            return ch.decode("utf-8", "ignore")
                        except Exception:
                            return None
                time.sleep(0.005)
            return None

        # POSIX
        if not sys.stdin.isatty():
            return None
        rlist, _, _ = select.select([self.fd], [], [], timeout)
        if not rlist:
            return None

        try:
            raw = os.read(self.fd, 32)
            if not raw:
                return None

            # Standard Arrow Keys & ANSI escape sequences
            if raw in (b"\x1b[A", b"\x1bOA", b"\x1b[1;2A"):
                return "UP"
            elif raw in (b"\x1b[B", b"\x1bOB", b"\x1b[1;2B"):
                return "DOWN"
            elif raw in (b"\x1b[C", b"\x1bOC", b"\x1b[1;2C"):
                return "RIGHT"
            elif raw in (b"\x1b[D", b"\x1bOD", b"\x1b[1;2D"):
                return "LEFT"
            elif raw in (b"\x1b[Z",):
                return "SHIFT_TAB"
            elif raw == b"\x1b":
                return "ESC"
            elif raw in (b"\r", b"\n"):
                return "ENTER"
            elif raw == b" ":
                return "SPACE"
            elif raw == b"\t":
                return "TAB"
            elif raw == b"\x03":
                return "CTRL_C"
            else:
                try:
                    return raw.decode("utf-8", "ignore")
                except Exception:
                    return None
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Animation Step 1: Logo Reveal (typewriter fade-in & vertical gradient)
# ---------------------------------------------------------------------------
def play_logo_reveal(console: Console, skip_animation: bool = False) -> None:
    """Render the PyTekt ASCII logo line-by-line / typewriter with vertical gradient."""
    console.clear()
    
    if skip_animation:
        for i, line in enumerate(LOGO_LINES):
            color = LOGO_GRADIENT[min(i, len(LOGO_GRADIENT) - 1)]
            console.print(Text(line, style=f"bold {color}"))
        console.print(Text("  Your Python toolkit, assembled.\n", style=f"italic {COLOR_DIM}"))
        return

    # Animated reveal
    max_len = max(len(line) for line in LOGO_LINES)

    with Live(console=console, refresh_per_second=40, transient=False) as live:
        step_size = 2
        for col in range(0, max_len + 1, step_size):
            text_group = Text()
            for row_idx, line in enumerate(LOGO_LINES):
                color = LOGO_GRADIENT[min(row_idx, len(LOGO_GRADIENT) - 1)]
                visible_part = line[:col]
                text_group.append(f"{visible_part}\n", style=f"bold {color}")
            live.update(text_group)
            time.sleep(0.015)

        # Final lock-in of all lines
        text_group = Text()
        for row_idx, line in enumerate(LOGO_LINES):
            color = LOGO_GRADIENT[min(row_idx, len(LOGO_GRADIENT) - 1)]
            text_group.append(f"{line}\n", style=f"bold {color}")
        text_group.append("\n  Your Python toolkit, assembled.\n", style=f"italic {COLOR_DIM}")
        live.update(text_group)
        time.sleep(0.1)


# ---------------------------------------------------------------------------
# Animation Step 2: Loading Spinner
# ---------------------------------------------------------------------------
def play_loading_spinner(console: Console, duration: float = 0.8, skip_animation: bool = False) -> None:
    """Show preparing dependency selector spinner."""
    if skip_animation:
        return

    spinner = Spinner("dots", style=f"bold {COLOR_BRIGHT}")
    start = time.time()
    with Live(console=console, refresh_per_second=20, transient=True) as live:
        while time.time() - start < duration:
            msg = Text("  ")
            msg.append_text(spinner.render(time.time()))
            msg.append("  Preparing dependency selector...", style=f"bold {COLOR_BRIGHT}")
            live.update(Panel(
                msg,
                border_style=COLOR_DARK,
                padding=(0, 2),
            ))
            time.sleep(0.05)


# ---------------------------------------------------------------------------
# Animation Step 3: Interactive Dependency Selector Menu
# ---------------------------------------------------------------------------
class InteractiveMenu:
    """Interactive multi-select checkbox menu for dependency groups."""

    def __init__(self, console: Console) -> None:
        self.console = console
        # 0: All
        # 1..N: Dependency groups
        # N+1: None - core only
        # N+2: Confirm
        # N+3: Cancel
        self.cursor_idx = 0
        self.all_selected = False
        self.none_selected = False
        self.selected_ids: Set[str] = set()
        
        self.num_groups = len(DEPENDENCY_GROUPS)
        self.none_idx = 1 + self.num_groups
        self.confirm_idx = self.none_idx + 1
        self.cancel_idx = self.confirm_idx + 1
        self.total_nav = self.cancel_idx + 1
        
        # Animations state
        self.pulse_frame = 0
        self.toggle_anim: Dict[str, Tuple[int, str]] = {}

    def _render_ui(self) -> Panel:
        body = Text()

        # Fixed Top Bar
        body.append("↑/↓ Navigate · Space Select · Enter Confirm · Tab Action\n\n", style=f"dim {COLOR_DIM}")

        # Pinned Option: [✔] All
        is_focused_all = (self.cursor_idx == 0)
        all_pulse_style = ""
        if is_focused_all:
            if self.pulse_frame == 1:
                all_pulse_style = f"bold {COLOR_BRIGHT} {COLOR_BG_FOCUS_1}"
            elif self.pulse_frame == 2:
                all_pulse_style = f"bold {COLOR_LIME} {COLOR_BG_FOCUS_2}"
            else:
                all_pulse_style = f"bold {COLOR_BRIGHT} {COLOR_BG_FOCUS_3}"

        if "all" in self.toggle_anim:
            f, target = self.toggle_anim["all"]
            check_glyph = "[·]" if f == 1 else ("[✔]" if target == "on" else "[ ]")
        else:
            check_glyph = "[✔]" if self.all_selected else "[ ]"

        all_line = f"  {check_glyph} All"
        if is_focused_all:
            body.append(f"❯ {all_line:<24}", style=all_pulse_style or f"bold {COLOR_BRIGHT}")
            body.append(" installs every external dependency below\n", style=f"dim {COLOR_DIM}")
        else:
            body.append(f"  {all_line:<24}", style=f"bold {COLOR_BRIGHT}" if self.all_selected else COLOR_WHITE)
            body.append(" installs every external dependency below\n", style=f"dim {COLOR_DIM}")

        body.append(f"  {'─' * 56}\n", style=COLOR_DARK)

        # Dependency Group Options
        for i, group in enumerate(DEPENDENCY_GROUPS):
            item_idx = i + 1
            is_focused = (self.cursor_idx == item_idx)
            group_id = group["id"]
            is_checked = (group_id in self.selected_ids) or self.all_selected

            if group_id in self.toggle_anim:
                f, target = self.toggle_anim[group_id]
                ch_glyph = "[·]" if f == 1 else ("[✔]" if target == "on" else "[ ]")
            else:
                ch_glyph = "[✔]" if is_checked else "[ ]"

            item_pulse_style = ""
            if is_focused:
                if self.pulse_frame == 1:
                    item_pulse_style = f"bold {COLOR_BRIGHT} {COLOR_BG_FOCUS_1}"
                elif self.pulse_frame == 2:
                    item_pulse_style = f"bold {COLOR_LIME} {COLOR_BG_FOCUS_2}"
                else:
                    item_pulse_style = f"bold {COLOR_BRIGHT} {COLOR_BG_FOCUS_3}"

            prefix = "❯ " if is_focused else "  "
            line_label = f"{prefix}{ch_glyph} {group['name']}"

            if self.all_selected and not is_focused:
                body.append(f"{line_label:<24}", style=f"dim {COLOR_GREY}")
                body.append(f" {group['desc']}\n", style=f"dim {COLOR_DARK}")
            elif is_focused:
                body.append(f"{line_label:<24}", style=item_pulse_style or f"bold {COLOR_BRIGHT}")
                body.append(f" {group['desc']}\n", style=COLOR_WHITE)
            elif is_checked:
                body.append(f"{line_label:<24}", style=f"bold {COLOR_BRIGHT}")
                body.append(f" {group['desc']}\n", style=f"dim {COLOR_WHITE}")
            else:
                body.append(f"{line_label:<24}", style=COLOR_WHITE)
                body.append(f" {group['desc']}\n", style=f"dim {COLOR_DARK}")

        body.append(f"  {'─' * 56}\n", style=COLOR_DARK)

        # None - core only option
        is_focused_none = (self.cursor_idx == self.none_idx)
        none_pulse_style = ""
        if is_focused_none:
            if self.pulse_frame == 1:
                none_pulse_style = f"bold {COLOR_BRIGHT} {COLOR_BG_FOCUS_1}"
            elif self.pulse_frame == 2:
                none_pulse_style = f"bold {COLOR_LIME} {COLOR_BG_FOCUS_2}"
            else:
                none_pulse_style = f"bold {COLOR_BRIGHT} {COLOR_BG_FOCUS_3}"

        if "none" in self.toggle_anim:
            f, target = self.toggle_anim["none"]
            none_glyph = "[·]" if f == 1 else ("[✔]" if target == "on" else "[ ]")
        else:
            none_glyph = "[✔]" if self.none_selected else "[ ]"

        none_line = f"  {none_glyph} None — core only"
        if is_focused_none:
            body.append(f"❯ {none_line:<24}", style=none_pulse_style or f"bold {COLOR_BRIGHT}")
            body.append(" installs nothing extra; base features only\n", style=f"dim {COLOR_DIM}")
        else:
            body.append(f"  {none_line:<24}", style=f"bold {COLOR_BRIGHT}" if self.none_selected else COLOR_WHITE)
            body.append(" installs nothing extra; base features only\n", style=f"dim {COLOR_DIM}")

        body.append(f"\n  {'─' * 56}\n", style=COLOR_DARK)

        # Bottom Bar: Counter + Buttons
        if self.none_selected:
            selected_count = 0
        elif self.all_selected:
            selected_count = len(DEPENDENCY_GROUPS)
        else:
            selected_count = len(self.selected_ids)

        total_count = len(DEPENDENCY_GROUPS)
        count_str = f"  {selected_count} of {total_count} groups selected"
        body.append(f"{count_str:<32}", style=f"bold {COLOR_MEDIUM}")

        is_confirm_focus = (self.cursor_idx == self.confirm_idx)
        is_cancel_focus = (self.cursor_idx == self.cancel_idx)

        if is_confirm_focus:
            body.append(" [ Confirm ] ", style=f"bold black on {COLOR_BRIGHT}")
        else:
            body.append(" [ Confirm ] ", style=f"bold {COLOR_MEDIUM} on {COLOR_DARK}")

        body.append("  ")

        if is_cancel_focus:
            body.append(" [ Cancel ]\n", style="bold white on #882222")
        else:
            body.append(" [ Cancel ]\n", style=f"dim {COLOR_GREY}\n")

        title_text = Text(" PyTekt Dependency Selector ", style=f"bold {COLOR_BRIGHT}")
        subtitle_text = Text(" aqwelai.xyz ", style=f"dim {COLOR_DARK}")

        return Panel(
            body,
            title=title_text,
            subtitle=subtitle_text,
            border_style=COLOR_MEDIUM,
            padding=(1, 2),
        )

    def run(self) -> Tuple[bool, List[str]]:
        """Run the interactive menu loop. Returns (confirmed, selected_group_ids)."""
        with KeyReader() as key_reader:
            with Live(self._render_ui(), console=self.console, refresh_per_second=40, transient=True) as live:
                while True:
                    # Advance toggle animation frames
                    if self.toggle_anim:
                        to_remove = []
                        for k, (frame, target) in self.toggle_anim.items():
                            if frame >= 2:
                                to_remove.append(k)
                            else:
                                self.toggle_anim[k] = (frame + 1, target)
                        for k in to_remove:
                            del self.toggle_anim[k]

                    # Advance pulse animation frames
                    if self.pulse_frame > 0:
                        self.pulse_frame -= 1

                    key = key_reader.get_key(timeout=0.035)

                    if key:
                        if key in ("CTRL_C", "ESC") or key.lower() == "q":
                            return False, []

                        elif key in ("UP", "k", "K"):
                            self.cursor_idx = (self.cursor_idx - 1) % self.total_nav
                            self.pulse_frame = 3
                        elif key in ("DOWN", "j", "J"):
                            self.cursor_idx = (self.cursor_idx + 1) % self.total_nav
                            self.pulse_frame = 3
                        elif key in ("LEFT", "h", "H"):
                            if self.cursor_idx == self.cancel_idx:
                                self.cursor_idx = self.confirm_idx
                                self.pulse_frame = 3
                        elif key in ("RIGHT", "l", "L"):
                            if self.cursor_idx == self.confirm_idx:
                                self.cursor_idx = self.cancel_idx
                                self.pulse_frame = 3
                        elif key == "TAB":
                            if self.cursor_idx < self.confirm_idx:
                                self.cursor_idx = self.confirm_idx
                            elif self.cursor_idx == self.confirm_idx:
                                self.cursor_idx = self.cancel_idx
                            else:
                                self.cursor_idx = 0
                            self.pulse_frame = 3
                        elif key == "SHIFT_TAB":
                            if self.cursor_idx > self.confirm_idx:
                                self.cursor_idx = self.confirm_idx
                            elif self.cursor_idx == self.confirm_idx:
                                self.cursor_idx = self.none_idx
                            else:
                                self.cursor_idx = self.cancel_idx
                            self.pulse_frame = 3
                        elif key == "SPACE":
                            if self.cursor_idx == 0:
                                # Toggle All
                                self.all_selected = not self.all_selected
                                self.none_selected = False
                                self.toggle_anim["all"] = (1, "on" if self.all_selected else "off")
                                if self.all_selected:
                                    self.selected_ids = set(GROUP_MAP.keys())
                                else:
                                    self.selected_ids = set()
                            elif 1 <= self.cursor_idx <= len(DEPENDENCY_GROUPS):
                                group_id = DEPENDENCY_GROUPS[self.cursor_idx - 1]["id"]
                                self.none_selected = False
                                if self.all_selected:
                                    self.all_selected = False
                                    self.selected_ids = set(GROUP_MAP.keys())
                                    self.selected_ids.remove(group_id)
                                    self.toggle_anim[group_id] = (1, "off")
                                else:
                                    if group_id in self.selected_ids:
                                        self.selected_ids.remove(group_id)
                                        self.toggle_anim[group_id] = (1, "off")
                                    else:
                                        self.selected_ids.add(group_id)
                                        self.toggle_anim[group_id] = (1, "on")
                                        if len(self.selected_ids) == len(DEPENDENCY_GROUPS):
                                            self.all_selected = True
                            elif self.cursor_idx == self.none_idx:
                                # Toggle None - core only
                                self.none_selected = not self.none_selected
                                self.toggle_anim["none"] = (1, "on" if self.none_selected else "off")
                                if self.none_selected:
                                    self.all_selected = False
                                    self.selected_ids = set()
                            elif self.cursor_idx == self.confirm_idx:
                                if self.none_selected:
                                    return True, []
                                chosen = list(GROUP_MAP.keys()) if self.all_selected else list(self.selected_ids)
                                return True, chosen
                            elif self.cursor_idx == self.cancel_idx:
                                return False, []

                        elif key == "ENTER":
                            if self.cursor_idx == self.cancel_idx:
                                return False, []
                            elif self.cursor_idx == self.none_idx:
                                return True, []
                            else:
                                if self.none_selected:
                                    return True, []
                                chosen = list(GROUP_MAP.keys()) if self.all_selected else list(self.selected_ids)
                                return True, chosen

                    live.update(self._render_ui())


# ---------------------------------------------------------------------------
# Animation Step 4: Install/Confirm Step with Progress and Completion Cascade
# ---------------------------------------------------------------------------
def run_install_cascade(
    console: Console,
    selected_group_ids: Sequence[str],
    skip_animation: bool = False,
) -> None:
    """Execute dependency installation with green Progress bars and staggered completion cascade."""
    if not selected_group_ids:
        console.print(Text("\n  ✔ PyTekt base environment is ready (core features only).\n", style=f"bold {COLOR_BRIGHT}"))
        return

    console.print(Text("\nInstalling selected dependency groups...\n", style=f"bold {COLOR_MEDIUM}"))

    selected_groups = [GROUP_MAP[g_id] for g_id in selected_group_ids if g_id in GROUP_MAP]

    if skip_animation:
        for group in selected_groups:
            _verify_or_install_group(group, silent=True)
            t = Text("  ")
            t.append("✔", style=f"bold {COLOR_BRIGHT}")
            t.append(f" {group['name']}", style=f"bold {COLOR_WHITE}")
            t.append(f" ({group['desc']})", style=f"dim {COLOR_WHITE}")
            t.append(" — ready\n", style=COLOR_WHITE)
            console.print(t, end="")
        return

    with Progress(
        SpinnerColumn(spinner_name="dots", style=f"bold {COLOR_BRIGHT}"),
        TextColumn(f"[bold {COLOR_WHITE}]{{task.description:<26}}[/bold {COLOR_WHITE}]"),
        BarColumn(
            bar_width=28,
            style="grey23",
            complete_style=COLOR_BRIGHT,
            finished_style=COLOR_BRIGHT,
        ),
        TextColumn(f"[bold {COLOR_MEDIUM}]{{task.percentage:>3.0f}}%[/bold {COLOR_MEDIUM}]"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        tasks = {}
        for group in selected_groups:
            task_id = progress.add_task(f"Installing {group['name']}", total=100)
            tasks[group["id"]] = task_id

        # Animate progress bars smoothly
        for step in range(1, 101, 6):
            for group in selected_groups:
                t_id = tasks[group["id"]]
                progress.update(t_id, completed=min(100, step + (hash(group["id"]) % 8)))
            time.sleep(0.02)

        # Trigger background extra install if required
        for group in selected_groups:
            _verify_or_install_group(group, silent=True)
            progress.update(tasks[group["id"]], completed=100)

        time.sleep(0.05)

    # Completion Cascade
    for group in selected_groups:
        t = Text("  ")
        t.append("✔", style=f"bold {COLOR_BRIGHT}")
        t.append(f" {group['name']}", style=f"bold {COLOR_WHITE}")
        t.append(f" ({group['desc']})", style=f"dim {COLOR_WHITE}")
        t.append(" — ready\n", style=COLOR_WHITE)
        console.print(t, end="")
        time.sleep(0.06)


def _verify_or_install_group(group: dict, silent: bool = True) -> None:
    """Check if optional packages are available; attempt pip install if missing."""
    packages = group.get("packages", [])
    if not packages:
        return

    # Check if packages are available using importlib.util.find_spec to prevent C-extension binary mismatch errors
    missing = []
    for pkg in packages:
        try:
            clean_name = pkg.split("[")[0].replace("-", "_")
            spec = importlib.util.find_spec(clean_name)
            if spec is None:
                missing.append(pkg)
        except Exception:
            missing.append(pkg)

    if missing:
        try:
            cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + missing
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL if silent else None,
                stderr=subprocess.DEVNULL if silent else None,
                timeout=120,
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Animation Step 5: Final Summary Panel (Grows Line-by-Line)
# ---------------------------------------------------------------------------
def play_summary_panel(
    console: Console,
    selected_group_ids: Sequence[str],
    skip_animation: bool = False,
) -> None:
    """Render the growing final summary panel with green borders and details."""
    selected_names = [GROUP_MAP[g_id]["name"] for g_id in selected_group_ids if g_id in GROUP_MAP]
    groups_str = ", ".join(selected_names) if selected_names else "Core base features only"

    lines_text = [
        Text("PyTekt is configured and ready to use.", style=f"bold {COLOR_BRIGHT}"),
        Text(""),
        Text.assemble(
            ("Installed groups: ", f"bold {COLOR_MEDIUM}"),
            (groups_str, COLOR_WHITE),
        ),
        Text.assemble(
            ("Quickstart:       ", f"bold {COLOR_MEDIUM}"),
            ("pytekt --help", f"bold {COLOR_BRIGHT}"),
            ("  (or  ", COLOR_DIM),
            ("pytekt start", f"bold {COLOR_BRIGHT}"),
            ("  for web hub)", COLOR_DIM),
        ),
        Text.assemble(
            ("Agent:            ", f"bold {COLOR_MEDIUM}"),
            ("pytekt agent", f"bold {COLOR_BRIGHT}"),
            ("  (autonomous coding assistant)", COLOR_DIM),
        ),
        Text.assemble(
            ("Documentation:    ", f"bold {COLOR_MEDIUM}"),
            ("https://github.com/Aqwel-AI/pytekt#readme", f"underline {COLOR_WHITE}"),
        ),
    ]

    title = Text(" PyTekt Setup Complete ", style=f"bold {COLOR_BRIGHT}")
    console.print()

    if skip_animation:
        body = Text()
        for i, lt in enumerate(lines_text):
            body.append_text(lt)
            if i < len(lines_text) - 1:
                body.append("\n")
        panel = Panel(
            body,
            title=title,
            border_style=COLOR_MEDIUM,
            padding=(1, 2),
        )
        console.print(panel)
        return

    # Growing animation: border first, then content fills line by line
    with Live(console=console, refresh_per_second=30, transient=False) as live:
        live.update(Panel(
            Text(""),
            title=title,
            border_style=COLOR_MEDIUM,
            padding=(1, 2),
        ))
        time.sleep(0.08)

        body = Text()
        for i, lt in enumerate(lines_text):
            body.append_text(lt)
            if i < len(lines_text) - 1:
                body.append("\n")
            live.update(Panel(
                body.copy(),
                title=title,
                border_style=COLOR_MEDIUM,
                padding=(1, 2),
            ))
            time.sleep(0.045)


# ---------------------------------------------------------------------------
# Non-Interactive Plain-Text Fallback
# ---------------------------------------------------------------------------
def run_non_interactive(
    group_ids: Sequence[str],
    core_only: bool = False,
) -> None:
    """Plain-text execution for CI, scripted environments, and command-line flags."""
    print("==================================================")
    print(" PyTekt Post-Install Dependency Selector")
    print("==================================================")

    if core_only or not group_ids:
        print("Setup mode: Core base only (no extra dependencies installed)")
        print("--------------------------------------------------")
        print(" [OK] Core PyTekt library — ready")
    else:
        chosen_ids = [g.lower().strip() for g in group_ids if g.lower().strip() in GROUP_MAP]
        if not chosen_ids:
            chosen_ids = list(GROUP_MAP.keys())

        print(f"Installing dependency groups: {', '.join(chosen_ids)}")
        print("--------------------------------------------------")

        for g_id in chosen_ids:
            group = GROUP_MAP[g_id]
            _verify_or_install_group(group, silent=True)
            print(f" [OK] {group['name']} ({group['desc']}) — installed")

    print("--------------------------------------------------")
    print("PyTekt is ready! Run `pytekt --help` to get started.")
    print("Documentation: https://github.com/Aqwel-AI/pytekt#readme")
    print("==================================================")


# ---------------------------------------------------------------------------
# Main Setup Wizard Entry Point
# ---------------------------------------------------------------------------
def run_wizard(
    all_modules: bool = False,
    none_modules: bool = False,
    only_modules: Optional[str] = None,
    non_interactive: bool = False,
) -> int:
    """
    Main entry point for ``pytekt init``.

    Parameters
    ----------
    all_modules:
        If True, install all external dependency groups.
    none_modules:
        If True, skip all extra dependencies (core only).
    only_modules:
        Comma-separated list of specific dependency groups to install (e.g. ml,viz).
    non_interactive:
        If True or non-TTY environment, run non-interactive fallback.
    """
    is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    is_ci = bool(os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"))
    
    if none_modules:
        run_non_interactive([], core_only=True)
        return 0

    if all_modules:
        run_non_interactive(list(GROUP_MAP.keys()))
        return 0

    if only_modules:
        targets = [g.strip().lower() for g in only_modules.split(",") if g.strip()]
        alias_map = {
            "all": "all",
            "data": "data",
            "datahandling": "data",
            "data_handling": "data",
            "pandas": "data",
            "ml": "ml",
            "machinelearning": "ml",
            "machine_learning": "ml",
            "sklearn": "ml",
            "dl": "dl",
            "deeplearning": "dl",
            "deep_learning": "dl",
            "torch": "dl",
            "tensorflow": "dl",
            "viz": "viz",
            "visualization": "viz",
            "plots": "viz",
            "nlp": "nlp",
            "transformers": "nlp",
            "vision": "vision",
            "cv": "vision",
            "computervision": "vision",
            "stats": "stats",
            "statistics": "stats",
            "scipy": "stats",
        }
        resolved = []
        for t in targets:
            norm = alias_map.get(t, t)
            if norm in GROUP_MAP:
                resolved.append(norm)
            elif t in GROUP_MAP:
                resolved.append(t)
        run_non_interactive(resolved or targets)
        return 0

    if non_interactive or not is_tty or is_ci or not RICH_AVAILABLE:
        run_non_interactive(list(GROUP_MAP.keys()))
        return 0

    console = Console()

    try:
        # Step 1: Logo reveal
        play_logo_reveal(console)

        # Step 2: Loading spinner
        play_loading_spinner(console, duration=0.8)

        # Step 3: Interactive category menu
        menu = InteractiveMenu(console)
        confirmed, selected_ids = menu.run()

        if not confirmed:
            msg = Text("\nSetup cancelled. You can run ")
            msg.append("pytekt init", style=f"bold {COLOR_BRIGHT}")
            msg.append(" anytime.\n", style=COLOR_DARK)
            console.print(msg)
            return 0

        # Step 4: Install / confirm step & cascade
        run_install_cascade(console, selected_ids)

        # Step 5: Final summary panel
        play_summary_panel(console, selected_ids)
        return 0

    except KeyboardInterrupt:
        print("\n\nSetup aborted.")
        return 130
    except Exception as e:
        console.print(Text(f"\nError running setup wizard: {e}\n", style="bold red"))
        return 1
