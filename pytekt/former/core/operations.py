"""
Core operations with gradient support.

Differentiable operations: matmul, transpose, relu, softmax, layer_norm,
and scaled_dot_product_attention. All return Tensor and register backward
functions for autograd.
"""

import numpy as np
from typing import Tuple, Optional
from .tensor import Tensor, _make_tensor


# -----------------------------------------------------------------------------
# Linear algebra and activations
# -----------------------------------------------------------------------------

def transpose(x: Tensor) -> Tensor:
    """
    Transpose last two dimensions (full transpose for 2D).

    Parameters
    ----------
    x : Tensor
        Input tensor; at least 2D.

    Returns
    -------
    Tensor
        Tensor with axes -2 and -1 swapped; supports backward.
    """
    data = np.swapaxes(x._data, -2, -1)
    def _backward(grad: np.ndarray, out: Tensor, xx: Tensor) -> Tuple[np.ndarray]:
        return (np.swapaxes(grad, -2, -1),)
    return _make_tensor(data, False, _backward, x)


def matmul(a: Tensor, b: Tensor) -> Tensor:
    """
    Matrix multiplication; supports batched (..., M, K) @ (..., K, N).

    Parameters
    ----------
    a : Tensor
        Left operand, shape (..., M, K).
    b : Tensor
        Right operand, shape (..., K, N).

    Returns
    -------
    Tensor
        Product, shape (..., M, N); supports backward.
    """
    data = np.matmul(a._data, b._data)

    def _backward(grad: np.ndarray, out: Tensor, aa: Tensor, bb: Tensor) -> Tuple[np.ndarray, np.ndarray]:
        ga = np.matmul(grad, np.swapaxes(bb._data, -2, -1))
        gb = np.matmul(np.swapaxes(aa._data, -2, -1), grad)
        return (ga, gb)

    return _make_tensor(data, False, _backward, a, b)


def relu(x: Tensor) -> Tensor:
    """
    Elementwise ReLU: max(0, x).

    Parameters
    ----------
    x : Tensor
        Input tensor.

    Returns
    -------
    Tensor
        Same shape; non-negative; supports backward.
    """
    data = np.maximum(0, x._data)

    def _backward(grad: np.ndarray, out: Tensor, xx: Tensor) -> Tuple[np.ndarray]:
        return (grad * (xx._data > 0),)

    return _make_tensor(data, False, _backward, x)


def softmax(x: Tensor, axis: int = -1) -> Tensor:
    """
    Numerically stable softmax along the given axis.

    Parameters
    ----------
    x : Tensor
        Logits; any shape.
    axis : int, optional
        Axis over which to apply softmax (default -1).

    Returns
    -------
    Tensor
        Probabilities (sum to 1 along axis); supports backward.
    """
    x_max = np.max(x._data, axis=axis, keepdims=True)
    exp_x = np.exp(x._data - x_max)
    data = exp_x / np.sum(exp_x, axis=axis, keepdims=True)

    def _backward(grad: np.ndarray, out: Tensor, xx: Tensor) -> Tuple[np.ndarray]:
        s = out._data
        gs = grad * s
        return (s * (grad - np.sum(gs, axis=axis, keepdims=True)),)

    return _make_tensor(data, False, _backward, x)


def layer_norm(x: Tensor, gamma: Tensor, beta: Tensor, eps: float = 1e-5) -> Tensor:
    """
    Layer normalization over the last dimension.

    Computes (x - mean) / sqrt(var + eps) * gamma + beta over the last axis.

    Parameters
    ----------
    x : Tensor
        Input, shape (..., D).
    gamma : Tensor
        Scale, shape (D,); learnable.
    beta : Tensor
        Shift, shape (D,); learnable.
    eps : float, optional
        Small constant for numerical stability (default 1e-5).

    Returns
    -------
    Tensor
        Normalized tensor, same shape as x; supports backward.
    """
    axis = -1
    mean = np.mean(x._data, axis=axis, keepdims=True)
    var = np.var(x._data, axis=axis, keepdims=True) + eps
    std = np.sqrt(var)
    x_centered = x._data - mean
    x_norm = x_centered / std
    data = gamma._data * x_norm + beta._data

    def _backward(
        grad: np.ndarray, out: Tensor, xx: Tensor, g: Tensor, b: Tensor
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        D = xx.shape[-1]
        x_centered = xx._data - np.mean(xx._data, axis=axis, keepdims=True)
        var = np.var(xx._data, axis=axis, keepdims=True) + eps
        std = np.sqrt(var)
        dnorm = grad * g._data
        dvar = np.sum(dnorm * x_centered * (-0.5) * (var ** (-1.5)), axis=axis, keepdims=True)
        dmean = np.sum(dnorm * (-1 / std), axis=axis, keepdims=True) + dvar * np.mean(-2 * x_centered, axis=axis, keepdims=True) / D
        dx = dnorm / std + dvar * 2 * x_centered / D + dmean / D
        dgamma = np.sum(grad * x_norm, axis=tuple(range(grad.ndim - 1)))
        dbeta = np.sum(grad, axis=tuple(range(grad.ndim - 1)))
        return (dx, dgamma, dbeta)

    return _make_tensor(data, False, _backward, x, gamma, beta)


# -----------------------------------------------------------------------------
# Attention
# -----------------------------------------------------------------------------

def scaled_dot_product_attention(
    q: Tensor, k: Tensor, v: Tensor, mask: Optional[np.ndarray] = None
) -> Tuple[Tensor, np.ndarray]:
    """
    Scaled dot-product attention: softmax(Q K^T / sqrt(d_k)) V.

    Parameters
    ----------
    q, k, v : Tensor
        Query, key, value; shape (batch, heads, seq, head_dim).
    mask : np.ndarray, optional
        Additive mask applied to scores before softmax (e.g. -inf for causal).

    Returns
    -------
    output : Tensor
        Attention output; shape (batch, heads, seq, head_dim).
    attention_weights : np.ndarray
        Attention weights (after softmax); shape (batch, heads, seq, seq).
    """
    from .tensor import Tensor
    d_k = q.shape[-1]
    scores = matmul(q, transpose(k))  # (B, H, seq, seq)
    scores = scores * (1.0 / np.sqrt(d_k))
    if mask is not None:
        scores._data = scores._data + mask
    attn = softmax(scores, axis=-1)
    out = matmul(attn, v)
    return out, attn._data
