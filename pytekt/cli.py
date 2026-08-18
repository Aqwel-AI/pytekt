#!/usr/bin/env python3
"""
PyTekt - Command Line Interface
===================================

Entry point for running PyTekt library functionality from the shell. Exposes
subcommands for chat, embeddings, evaluation, prompt templates, file watching,
and Git operations (status, log, diff, etc.). Uses argparse for parsing;
help text and defaults are defined per subcommand. The Git subcommands
require the optional pytekt.git module; if it is not importable, Git-related
options are still defined but may report that Git is unavailable at runtime.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import argparse
import os
import signal
import subprocess
import sys
import time

try:
    from . import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


def _version_string():
    from . import __version__
    return __version__


def run_monitor_command(
    host: str = "127.0.0.1",
    port: int = 8000,
    open_browser: bool = True,
    open_docs: bool = False,
) -> None:
    """Delegate to ``pytekt.monitor.launch`` (keeps optional deps out of import graph until used)."""
    from .monitor.launch import run_monitor_command as _run

    _run(
        host=host,
        port=port,
        open_browser=open_browser,
        open_docs=open_docs,
    )

def run_command(command):
    """
    Execute a shell command and return its standard output as a stripped string.
    Uses subprocess with shell=True, capture_output=True, and text=True.
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def _build_parser():
    parser = argparse.ArgumentParser(
        description="PyTekt - AI utilities and research library CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
High-value commands:
  pytekt help                      Show all available PyTekt commands
  pytekt config                    Manage CLI settings (~/.pytekt.yaml)
  pytekt start                     Open the PyTekt Hub dashboard in the browser
  pytekt info                      Show environment and optional dependencies
  pytekt embed <file>              Embed a file (or use --text)
  pytekt eval <preds> <answers>    Evaluate predictions
  pytekt prompt --list             List prompt templates
  pytekt chat                      Interactive prompt tool (template-only)
  pytekt physics / pytekt universe   Physics toolkit / astronomy toolkit
  pytekt vision                    Computer vision (I/O, convert, edges) — needs [vision]

Other commands:
  pytekt git --help                Git repository tools
  pytekt monitor / dashboard       Hardware dashboard + API (needs pip install 'pytekt[monitor]')
  pytekt --version                 Show version
  pytekt welcome                   Animated install screen (module list)
  pytekt doctor                    Check research environment (deps, tracker, native ext)
  pytekt benchmark                 Run standard ML benchmark suite

If ``pytekt`` is not found after pip install, your Python scripts directory is not on PATH.
Use the same commands as: python3 -m pytekt …   (example: python3 -m pytekt monitor)
        """,
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # start (hub)
    start_parser = subparsers.add_parser("start", help="Open the PyTekt Hub dashboard in the browser")
    start_parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    start_parser.add_argument("--port", "-p", type=int, default=3000, help="Port (default 3000)")
    start_parser.add_argument("--no-browser", action="store_true", help="Do not open a browser tab")

    # info
    subparsers.add_parser("info", help="Show environment and optional dependencies")

    # embed
    embed_parser = subparsers.add_parser("embed", help="Embed a file or text (sentence-transformers or hash fallback)")
    embed_parser.add_argument("filepath", nargs="?", default=None, help="File to embed")
    embed_parser.add_argument("--text", type=str, default=None, help="Text to embed (instead of file)")
    embed_parser.add_argument("--model", type=str, default="all-MiniLM-L6-v2", help="Model name (default: all-MiniLM-L6-v2)")
    embed_parser.add_argument("--output", "-o", type=str, default=None, help="Save vector to .npy file")

    # eval
    eval_parser = subparsers.add_parser("eval", help="Evaluate prediction accuracy (classification or regression)")
    eval_parser.add_argument("preds", type=str, help="Predictions file (JSON, CSV, or text)")
    eval_parser.add_argument("answers", type=str, help="Ground truth file (same format)")

    # prompt
    prompt_parser = subparsers.add_parser("prompt", help="Show or list prompt templates")
    prompt_parser.add_argument("--type", "-t", type=str, default="system", help="Template type (system, code_review, etc.)")
    prompt_parser.add_argument("--list", "-l", action="store_true", help="List available prompt types")

    # watch
    watch_parser = subparsers.add_parser("watch", help="Watch a file for changes and re-embed on save")
    watch_parser.add_argument("filepath", type=str, help="File to watch")
    watch_parser.add_argument("--interval", "-i", type=float, default=1.0, help="Poll interval in seconds (default: 1.0)")
    watch_parser.add_argument("--output-dir", "-o", type=str, default=None, help="Directory to save .npy embeddings on change")

    # chat
    subparsers.add_parser("chat", help="Start interactive chat (prompt templates + embedding)")

    # git
    git_parser = subparsers.add_parser("git", help="Git repository operations")
    git_subparsers = git_parser.add_subparsers(dest="git_command", help="Git commands")

    git_status_parser = git_subparsers.add_parser("status", help="Show repository status")
    git_status_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")

    git_log_parser = git_subparsers.add_parser("log", help="Show commit history")
    git_log_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    git_log_parser.add_argument("--limit", type=int, default=10, help="Maximum number of commits to show")

    git_branches_parser = git_subparsers.add_parser("branches", help="List all branches")
    git_branches_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")

    git_diff_parser = git_subparsers.add_parser("diff", help="Show diff output")
    git_diff_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    git_diff_parser.add_argument("--commit", help="Commit hash to diff against")

    # version
    subparsers.add_parser("version", help="Show package version")

    # welcome (install animation)
    welcome_parser = subparsers.add_parser(
        "welcome",
        help="Show install celebration screen with animated module list",
    )
    welcome_parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Print static list (no delays)",
    )

    subparsers.add_parser("doctor", help="Diagnose environment for research workflows")

    bench_parser = subparsers.add_parser(
        "benchmark",
        help="Run multi-seed ML benchmark suite on built-in datasets",
    )
    bench_parser.add_argument(
        "--seeds",
        type=int,
        default=3,
        help="Number of random seeds (0..n-1) (default: 3)",
    )
    bench_parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Save leaderboard markdown to file",
    )

    # monitor / dashboard (optional deps: fastapi, uvicorn, psutil, nvidia-ml-py)
    def _add_monitor_args(p):
        p.add_argument("--host", default="127.0.0.1", help="Bind address")
        p.add_argument("--port", "-p", type=int, default=8000, help="Port (default 8000)")
        p.add_argument(
            "--no-browser",
            action="store_true",
            help="Do not open a browser tab (dashboard at /dashboard/ by default)",
        )
        p.add_argument(
            "--docs",
            action="store_true",
            help="Open Swagger UI (/docs) instead of the hardware dashboard",
        )

    mon_parser = subparsers.add_parser(
        "monitor",
        help="Start hardware dashboard and metrics API (install 'pytekt[monitor]')",
    )
    _add_monitor_args(mon_parser)
    dash_parser = subparsers.add_parser(
        "dashboard",
        help="Same as monitor: open live hardware dashboard in the browser",
    )
    _add_monitor_args(dash_parser)

    # agent — autonomous terminal coding assistant
    agent_parser = subparsers.add_parser(
        "agent",
        help="Autonomous coding agent (read, edit, run in your project)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "PyTekt Agent — autonomous terminal coding assistant.\n\n"
            "One-shot:    pytekt agent \"fix the type error in utils.py\"\n"
            "Interactive: pytekt agent\n"
        ),
    )
    agent_parser.add_argument(
        "task",
        nargs="?",
        default=None,
        help="Task description for one-shot mode (omit to enter the REPL)",
    )
    agent_parser.add_argument(
        "--provider", "-P",
        default="openai",
        metavar="NAME",
        help=(
            "LLM provider: openai, anthropic, gemini, ollama, deepseek, nvidia "
            "(default: openai)"
        ),
    )
    agent_parser.add_argument(
        "--model", "-m",
        default=None,
        metavar="MODEL",
        help="Model name forwarded to the provider (default: provider's default)",
    )
    agent_parser.add_argument(
        "--api-key", "-k",
        default=None,
        metavar="KEY",
        help="API key (overrides env vars and ~/.pytekt.yaml)",
    )
    agent_parser.add_argument(
        "--mode", "-M",
        choices=["code", "talk"],
        default="code",
        help="Agent mode: 'code' (autonomous coding like Cursor) or 'talk' (technical chat & questions) (default: code)",
    )
    agent_parser.add_argument(
        "--workspace", "-w",
        default=None,
        metavar="DIR",
        help="Root directory for file operations (default: current directory)",
    )
    agent_parser.add_argument(
        "--max-rounds",
        type=int,
        default=16,
        metavar="N",
        help="Maximum tool-call rounds per turn (default: 16)",
    )
    agent_parser.add_argument(
        "--no-shell",
        action="store_true",
        help="Disable run_command (safer for untrusted code bases)",
    )
    subparsers.add_parser(
        "api",
        help="API connect (not available in this version)",
    )
    subparsers.add_parser(
        "auth",
        help="Auth commands (not available in this version)",
    )

    # config
    config_parser = subparsers.add_parser("config", help="Manage PyTekt CLI configuration")
    config_parser.add_argument("key", nargs="?", help="Config key (e.g., universe.latitude)")
    config_parser.add_argument("value", nargs="?", help="Value to set")

    # help
    subparsers.add_parser("help", help="Show all available PyTekt commands")

    # db
    db_parser = subparsers.add_parser("db", help="Database sync, status, and demos")
    db_sub = db_parser.add_subparsers(dest="db_action", help="Database actions")
    db_sub.add_parser("status", help="Show configured database URL and connection")
    db_sync_usage = db_sub.add_parser("sync-usage", help="Import usage JSONL into DB")
    db_sync_usage.add_argument("--url", help="Database URL (default from ~/.pytekt.yaml db.url)")
    db_sync_usage.add_argument("--table", default="usage_events", help="Target table")
    db_sync_tracker = db_sub.add_parser("sync-tracker", help="Import experiment runs into DB")
    db_sync_tracker.add_argument("--url", help="Database URL")
    db_sync_tracker.add_argument("--root", default=".pytekt_runs", help="Tracker root directory")
    db_sync_tracker.add_argument("--table", default="experiments", help="Target table")
    db_sub.add_parser("demo", help="Quick in-memory SQLite demo")

    def _add_universe_subparsers(parent):
        u_sub = parent.add_subparsers(dest="universe_action", help="Universe actions")
        u_sub.add_parser("moon", help="Current moon phase")
        u_sky = u_sub.add_parser("sky", help="Bright stars above horizon")
        u_sky.add_argument("--lat", type=float, default=40.18, help="Observer latitude (deg)")
        u_sky.add_argument("--lon", type=float, default=44.51, help="Observer longitude (deg, east +)")
        u_sky.add_argument("--min-alt", type=float, default=10.0, help="Minimum altitude (deg)")
        u_sky.add_argument("--limit", type=int, default=20, help="Max objects to print")
        u_coords = u_sub.add_parser("coords", help="RA/Dec to Alt/Az now")
        u_coords.add_argument("ra", help='RA e.g. "6h 45m 08s"')
        u_coords.add_argument("dec", help='Dec e.g. "-16d 42m 58s"')
        u_coords.add_argument("--lat", type=float, default=40.18)
        u_coords.add_argument("--lon", type=float, default=44.51)
        u_sep = u_sub.add_parser("separation", help="Angular separation between two points")
        u_sep.add_argument("--ra1", required=True)
        u_sep.add_argument("--dec1", required=True)
        u_sep.add_argument("--ra2", required=True)
        u_sep.add_argument("--dec2", required=True)
        u_sub.add_parser("demo", help="Run coordinate transform demo")
        u_web = u_sub.add_parser("web", help="Open Universe astronomy dashboard (browser)")
        u_web.add_argument("--host", default="127.0.0.1", help="Bind address")
        u_web.add_argument("--port", "-p", type=int, default=3857, help="Port (default 3857)")
        u_web.add_argument("--no-browser", action="store_true", help="Do not open browser")

    universe_parser = subparsers.add_parser("universe", help="Astronomy: moon, sky, coordinates (C++ fast path)")
    _add_universe_subparsers(universe_parser)
    cosmos_parser = subparsers.add_parser("cosmos", help="[deprecated] use: pytekt universe")
    _add_universe_subparsers(cosmos_parser)

    def _add_universe_dashboard_args(p):
        p.add_argument("--host", default="127.0.0.1", help="Bind address")
        p.add_argument("--port", "-p", type=int, default=3857, help="Port (default 3857)")
        p.add_argument("--no-browser", action="store_true", help="Do not open browser")

    universe_dash_parser = subparsers.add_parser(
        "universe-dashboard",
        help="Open Universe astronomy dashboard (browser)",
    )
    _add_universe_dashboard_args(universe_dash_parser)
    cosmos_dash_parser = subparsers.add_parser(
        "cosmos-dashboard",
        help="[deprecated] use: pytekt universe-dashboard",
    )
    _add_universe_dashboard_args(cosmos_dash_parser)

    def _add_physics_subparsers(parent):
        p_sub = parent.add_subparsers(dest="physics_action", help="Physics actions")
        p_query = p_sub.add_parser("query", help="Natural-language physics query")
        p_query.add_argument("text", help='Query e.g. "kinetic energy mass=2 velocity=3"')
        p_pend = p_sub.add_parser("pendulum", help="Simulate simple pendulum")
        p_pend.add_argument("--length", type=float, default=1.0, help="Pendulum length (m)")
        p_pend.add_argument("--angle-deg", type=float, default=15.0, help="Initial angle (deg)")
        p_pend.add_argument("--dt", type=float, default=0.01, help="Time step (s)")
        p_pend.add_argument("--steps", type=int, default=2000, help="Integration steps")
        p_proj = p_sub.add_parser("projectile", help="Simulate projectile motion")
        p_proj.add_argument("--v0", type=float, default=20.0, help="Initial speed (m/s)")
        p_proj.add_argument("--angle", type=float, default=45.0, help="Launch angle (deg)")
        p_proj.add_argument("--drag", type=float, default=0.0, help="Drag coefficient")
        p_proj.add_argument("--dt", type=float, default=0.01)
        p_proj.add_argument("--steps", type=int, default=1000)
        p_force = p_sub.add_parser("force", help="Compute F = m*a")
        p_force.add_argument("--mass", type=float, required=True)
        p_force.add_argument("--acceleration", type=float, required=True)
        p_ke = p_sub.add_parser("ke", help="Compute kinetic energy")
        p_ke.add_argument("--mass", type=float, required=True)
        p_ke.add_argument("--velocity", type=float, required=True)
        p_gas = p_sub.add_parser("gas", help="Ideal gas pressure")
        p_gas.add_argument("--moles", type=float, required=True)
        p_gas.add_argument("--temperature", type=float, required=True)
        p_gas.add_argument("--volume", type=float, required=True)
        p_units = p_sub.add_parser("units", help="Unit conversion")
        p_units.add_argument("value", type=float, help="Numeric value")
        p_units.add_argument("convert", help="Conversion name e.g. km_to_m")
        p_sub.add_parser("tasks", help="List supported NL query tasks")
        p_sub.add_parser("demo", help="Run pendulum demo")
        p_web = p_sub.add_parser("web", help="Open physics dashboard (browser)")
        p_web.add_argument("--host", default="127.0.0.1")
        p_web.add_argument("--port", "-p", type=int, default=3858)
        p_web.add_argument("--no-browser", action="store_true")

    physics_parser = subparsers.add_parser(
        "physics",
        help="Classical physics: simulations, formulas, query router (C++ fast path)",
    )
    _add_physics_subparsers(physics_parser)

    def _add_physics_dashboard_args(p):
        p.add_argument("--host", default="127.0.0.1")
        p.add_argument("--port", "-p", type=int, default=3858)
        p.add_argument("--no-browser", action="store_true")

    physics_dash_parser = subparsers.add_parser(
        "physics-dashboard",
        help="Open physics dashboard (browser)",
    )
    _add_physics_dashboard_args(physics_dash_parser)

    vision_parser = subparsers.add_parser(
        "vision",
        help="Computer vision: image info, convert/resize, Canny edges (needs [vision])",
    )
    from .vision.cli import build_vision_parser

    build_vision_parser(vision_parser)

    return parser, git_parser


def run_help():
    """
    Build the same parser structure as main() and return its --help output as a string.
    Used when the CLI help text is needed programmatically (e.g. from another module).
    """
    from io import StringIO

    parser, _ = _build_parser()
    help_io = StringIO()
    sys.stdout = help_io
    parser.print_help()
    sys.stdout = sys.__stdout__
    return help_io.getvalue()


def version_command():
    """Print package version."""
    print(f"pytekt {_version_string()}")


def info_command():
    """Print environment and optional dependency status."""
    from . import __version__
    from . import embed
    print("PyTekt (pytekt) - Environment")
    print("=" * 50)
    print(f"Version:    {__version__}")
    print(f"Python:     {sys.version.split()[0]}")
    print()
    optional = []
    try:
        from . import embed
        optional.append(("sentence-transformers", getattr(embed, "_HAS_SENTENCE_TRANSFORMERS", False)))
    except Exception:
        optional.append(("sentence-transformers", False))
    try:
        import matplotlib  # type: ignore[import-untyped]
        optional.append(("matplotlib", True))
    except ImportError:
        optional.append(("matplotlib", False))
    try:
        import openai  # type: ignore[import-untyped]
        optional.append(("openai", True))
    except ImportError:
        optional.append(("openai", False))
    print("Optional dependencies:")
    for name, available in optional:
        print(f"  {name}: {'available' if available else 'not installed'}")
    try:
        from .native import native_backends

        for status in native_backends().values():
            state = "available" if status.available else f"fallback ({status.fallback})"
            print(f"  {status.name} (C++): {state}")
    except Exception:
        print("  native C++ backends: unavailable")
    print()
    print("Git integration:", "available" if GIT_AVAILABLE else "not installed (pip install gitpython)")
    print()

    print("Usage: pytekt <command> [options]")
    print("       pytekt --help")


def embed_command(filepath=None, text=None, model="all-MiniLM-L6-v2", output=None):
    """Embed a file or text and optionally save the vector."""
    from . import embed as embed_module
    if text is not None:
        vec = embed_module.embed_text(text, model_name=model)
        print(f"Embedded text (length {len(text)} chars) -> vector shape {vec.shape}")
    elif filepath:
        if not os.path.isfile(filepath):
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        vec = embed_module.embed_file(filepath, model_name=model)
        if vec is None:
            sys.exit(1)
        print(f"Embedded file: {filepath} -> vector shape {vec.shape}")
    else:
        print("Error: Provide either a file path or --text \"...\"", file=sys.stderr)
        sys.exit(1)
    if output:
        import numpy as np
        np.save(output, vec)
        print(f"Saved vector to: {output}")


def eval_command(preds_path, answers_path):
    """Evaluate predictions against ground truth and print metrics."""
    from . import evaluate as eval_module
    if not os.path.isfile(preds_path):
        print(f"Error: Predictions file not found: {preds_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(answers_path):
        print(f"Error: Answers file not found: {answers_path}", file=sys.stderr)
        sys.exit(1)
    metrics = eval_module.evaluate_predictions(preds_path, answers_path)
    if not metrics:
        print("Evaluation failed or produced no metrics.", file=sys.stderr)
        sys.exit(1)
    print("Metrics:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")


def prompt_command(prompt_type="user", list_types=False):
    """Show a prompt template or list available types."""
    from . import prompt as prompt_module
    templates = prompt_module.get_prompt_templates()
    if list_types:
        print("Available prompt types:", ", ".join(templates.keys()))
        return
    if prompt_type == "user" and "user" not in templates:
        prompt_type = "system"
    if prompt_type not in templates:
        print(f"Unknown type '{prompt_type}'. Available: {', '.join(templates.keys())}")
        prompt_type = "system"
    prompt_module.show_prompt(prompt_type)


def watch_command(filepath, interval=1.0, output_dir=None):
    """Watch a file for changes and re-embed on modification."""
    from . import embed as embed_module
    from . import watcher
    if not os.path.isfile(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    def on_change(path):
        print(f"[{path}] changed, embedding...")
        vec = embed_module.embed_file(path)
        if vec is not None and output_dir:
            import numpy as np
            base = os.path.splitext(os.path.basename(path))[0]
            out = os.path.join(output_dir, f"{base}.npy")
            np.save(out, vec)
            print(f"  Saved to {out}")

    ok = watcher.watch_file_for_changes(filepath, on_change, interval=interval)
    if not ok:
        sys.exit(1)
    print(f"Watching {filepath} (interval={interval}s). Ctrl+C to stop.")
    try:
        signal.pause()
    except AttributeError:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        watcher.stop_all_watchers()
        print("\nStopped.")


def chat_command():
    """Interactive chat REPL with prompt templates and optional embedding."""
    from . import prompt as prompt_module
    templates = prompt_module.get_prompt_templates()
    print("PyTekt Chat (prompt templates + helpers)")
    print("Commands: /list, /prompt <type>, /quit")
    print("Types:", ", ".join(templates.keys()))
    print("-" * 50)
    while True:
        try:
            line = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not line:
            continue
        if line.lower() == "/quit":
            print("Bye.")
            break
        if line.lower() == "/list":
            for k, v in templates.items():
                print(f"  {k}: {v[:60]}...")
            continue
        if line.lower().startswith("/prompt "):
            name = line[8:].strip().lower()
            if name in templates:
                print(templates[name])
            else:
                print(f"Unknown type. Use one of: {', '.join(templates.keys())}")
            continue
        optimized = prompt_module.optimize_prompt_for_ai(line)
        if optimized != line:
            print(f"(Optimized) {optimized}")
        else:
            print(f"You said: {line}")
        try:
            from . import embed as embed_module
            if getattr(embed_module, "_HAS_SENTENCE_TRANSFORMERS", False):
                vec = embed_module.embed_text(line)
                print(f"  [embedding dim: {vec.shape[0]}]")
        except Exception:
            pass


def git_status_command(repo_path="."):
    """
    Print repository status for the given path: branch, working tree state,
    staged files, and untracked files. Requires GIT_AVAILABLE; otherwise prints
    an installation message.
    """
    if not GIT_AVAILABLE:
        print("Git integration not available. Install GitPython with: pip install gitpython")
        return

    status = git.get_git_status(repo_path)
    if "error" in status:
        print(status["error"])
        return

    print(f"Repository: {status['repo_path']}")
    print(f"Branch: {status['current_branch']}")
    print(f"Working directory: {'Clean' if status['working_dir_clean'] else 'Dirty'}")

    if status["staged_files"]:
        print(f"Staged files ({len(status['staged_files'])}):")
        for file in status["staged_files"]:
            print(f"   + {file}")

    if status["untracked_files"]:
        print(f"Untracked files ({len(status['untracked_files'])}):")
        for file in status["untracked_files"]:
            print(f"   ? {file}")


def git_log_command(repo_path=".", limit=10):
    """
    Print recent commit history for the repository at repo_path, limited to
    limit entries. Requires GIT_AVAILABLE; otherwise prints an installation message.
    """
    if not GIT_AVAILABLE:
        print("Git integration not available. Install GitPython with: pip install gitpython")
        return

    commits = git.get_recent_commits(repo_path, limit)
    if not commits or "error" in commits[0]:
        print("No commits found or error occurred")
        return

    print(f"Recent commits (showing {len(commits)}):")
    print("-" * 80)
    for commit in commits:
        print(f"{commit['hash']} - {commit['message']}")
        print(f"   {commit['author']} | {commit['date']} | {commit['files_changed']} files")
        print()


def git_branches_command(repo_path="."):
    """
    List all branches for the repository at repo_path, with the active branch
    marked. Requires GIT_AVAILABLE; otherwise prints an installation message.
    """
    if not GIT_AVAILABLE:
        print("Git integration not available. Install GitPython with: pip install gitpython")
        return

    branches = git.list_branches(repo_path)
    if not branches or "error" in branches[0]:
        print("No branches found or error occurred")
        return

    print("Branches:")
    print("-" * 40)
    for branch in branches:
        active_marker = "*" if branch["is_active"] else " "
        print(f"{active_marker} {branch['name']}")
        print(f"   Last commit: {branch['last_commit']} ({branch['last_commit_date']})")
        print()


def git_diff_command(repo_path=".", commit_hash=None):
    """
    Print diff for the working directory or for a specific commit. Requires
    GIT_AVAILABLE; otherwise prints an installation message.
    """
    if not GIT_AVAILABLE:
        print("Git integration not available. Install GitPython with: pip install gitpython")
        return

    if commit_hash:
        diff_output = git.GitManager(repo_path).get_diff(commit_hash)
    else:
        diff_output = git.GitManager(repo_path).get_diff()

    if diff_output:
        print("Diff output:")
        print("=" * 80)
        print(diff_output)
    else:
        print("No changes to show.")


def main():
    """
    Parse command-line arguments and dispatch to the appropriate subcommand.
    Prints help when no command is given or when a subcommand is unknown.
    """
    parser, git_parser = _build_parser()
    args = parser.parse_args()

    # Once per installed/updated version (wheel installs skip setuptools hooks).
    # Skip for ``pytekt welcome`` so the animation is not shown twice.
    if args.command != "welcome" and not os.environ.get("PYTEKT_NO_SPLASH"):
        try:
            from .install_splash import maybe_show_install_splash

            maybe_show_install_splash()
        except Exception:
            pass

    if getattr(args, "version", False) or args.command == "version":
        version_command()
        return
    if args.command == "start":
        from .hub.launch import run_hub

        run_hub(
            host=args.host,
            port=args.port or 3000,
            open_browser=not args.no_browser,
        )
        return
    if args.command == "welcome":
        from .install_splash import show_install_splash

        show_install_splash(animated=not getattr(args, "no_animation", False))
        return
    if args.command == "doctor":
        from .doctor import main as doctor_main

        doctor_main()
        return
    if args.command == "benchmark":
        from .experiments import BenchmarkSuite

        suite = BenchmarkSuite(seeds=list(range(args.seeds)))
        results = suite.run()
        md = suite.leaderboard_markdown(results)
        print(md)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"\nSaved: {args.output}")
        return
    if args.command == "info":
        info_command()
        return
    if args.command == "chat":
        chat_command()
        return
    if args.command == "embed":
        if args.text and args.filepath:
            print("Error: Use either filepath or --text, not both.", file=sys.stderr)
            sys.exit(1)
        embed_command(
            filepath=args.filepath,
            text=args.text,
            model=args.model,
            output=args.output,
        )
        return
    if args.command == "eval":
        eval_command(args.preds, args.answers)
        return
    if args.command == "prompt":
        prompt_command(prompt_type=args.type, list_types=args.list)
        return
    if args.command == "watch":
        watch_command(args.filepath, interval=args.interval, output_dir=args.output_dir)
        return

    if args.command in ("monitor", "dashboard"):
        run_monitor_command(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
            open_docs=args.docs,
        )
        return

    if args.command == "help":
        parser.print_help()
        return


    if args.command == "agent":
        from .agent import run_agent_cli

        # Provider-specific model defaults
        _default_models = {
            "openai":    "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-latest",
            "claude":    "claude-3-5-haiku-latest",
            "gemini":    "gemini-2.0-flash",
            "google":    "gemini-2.0-flash",
            "ollama":    "llama3",
            "deepseek":  "deepseek-chat",
            "nvidia":    "meta/llama-3.1-8b-instruct",
            "nim":       "meta/llama-3.1-8b-instruct",
        }
        provider = args.provider
        model = args.model or _default_models.get(provider.lower(), "gpt-4o-mini")

        run_agent_cli(
            task=args.task,
            workspace=args.workspace,
            provider=provider,
            model=model,
            mode=getattr(args, "mode", None),
            api_key=args.api_key,
            max_rounds=args.max_rounds,
            no_shell=args.no_shell,
        )
        return


    if args.command in ("api", "auth"):
        print(f"pytekt {args.command} — not available in 0.2.0.")
        return

    if args.command == "config":
        from .user_config import config_command

        config_command(key=args.key, value=args.value)
        return

    if args.command == "db":
        from .db.cli import db_main

        db_main(args)
        return

    if args.command in ("universe", "cosmos"):
        if args.command == "cosmos":
            import warnings

            warnings.warn("pytekt cosmos is deprecated; use pytekt universe", DeprecationWarning)
        from .universe.cli import universe_main

        universe_main(args)
        return

    if args.command in ("universe-dashboard", "cosmos-dashboard"):
        if args.command == "cosmos-dashboard":
            import warnings

            warnings.warn("pytekt cosmos-dashboard is deprecated; use pytekt universe-dashboard", DeprecationWarning)
        from .universe.launch import run_universe_dashboard

        run_universe_dashboard(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
        )
        return

    if args.command == "physics":
        from .physics.cli import physics_main

        physics_main(args)
        return

    if args.command == "physics-dashboard":
        from .physics.launch import run_physics_dashboard

        run_physics_dashboard(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
        )
        return

    if args.command == "vision":
        from .vision.cli import vision_main

        vision_main(args)
        return

    if args.command == "git" and hasattr(args, "git_command"):
        if args.git_command == "status":
            git_status_command(args.path)
        elif args.git_command == "log":
            git_log_command(args.path, args.limit)
        elif args.git_command == "branches":
            git_branches_command(args.path)
        elif args.git_command == "diff":
            git_diff_command(args.path, args.commit)
        else:
            git_parser.print_help()
    elif args.command == "git":
        git_parser.print_help()
    else:
        parser.print_help()
