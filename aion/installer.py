"""Interactive installation profiles for Aqwel-Aion.

The normal ``pip install aqwel-aion`` flow stays non-interactive. After the
core package is installed, ``aion setup`` lets users choose optional feature
profiles from a green terminal menu.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from .terminal_theme import ansi_code, configured_theme, supports_color


CORE_PACKAGES = ("Python >= 3.8", "numpy", "watchdog", "gitpython", "certifi")

PROFILES: Dict[str, Tuple[str, str, Tuple[str, ...]]] = {
    "core": ("Core", "Required runtime and lightweight research tools", ()),
    "ai": ("AI / Machine Learning", "Models, metrics, SciPy, pandas, and visualization", ("ai", "viz")),
    "science": ("Physics + Astronomy", "Physics, universe, and visualization", ("physics", "universe", "viz")),
    "vision": ("Computer Vision", "Pillow, OpenCV, and image operations", ("vision",)),
    "llm": ("LLM + RAG", "AI providers, tools, embeddings, and vector search", ("ai", "tools", "rag")),
    "full": ("Full installation", "All supported feature dependencies", ("full",)),
}

PROFILE_ORDER: Tuple[str, ...] = ("core", "ai", "science", "vision", "llm", "full")

PROFILE_PACKAGES: Dict[str, Tuple[str, ...]] = {
    "core": (),
    "ai": ("scipy", "scikit-learn", "pandas", "matplotlib", "transformers", "torch", "openai"),
    "science": ("matplotlib",),
    "vision": ("pillow", "opencv-python-headless"),
    "llm": ("scipy", "scikit-learn", "pandas", "transformers", "torch", "openai", "tiktoken", "sentence-transformers", "faiss-cpu"),
    "full": ("All optional Aion feature dependencies",),
}

INSTALL_LOG_PATH = Path.home() / ".aion" / "logs" / "install.log"
FIRST_RUN_MARKER = Path.home() / ".aion" / ".first_run_complete"
_ACTIVE_THEME = "cyberpunk"


def _set_active_theme(theme: str) -> str:
    """Set the theme used by installer output and return its name."""
    global _ACTIVE_THEME
    _ACTIVE_THEME = theme if theme in ("cyberpunk", "minimal", "monochrome") else "cyberpunk"
    return _ACTIVE_THEME


def _style(text: str, code: str, enabled: bool) -> str:
    mapped_code = ansi_code(code, _ACTIVE_THEME)
    return f"\033[{mapped_code}m{text}\033[0m" if enabled else text


def _append_install_log(message: str) -> None:
    """Append an installer event without making logging a fatal operation."""
    try:
        INSTALL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with INSTALL_LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
    except OSError:
        pass


def _print_log_path(*, color: bool) -> None:
    print(_style(f"  Install log: {INSTALL_LOG_PATH}", "2", color))


def _preflight_checks(*, local: bool = False) -> List[Tuple[str, str, str, bool]]:
    """Check the local environment before starting a package installation."""
    checks: List[Tuple[str, str, str, bool]] = []
    python_ok = sys.version_info >= (3, 8)
    checks.append(("Python", "OK" if python_ok else "FAIL", f"{sys.version.split()[0]} (requires >=3.8)", True))

    pip_ok = importlib.util.find_spec("pip") is not None
    checks.append(("pip", "OK" if pip_ok else "FAIL", "available" if pip_ok else "not found", True))

    writable = os.access(str(Path.cwd()), os.W_OK)
    checks.append(("Permissions", "OK" if writable else "WARN", "current directory writable" if writable else "check environment permissions", False))

    try:
        free_gb = shutil.disk_usage(Path.cwd()).free / (1024 ** 3)
        disk_status = "OK" if free_gb >= 0.25 else "WARN"
        checks.append(("Disk", disk_status, f"{free_gb:.1f} GB free", False))
    except OSError:
        checks.append(("Disk", "WARN", "could not read free space", False))

    if local:
        checks.append(("Network", "SKIP", "local checkout selected", False))
    elif os.environ.get("CI"):
        checks.append(("Network", "SKIP", "CI environment", False))
    else:
        try:
            request = urllib.request.Request("https://pypi.org/simple/aqwel-aion/", method="HEAD")
            with urllib.request.urlopen(request, timeout=3):
                checks.append(("Network", "OK", "PyPI reachable", False))
        except (OSError, urllib.error.URLError):
            checks.append(("Network", "WARN", "PyPI is not reachable; pip may use a cache", False))

    installed = importlib.util.find_spec("aion") is not None
    checks.append(("Aion", "OK" if installed else "NEW", "existing install detected" if installed else "first installation", False))
    return checks


def _print_preflight(checks: Sequence[Tuple[str, str, str, bool]], *, color: bool, theme: str) -> None:
    print()
    print(_style("  AION PREFLIGHT CHECK", "1", color))
    print(_style(f"  Theme: {theme}", "36", color))
    for label, status, detail, _required in checks:
        status_code = "31" if status == "FAIL" else "33" if status in ("WARN", "SKIP") else "92"
        print(f"  {_style(status, status_code, color):<18} {label:<12} {detail}")
    print()


def _preflight_ok(checks: Sequence[Tuple[str, str, str, bool]]) -> bool:
    return not any(status == "FAIL" and required for _, status, _, required in checks)


def install_spec(profile: str, *, local: bool = False, full: bool = False) -> str:
    """Return the pip requirement for an installation profile."""
    if profile not in PROFILES:
        raise ValueError(f"Unknown installation profile: {profile}")
    target = "." if local else "aqwel-aion"
    extras = ("full",) if full else PROFILES[profile][2]
    if extras:
        target += "[" + ",".join(extras) + "]"
    return target


def _print_menu(*, color: bool) -> None:
    print()
    print(_style("  Aqwel-Aion Setup", "1", color))
    print(_style("  Step 1 — Choose an installation profile.", "36", color))
    print(_style("  Core dependencies are always included.", "36", color))
    print()
    for number, profile in enumerate(PROFILE_ORDER, start=1):
        label, description, _ = PROFILES[profile]
        marker = " (recommended)" if profile == "core" else ""
        print(f"  {_style(str(number), '92', color)}. {_style(label, '1', color)}{marker}")
        print(f"     {_style(description, '2', color)}")
    print()


def _read_key() -> str:
    """Read one navigation key from a Unix or Windows terminal."""
    if os.name == "nt":
        import msvcrt

        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            key = msvcrt.getwch()
            return {"H": "up", "P": "down"}.get(key, "")
        return {"\r": "enter", "\x03": "cancel", "\x1b": "cancel"}.get(key, "")

    import termios
    import tty

    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        first = os.read(fd, 1)
        if first == b"\x03":
            return "cancel"
        if first in (b"\r", b"\n"):
            return "enter"
        if first == b"\x1b":
            sequence = os.read(fd, 2)
            return {b"[A": "up", b"[B": "down"}.get(sequence, "cancel")
        return ""
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous)


def _arrow_select(title: str, options: Sequence[Tuple[str, str]], *, color: bool) -> str:
    """Render an arrow-key menu and return the selected option key."""
    selected = 0
    while True:
        # Clear and redraw so the selected row behaves like a terminal button.
        if color:
            sys.stdout.write("\033[2J\033[H")
        else:
            sys.stdout.write("\033[2J\033[H")
        print(_style("  Aqwel-Aion Installer", "1", color))
        print(_style(f"  {title}", "36", color))
        print()
        for index, (_, label) in enumerate(options):
            if index == selected:
                row = _style(f"  ❯ {label}", "42;30", color)
            else:
                row = f"    {label}"
            print(row)
        print()
        print(_style("  ↑/↓ Move   Enter Select   Ctrl+C Cancel", "2", color))
        sys.stdout.flush()

        key = _read_key()
        if key == "up":
            selected = (selected - 1) % len(options)
        elif key == "down":
            selected = (selected + 1) % len(options)
        elif key == "enter":
            return options[selected][0]
        elif key == "cancel":
            raise KeyboardInterrupt


def choose_profile(input_fn=None, *, color: bool = True) -> str:
    """Choose a profile using arrow keys and Enter."""
    if input_fn is not None:
        answer = input_fn().strip().lower()
        return answer if answer in PROFILE_ORDER else "core"
    options = tuple((profile, PROFILES[profile][0]) for profile in PROFILE_ORDER)
    return _arrow_select("Step 1 — Choose an installation profile", options, color=color)


def choose_full_install(input_fn=None, *, color: bool = True) -> bool:
    """Choose selected-profile or full dependency installation."""
    if input_fn is not None:
        return input_fn().strip().lower() in ("2", "full", "all", "y", "yes")
    choice = _arrow_select(
        "Step 2 — Choose dependency size",
        (("profile", "Selected profile only"), ("full", "Full Aion installation")),
        color=color,
    )
    return choice == "full"


def confirm_install(input_fn=None, *, color: bool = True) -> bool:
    """Ask for final confirmation before invoking pip."""
    if input_fn is not None:
        return input_fn().strip().lower() in ("", "y", "yes")
    choice = _arrow_select(
        "Step 3 — Start installation?",
        (("yes", "Yes, start installation"), ("no", "No, cancel")),
        color=color,
    )
    return choice == "yes"


def _print_plan(profile: str, *, full: bool, spec: str, color: bool) -> None:
    print()
    print(_style("  Installation plan", "1", color))
    print(f"  Profile: {_style(PROFILES[profile][0], '92', color)}")
    print("  Required: " + ", ".join(CORE_PACKAGES))
    if full:
        print("  Optional: all Aion feature libraries")
    else:
        optional = PROFILE_PACKAGES[profile]
        print("  Optional: " + (", ".join(optional) if optional else "none"))
    print(f"  Package: {_style(spec, '96', color)}")
    print()


def _print_success(*, color: bool) -> None:
    """Print the post-installation welcome screen."""
    banner = (
        "  ╔════════════════════════════════════════════╗\n"
        "  ║                 THANK YOU                  ║\n"
        "  ╚════════════════════════════════════════════╝"
    )
    print()
    print(_style(banner, "92", color))
    print()
    print(_style("  Your Aion installation is ready.", "1", color))
    print("  Start using the library:")
    print("    import aion")
    print("    aion.doctor")
    print()
    print(_style("  Aqwel AI: https://aqwelai.xyz", "96", color))
    print(_style("  Aion GitHub: https://github.com/Aqwel-AI/Aion", "96", color))
    print()


def _print_first_run_welcome(*, color: bool) -> None:
    """Show the AION ONLINE screen once after a successful first install."""
    if FIRST_RUN_MARKER.exists():
        return
    banner = (
        "  ╔════════════════════════════════════════════╗\n"
        "  ║                 AION ONLINE               ║\n"
        "  ╚════════════════════════════════════════════╝"
    )
    print(_style(banner, "96", color))
    print(_style("  Welcome to the Aqwel AI research environment.", "1", color))
    print()
    print("  Try these commands:")
    print(_style("    aion info       Check your environment", "36", color))
    print(_style("    aion doctor     Run diagnostics", "36", color))
    print(_style("    aion start      Open the Aion Hub", "36", color))
    print()
    try:
        FIRST_RUN_MARKER.parent.mkdir(parents=True, exist_ok=True)
        FIRST_RUN_MARKER.touch()
    except OSError:
        pass


def _print_cancelled(*, color: bool) -> None:
    """Show a friendly cancellation message instead of a traceback."""
    print()


def _choose_failure_action(*, color: bool) -> str:
    """Choose whether to retry a failed installation or leave the installer."""
    return _arrow_select(
        "Installation failed — choose an action",
        (
            ("retry", "Retry installation"),
            ("skip", "Skip and exit"),
            ("cancel", "Cancel"),
        ),
        color=color,
    )
    print(_style("  ✕ Installation cancelled by user.", "31", color))
    print(_style("  No changes were made.", "2", color))
    print()


def _run_install(command: Sequence[str], *, color: bool) -> int:
    """Run pip with a compact animated progress display in a real terminal."""
    _append_install_log("COMMAND: " + " ".join(command))
    interactive = color and hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    if not interactive:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        if output:
            print(output.rstrip())
        _append_install_log(f"RESULT: exit code {completed.returncode}")
        if output:
            _append_install_log("OUTPUT:\n" + output.rstrip())
        return completed.returncode

    quiet_command = list(command) + ["--quiet", "--disable-pip-version-check"]
    process = subprocess.Popen(
        quiet_command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    frames = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    phases = (
        "resolving dependencies",
        "checking installed packages",
        "installing Aion components",
        "finalizing environment",
    )
    started = time.monotonic()
    tick = 0
    try:
        while process.poll() is None:
            elapsed = int(time.monotonic() - started)
            phase = phases[min(elapsed // 2, len(phases) - 1)]
            frame = frames[tick % len(frames)]
            line = _style(f"  {frame} {phase} ...", "92", color)
            sys.stdout.write("\r\033[K" + line)
            sys.stdout.flush()
            tick += 1
            time.sleep(0.08)
    except KeyboardInterrupt:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        _append_install_log("RESULT: interrupted by user")
        raise

    error_output = process.stderr.read() if process.stderr is not None else ""
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()
    if process.returncode == 0:
        print(_style("  ✓ Dependencies installed", "92", color))
    elif error_output.strip():
        print(_style("  Installation output:", "31", color))
        print(error_output.rstrip())
    _append_install_log(f"RESULT: exit code {process.returncode}")
    if error_output.strip():
        _append_install_log("OUTPUT:\n" + error_output.rstrip())
    return process.returncode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aion setup",
        description="Choose and install an Aqwel-Aion feature profile.",
    )
    parser.add_argument(
        "--profile",
        choices=PROFILE_ORDER,
        help="Install a profile without opening the interactive menu.",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Install the current checkout in editable mode instead of PyPI.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the pip command without running it.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Choose the full dependency set without asking the second question.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Start installation without the final confirmation prompt.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable green terminal colors.",
    )
    parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Show the AION logo without animation.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the interactive installer and return a process exit code."""
    args = _build_parser().parse_args(argv)
    theme = _set_active_theme(configured_theme())
    color = (
        not args.no_color
        and not os.environ.get("NO_COLOR")
        and supports_color(theme)
    )

    try:
        interactive = not args.profile and sys.stdin.isatty()
        if not args.profile and not interactive:
            print("Aion setup needs an interactive terminal. Use --profile for scripts or CI.")
            return 2

        if interactive:
            from .install_splash import show_install_intro

            show_install_intro(animated=not args.no_animation, color=color)

        checks = _preflight_checks(local=args.local)
        _print_preflight(checks, color=color, theme=theme)
        if not _preflight_ok(checks):
            print(_style("  Preflight failed. Fix the required checks and try again.", "31", color))
            _append_install_log("PREFLIGHT: failed")
            _print_log_path(color=color)
            return 1

        if args.profile:
            profile = args.profile
        else:
            profile = choose_profile(color=color)

        full = args.full
        if interactive and not args.full:
            full = choose_full_install(color=color)

        spec = install_spec(profile, local=args.local, full=full)
        command = [sys.executable, "-m", "pip", "install", "--upgrade"]
        if args.local:
            command.extend(["-e", spec])
        else:
            command.append(spec)

        rendered = " ".join(command)
        _append_install_log(f"PROFILE: {profile}; full={full}; theme={theme}")
        _print_plan(profile, full=full, spec=spec, color=color)
        print(_style(f"  $ {rendered}", "2", color))
        if interactive and not args.yes and not confirm_install(color=color):
            _print_cancelled(color=color)
            return 0
    except KeyboardInterrupt:
        _print_cancelled(color=color)
        return 130

    if args.dry_run:
        print(_style("  Dry run complete.", "92", color))
        return 0

    try:
        result_code = _run_install(command, color=color)
        while result_code != 0 and interactive:
            action = _choose_failure_action(color=color)
            if action == "retry":
                print(_style("  Retrying installation...", "33", color))
                result_code = _run_install(command, color=color)
            elif action == "skip":
                print(_style("  Installation skipped; some dependencies may be missing.", "33", color))
                _print_log_path(color=color)
                return result_code
            else:
                _print_cancelled(color=color)
                return 130
    except KeyboardInterrupt:
        _print_cancelled(color=color)
        return 130
    if result_code == 0:
        _print_success(color=color)
        _print_first_run_welcome(color=color)
        _print_log_path(color=color)
        print("  Run `aion doctor` to verify your environment.")
    else:
        print(_style(f"\n  Installation failed with exit code {result_code}.", "31", color))
        _print_log_path(color=color)
    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
