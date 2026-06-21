"""Git slash commands for the agent CLI."""

from __future__ import annotations

import subprocess
from typing import Any, Dict, List, Optional

from . import ui
from .git_context import expand_git_mention


def _run_git(args: List[str], cwd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=60,
    )


def handle_commit(args: str, *, workspace: str, pinned_files: Optional[List[str]] = None) -> None:
    if pinned_files:
        for f in pinned_files:
            _run_git(["add", f], workspace)
    else:
        _run_git(["add", "-A"], workspace)
    msg = args.strip() or "Aion agent commit"
    result = _run_git(["commit", "-m", msg], workspace)
    if result.returncode == 0:
        ui.success_print(result.stdout.strip() or "Committed.")
    else:
        ui.error_print(result.stderr.strip() or result.stdout.strip() or "Commit failed.")


def handle_branch(args: str, *, workspace: str) -> None:
    name = args.strip()
    if not name:
        ui.error_print("Usage: /branch <name>")
        return
    result = _run_git(["checkout", "-b", name], workspace)
    if result.returncode != 0:
        result = _run_git(["checkout", name], workspace)
    if result.returncode == 0:
        ui.success_print(f"Switched to branch {ui.bold(name)}")
    else:
        ui.error_print(result.stderr.strip() or "Branch failed.")


def handle_pr_summary(args: str, *, workspace: str, connector: Any) -> None:
    if not connector.agent:
        ui.error_print("Connect first.")
        return
    _, git_block = expand_git_mention("diff", workspace)
    _, staged = expand_git_mention("staged", workspace)
    prompt = (
        "Write a concise PR summary in markdown from this git context:\n\n"
        + git_block
        + "\n\n"
        + staged
    )
    summary = connector.agent.chat(prompt)
    print()
    ui.agent_print(summary, name="PR Summary")
    print()
