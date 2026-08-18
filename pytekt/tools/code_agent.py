"""Coding-agent filesystem tools (read, edit, write, search)."""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional

from .workspace import Workspace

# Skip huge / noisy dirs when searching
_SKIP_DIRS = frozenset({
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".eggs",
})


def _skip_dirs(workspace: Workspace) -> frozenset:
    del workspace  # reserved for future .pytektignore support
    return _SKIP_DIRS


def _fmt_lines(text: str, *, start_line: int = 1) -> str:
    lines = text.splitlines()
    width = len(str(start_line + len(lines) - 1)) if lines else 1
    out: List[str] = []
    for i, line in enumerate(lines):
        n = start_line + i
        out.append(f"{n:>{width}}|{line}")
    return "\n".join(out)


def read_file(
    workspace: Workspace,
    path: str,
    offset: int = 1,
    limit: int = 500,
) -> str:
    """Read a file with line numbers (offset is 1-based)."""
    try:
        p = workspace.resolve(path)
        if not p.is_file():
            return f"Error: not a file: {path}"
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        start = max(1, int(offset)) - 1
        end = start + max(1, int(limit))
        chunk = lines[start:end]
        if not chunk and start >= len(lines):
            return f"Error: offset {offset} past end of file ({len(lines)} lines)."
        numbered = _fmt_lines("\n".join(chunk), start_line=start + 1)
        total = len(lines)
        header = f"File: {path} ({total} lines"
        if start > 0 or end < total:
            header += f", showing {start + 1}-{min(end, total)}"
        return f"{header})\n{numbered}"
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error reading {path}: {e}"


def write_file(workspace: Workspace, path: str, content: str) -> str:
    """Create or overwrite a file."""
    try:
        p = workspace.resolve(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        lines = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
        return f"Wrote {path} ({lines} lines, {len(content)} bytes)."
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error writing {path}: {e}"


def edit_file(
    workspace: Workspace,
    path: str,
    old_string: str,
    new_string: str,
) -> str:
    """
  Replace ``old_string`` with ``new_string`` once in the file.

  The old block must match exactly (including whitespace). Use for surgical edits.
  """
    try:
        p = workspace.resolve(path)
        if not p.is_file():
            return f"Error: not a file: {path}"
        text = p.read_text(encoding="utf-8")
        count = text.count(old_string)
        if count == 0:
            return (
                f"Error: old_string not found in {path}. "
                "Read the file first and copy the exact text to replace."
            )
        if count > 1:
            return (
                f"Error: old_string appears {count} times in {path}. "
                "Include more surrounding lines so the match is unique."
            )
        updated = text.replace(old_string, new_string, 1)
        p.write_text(updated, encoding="utf-8")
        old_lines = old_string.count("\n") + 1
        new_lines = new_string.count("\n") + 1
        return f"Edited {path}: replaced {old_lines} line(s) with {new_lines} line(s)."
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error editing {path}: {e}"


def list_files(
    workspace: Workspace,
    path: str = ".",
    *,
    recursive: bool = False,
) -> str:
    """List files and directories under ``path``."""
    try:
        base = workspace.resolve(path)
        if not base.exists():
            return f"Error: path does not exist: {path}"
        if not base.is_dir():
            return f"Error: not a directory: {path}"

        entries: List[str] = []
        if recursive:
            skip = _skip_dirs(workspace)
            for root, dirs, files in os.walk(base):
                dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
                rel_root = Path(root).relative_to(workspace.root)
                for name in sorted(files):
                    if name.startswith("."):
                        continue
                    rel = rel_root / name
                    entries.append(str(rel).replace("\\", "/"))
                if len(entries) > 400:
                    entries.append("… (truncated)")
                    break
        else:
            for child in sorted(base.iterdir(), key=lambda x: x.name.lower()):
                if child.name.startswith("."):
                    continue
                rel = child.relative_to(workspace.root)
                suffix = "/" if child.is_dir() else ""
                entries.append(str(rel).replace("\\", "/") + suffix)

        if not entries:
            return "Directory is empty."
        return "\n".join(entries[:500])
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error listing {path}: {e}"


def grep_search(
    workspace: Workspace,
    pattern: str,
    path: str = ".",
    glob_pattern: str = "*",
) -> str:
    """Search file contents with a regex pattern."""
    try:
        base = workspace.resolve(path)
        regex = re.compile(pattern)
    except PermissionError as e:
        return f"Error: {e}"
    except re.error as e:
        return f"Error: invalid regex: {e}"

    hits: List[str] = []
    max_hits = 80

    def scan_file(fp: Path) -> None:
        nonlocal hits
        if len(hits) >= max_hits:
            return
        try:
            rel = fp.relative_to(workspace.root)
        except ValueError:
            return
        if not fnmatch.fnmatch(fp.name, glob_pattern) and not fnmatch.fnmatch(
            str(rel), glob_pattern
        ):
            return
        try:
            lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
        except (OSError, UnicodeError):
            return
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                hits.append(f"{rel}:{i}:{line[:200]}")
                if len(hits) >= max_hits:
                    return

    if base.is_file():
        scan_file(base)
    elif base.is_dir():
        skip = _skip_dirs(workspace)
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in skip]
            for name in files:
                scan_file(Path(root) / name)
                if len(hits) >= max_hits:
                    break

    if not hits:
        return f"No matches for /{pattern}/ under {path}"
    extra = f"\n… ({max_hits}+ matches truncated)" if len(hits) >= max_hits else ""
    return "\n".join(hits) + extra


def glob_search(workspace: Workspace, pattern: str) -> str:
    """Find files matching a glob (e.g. ``**/*.py``)."""
    try:
        skip = _skip_dirs(workspace)
        matches = sorted(
            p.relative_to(workspace.root)
            for p in workspace.root.glob(pattern)
            if p.is_file() and not any(part in skip for part in p.parts)
        )
        if not matches:
            return f"No files match {pattern!r}"
        lines = [str(m).replace("\\", "/") for m in matches[:200]]
        if len(matches) > 200:
            lines.append(f"… and {len(matches) - 200} more")
        return "\n".join(lines)
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"


def run_command(workspace: Workspace, command: str, timeout: int = 60) -> str:
    """Run a shell command in the workspace directory (trusted mode only)."""
    if not command.strip():
        return "Error: empty command"
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(workspace.root),
            capture_output=True,
            text=True,
            timeout=min(max(5, int(timeout)), 120),
        )
        parts = [f"exit code: {result.returncode}"]
        if result.stdout:
            parts.append("stdout:\n" + result.stdout[:8000])
        if result.stderr:
            parts.append("stderr:\n" + result.stderr[:4000])
        if result.returncode != 0 and not result.stdout and not result.stderr:
            parts.append("(no output)")
        return "\n".join(parts)
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error running command: {e}"
