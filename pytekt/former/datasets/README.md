# pytekt.former.datasets — Package documentation

## 1. Title and overview

**`pytekt.former.datasets`** provides **tokenization** and a **sliding-window text dataset** for **next-token prediction** inside `pytekt.former`. For generic file I/O (streaming lines, atomic writes, checksums), use **`pytekt.io`** or the standard library.

**Typical flow:** fit a `SimpleTokenizer` on a corpus → build `TextDataset` → use `create_dataloader` to obtain `(dataset, get_batch)` for `Trainer.train_epoch`.

---

## 2. Module layout

| File | Role |
|------|------|
| `tokenizer.py` | `SimpleTokenizer` — character- or word-level `fit`, `encode`, `decode`, `vocab_size`. |
| `loader.py` | `TextDataset` (contiguous token windows + next-token targets), `create_dataloader` factory. |

---

## 3. Public API (from `pytekt.former.datasets`)

| Symbol | Description |
|--------|-------------|
| `SimpleTokenizer` | `level="char"` or `"word"`; builds vocab from `fit(text)`. |
| `TextDataset` | `ids` array, `vocab_size`, `seq_length`; yields `(input_ids, target_ids)` windows. |
| `create_dataloader` | Returns `(dataset, get_batch)` where `get_batch` samples random batches for training. |

```python
from pytekt.former.datasets import TextDataset, create_dataloader, SimpleTokenizer

dataset, get_batch = create_dataloader(corpus, seq_length=64, batch_size=32, level="char")
```

---

## 4. Conventions

- **Targets:** For each window, targets are the **next** token at each position (standard LM objective).
- **Batching:** `get_batch` is a callable with no arguments; used by `Trainer.train_epoch(get_batch, steps)`.

---

## 5. Dependencies

- **NumPy** (via `[former]`).

---

## Examples

[`examples/README.md`](examples/README.md) — `python -m pytekt.former.datasets.examples.demo_tokenizer`.

---

## 6. See also

- Parent: [`../README.md`](../README.md)
- Training: [`../training/README.md`](../training/README.md)
- Safe file I/O: [`../../io/README.md`](../../io/README.md)
