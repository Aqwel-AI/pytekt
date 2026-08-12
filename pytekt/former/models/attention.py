"""
Multi-head self-attention.

Q/K/V projections, split into heads, scaled dot-product attention,
then merge heads and output projection. Returns output and attention
weights for visualization.
"""

import numpy as np
from typing import Optional, Tuple
from ..core.tensor import Tensor
from ..core.operations import matmul, softmax, transpose, scaled_dot_product_attention


# -----------------------------------------------------------------------------
# Multi-head attention layer
# -----------------------------------------------------------------------------

class MultiHeadAttention:
    """
    Multi-head self-attention over the sequence dimension.

    Parameters
    ----------
    embed_dim : int
        Total embedding dimension; must be divisible by num_heads.
    num_heads : int
        Number of attention heads.
    dropout : float, optional
        Reserved for future use; currently unused (default 0).
    """

    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        dropout: float = 0.0,
    ):
        assert embed_dim % num_heads == 0
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        # Q, K, V, and output projections (learnable)
        scale = 0.02
        self.W_q = Tensor(
            np.random.randn(embed_dim, embed_dim).astype(np.float64) * scale,
            requires_grad=True,
        )
        self.W_k = Tensor(
            np.random.randn(embed_dim, embed_dim).astype(np.float64) * scale,
            requires_grad=True,
        )
        self.W_v = Tensor(
            np.random.randn(embed_dim, embed_dim).astype(np.float64) * scale,
            requires_grad=True,
        )
        self.W_o = Tensor(
            np.random.randn(embed_dim, embed_dim).astype(np.float64) * scale,
            requires_grad=True,
        )

    def forward(
        self,
        x: Tensor,
        mask: Optional[np.ndarray] = None,
    ) -> Tuple[Tensor, np.ndarray]:
        """
        Compute multi-head attention over input sequence.

        Parameters
        ----------
        x : Tensor
            Input, shape (batch, seq, embed_dim).
        mask : np.ndarray, optional
            Additive mask on attention scores.

        Returns
        -------
        out : Tensor
            Output, shape (batch, seq, embed_dim).
        attn_weights : np.ndarray
            Attention weights, shape (batch, num_heads, seq, seq).
        """
        batch, seq, _ = x.shape
        q = matmul(x, self.W_q)
        k = matmul(x, self.W_k)
        v = matmul(x, self.W_v)
        q = _reshape_heads(q, self.num_heads)
        k = _reshape_heads(k, self.num_heads)
        v = _reshape_heads(v, self.num_heads)
        out, attn_weights = scaled_dot_product_attention(q, k, v, mask)
        out = _merge_heads(out)
        out = matmul(out, self.W_o)
        return out, attn_weights

    def parameters(self):
        """Return Q, K, V, and output projection parameters."""
        return [self.W_q, self.W_k, self.W_v, self.W_o]


# -----------------------------------------------------------------------------
# Head reshape helpers (with gradient support)
# -----------------------------------------------------------------------------

def _reshape_heads(x: Tensor, num_heads: int) -> Tensor:
    """Reshape (batch, seq, embed) -> (batch, num_heads, seq, head_dim)."""
    batch, seq, embed = x.shape
    head_dim = embed // num_heads
    data = x._data.reshape(batch, seq, num_heads, head_dim)
    data = np.transpose(data, (0, 2, 1, 3))

    def _backward(grad: np.ndarray, out: Tensor, xx: Tensor) -> Tuple[np.ndarray]:
        batch, _, seq, head_dim = grad.shape
        data = np.transpose(grad, (0, 2, 1, 3)).reshape(batch, seq, num_heads * head_dim)
        return (data,)

    return Tensor(data, requires_grad=x.requires_grad, _grad_fn=_backward, _prev=(x,))


def _merge_heads(x: Tensor) -> Tensor:
    """Reshape (batch, num_heads, seq, head_dim) -> (batch, seq, embed)."""
    batch, num_heads, seq, head_dim = x.shape
    data = np.transpose(x._data, (0, 2, 1, 3)).reshape(batch, seq, num_heads * head_dim)
    return Tensor(data, requires_grad=x.requires_grad, _grad_fn=_merge_heads_backward, _prev=(x,))


def _merge_heads_backward(grad: np.ndarray, out: Tensor, x: Tensor) -> Tuple[np.ndarray]:
    """Backward for merge_heads."""
    batch, num_heads, seq, head_dim = x.shape
    data = grad.reshape(batch, seq, num_heads, head_dim)
    data = np.transpose(data, (0, 2, 1, 3))
    return (data,)
