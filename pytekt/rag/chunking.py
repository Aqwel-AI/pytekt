"""Text chunking for RAG-style indexing."""

from __future__ import annotations

from typing import List


def chunk_text(
    text: str,
    chunk_size: int,
    overlap: int = 0,
) -> List[str]:
    """
    Split ``text`` into chunks of at most ``chunk_size`` characters with
    optional ``overlap`` between consecutive chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be in [0, chunk_size)")
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end >= n:
            break
        start = end - overlap
    return chunks


def chunk_by_paragraphs(
    text: str,
    max_chunk_chars: int,
    overlap_paras: int = 0,
) -> List[str]:
    """
    Split on blank lines (``\\n\\n``), then merge paragraphs until under
    ``max_chunk_chars``. ``overlap_paras`` repeats trailing paragraphs in the
    next chunk (simple context carry).
    """
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paras:
        return []
    chunks: List[str] = []
    buf: List[str] = []
    buf_len = 0
    for p in paras:
        plen = len(p) + (2 if buf else 0)
        if buf and buf_len + plen > max_chunk_chars:
            chunks.append("\n\n".join(buf))
            if overlap_paras > 0 and buf:
                tail = buf[-overlap_paras:] if len(buf) >= overlap_paras else list(buf)
                buf = list(tail)
                buf_len = sum(len(x) + 2 for x in buf) - (2 if len(buf) > 1 else 0)
            else:
                buf = []
                buf_len = 0
        if not buf:
            buf = [p]
            buf_len = len(p)
        else:
            buf.append(p)
            buf_len += plen
    if buf:
        chunks.append("\n\n".join(buf))
    return chunks
