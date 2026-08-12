"""High-level chunk → embed → store → query."""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence

import numpy as np

from .chunking import chunk_text
from .stores.memory import MemoryVectorStore
from .types import ScoredChunk, VectorStore


class SimpleRAGIndex:
    """
    Reference RAG index: chunk plain texts, embed with a callable, add to a
    :class:`VectorStore`, query by embedding the question.

    ``embed_fn`` defaults to :func:`aion.embed.embed_text` when omitted.
    """

    def __init__(
        self,
        store: Optional[VectorStore] = None,
        *,
        embed_fn: Optional[Callable[[str], np.ndarray]] = None,
    ) -> None:
        self.store = store or MemoryVectorStore()
        self._embed_fn = embed_fn

    def _embed(self, text: str) -> np.ndarray:
        if self._embed_fn is not None:
            return np.asarray(self._embed_fn(text), dtype=float)
        from ..embed import embed_text

        return np.asarray(embed_text(text), dtype=float)

    def index_texts(
        self,
        texts: Sequence[str],
        *,
        chunk_size: int = 512,
        overlap: int = 64,
        id_prefix: str = "doc",
    ) -> int:
        """
        Chunk each string, embed chunks, add to the store. Returns number of
        chunks indexed.
        """
        n = 0
        for di, raw in enumerate(texts):
            for ci, ch in enumerate(chunk_text(raw, chunk_size, overlap)):
                eid = f"{id_prefix}-{di}-{ci}"
                vec = self._embed(ch).ravel()
                row = vec.reshape(1, -1)
                self.store.add(
                    ids=[eid],
                    vectors=row,
                    metadatas=[{"text": ch, "doc_index": di, "chunk_index": ci}],
                )
                n += 1
        return n

    def query(self, question: str, k: int = 5) -> List[ScoredChunk]:
        q = self._embed(question).ravel()
        return self.store.search(q, k)
