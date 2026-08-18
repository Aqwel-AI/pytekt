"""In-memory vector store: brute-force cosine similarity (NumPy only)."""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from ..types import ScoredChunk, VectorStore


class MemoryVectorStore(VectorStore):
    """O(n) scan per query; fine for small corpora and tests."""

    def __init__(self) -> None:
        self._ids: List[str] = []
        self._mat: np.ndarray | None = None
        self._meta: List[Dict] = []

    def add(
        self,
        ids: List[str],
        vectors: np.ndarray,
        metadatas: List[Dict],
    ) -> None:
        if len(ids) != len(metadatas):
            raise ValueError("ids and metadatas length mismatch")
        v = np.asarray(vectors, dtype=float)
        if v.ndim != 2:
            raise ValueError("vectors must be 2D (n, dim)")
        if v.shape[0] != len(ids):
            raise ValueError("vectors row count must match ids")
        for i, eid in enumerate(ids):
            row = v[i : i + 1]
            if eid in self._ids:
                j = self._ids.index(eid)
                if self._mat is not None and self._mat.shape[1] != row.shape[1]:
                    raise ValueError("vector dimension mismatch")
                self._mat[j] = row
                self._meta[j] = dict(metadatas[i])
            else:
                self._ids.append(eid)
                self._meta.append(dict(metadatas[i]))
                if self._mat is None:
                    self._mat = row.copy()
                else:
                    if self._mat.shape[1] != row.shape[1]:
                        raise ValueError("vector dimension mismatch")
                    self._mat = np.vstack([self._mat, row])

    def search(self, query_vector: np.ndarray, k: int) -> List[ScoredChunk]:
        q = np.asarray(query_vector, dtype=float).ravel()
        if self._mat is None or self._mat.size == 0:
            return []
        if q.shape[0] != self._mat.shape[1]:
            raise ValueError("query dimension mismatch")
        norms = np.linalg.norm(self._mat, axis=1) * np.linalg.norm(q)
        norms = np.where(norms == 0, 1e-12, norms)
        sims = (self._mat @ q) / norms
        k = min(k, len(sims))
        idx = np.argsort(-sims)[:k]
        return [
            ScoredChunk(id=self._ids[i], score=float(sims[i]), metadata=dict(self._meta[i]))
            for i in idx
        ]
