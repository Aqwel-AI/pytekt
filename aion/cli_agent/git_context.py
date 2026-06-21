"""Git context for @git / @changed / @diff / @staged mentions."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from ..tools.code_agent import read_file
from ..tools.workspace import Workspace

_GIT_TOKENS = frozenset({"git", "changed", "diff", "staged"})
_MAX_DIFF_CHARS = 12000
_MAX_FILE_CHARS = 4000
_MAX_CHANGED_FILES = 8


def is_git_token(token: str) -> bool:
    return token.lower().strip().lstrip("@") in _GIT_TOKENS


def _run_git(workspace_root: str, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"Error running git: {e}"
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        return f"Git error: {err or 'unknown'}"
    return proc.stdout.strip()


def _changed_file_paths(workspace_root: str, *, staged: bool = False) -> List[str]:
    if staged:
        out = _run_git(workspace_root, "diff", "--cached", "--name-only")
    else:
        out = _run_git(workspace_root, "status", "--short")
        if out.startswith("Git error"):
            return []
        paths: List[str] = []
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            part = line[3:].strip()
            if " -> " in part:
                part = part.split(" -> ", 1)[1]
            paths.append(part)
        return paths[:_MAX_CHANGED_FILES]
    if out.startswith("Git error"):
        return []
        return [p.strip() for p in out.splitlines() if p.strip()][:_MAX_CHANGED_FILES]


def expand_git_mention(token: str, workspace_root: str) -> Tuple[str, str]:
    """
    Expand a git special mention.

    Returns (label_for_ui, context_block).
    """
    key = token.lower().strip().lstrip("@")
    ws = Workspace(workspace_root)

    if key == "diff":
        diff = _run_git(workspace_root, "diff")
        if len(diff) > _MAX_DIFF_CHARS:
            diff = diff[:_MAX_DIFF_CHARS] + "\n[... diff truncated ...]"
        block = f"<git-diff>\n{diff or '(no unstaged diff)'}\n</git-diff>"
        return "@diff", block

    if key == "staged":
        diff = _run_git(workspace_root, "diff", "--cached")
        if len(diff) > _MAX_DIFF_CHARS:
            diff = diff[:_MAX_DIFF_CHARS] + "\n[... diff truncated ...]"
        block = f"<git-staged-diff>\n{diff or '(no staged diff)'}\n</git-staged-diff>"
        return "@staged", block

    if key in ("git", "changed"):
        status = _run_git(workspace_root, "status", "--short")
        paths = _changed_file_paths(workspace_root)
        parts = [f"<git-status>\n{status or '(clean)'}\n</git-status>"]
        labels = ["@git"]
        for rel in paths:
            content = read_file(ws, rel, limit=200)
            if content.startswith("Error"):
                continue
            if len(content) > _MAX_FILE_CHARS:
                content = content[:_MAX_FILE_CHARS] + "\n[... truncated ...]"
            parts.append(f'<file path="{rel}">\n{content}\n</file>')
            labels.append(rel)
        block = "\n".join(parts)
        return ", ".join(labels[:4]), block

    return token, ""
