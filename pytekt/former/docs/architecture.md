# Aion Transformer Architecture

## Overview

The Aion transformer module implements a **decoder-only** transformer (GPT-style) for next-token prediction. The implementation is minimal and NumPy-based, with a custom autograd for clarity and experimentation.

## Components

### Core

- **Tensor**: NumPy array with `requires_grad`, `grad`, and optional `_grad_fn` / `_prev` for backward.
- **Operations**: `matmul`, `transpose`, `relu`, `softmax`, `layer_norm`, and `scaled_dot_product_attention` with gradients.
- **Autograd**: Backward pass via `tensor.backward()`; gradients flow through `_grad_fn(grad, out, *inputs)`.

### Model

- **Embedding**: `(vocab_size, embed_dim)` lookup; gradient scattered back to embedding matrix.
- **PositionalEncoding**: Sinusoidal (no learnable params).
- **MultiHeadAttention**: Q/K/V projections, reshape to heads, scaled dot-product attention, output projection.
- **FeedForward**: Two linear layers with ReLU: `embed_dim -> hidden_dim -> embed_dim`.
- **TransformerBlock**: Pre-norm attention + residual; pre-norm feed-forward + residual.
- **Transformer**: Embedding → positional encoding → N × TransformerBlock → final layer norm → LM head.

### Training

- **Loss**: Cross-entropy over next-token prediction; masking for padding (e.g. `target == -1`).
- **Optimizer**: Adam (with optional bias correction).
- **Trainer**: `train_step(input_ids, targets)`, `train_epoch(get_batch, steps_per_epoch)`.

### Data

- **SimpleTokenizer**: Character- or word-level vocab; `encode` / `decode`.
- **TextDataset**: Sliding window over token ids; `get_batch(batch_size)` → `(inputs, targets)`.

## MVP Sizes

- `embed_dim = 128`, `num_heads = 4`, `num_layers = 2`, `seq_length = 64`.
- Feed-forward `hidden_dim` default `4 * embed_dim`.

## Visualization

- **Attention maps**: Per-layer, per-head attention weights (heatmaps).
- **Training metrics**: Loss over epochs.
- **Weight spectrum**: Eigenvalue or singular-value distribution of weight matrices.

## Design

- **Pre-norm**: Layer norm before attention and FFN for training stability.
- **NumPy only**: No CUDA; single CPU. Optional PyTorch backend can be added later.
