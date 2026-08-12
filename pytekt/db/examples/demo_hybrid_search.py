"""Demo: hybrid text + vector search."""

from __future__ import annotations

import pytekt.db as db


def main() -> None:
    conn = db.connect("sqlite://./demo_hybrid.db")
    conn.docs.insert({
        "content": "Training transformers with PyTekt",
        "embedding": [0.9, 0.1, 0.0],
        "source": "docs",
    })
    conn.docs.insert({
        "content": "Baking sourdough bread",
        "embedding": [0.1, 0.9, 0.0],
        "source": "blog",
    })
    hits = db.hybrid_search(
        conn,
        "docs",
        text="transformer",
        vector=[1.0, 0.0, 0.0],
        top_k=3,
    )
    for h in hits:
        print("-", h.get("content"))
    conn.close()
    print("demo_hybrid_search ok")


if __name__ == "__main__":
    main()
