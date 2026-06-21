"""Run project linter after edits in test/debug mode."""

from __future__ import annotations

import subprocess
from typing import Optional

from .project import ProjectInfo


def run_lint_on_file(project: ProjectInfo, file_path: str) -> Optional[str]:
    if not project.lint_command:
        return None
    cmd = project.lint_command
    if "ruff" in cmd and file_path.endswith(".py"):
        full = f"ruff check {file_path}"
    elif "eslint" in cmd and file_path.endswith((".js", ".ts", ".tsx", ".jsx")):
        full = f"npm run lint -- {file_path}"
    else:
        return None
    try:
        result = subprocess.run(
            full,
            shell=True,
            cwd=project.root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return None
        return (result.stdout or "") + (result.stderr or "")
    except (subprocess.TimeoutExpired, OSError) as e:
        return str(e)
