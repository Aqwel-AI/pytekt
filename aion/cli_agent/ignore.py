"""Parse ``.aionignore`` and filter paths (gitignore-like patterns)."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set

DEFAULT_IGNORE_PATTERNS = frozenset({
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
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    "coverage",
    ".cursor",
})


def _load_aionignore(root: Path) -> List[str]:
    path = root / ".aionignore"
    if not path.is_file():
        return []
    patterns: List[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


class IgnoreMatcher:
    """Match relative paths against default skips and ``.aionignore``."""

    def __init__(self, workspace_root: str) -> None:
        self.root = Path(workspace_root).resolve()
        self._patterns = _load_aionignore(self.root)

    @property
    def patterns(self) -> List[str]:
        return list(self._patterns)

    def should_skip_dir(self, name: str) -> bool:
        if name.startswith(".") and name not in {".env.example"}:
            if name in DEFAULT_IGNORE_PATTERNS:
                return True
        return name in DEFAULT_IGNORE_PATTERNS or self._matches(name)

    def should_skip_path(self, rel_path: str) -> bool:
        rel = rel_path.replace("\\", "/").strip("./")
        if not rel:
            return False
        parts = rel.split("/")
        for part in parts:
            if part in DEFAULT_IGNORE_PATTERNS:
                return True
        return self._matches(rel)

    def _matches(self, rel_path: str) -> bool:
        rel = rel_path.replace("\\", "/")
        for pattern in self._patterns:
            p = pattern.rstrip("/")
            if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel, f"*/{p}"):
                return True
            if rel == p or rel.startswith(p + "/"):
                return True
        return False

    def filter_paths(self, paths: Iterable[str]) -> List[str]:
        return [p for p in paths if not self.should_skip_path(p)]


def merged_skip_dirs(workspace_root: str) -> Set[str]:
    """Default skip dirs plus top-level names from ``.aionignore``."""
    out = set(DEFAULT_IGNORE_PATTERNS)
    matcher = IgnoreMatcher(workspace_root)
    for pattern in matcher.patterns:
        if "/" not in pattern and not pattern.startswith("*"):
            out.add(pattern.rstrip("/"))
    return out
