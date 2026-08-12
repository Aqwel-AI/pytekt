# pytekt.rag — Examples

Uses **NumPy** and a **local fake `embed_fn`** so nothing hits the network or optional embedding stacks.

```bash
pip install -e .
python -m pytekt.rag.examples.demo_simple_index
```

| Script | What it does |
|--------|----------------|
| **demo_simple_index.py** | `SimpleRAGIndex.index_texts` on two short strings, then `query` with `MemoryVectorStore` under the hood. |

For real embeddings, pass your own `embed_fn` or omit it to use **`pytekt.embed`** (see [`../README.md`](../README.md)). Optional FAISS: `pip install pytekt[rag]`.
