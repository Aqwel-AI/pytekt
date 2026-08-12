# pytekt.former.models — Package documentation

## 1. Title and overview

**`pytekt.former.models`** implements a **decoder-only (GPT-style) transformer**: token **embedding**, **sinusoidal positional encoding**, **multi-head self-attention**, **feed-forward** blocks, and a stacked **Transformer** with **LM head** for next-token logits.

All parameters and activations are **`pytekt.former.core.Tensor`** with autograd.

---

## 2. Module layout

| File | Role |
|------|------|
| `embedding.py` | `Embedding` (lookup), `PositionalEncoding` (sin/cos, optional dropout). |
| `attention.py` | `MultiHeadAttention` — pre-norm, causal mask, scaled dot-product per head. |
| `feedforward.py` | `FeedForward` — two linear layers with ReLU (dims `embed_dim` → `hidden_dim` → `embed_dim`). |
| `transformer.py` | `Transformer` — stacks `TransformerBlock` (attention + FFN), final layer norm, vocabulary projection. |

---

## 3. Public API (from `pytekt.former.models`)

| Symbol | Description |
|--------|-------------|
| `Transformer` | Main model; `forward(x)` → logits `(batch, seq, vocab_size)`. |
| `MultiHeadAttention` | Self-attention block (used inside the decoder stack). |
| `FeedForward` | Position-wise FFN. |
| `Embedding` | Token embeddings. |
| `PositionalEncoding` | Adds positional signal to embeddings. |

```python
from pytekt.former.models import Transformer

model = Transformer(
    vocab_size=vocab_size,
    embed_dim=128,
    num_heads=4,
    num_layers=2,
    max_seq_len=64,
    hidden_dim=512,
)
```

---

## 4. Architecture notes

- **Pre-norm:** Layer normalization is applied **before** attention and before the FFN inside each block (training stability).
- **Causal mask:** Attention is masked so positions cannot attend to future tokens.

Details: [`../docs/architecture.md`](../docs/architecture.md).

---

## 5. Dependencies

- **`pytekt.former.core`** (NumPy tensors + ops).

---

## Examples

[`examples/README.md`](examples/README.md) — `python -m pytekt.former.models.examples.demo_forward`.

---

## 6. See also

- Parent: [`../README.md`](../README.md)
- Core tensors/ops: [`../core/README.md`](../core/README.md)
- Training loop: [`../training/README.md`](../training/README.md)
