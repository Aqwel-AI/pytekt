"""Auto-discover project type, test, and lint commands."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ProjectInfo:
    """Detected project metadata for agent prompts and commands."""

    root: str
    kinds: List[str]
    test_command: Optional[str] = None
    lint_command: Optional[str] = None
    package_name: Optional[str] = None

    def summary(self) -> str:
        lines = [f"Project root: {self.root}"]
        if self.kinds:
            lines.append(f"Detected: {', '.join(self.kinds)}")
        if self.package_name:
            lines.append(f"Package: {self.package_name}")
        if self.test_command:
            lines.append(f"Test: {self.test_command}")
        if self.lint_command:
            lines.append(f"Lint: {self.lint_command}")
        return "\n".join(lines)


def discover_project(workspace_root: Optional[str] = None) -> ProjectInfo:
    root = Path(workspace_root or os.getcwd()).resolve()
    kinds: List[str] = []
    test_cmd: Optional[str] = None
    lint_cmd: Optional[str] = None
    package_name: Optional[str] = None

    if (root / "pyproject.toml").is_file():
        kinds.append("python")
        test_cmd = test_cmd or "pytest"
        lint_cmd = lint_cmd or "ruff check ."
        try:
            text = (root / "pyproject.toml").read_text(encoding="utf-8")
            if "[project]" in text and "name" in text:
                for line in text.splitlines():
                    if line.strip().startswith("name"):
                        package_name = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except OSError:
            pass
    elif (root / "setup.py").is_file():
        kinds.append("python")
        test_cmd = test_cmd or "pytest"

    if (root / "package.json").is_file():
        kinds.append("node")
        try:
            data = json.loads((root / "package.json").read_text(encoding="utf-8"))
            package_name = data.get("name") or package_name
            scripts = data.get("scripts") or {}
            if "test" in scripts:
                test_cmd = test_cmd or "npm test"
            if "lint" in scripts:
                lint_cmd = lint_cmd or "npm run lint"
        except (OSError, json.JSONDecodeError):
            pass

    if (root / "Makefile").is_file():
        kinds.append("make")
        if not test_cmd:
            test_cmd = "make test"

    if (root / "tox.ini").is_file():
        kinds.append("tox")
        test_cmd = test_cmd or "tox"

    if (root / "Cargo.toml").is_file():
        kinds.append("rust")
        test_cmd = test_cmd or "cargo test"

    return ProjectInfo(
        root=str(root),
        kinds=kinds or ["generic"],
        test_command=test_cmd,
        lint_command=lint_cmd,
        package_name=package_name,
    )
