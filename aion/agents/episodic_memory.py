"""Persistent episodic memory across agent sessions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Union


PathLike = Union[str, Path]


class EpisodicMemory:
    """Store and retrieve durable project or user facts."""

    def __init__(self, path: PathLike) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def add(self, kind: str, content: str, **metadata: Any) -> None:
        """Append one memory item."""
        items = self.list()
        items.append({"kind": kind, "content": content, "metadata": metadata})
        self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def list(self) -> List[Dict[str, Any]]:
        """Return all stored memory items."""
        return json.loads(self.path.read_text(encoding="utf-8"))

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Return memories containing the query text."""
        normalized = query.casefold()
        return [item for item in self.list() if normalized in item["content"].casefold()]
