"""
Embedding and sinusoidal positional encoding.

Token embedding lookup (with gradient through weights) and fixed
sinusoidal positional encoding. No learnable parameters in positional encoding.
"""

import numpy as np
from typing import Tuple
from ..core.tensor import Tensor, _make_tensor


# -----------------------------------------------------------------------------
# Embedding lookup and layers
# -----------------------------------------------------------------------------

def embed_lookup(weight: Tensor, indices: np.ndarray) -> Tensor:
    """
    Look up embedding rows for integer indices. Supports backward to weight.

    Parameters
    ----------
    weight : Tensor
        Embedding matrix, shape (vocab_size, embed_dim).
    indices : np.ndarray
        Integer indices, shape (batch, seq) or similar.

    Returns
    -------
    Tensor
        Embedded vectors, shape (batch, seq, embed_dim); gradient flows to weight.
    """
    data = weight._data[indices]

    def _backward(grad: np.ndarray, out: Tensor, w: Tensor) -> Tuple[np.ndarray]:
        g = np.zeros_like(w._data)
        np.add.at(g, indices, grad)
        return (g,)

    return _make_tensor(data, False, _backward, weight)


class Embedding:
    """
    Token embedding layer: integer ids -> dense vectors.

    Parameters
    ----------
    vocab_size : int
        Size of the vocabulary.
    embed_dim : int
        Embedding dimension.
    """

    def __init__(self, vocab_size: int, embed_dim: int):
        scale = 0.02
        self.weight = Tensor(
            np.random.randn(vocab_size, embed_dim).astype(np.float64) * scale,
            requires_grad=True,
        )
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim

    def forward(self, indices: np.ndarray) -> Tensor:
        """Look up embeddings for the given indices."""
        return embed_lookup(self.weight, indices)

    def __call__(self, indices: np.ndarray) -> Tensor:
        return self.forward(indices)


class PositionalEncoding:
    """
    Sinusoidal positional encoding. No learnable parameters.

    Parameters
    ----------
    embed_dim : int
        Embedding dimension (must match model).
    max_len : int, optional
        Maximum sequence length to precompute (default 512).
    """

    def __init__(self, embed_dim: int, max_len: int = 512):
        self.embed_dim = embed_dim
        self.max_len = max_len
        pe = np.zeros((max_len, embed_dim))
        position = np.arange(0, max_len)[:, np.newaxis]
        div_term = np.exp(np.arange(0, embed_dim, 2) * (-np.log(10000.0) / embed_dim))
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)
        self._pe = pe

    def forward(self, x: Tensor, start: int = 0) -> Tensor:
        """
        Add positional encoding for positions [start, start+seq_len).

        Parameters
        ----------
        x : Tensor
            Input, shape (batch, seq, embed_dim).
        start : int, optional
            Start position index (default 0).

        Returns
        -------
        Tensor
            x + positional_encoding; same shape as x.
        """
        seq_len = x.shape[1]
        pe = self._pe[start : start + seq_len]
        from ..core.tensor import _add
        return _add(x, Tensor(pe))
