"""Build a tiny in-memory RAG index with a deterministic fake embedder."""
from __future__ import annotations

import numpy as np

from pytekt.rag import SimpleRAGIndex


def _fake_embed(text: str) -> np.ndarray:
    """Fixed small dim, reproducible from string hash (demo only)."""
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    v = rng.standard_normal(16)
    return v.astype(np.float64)


def main() -> None:
    idx = SimpleRAGIndex(embed_fn=_fake_embed)
    n = idx.index_texts(
        ["Paris is the capital of France.", "London is in the United Kingdom."],
        chunk_size=128,
        overlap=0,
    )
    assert n >= 2
    hits = idx.query("capital France", k=2)
    assert hits
    top = hits[0].metadata.get("text", "") if hits[0].metadata else ""
    print("demo_simple_index ok — chunks indexed:", n, "top snippet:", top[:50] + ("…" if len(top) > 50 else ""))


if __name__ == "__main__":
    main()
