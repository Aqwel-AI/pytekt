#!/usr/bin/env python3
"""
Aqwel-Aion - Command Line Interface
===================================

Entry point for running Aion library functionality from the shell. Exposes
subcommands for chat, embeddings, evaluation, prompt templates, file watching,
and Git operations (status, log, diff, etc.). Uses argparse for parsing;
help text and defaults are defined per subcommand. The Git subcommands
require the optional aion.git module; if it is not importable, Git-related
options are still defined but may report that Git is unavailable at runtime.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import argparse
import importlib.util
import json
import os
import platform
import shlex
import signal
import subprocess
import sys
import textwrap

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
    """Delegate to ``aion.monitor.launch`` (keeps optional deps out of import graph until used)."""
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


_HELP_EXAMPLES = {
    "start": "aion start",
    "ui": "aion ui --list",
    "info": "aion info",
    "embed": "aion embed notes.txt",
    "eval": "aion eval preds.json answers.json",
    "prompt": "aion prompt --list",
    "watch": "aion watch notes.txt",
    "chat": "aion chat",
    "git": "aion git status",
    "version": "aion --version",
    "setup": "aion setup",
    "install": "aion install",
    "welcome": "aion welcome",
    "doctor": "aion doctor",
    "benchmark": "aion benchmark",
    "monitor": "aion monitor",
    "dashboard": "aion dashboard",
    "agent": "aion agent search TODO",
    "api": "aion api",
    "auth": "aion auth",
    "config": "aion config",
    "help": "aion help",
    "usage": "aion usage",
    "stats": "aion stats",
    "db": "aion db status",
    "universe": "aion universe moon",
    "cosmos": "aion cosmos",
    "universe-dashboard": "aion universe-dashboard",
    "cosmos-dashboard": "aion cosmos-dashboard",
    "physics": "aion physics tasks",
    "physics-dashboard": "aion physics-dashboard",
    "vision": "aion vision --help",
    "completion": "aion completion zsh",
    "notebook": "aion notebook create research.ipynb",
    "explain": "aion explain aion/cli.py",
    "summarize": "aion summarize README.md",
    "rag": 'aion rag query "search terms"',
    "visualize": "aion visualize data.csv",
    "observe": "aion observe",
    "hardware": "aion hardware info",
    "profile": "aion profile train.py",
    "lint": "aion lint",
    "dependency-audit": "aion dependency-audit",
    "snapshot": "aion snapshot create",
    "session": "aion session list",
    "release": "aion release check",
    "changelog": "aion changelog generate",
    "completion-install": "aion completion-install zsh",
    "shell": "aion shell",
    "ask": 'aion ask "explain this result"',
    "project": "aion project init my-research",
    "run": "aion run experiment.py --experiment baseline",
    "experiment": "aion experiment compare --metric accuracy",
    "data": "aion data inspect data.csv",
    "model": "aion model list",
    "pipeline": "aion pipeline run pipeline.json",
    "test": "aion test",
    "logs": "aion logs",
    "cache": "aion cache status",
    "serve": "aion serve",
    "security": "aion security",
    "upgrade": "aion upgrade",
}

_HELP_METADATA = {
    "start": ("CORE", "Python", "READY"),
    "ui": ("CORE", "Hub / UI extras", "READY"),
    "info": ("CORE", "Python", "READY"),
    "embed": ("AI", "sentence-transformers optional", "READY"),
    "eval": ("AI", "Python", "READY"),
    "prompt": ("AI", "Python", "READY"),
    "watch": ("AI", "watchdog", "READY"),
    "chat": ("AI", "Python", "READY"),
    "git": ("DEVELOPER", "GitPython optional", "READY"),
    "version": ("CORE", "Python", "READY"),
    "setup": ("INSTALL", "pip + internet", "READY"),
    "install": ("INSTALL", "pip + internet", "READY"),
    "welcome": ("INSTALL", "Python", "READY"),
    "doctor": ("DEVELOPER", "Python", "READY"),
    "benchmark": ("AI", "numpy", "READY"),
    "monitor": ("SYSTEM", "[monitor] extra", "OPTIONAL"),
    "dashboard": ("SYSTEM", "[monitor] extra", "OPTIONAL"),
    "agent": ("AI", "Python", "READY"),
    "api": ("INTEGRATION", "FastAPI + uvicorn", "OPTIONAL"),
    "auth": ("INTEGRATION", "Environment variables", "READY"),
    "config": ("CORE", "Python", "READY"),
    "help": ("CORE", "Python", "READY"),
    "usage": ("DEVELOPER", "Python + dashboard assets", "READY"),
    "stats": ("DEVELOPER", "Python + dashboard assets", "READY"),
    "db": ("DATABASE", "[db] extra", "OPTIONAL"),
    "universe": ("SCIENCE", "native extra optional", "OPTIONAL"),
    "cosmos": ("SCIENCE", "Use universe", "DEPRECATED"),
    "universe-dashboard": ("SCIENCE", "native extra optional", "OPTIONAL"),
    "cosmos-dashboard": ("SCIENCE", "Use universe-dashboard", "DEPRECATED"),
    "physics": ("SCIENCE", "native extra optional", "OPTIONAL"),
    "physics-dashboard": ("SCIENCE", "native extra optional", "OPTIONAL"),
    "vision": ("SCIENCE", "[vision] extra", "OPTIONAL"),
    "completion": ("DEVELOPER", "Python", "READY"),
    "ask": ("AI", "provider + API key", "READY"),
    "project": ("CORE", "Python", "READY"),
    "run": ("RESEARCH", "Python", "READY"),
    "experiment": ("RESEARCH", "Python", "READY"),
    "data": ("DATA", "Python", "READY"),
    "model": ("AI", "provider optional", "READY"),
    "pipeline": ("RESEARCH", "Python", "READY"),
    "test": ("DEVELOPER", "pytest", "READY"),
    "logs": ("DEVELOPER", "Python", "READY"),
    "cache": ("SYSTEM", "SQLite", "READY"),
    "serve": ("INTEGRATION", "FastAPI + uvicorn", "OPTIONAL"),
    "security": ("DEVELOPER", "Python", "READY"),
    "upgrade": ("INSTALL", "pip + internet", "READY"),
    "notebook": ("RESEARCH", "Jupyter optional", "READY"),
    "explain": ("AI", "Python", "READY"),
    "summarize": ("AI", "Python", "READY"),
    "rag": ("AI", "RAG optional", "READY"),
    "visualize": ("VIZ", "matplotlib", "READY"),
    "observe": ("SCIENCE", "universe", "READY"),
    "hardware": ("SYSTEM", "psutil optional", "OPTIONAL"),
    "profile": ("DEVELOPER", "Python", "READY"),
    "lint": ("DEVELOPER", "Ruff/Black/Pytest", "OPTIONAL"),
    "dependency-audit": ("DEVELOPER", "pip", "READY"),
    "snapshot": ("DEVELOPER", "Python", "READY"),
    "session": ("AI", "Python", "READY"),
    "release": ("RELEASE", "Python", "READY"),
    "changelog": ("RELEASE", "Git", "READY"),
    "completion-install": ("DEVELOPER", "Python", "READY"),
    "shell": ("CORE", "Python", "READY"),
}


def _get_subparsers(parser):
    """Return the root command registry from an argparse parser."""
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    raise RuntimeError("Aion command parser has no subcommands")


def _command_rows(subparsers, search=None):
    descriptions = {action.dest: action.help for action in subparsers._choices_actions}
    query = search.casefold().strip() if search else ""
    rows = []
    for command, command_parser in subparsers.choices.items():
        description = command_parser.description or descriptions.get(command)
        if not description or description == "==SUPPRESS==":
            description = "Command options and actions"
        category, requirements, status = _HELP_METADATA.get(
            command,
            ("OTHER", "See command help", "READY"),
        )
        row = {
            "command": command,
            "category": category,
            "description": description,
            "requirements": requirements,
            "status": status,
            "example": _HELP_EXAMPLES.get(command, f"aion {command}"),
        }
        if query and not any(query in str(value).casefold() for value in row.values()):
            continue
        rows.append(row)
    return rows


def _render_table(headers, rows, widths):
    """Render wrapped rows as a portable ASCII table."""
    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    lines = [
        separator,
        "| "
        + " | ".join(f"{header:<{width}}" for header, width in zip(headers, widths))
        + " |",
        separator,
    ]
    for row in rows:
        wrapped = [
            textwrap.wrap(
                str(value),
                width=width,
                break_long_words=False,
                break_on_hyphens=False,
            )
            or [""]
            for value, width in zip(row, widths)
        ]
        for index in range(max(len(cell) for cell in wrapped)):
            lines.append(
                "| "
                + " | ".join(
                    f"{cell[index] if index < len(cell) else '':<{width}}"
                    for cell, width in zip(wrapped, widths)
                )
                + " |"
            )
        lines.append(separator)
    return lines


def _format_help_table(subparsers, search=None) -> str:
    """Build the categorized command reference shown by ``aion --help``."""
    rows = _command_rows(subparsers, search=search)
    overview_rows = [
        (row["command"], row["category"], row["description"], row["status"])
        for row in rows
    ]
    detail_rows = [
        (row["command"], row["requirements"], row["example"]) for row in rows
    ]
    lines = [
        "",
        "AION COMMAND REFERENCE" + (f" — SEARCH: {search}" if search else ""),
    ]
    lines.extend(
        _render_table(
            ("COMMAND", "CATEGORY", "DESCRIPTION", "STATUS"),
            overview_rows,
            (18, 12, 48, 10),
        )
    )
    lines.extend(["", "COMMAND DETAILS"])
    lines.extend(
        _render_table(
            ("COMMAND", "REQUIREMENTS", "EXAMPLE"),
            detail_rows,
            (18, 28, 38),
        )
    )

    lines.extend(
        [
            "",
            "QUICK START",
            "  aion install                 Interactive dependency installer",
            "  aion info                    Show runtime and optional modules",
            "  aion doctor                  Diagnose the research environment",
            "  aion start                   Open the Aion Hub dashboard",
            "  aion shell                   Run Aion commands interactively",
            "",
            "COMMON OPTIONS",
            "  aion --help                  Show this command table",
            "  aion --version               Show the installed Aion version",
            "  aion <command> --help        Show options for one command",
            "  aion help --search physics  Find commands by name or description",
            "  aion --help --json           Export this reference as JSON",
            "  aion completion zsh          Install shell completion support",
            "",
            "NOTES",
            "  Optional features may need an extra, for example:",
            "  pip install 'aqwel-aion[monitor]'",
            "  If the aion command is not on PATH, use: python3 -m aion <command>",
        ]
    )
    return "\n".join(lines)


def _format_help_json(subparsers, search=None) -> str:
    """Return command metadata for scripts and documentation tooling."""
    return json.dumps(
        _command_rows(subparsers, search=search), indent=2, ensure_ascii=False
    )


def _completion_script(shell, commands):
    """Return a lightweight completion script for a supported shell."""
    command_list = " ".join(commands)
    if shell == "bash":
        return f'''_aion_completion() {{
    local current="${{COMP_WORDS[COMP_CWORD]}}"
    COMPREPLY=( $(compgen -W "{command_list}" -- "$current") )
}}
complete -F _aion_completion aion
'''
    if shell == "zsh":
        return f"""#compdef aion
