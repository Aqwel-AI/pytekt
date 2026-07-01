"""Lightweight retrieval-backed memory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from ..text import compute_jaccard_similarity


@dataclass
class MemoryItem:
    """One retrievable text memory."""

    text: str
    metadata: Dict[str, Any]


class VectorMemory:
    """
    Dependency-light retrieval memory.

    This MVP uses Jaccard similarity as a fallback scoring method so it works
    without embedding dependencies.
    """

    def __init__(self) -> None:
        self._items: List[MemoryItem] = []

    def add(self, text: str, **metadata: Any) -> None:
        """Insert one retrievable memory item."""
        self._items.append(MemoryItem(text=text, metadata=dict(metadata)))

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Return the top-k most similar memory items."""
        scored = [
            {
                "text": item.text,
                "metadata": item.metadata,
                "score": compute_jaccard_similarity(query, item.text),
            }
            for item in self._items
        ]
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]
