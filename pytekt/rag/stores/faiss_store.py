"""FAISS-backed vector store (optional ``faiss-cpu``)."""

from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING

import numpy as np

from ..types import ScoredChunk, VectorStore

try:
    import faiss  # type: ignore[import-not-found]
except ImportError:
    faiss = None  # type: ignore[misc, assignment]

if TYPE_CHECKING:
    pass


class FaissVectorStore(VectorStore):
    """
    Inner-product index on L2-normalized vectors (cosine similarity).

    Requires ``pip install faiss-cpu`` (e.g. via ``pytekt[full]`` or ``[rag]``).
    """

    def __init__(self, dim: int) -> None:
        if faiss is None:
            raise ImportError(
                "FaissVectorStore requires faiss; install with pip install faiss-cpu "
                "or pip install pytekt[rag]"
            )
        if dim <= 0:
            raise ValueError("dim must be positive")
        self._dim = dim
        self._index = faiss.IndexFlatIP(dim)
        self._ids: List[str] = []
        self._meta: List[Dict[str, Any]] = []

    def add(
        self,
        ids: List[str],
        vectors: np.ndarray,
        metadatas: List[Dict[str, Any]],
    ) -> None:
        if faiss is None:
            raise ImportError("faiss is not installed")
        if len(ids) != len(metadatas):
            raise ValueError("ids and metadatas length mismatch")
        v = np.asarray(vectors, dtype=np.float32)
        if v.ndim != 2 or v.shape[1] != self._dim:
            raise ValueError(f"vectors must be (n, {self._dim})")
        if v.shape[0] != len(ids):
            raise ValueError("vectors row count must match ids")
        faiss.normalize_L2(v)
        self._index.add(v)
        self._ids.extend(ids)
        self._meta.extend(dict(m) for m in metadatas)

    def search(self, query_vector: np.ndarray, k: int) -> List[ScoredChunk]:
        if faiss is None:
            raise ImportError("faiss is not installed")
        q = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        if q.shape[1] != self._dim:
            raise ValueError("query dimension mismatch")
        if self._index.ntotal == 0:
            return []
        faiss.normalize_L2(q)
        k = min(k, self._index.ntotal)
        sims, idxs = self._index.search(q, k)
        out: List[ScoredChunk] = []
        for col, i in enumerate(idxs[0]):
            if i < 0:
                continue
            out.append(
                ScoredChunk(
                    id=self._ids[i],
                    score=float(sims[0][col]),
                    metadata=dict(self._meta[i]),
                )
            )
        return out