_arguments '1:command:(({command_list}))'
"""
    if shell == "fish":
        return f'''complete -c aion -f -a "{command_list}"
'''
    if shell == "powershell":
        return f'''Register-ArgumentCompleter -Native -CommandName aion -ScriptBlock {{
    param($wordToComplete, $commandAst, $cursorPosition)
    "{command_list}" -split " " | Where-Object {{ $_ -like "$wordToComplete*" }} |
        ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
}}
'''
    raise ValueError(f"Unsupported shell: {shell}")


_SHELL_HELP = """Aion shell commands:
  help, ?              Show this message
  history              Show commands entered in this session
  exit, quit           Leave the Aion shell

Enter any Aion command without the `aion` prefix, for example:
  info
  physics force --mass 2 --acceleration 3
  help --search physics

The shell only runs Aion commands. It does not execute arbitrary system commands.
"""


def shell_command(command=None, *, input_fn=input, runner=None, output=print):
    """Run an interactive prompt for Aion commands without invoking a system shell."""
    runner = runner or subprocess.run
    history = []

    def run_line(line):
        line = line.strip()
        if not line:
            return True
        if line in {"help", "?"}:
            output(_SHELL_HELP.rstrip())
            return True
        if line == "history":
            for index, item in enumerate(history, start=1):
                output(f"{index:>3}  {item}")
            return True
        if line in {"exit", "quit"}:
            return False
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            output(f"Invalid command: {exc}")
            return True
        if parts and parts[0] == "aion":
            parts = parts[1:]
        if not parts:
            output("Enter an Aion command, for example: info")
            return True
        if parts[0] == "shell":
            output("Nested Aion shells are not supported.")
            return True
        history.append(line)
        runner([sys.executable, "-m", "aion", *parts], check=False)
        return True

    if command is not None:
        run_line(command)
        return

    output("Aion shell — type 'help' for commands and 'exit' to leave.")
    while True:
        try:
            line = input_fn("aion> ")
        except EOFError:
            output("")
            return
        if not run_line(line):
            return


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Aqwel-Aion - AI utilities and research library CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Use `aion <command> --help` for detailed options.",
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument(
        "--json",
        dest="json_help",
        action="store_true",
        help="Export command reference as JSON",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
        help=argparse.SUPPRESS,
    )

    # start (hub)
    start_parser = subparsers.add_parser(
        "start", help="Open the Aion Hub dashboard in the browser"
    )
    start_parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    start_parser.add_argument(
        "--port", "-p", type=int, default=3000, help="Port (default 3000)"
    )
    start_parser.add_argument(
        "--no-browser", action="store_true", help="Do not open a browser tab"
    )

    # ui (hub, monitor, reports, optional gradio/streamlit)
    ui_parser = subparsers.add_parser(
        "ui", help="User interfaces: hub, monitor, HTML reports, Gradio/Streamlit"
    )
    ui_parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    ui_parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=None,
        help="Port (hub default 3000, monitor 8000)",
    )
    ui_parser.add_argument(
        "--no-browser", action="store_true", help="Do not open a browser tab"
    )
    ui_parser.add_argument(
        "--monitor", action="store_true", help="Launch hardware monitor instead of Hub"
    )
    ui_parser.add_argument(
        "--report",
        metavar="TRACKER_DIR",
        default=None,
        help="Build experiment HTML report from tracker directory and exit",
    )
    ui_parser.add_argument(
        "-o", "--output", default="experiments.html", help="Output path for --report"
    )
    ui_parser.add_argument(
        "--gradio",
        action="store_true",
        help="Launch Gradio playground (needs [ui] extra)",
    )
    ui_parser.add_argument(
        "--streamlit",
        action="store_true",
        help="Launch Streamlit dataset explorer (needs [ui] extra)",
    )
    ui_parser.add_argument(
        "--list", action="store_true", help="List available UI interfaces"
    )

    # info
    subparsers.add_parser("info", help="Show environment and optional dependencies")

    # embed
    embed_parser = subparsers.add_parser(
        "embed", help="Embed a file or text (sentence-transformers or hash fallback)"
    )
    embed_parser.add_argument("filepath", nargs="?", default=None, help="File to embed")
    embed_parser.add_argument(
        "--text", type=str, default=None, help="Text to embed (instead of file)"
    )
    embed_parser.add_argument(
        "--model",
        type=str,
        default="all-MiniLM-L6-v2",
        help="Model name (default: all-MiniLM-L6-v2)",
    )
    embed_parser.add_argument(
        "--output", "-o", type=str, default=None, help="Save vector to .npy file"
    )

    # eval
    eval_parser = subparsers.add_parser(
        "eval", help="Evaluate prediction accuracy (classification or regression)"
    )
    eval_parser.add_argument(
        "preds", type=str, help="Predictions file (JSON, CSV, or text)"
    )
    eval_parser.add_argument(
        "answers", type=str, help="Ground truth file (same format)"
    )

    # prompt
    prompt_parser = subparsers.add_parser(
        "prompt", help="Show or list prompt templates"
    )
    prompt_parser.add_argument(
        "--type",
        "-t",
        type=str,
        default="system",
        help="Template type (system, code_review, etc.)",
    )
    prompt_parser.add_argument(
        "--list", "-l", action="store_true", help="List available prompt types"
    )

    # watch
    watch_parser = subparsers.add_parser(
        "watch", help="Watch a file for changes and re-embed on save"
    )
    watch_parser.add_argument("filepath", type=str, help="File to watch")
    watch_parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=1.0,
        help="Poll interval in seconds (default: 1.0)",
    )
    watch_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=None,
        help="Directory to save .npy embeddings on change",
    )

    # chat
    subparsers.add_parser(
        "chat", help="Start interactive chat (prompt templates + embedding)"
    )

    shell_parser = subparsers.add_parser(
        "shell", help="Open an interactive prompt for running Aion commands"
    )
    shell_parser.add_argument(
        "-c",
        "--command",
        dest="shell_command",
        help="Run one Aion command and exit (without the `aion` prefix)",
    )

    # git
    git_parser = subparsers.add_parser("git", help="Git repository operations")
    git_subparsers = git_parser.add_subparsers(dest="git_command", help="Git commands")

    git_status_parser = git_subparsers.add_parser(
        "status", help="Show repository status"
    )
    git_status_parser.add_argument(
        "--path", default=".", help="Repository path (default: current directory)"
    )

    git_log_parser = git_subparsers.add_parser("log", help="Show commit history")
    git_log_parser.add_argument(
        "--path", default=".", help="Repository path (default: current directory)"
    )
    git_log_parser.add_argument(
        "--limit", type=int, default=10, help="Maximum number of commits to show"
    )

    git_branches_parser = git_subparsers.add_parser(
        "branches", help="List all branches"
    )
    git_branches_parser.add_argument(
        "--path", default=".", help="Repository path (default: current directory)"
    )

    git_diff_parser = git_subparsers.add_parser("diff", help="Show diff output")
    git_diff_parser.add_argument(
        "--path", default=".", help="Repository path (default: current directory)"
    )
    git_diff_parser.add_argument("--commit", help="Commit hash to diff against")

    # version
    subparsers.add_parser("version", help="Show package version")

    # setup (interactive optional dependency profiles)
    setup_parser = subparsers.add_parser(
        "setup",
        help="Choose and install an Aion feature profile",
    )
    setup_parser.add_argument(
        "--profile",
        choices=("core", "ai", "science", "vision", "llm", "full"),
        help="Install a profile without opening the interactive menu",
    )
    setup_parser.add_argument(
        "--local",
        action="store_true",
        help="Install the current checkout in editable mode",
    )
    setup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the pip command without running it",
    )
    setup_parser.add_argument(
        "--full",
        action="store_true",
        help="Choose the full dependency set without asking",
    )
    setup_parser.add_argument(
        "--yes",
        action="store_true",
        help="Start installation without final confirmation",
    )
    setup_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable terminal colors",
    )
    setup_parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Show the AION logo without animation",
    )

    # install is the framework-style alias for setup.
    install_parser = subparsers.add_parser(
        "install",
        help="Interactive installation wizard for Aion feature profiles",
    )
    install_parser.add_argument(
        "--profile", choices=("core", "ai", "science", "vision", "llm", "full")
    )
    install_parser.add_argument(
        "--local",
        action="store_true",
        help="Install the current checkout in editable mode",
    )
    install_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the pip command without running it",
    )
    install_parser.add_argument(
        "--full",
        action="store_true",
        help="Choose all optional dependencies without asking",
    )
    install_parser.add_argument(
        "--yes", action="store_true", help="Start without final confirmation"
    )
    install_parser.add_argument(
        "--no-color", action="store_true", help="Disable terminal colors"
    )
    install_parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Show the AION logo without animation",
    )

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
        "-o",
        "--output",
        type=str,
        default=None,
        help="Save leaderboard markdown to file",
    )

    # monitor / dashboard (optional deps: fastapi, uvicorn, psutil, nvidia-ml-py)
    def _add_monitor_args(p):
        p.add_argument("--host", default="127.0.0.1", help="Bind address")
        p.add_argument(
            "--port", "-p", type=int, default=8000, help="Port (default 8000)"
        )
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
        help="Start hardware dashboard and metrics API (install 'aqwel-aion[monitor]')",
    )
    _add_monitor_args(mon_parser)
    dash_parser = subparsers.add_parser(
        "dashboard",
        help="Same as monitor: open live hardware dashboard in the browser",
    )
    _add_monitor_args(dash_parser)

    # High-level AI/research/developer commands.
    from .cli_extensions import add_extended_parsers

    add_extended_parsers(subparsers)

    # config
    config_parser = subparsers.add_parser(
        "config", help="Manage Aion CLI configuration"
    )
    config_parser.add_argument(
        "items", nargs="*", help="Use list, get KEY, set KEY VALUE, or reset --yes"
    )
    config_parser.add_argument("--yes", action="store_true", help="Confirm reset")

    # shell completion
    completion_parser = subparsers.add_parser(
        "completion",
        help="Print shell completion script",
    )
    completion_parser.add_argument(
        "shell",
        choices=("bash", "zsh", "fish", "powershell", "install"),
        help="Shell to configure",
    )
    completion_parser.add_argument(
        "install_shell",
        nargs="?",
        choices=("bash", "zsh", "fish", "powershell"),
        help="Shell for `completion install`",
    )

    # help
    help_parser = subparsers.add_parser("help", help="Show all available Aion commands")
    help_parser.add_argument(
        "topic", nargs="?", help="Command to explain, for example: install"
    )
    help_parser.add_argument(
        "--search", metavar="TEXT", help="Find commands by name or description"
    )
    help_parser.add_argument(
        "--json",
        dest="json_help",
        action="store_true",
        help="Export matching commands as JSON",
    )

    def _add_usage_args(p):
        p.add_argument(
            "--host", default="127.0.0.1", help="Bind address (default 127.0.0.1)"
        )
        p.add_argument(
            "--port", "-p", type=int, default=3847, help="Port (default 3847)"
        )
        p.add_argument(
            "--no-browser", action="store_true", help="Do not open a browser tab"
        )

    usage_parser = subparsers.add_parser(
        "usage",
        help="Open usage dashboard: tokens, cost, charts (today / week / month)",
    )
    _add_usage_args(usage_parser)

    stats_parser = subparsers.add_parser(
        "stats",
        help="Alias for aion usage — LLM usage analytics dashboard",
    )
    _add_usage_args(stats_parser)

    # db
    db_parser = subparsers.add_parser("db", help="Database sync, status, and demos")
    db_sub = db_parser.add_subparsers(dest="db_action", help="Database actions")
    db_sub.add_parser("status", help="Show configured database URL and connection")
    db_sync_usage = db_sub.add_parser("sync-usage", help="Import usage JSONL into DB")
    db_sync_usage.add_argument(
        "--url", help="Database URL (default from ~/.aion.yaml db.url)"
    )
    db_sync_usage.add_argument("--table", default="usage_events", help="Target table")
    db_sync_tracker = db_sub.add_parser(
        "sync-tracker", help="Import experiment runs into DB"
    )
    db_sync_tracker.add_argument("--url", help="Database URL")
    db_sync_tracker.add_argument(
        "--root", default=".aion_runs", help="Tracker root directory"
    )
    db_sync_tracker.add_argument("--table", default="experiments", help="Target table")
    db_sub.add_parser("demo", help="Quick in-memory SQLite demo")

    def _add_universe_subparsers(parent):
        u_sub = parent.add_subparsers(dest="universe_action", help="Universe actions")
        u_sub.add_parser("moon", help="Current moon phase")
        u_sky = u_sub.add_parser("sky", help="Bright stars above horizon")
        u_sky.add_argument(
            "--lat", type=float, default=40.18, help="Observer latitude (deg)"
        )
        u_sky.add_argument(
            "--lon", type=float, default=44.51, help="Observer longitude (deg, east +)"
        )
        u_sky.add_argument(
            "--min-alt", type=float, default=10.0, help="Minimum altitude (deg)"
        )
        u_sky.add_argument("--limit", type=int, default=20, help="Max objects to print")
        u_observe = u_sub.add_parser(
            "observe", help="Alias for sky: visible objects above horizon"
        )
        u_observe.add_argument("--lat", type=float, default=40.18)
        u_observe.add_argument("--lon", type=float, default=44.51)
        u_observe.add_argument("--min-alt", type=float, default=10.0)
        u_observe.add_argument("--limit", type=int, default=20)
        u_coords = u_sub.add_parser("coords", help="RA/Dec to Alt/Az now")
        u_coords.add_argument("ra", help='RA e.g. "6h 45m 08s"')
        u_coords.add_argument("dec", help='Dec e.g. "-16d 42m 58s"')
        u_coords.add_argument("--lat", type=float, default=40.18)
        u_coords.add_argument("--lon", type=float, default=44.51)
        u_sep = u_sub.add_parser(
            "separation", help="Angular separation between two points"
        )
        u_sep.add_argument("--ra1", required=True)
        u_sep.add_argument("--dec1", required=True)
        u_sep.add_argument("--ra2", required=True)
        u_sep.add_argument("--dec2", required=True)
        u_sub.add_parser("demo", help="Run coordinate transform demo")
        u_web = u_sub.add_parser(
            "web", help="Open Universe astronomy dashboard (browser)"
        )
        u_web.add_argument("--host", default="127.0.0.1", help="Bind address")
        u_web.add_argument(
            "--port", "-p", type=int, default=3857, help="Port (default 3857)"
        )
        u_web.add_argument(
            "--no-browser", action="store_true", help="Do not open browser"
        )

    universe_parser = subparsers.add_parser(
        "universe", help="Astronomy: moon, sky, coordinates (C++ fast path)"
    )
    _add_universe_subparsers(universe_parser)
    cosmos_parser = subparsers.add_parser(
        "cosmos", help="[deprecated] use: aion universe"
    )
    _add_universe_subparsers(cosmos_parser)

    def _add_universe_dashboard_args(p):
        p.add_argument("--host", default="127.0.0.1", help="Bind address")
        p.add_argument(
            "--port", "-p", type=int, default=3857, help="Port (default 3857)"
        )
        p.add_argument("--no-browser", action="store_true", help="Do not open browser")

    universe_dash_parser = subparsers.add_parser(
        "universe-dashboard",
        help="Open Universe astronomy dashboard (browser)",
    )
    _add_universe_dashboard_args(universe_dash_parser)
    cosmos_dash_parser = subparsers.add_parser(
        "cosmos-dashboard",
        help="[deprecated] use: aion universe-dashboard",
    )
    _add_universe_dashboard_args(cosmos_dash_parser)

    def _add_physics_subparsers(parent):
        p_sub = parent.add_subparsers(dest="physics_action", help="Physics actions")
        p_query = p_sub.add_parser("query", help="Natural-language physics query")
        p_query.add_argument(
            "text", help='Query e.g. "kinetic energy mass=2 velocity=3"'
        )
        p_pend = p_sub.add_parser("pendulum", help="Simulate simple pendulum")
        p_pend.add_argument(
            "--length", type=float, default=1.0, help="Pendulum length (m)"
        )
        p_pend.add_argument(
            "--angle-deg", type=float, default=15.0, help="Initial angle (deg)"
        )
        p_pend.add_argument("--dt", type=float, default=0.01, help="Time step (s)")
        p_pend.add_argument("--steps", type=int, default=2000, help="Integration steps")
        p_proj = p_sub.add_parser("projectile", help="Simulate projectile motion")
        p_proj.add_argument(
            "--v0", type=float, default=20.0, help="Initial speed (m/s)"
        )
        p_proj.add_argument(
            "--angle", type=float, default=45.0, help="Launch angle (deg)"
        )
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
        p_fit = p_sub.add_parser("fit", help="Fit a linear model to measured x/y data")
        p_fit.add_argument("path")
        p_fit.add_argument("--x", default="x")
        p_fit.add_argument("--y", default="y")
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

    # Keep the root usage compact without leaking it into subcommand help.
    parser.usage = "%(prog)s [--version] COMMAND [OPTIONS]"
    parser.epilog = _format_help_table(subparsers)
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
    print(f"aion {_version_string()}")


def _info_style(text: str, code: str, enabled: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if enabled else text


def _info_status(available: bool, *, color: bool) -> str:
    if available:
        return _info_style("● ready", "92", color)
    return _info_style("○ optional", "2", color)


def _module_available(module_name: str) -> bool:
    """Check an optional module without importing its compiled dependencies."""
    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception:
        return False


def info_command():
    """Print a modern environment and optional dependency dashboard."""
    from . import __version__

    color = (
        hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
        and not os.environ.get("NO_COLOR")
    )

    def green(value: str) -> str:
        return _info_style(value, "92", color)

    def cyan(value: str) -> str:
        return _info_style(value, "96", color)

    def muted(value: str) -> str:
        return _info_style(value, "2", color)

    def white(value: str) -> str:
        return _info_style(value, "1", color)

    width = 58
    print()
    print(cyan("  ╭" + "─" * width + "╮"))
    print(
        cyan("  │") + white("  AION  /  ENVIRONMENT") + " " * (width - 24) + cyan("│")
    )
    print(
        cyan("  │")
        + muted("  Aqwel AI research library")
        + " " * (width - 28)
        + cyan("│")
    )
    print(cyan("  ╰" + "─" * width + "╯"))
    print()

    print(white("  Runtime"))
    print(f"  {green('●')} Aion       {__version__}")
    print(
        f"  {green('●')} Python     {sys.version.split()[0]}  ({platform.system()} {platform.machine()})"
    )

    try:
        import numpy as np

        numpy_state = f"{_info_status(True, color=color)}  {np.__version__}"
    except ImportError:
        numpy_state = _info_status(False, color=color)
    print(f"  {green('●')} NumPy      {numpy_state}")
    print()

    print(white("  Optional modules"))
    optional = []
    try:
        optional.append(
            ("sentence-transformers", _module_available("sentence_transformers"), "rag")
        )
    except Exception:
        optional.append(("sentence-transformers", False, "rag"))
    optional.extend(
        [
            ("matplotlib", _module_available("matplotlib"), "viz"),
            ("openai", _module_available("openai"), "ai"),
            ("pandas", _module_available("pandas"), "ai"),
            ("Pillow", _module_available("PIL"), "vision"),
            ("OpenCV", _module_available("cv2"), "vision"),
        ]
    )
    for name, available, extra in optional:
        detail = _info_status(available, color=color)
        if not available:
            detail += muted(f"  pip install 'aqwel-aion[{extra}]'")
        print(f"  {detail:<18} {name}")

    try:
        from .native import native_backends

        native = list(native_backends().values())
    except Exception:
        native = []
    print()
    print(white("  Native acceleration"))
    for status in native:
        state = _info_status(status.available, color=color)
        if not status.available:
            state += muted(f"  {status.fallback} fallback")
        print(f"  {state:<18} {status.name}")

    print()
    git_state = _info_status(GIT_AVAILABLE, color=color)
    if not GIT_AVAILABLE:
        git_state += muted("  pip install gitpython")
    print(white("  Integrations"))
    print(f"  {git_state:<18} Git integration")
    print()
    print(white("  Quick commands"))
    print(f"  {cyan('aion install')}   Choose and install feature dependencies")
    print(f"  {cyan('aion doctor')}    Check the research environment")
    print(f"  {cyan('aion start')}     Open Aion Hub")
    print(f"  {cyan('aion --help')}    Show all commands")
    print()


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
        print('Error: Provide either a file path or --text "..."', file=sys.stderr)
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
    print("Aion Chat (prompt templates + helpers)")
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
        print(
            "Git integration not available. Install GitPython with: pip install gitpython"
        )
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
        print(
            "Git integration not available. Install GitPython with: pip install gitpython"
        )
        return

    commits = git.get_recent_commits(repo_path, limit)
    if not commits or "error" in commits[0]:
        print("No commits found or error occurred")
        return

    print(f"Recent commits (showing {len(commits)}):")
    print("-" * 80)
    for commit in commits:
        print(f"{commit['hash']} - {commit['message']}")
        print(
            f"   {commit['author']} | {commit['date']} | {commit['files_changed']} files"
        )
        print()


def git_branches_command(repo_path="."):
    """
    List all branches for the repository at repo_path, with the active branch
    marked. Requires GIT_AVAILABLE; otherwise prints an installation message.
    """
    if not GIT_AVAILABLE:
        print(
            "Git integration not available. Install GitPython with: pip install gitpython"
        )
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
        print(
            "Git integration not available. Install GitPython with: pip install gitpython"
        )
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


def _main():
    """
    Parse command-line arguments and dispatch to the appropriate subcommand.
    Prints help when no command is given or when a subcommand is unknown.
    """
    parser, git_parser = _build_parser()
    subparsers = _get_subparsers(parser)
    raw_args = sys.argv[1:]

    # argparse exits immediately for --help, so handle the root JSON form first.
    if (
        ("--help" in raw_args or "-h" in raw_args)
        and "--json" in raw_args
        and all(argument in {"--help", "-h", "--json"} for argument in raw_args)
    ):
        print(_format_help_json(subparsers))
        return

    args = parser.parse_args()

    if getattr(args, "json_help", False) and args.command is None:
        print(_format_help_json(subparsers))
        return

    if args.command == "shell":
        shell_command(args.shell_command)
        return

    from .cli_extensions import run_extended_command

    if run_extended_command(args):
        return

    # Once per installed/updated version (wheel installs skip setuptools hooks).
    # Skip informational commands so output stays directly usable in scripts.
    if args.command not in (
        "welcome",
        "help",
        "completion",
        "shell",
        "setup",
        "install",
    ) and not os.environ.get("AION_NO_SPLASH"):
        try:
            from .install_splash import maybe_show_install_splash

            maybe_show_install_splash()
        except Exception:
            pass

    if getattr(args, "version", False) or args.command == "version":
        version_command()
        return
    if args.command in ("start", "ui"):
        if args.command == "ui" and getattr(args, "list", False):
            from .ui import list_ui_interfaces

            for item in list_ui_interfaces():
                print(f"{item['name']} ({item['id']})")
                print(f"  {item['description']}")
                print(f"  Command: {item['command']}  |  API: {item['api']}")
                print()
            return
        if args.command == "ui" and getattr(args, "report", None):
            from .ui import build_experiment_dashboard

            path = build_experiment_dashboard(
                args.report,
                output=args.output,
                open_browser=not args.no_browser,
            )
            print(f"Report saved: {path}")
            return
        if args.command == "ui" and getattr(args, "gradio", False):
            from .ui import launch_gradio_playground

            launch_gradio_playground(server_port=args.port or 7860)
            return
        if args.command == "ui" and getattr(args, "streamlit", False):
            from .ui import launch_streamlit_dataset_explorer

            launch_streamlit_dataset_explorer(server_port=args.port or 8501)
            return
        if args.command == "ui" and getattr(args, "monitor", False):
            from .ui import launch_monitor

            launch_monitor(
                host=args.host,
                port=args.port or 8000,
                open_browser=not args.no_browser,
            )
            return
        from .ui import launch_hub

        launch_hub(
            host=args.host,
            port=args.port or 3000,
            open_browser=not args.no_browser,
        )
        return
    if args.command == "welcome":
        from .install_splash import show_install_splash

        show_install_splash(animated=not getattr(args, "no_animation", False))
        return
    if args.command == "completion":
        if args.shell == "install":
            shell = args.install_shell or "zsh"
            print(f"Run: aion completion {shell} >> your shell startup file")
            return
        print(_completion_script(args.shell, subparsers.choices.keys()), end="")
        return
    if args.command in ("setup", "install"):
        from .installer import main as installer_main

        installer_args = []
        if args.profile:
            installer_args.extend(["--profile", args.profile])
        if args.local:
            installer_args.append("--local")
        if args.dry_run:
            installer_args.append("--dry-run")
        if args.full:
            installer_args.append("--full")
        if args.yes:
            installer_args.append("--yes")
        if args.no_color:
            installer_args.append("--no-color")
        if args.no_animation:
            installer_args.append("--no-animation")
        raise SystemExit(installer_main(installer_args))
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
        if args.search:
            if args.json_help:
                print(_format_help_json(subparsers, search=args.search))
            else:
                print(_format_help_table(subparsers, search=args.search))
            return
        if args.topic:
            command_parser = subparsers.choices.get(args.topic)
            if command_parser is None:
                parser.error(f"unknown help topic: {args.topic}")
            if args.json_help:
                rows = _command_rows(subparsers)
                print(
                    json.dumps(
                        [row for row in rows if row["command"] == args.topic],
                        indent=2,
                        ensure_ascii=False,
                    )
                )
            else:
                command_parser.print_help()
            return
        if args.json_help:
            print(_format_help_json(subparsers))
        else:
            parser.print_help()
        return

    if args.command in ("usage", "stats"):
        from .usage import run_usage_dashboard

        run_usage_dashboard(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
        )
        return

    if args.command == "agent":
        print(
            "aion agent — not available in 0.2.0.\n"
            "Use aion.providers and aion.tools from Python for LLM workflows."
        )
        return

    if args.command in ("api", "auth"):
        print(f"aion {args.command} — not available in 0.2.0.")
        return

    if args.command == "config":
        from .user_config import config_command

        config_command(items=args.items, confirm=args.yes)
        return

    if args.command == "db":
        from .db.cli import db_main

        db_main(args)
        return

    if args.command in ("universe", "cosmos"):
        if args.command == "cosmos":
            import warnings

            warnings.warn(
                "aion cosmos is deprecated; use aion universe", DeprecationWarning
            )
        from .universe.cli import universe_main

        universe_main(args)
        return

    if args.command in ("universe-dashboard", "cosmos-dashboard"):
        if args.command == "cosmos-dashboard":
            import warnings

            warnings.warn(
                "aion cosmos-dashboard is deprecated; use aion universe-dashboard",
                DeprecationWarning,
            )
        from .universe.launch import run_universe_dashboard

        run_universe_dashboard(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
        )
        return

    if args.command == "physics":
        if getattr(args, "physics_action", None) == "fit":
            from .cli_extensions import physics_fit_command

            physics_fit_command(args.path, args.x, args.y)
            return
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


def _print_cli_cancelled() -> None:
    """Print one consistent cancellation message for every CLI command."""
    color = (
        hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
        and not os.environ.get("NO_COLOR")
    )
    if color:
        print("\033[31m\n  ✕ Operation cancelled by user.\033[0m")
        print("\033[2m  No changes were made.\033[0m\n")
    else:
        print("\n  ✕ Operation cancelled by user.")
        print("  No changes were made.\n")


def main():
    """Run the CLI and handle Ctrl+C without displaying a traceback."""
    try:
        return _main()
    except KeyboardInterrupt:
        _print_cli_cancelled()
        return 130
