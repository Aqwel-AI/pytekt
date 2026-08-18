"""Types for vector retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, runtime_checkable

import numpy as np


@dataclass
class ScoredChunk:
    """One search hit with cosine (or store-defined) score."""

    id: str
    score: float
    metadata: Dict[str, Any]


@runtime_checkable
class VectorStore(Protocol):
    """Minimal vector index for RAG-style retrieval."""

    def add(
        self,
        ids: List[str],
        vectors: np.ndarray,
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """Add or replace vectors (2D float array, shape (n, dim))."""
        ...

    def search(self, query_vector: np.ndarray, k: int) -> List[ScoredChunk]:
        """Return up to ``k`` nearest neighbors to ``query_vector`` (1D)."""
        ...
