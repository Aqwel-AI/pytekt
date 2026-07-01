"""Artifact tracking for agent-created files and outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class Artifact:
    """One tracked artifact created or modified by an agent."""

    path: str
    kind: str
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ArtifactTracker:
    """Collect and summarize artifacts produced during a run."""

    def __init__(self) -> None:
        self._items: List[Artifact] = []

    def add(self, path: str, kind: str, description: str = "", **metadata: Any) -> None:
        """Track a new artifact."""
        self._items.append(
            Artifact(path=path, kind=kind, description=description, metadata=dict(metadata))
        )

    def list(self) -> List[Artifact]:
        """Return tracked artifacts."""
        return list(self._items)

    def to_dicts(self) -> List[Dict[str, Any]]:
        """Return tracked artifacts as plain dictionaries."""
        return [asdict(item) for item in self._items]
