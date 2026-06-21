"""Unified diff preview for proposed edits."""

from __future__ import annotations

import difflib
from pathlib import Path
from typing import Optional


def unified_diff(
    old_text: str,
    new_text: str,
    *,
    path: str = "file",
    context: int = 3,
) -> str:
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    if old_lines and not old_lines[-1].endswith("\n"):
        old_lines[-1] += "\n"
    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] += "\n"
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        n=context,
    )
    return "".join(diff) or f"(no diff for {path})"


def preview_write(workspace_root: str, path: str, content: str) -> str:
    target = Path(workspace_root) / path
    old = ""
    if target.is_file():
        try:
            old = target.read_text(encoding="utf-8", errors="replace")
        except OSError:
            old = ""
    return unified_diff(old, content, path=path)


def preview_edit(workspace_root: str, path: str, old_string: str, new_string: str) -> str:
    target = Path(workspace_root) / path
    if not target.is_file():
        return f"Error: file not found: {path}"
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"Error reading {path}: {e}"
    if old_string not in text:
        return f"Error: old_string not found in {path}"
    new_text = text.replace(old_string, new_string, 1)
    return unified_diff(text, new_text, path=path)
