"""Sandbox file paths to a workspace root."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike[str]]


class Workspace:
    """Resolve paths relative to a root; block escapes outside the workspace."""

    def __init__(self, root: PathLike) -> None:
        self.root = Path(root).resolve()

    def resolve(self, path: str) -> Path:
        if not path or path == ".":
            return self.root
        candidate = (self.root / path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as e:
            raise PermissionError(
                f"Path {path!r} is outside the workspace {self.root}"
            ) from e
        return candidate
