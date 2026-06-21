"""Multi-root workspace resolution."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

from ..tools.workspace import Workspace


class MultiWorkspace:
    """Resolve paths across multiple workspace roots with optional aliases."""

    def __init__(
        self,
        primary_root: str,
        extra_roots: Optional[List[str]] = None,
        aliases: Optional[Dict[str, str]] = None,
    ) -> None:
        self.primary = Path(primary_root).resolve()
        self.roots: List[Path] = [self.primary]
        self.aliases: Dict[str, Path] = {}
        for r in extra_roots or []:
            p = Path(r).expanduser().resolve()
            if p.is_dir() and p not in self.roots:
                self.roots.append(p)
        for alias, path in (aliases or {}).items():
            p = Path(path).expanduser().resolve()
            if p.is_dir():
                self.aliases[alias] = p
                if p not in self.roots:
                    self.roots.append(p)

    def resolve_root_for(self, path: str) -> Optional[Path]:
        path = path.replace("\\", "/").lstrip("./")
        if "/" in path:
            alias, _, rest = path.partition("/")
            if alias in self.aliases:
                return self.aliases[alias]
        for root in self.roots:
            candidate = (root / path).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                continue
            if candidate.exists():
                return root
        return self.primary

    def workspace_for(self, path: str) -> Workspace:
        root = self.resolve_root_for(path)
        return Workspace(root or self.primary)

    def add_root(self, path: str, alias: Optional[str] = None) -> str:
        p = Path(path).expanduser().resolve()
        if not p.is_dir():
            raise ValueError(f"Not a directory: {path}")
        if p not in self.roots:
            self.roots.append(p)
        if alias:
            self.aliases[alias] = p
        return str(p)

    def list_roots(self) -> List[str]:
        return [str(r) for r in self.roots]
