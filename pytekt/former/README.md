# Aion — Transformer module

**Lightweight decoder-only transformer training for research and experimentation.**

The **transformer module** is part of the [Aion](https://github.com/Aqwel-AI/pytekt) library. It lives under `pytekt.former` and provides a minimal, NumPy-based implementation of GPT-style transformers with autograd, training utilities, and visualization. Use it to understand transformer internals, try architecture changes, and run small-scale next-token prediction experiments without PyTorch or TensorFlow.

---

## Table of contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Features](#features)
- [Public API summary](#public-api-summary)
- [Module reference](#module-reference)
- [Configuration](#configuration)
- [Package layout](#package-layout)
- [Architecture](#architecture)
- [Design and conventions](#design-and-conventions)
- [Dependencies](#dependencies)
- [Usage examples](#usage-examples)
- [Command-line scripts](#command-line-scripts)
- [Known limitations](#known-limitations)
- [License](#license)

---

## Overview

The Aion transformer module (`pytekt.former`) is a **library** you call from your code; it does not take over your program flow. It offers:

- **Core:** NumPy-backed `Tensor` with autograd; operations such as `matmul`, `softmax`, `layer_norm`, and scaled dot-product attention.
- **Model:** Embedding, sinusoidal positional encoding, multi-head attention, feed-forward blocks, and a pre-norm decoder stack with LM head.
- **Training:** Cross-entropy loss, Adam optimizer, and a `Trainer` with `train_step` / `train_epoch`.
- **Data:** Character- or word-level tokenizer and a sliding-window text dataset with batch loader.
- **Visualization:** Attention heatmaps (per head/layer), training loss over epochs, and weight eigenvalue/singular-value spectrum.

It is **not** a general-purpose deep learning framework. For production or large-scale training, use PyTorch, TensorFlow, or JAX.

---

## Requirements

- **Python** 3.8+
- **NumPy** ≥ 1.20
- **Matplotlib** ≥ 3.5 (for visualization)
- **PyYAML** ≥ 6.0 (for experiment config)

---

## Installation

The transformer module is an optional part of Aion. Install Aion with the `former` extra:

From the Aion repository (editable):

```bash
pip install -e ".[former]"
```

From PyPI:

```bash
pip install pytekt[former]
```

Then use:

```python
import pytekt
from pytekt.former import Transformer, Trainer
```

---

## Quick start

### Programmatic use

```python
from pytekt.former import Transformer, Trainer
from pytekt.former.datasets import create_dataloader
from pytekt.former.visualization import plot_attention_map, plot_training_metrics

# Data and model
text = "Your training corpus here. " * 100
dataset, get_batch = create_dataloader(text, seq_length=64, batch_size=32, level="char")
model = Transformer(
    vocab_size=dataset.vocab_size,
    embed_dim=128,
    num_heads=4,
    num_layers=2,
    max_seq_len=64,
)
trainer = Trainer(model, lr=0.001)

# Train
for epoch in range(10):
    loss = trainer.train_epoch(get_batch, 50)
    print(f"Epoch {epoch + 1}  loss = {loss:.4f}")

# Visualize
plot_training_metrics(trainer.history)
```

### Run scripts

See [Command-line scripts](#command-line-scripts) for `train_small_model`, `attention_demo`, and `text_generation`.

---

## Features

| Area | Description |
|------|-------------|
| **Core** | NumPy-backed `Tensor` with autograd; `matmul`, `transpose`, `relu`, `softmax`, `layer_norm`, scaled dot-product attention |
| **Model** | Embedding, sinusoidal positional encoding, multi-head attention, feed-forward blocks, pre-norm transformer stack, LM head |
| **Training** | Cross-entropy loss, Adam optimizer, `Trainer` with `train_step` / `train_epoch` |
| **Data** | Character- or word-level tokenizer, sliding-window text dataset, batch loader |
| **Visualization** | Attention heatmaps (per head/layer), training loss over epochs, weight eigenvalue/singular-value spectrum |

---

## Public API summary

The following symbols are exported from `pytekt.former` (package root):

| Symbol | Description |
|--------|-------------|
| `__version__` | Module version string (e.g. `"0.1.0"`). |
| `Transformer` | Decoder-only transformer for next-token prediction. |
| `MultiHeadAttention` | Multi-head self-attention layer. |
| `FeedForward` | Position-wise feed-forward network (two linear + ReLU). |
| `Embedding` | Token embedding layer. |
| `PositionalEncoding` | Sinusoidal positional encoding (no learnable params). |
| `Trainer` | Training loop: forward, loss, backward, optimizer step. |
| `Adam` | Adam optimizer for `Tensor` parameters. |
| `cross_entropy_loss` | Cross-entropy loss for next-token prediction. |
| `TextDataset` | Sliding-window next-token dataset from text. |
| `create_dataloader` | Build dataset and `get_batch` callable. |
| `SimpleTokenizer` | Character- or word-level tokenizer. |
| `plot_attention_map` | Plot attention matrix for one layer/head. |
| `plot_multi_head_attention` | Plot all heads for one layer in a grid. |
| `plot_training_metrics` | Plot metrics (e.g. loss) over epochs. |
| `plot_weight_spectrum` | Plot eigenvalue/singular-value distribution of a weight matrix. |

Subpackages: `pytekt.former.core`, `pytekt.former.models`, `pytekt.former.training`, `pytekt.former.datasets`, `pytekt.former.visualization`. Import from them when you need lower-level types (e.g. `Tensor`, `TransformerBlock`).

---

## Module reference

### core

**Purpose:** Differentiable tensor and operations for the computation graph.

| Symbol | Description |
|--------|-------------|
| `Tensor` | Array with `requires_grad`, `grad`, and backward via `_grad_fn`. |
| `matmul` | Matrix multiplication with gradients. |
| `transpose` | Transpose last two dimensions. |
| `relu` | Elementwise ReLU. |
| `softmax` | Numerically stable softmax along an axis. |
| `layer_norm` | Layer normalization over last dimension (gamma, beta). |
| `scaled_dot_product_attention` | Scaled dot-product attention (returns output tensor and attention weights array). |

**Entry:** `from pytekt.former.core import Tensor, matmul, softmax, layer_norm, relu, transpose`.

---

### models

**Purpose:** Transformer architecture components.

| Symbol | Description |
|--------|-------------|
| `Transformer` | Full decoder-only model: embedding → pos → N blocks → ln → LM head. |
| `TransformerBlock` | Single block: pre-norm attention + residual, pre-norm FFN + residual. |
| `MultiHeadAttention` | Q/K/V projections, multi-head attention, output projection. |
| `FeedForward` | Two linear layers with ReLU: embed_dim → hidden_dim → embed_dim. |
| `Embedding` | Token embedding lookup. |
| `PositionalEncoding` | Sinusoidal positions (fixed). |

**Entry:** `from pytekt.former.models import Transformer, MultiHeadAttention, FeedForward, Embedding, PositionalEncoding`.

---

### training

**Purpose:** Loss, optimizer, and training loop.

| Symbol | Description |
|--------|-------------|
| `Trainer` | Wraps model and Adam; `train_step(token_ids, targets)`, `train_epoch(get_batch, steps)`, `evaluate(get_batch, num_batches)`. |
| `Adam` | Adam optimizer; `step()`, `zero_grad()`. |
| `cross_entropy_loss` | Cross-entropy over next-token prediction; supports padding mask (target == -1). |

**Entry:** `from pytekt.former.training import Trainer, Adam, cross_entropy_loss`.

---

### datasets

**Purpose:** Text tokenization and batching.

| Symbol | Description |
|--------|-------------|
| `TextDataset` | Build from text + seq_length; `get_batch(batch_size)` → (inputs, targets). |
| `create_dataloader` | Returns (dataset, get_batch) for given text, seq_length, batch_size, level. |
| `SimpleTokenizer` | `fit(text)`, `encode(text)`, `decode(ids)`; level `"char"` or `"word"`. |

**Entry:** `from pytekt.former.datasets import TextDataset, create_dataloader, SimpleTokenizer`.

---

### visualization

**Purpose:** Attention, training curves, and weight spectra.

| Symbol | Description |
|--------|-------------|
| `plot_attention_map` | One layer/head; optional token labels; returns matplotlib Axes. |
| `plot_multi_head_attention` | All heads for one layer in a grid; returns Figure. |
| `plot_training_metrics` | Plot dicts of metrics over epochs; returns Axes. |
| `plot_weight_spectrum` | Histogram of eigenvalues or singular values of a 2D weight; returns Axes. |
| `plot_weight_spectra` | Multiple weight matrices in a row. |

**Entry:** `from pytekt.former.visualization import plot_attention_map, plot_multi_head_attention, plot_training_metrics, plot_weight_spectrum`.

---

## Configuration

Training is configured via **`aion/former/experiments/config.yaml`** (or the fallback dict in `train_small_model.py`).

| Section | Key | Description |
|--------|-----|-------------|
| **model** | `vocab_size` | Set from dataset; override in config optional. |
| | `embedding_dim` | Default `128`. |
| | `num_heads` | Default `4`. |
| | `num_layers` | Default `2`. |
| | `max_seq_len` | Default `64`. |
| | `hidden_dim` | FFN hidden size (default `4 * embedding_dim`). |
| **training** | `batch_size` | Default `32`. |
| | `lr` | Learning rate; use a number in YAML (e.g. `0.001`), not `1e-3` as string. |
| | `epochs` | Default `10`. |
| | `steps_per_epoch` | Default `50`. |
| **data** | `seq_length` | Context length. |
| | `level` | `char` or `word` tokenization. |
| | `data_file` | Optional path to text file. |

---

## Package layout

```
aion/former/
├── __init__.py          # Version, Transformer, Trainer, datasets, visualization
├── core/                # Tensor, ops — core/README.md, core/examples/
├── models/              # Transformer — models/README.md, models/examples/
├── training/            # Trainer, loss — training/README.md, training/examples/
├── datasets/            # TextDataset, tokenizer — datasets/README.md, datasets/examples/
├── visualization/       # Plots — visualization/README.md, visualization/examples/
├── experiments/         # train_small_model, config.yaml — experiments/README.md, experiments/examples/
├── examples/            # attention_demo, text_generation
├── docs/                # architecture.md
└── README.md            # This file
```

Each of **`core/`**, **`datasets/`**, **`experiments/`**, **`models/`**, **`training/`**, and **`visualization/`** includes a **`README.md`** with module-level documentation (API tables, layout, and cross-links), similar in spirit to **`aion/algorithms/README.md`**.

---

## Architecture

- **Decoder-only** (GPT-style): embedding → positional encoding → N × (pre-norm attention + pre-norm FFN) → final layer norm → LM head.
- **Autograd:** Scalar/array backward via `_grad_fn(grad, out, *inputs)`; gradients accumulated on parameters.
- **Default sizes:** `embed_dim=128`, `num_heads=4`, `num_layers=2`, `seq_length=64`; FFN `hidden_dim` default `4 * embed_dim`.

Details: **`docs/architecture.md`**.

---

## Design and conventions

- **Pre-norm:** Layer norm is applied before attention and before the feed-forward block in each transformer block for training stability.
- **NumPy only:** No CUDA; single CPU. Suitable for education and small experiments.
- **Library usage:** You import and call APIs; the module does not control your program flow.
- **Optional dependency:** Install with `pip install pytekt[former]` so Aion core can remain minimal.

---

## Dependencies

- **NumPy** ≥ 1.20 — tensors and math.
- **Matplotlib** ≥ 3.5 — visualization (attention, metrics, weight spectrum).
- **PyYAML** ≥ 6.0 — reading `config.yaml` in experiments.

All are included when installing the `[former]` extra.

---

## Usage examples

### Full training and visualization

```python
from pytekt.former import Transformer, Trainer
from pytekt.former.datasets import create_dataloader
from pytekt.former.visualization import plot_training_metrics, plot_attention_map
import matplotlib.pyplot as plt

text = open("data.txt").read()  # or use built-in sample
dataset, get_batch = create_dataloader(text, seq_length=64, batch_size=32, level="char")
model = Transformer(
    vocab_size=dataset.vocab_size,
    embed_dim=128,
    num_heads=4,
    num_layers=2,
    max_seq_len=64,
)
trainer = Trainer(model, lr=0.001)
for epoch in range(10):
    loss = trainer.train_epoch(get_batch, 50)
    print(f"Epoch {epoch + 1}  loss = {loss:.4f}")

plot_training_metrics(trainer.history, title="Aion transformer training loss")
plt.savefig("training_metrics.png")
plt.close()

# One forward to get attention weights
inputs, _ = get_batch()
logits, attn_weights_list = model.forward(inputs)
tokens = [dataset.tokenizer.reverse_vocab.get(i, "?") for i in inputs[0]]
plot_attention_map(attn_weights_list[0], tokens=tokens, layer=0, head=0)
plt.savefig("attention_layer0_head0.png")
plt.close()
```

### Tokenizer and generation

```python
from pytekt.former import Transformer
from pytekt.former.datasets import TextDataset, SimpleTokenizer
import numpy as np

text = "To be or not to be " * 50
seq_length = 64
dataset = TextDataset(text, seq_length=seq_length, level="char")
model = Transformer(
    vocab_size=dataset.vocab_size,
    embed_dim=128,
    num_heads=4,
    num_layers=2,
    max_seq_len=seq_length,
)
prompt = "To be "
ids = dataset.tokenizer.encode(prompt)
generated = list(ids)
for _ in range(40):
    context = np.array([generated[-seq_length:]], dtype=np.int64)
    logits, _ = model.forward(context)
    next_logits = logits._data[0, -1]
    next_id = np.argmax(next_logits)
    generated.append(next_id)
print(dataset.tokenizer.decode(generated))
```

---

## Command-line scripts

Run from the project root (or with `python -m` from anywhere Aion is installed).

- **Train a small model** (uses built-in sample text or `aion/former/experiments/config.yaml`):

  ```bash
  python -m pytekt.former.experiments.train_small_model
  ```

  Writes `training_metrics.png` (and optionally `weight_spectrum.png`) into `aion/former/experiments/`.

- **Attention visualization** (no training):

  ```bash
  python -m pytekt.former.examples.attention_demo
  ```

  Saves `attention_demo_head0.png` and `attention_demo_all_heads.png` in `aion/former/examples/`.

- **Text generation** (demo with random weights; extend to load a trained model):

  ```bash
  python -m pytekt.former.examples.text_generation
  ```

---

## Known limitations

- **CPU only:** NumPy-based; no GPU acceleration.
- **Small scale:** Intended for learning and small experiments; for large models use PyTorch/JAX/TF.
- **No checkpointing:** Save/load of model weights is not implemented; add it in your script if needed.
- **Single config file:** Experiments use one `config.yaml`; override via code or a different path if required.

---

## License

Part of **Aion** (PyTekt). See the root [LICENSE](../../LICENSE) and [README](../../README.md).

**Aion** — AI Research & Development Library · **Aqwel AI**
