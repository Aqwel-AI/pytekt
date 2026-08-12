"""
RAG helpers: chunking, in-memory or FAISS vector stores, simple index pipeline.

Reference / teaching tier — not a full production RAG platform. Uses
:mod:`aion.embed` for embeddings unless you pass a custom ``embed_fn``.

Optional: ``pip install faiss-cpu`` or ``pytekt[rag]`` for :class:`FaissVectorStore`.
See ``aion/rag/README.md`` for package documentation.
"""

from .chunking import chunk_by_paragraphs, chunk_text
from .pipeline import SimpleRAGIndex
from .stores.memory import MemoryVectorStore
from .stores.faiss_store import FaissVectorStore
from .types import ScoredChunk, VectorStore

__all__ = [
    "FaissVectorStore",
    "MemoryVectorStore",
    "ScoredChunk",
    "SimpleRAGIndex",
    "VectorStore",
    "chunk_by_paragraphs",
    "chunk_text",
]
