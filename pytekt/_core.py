"""
Optional C++ extension bridge.

Exposes fast numerical routines: uses the native _pytekt_core extension if built,
otherwise falls back to NumPy. Install with pybind11 and a C++ compiler
to build the extension: pip install pybind11 && pip install -e .
"""

from typing import Union, Sequence

import numpy as np

try:
    from pytekt._pytekt_core import (
        fast_sum as _fast_sum_native,
        fast_dot as _fast_dot_native,
        fast_norm2 as _fast_norm2_native,
        fast_mean as _fast_mean_native,
        fast_variance as _fast_variance_native,
        fast_argmax as _fast_argmax_native,
        fast_argmin as _fast_argmin_native,
        fast_min as _fast_min_native,
        fast_max as _fast_max_native,
        fast_norm1 as _fast_norm1_native,
        fast_relu as _fast_relu_native,
        fast_softmax as _fast_softmax_native,
        fast_sigmoid as _fast_sigmoid_native,
        fast_tanh as _fast_tanh_native,
        fast_clip as _fast_clip_native,
        fast_cumsum as _fast_cumsum_native,
        fast_matrix_vector_mul as _fast_matrix_vector_mul_native,
        fast_lower_bound as _fast_lower_bound_native,
        fast_upper_bound as _fast_upper_bound_native,
    )
    _NATIVE_AVAILABLE = True
except ImportError:
    _fast_sum_native = None
    _fast_dot_native = None
    _fast_norm2_native = None
    _fast_mean_native = None
    _fast_variance_native = None
    _fast_argmax_native = None
    _fast_argmin_native = None
    _fast_min_native = None
    _fast_max_native = None
    _fast_norm1_native = None
    _fast_relu_native = None
    _fast_softmax_native = None
    _fast_sigmoid_native = None
    _fast_tanh_native = None
    _fast_clip_native = None
    _fast_cumsum_native = None
    _fast_matrix_vector_mul_native = None
    _fast_lower_bound_native = None
    _fast_upper_bound_native = None
    _NATIVE_AVAILABLE = False


def fast_sum(arr: Union[Sequence[float], np.ndarray]) -> float:
    """
    Sum of a 1D array. Uses C++ when the native extension is built.

    Parameters
    ----------
    arr : array-like, 1D
        Values to sum (float64 or coercible).

    Returns
    -------
    float
        Sum of the array.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_sum expects a 1D array")
    if _NATIVE_AVAILABLE:
        return float(_fast_sum_native(a))
    return float(np.sum(a))


def fast_dot(a: Union[Sequence[float], np.ndarray], b: Union[Sequence[float], np.ndarray]) -> float:
    """
    Dot product of two 1D arrays of the same length.

    Parameters
    ----------
    a, b : array-like, 1D
        Vectors (float64 or coercible).

    Returns
    -------
    float
        Dot product.
    """
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    if aa.ndim != 1 or bb.ndim != 1:
        raise ValueError("fast_dot expects 1D arrays")
    if aa.shape[0] != bb.shape[0]:
        raise ValueError("fast_dot: shape mismatch")
    if _NATIVE_AVAILABLE:
        return float(_fast_dot_native(aa, bb))
    return float(np.dot(aa, bb))


def fast_norm2(arr: Union[Sequence[float], np.ndarray]) -> float:
    """
    L2 (Euclidean) norm of a 1D array.

    Parameters
    ----------
    arr : array-like, 1D
        Vector (float64 or coercible).

    Returns
    -------
    float
        sqrt(sum(x_i^2)).
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_norm2 expects a 1D array")
    if _NATIVE_AVAILABLE:
        return float(_fast_norm2_native(a))
    return float(np.linalg.norm(a))


def fast_mean(arr: Union[Sequence[float], np.ndarray]) -> float:
    """
    Mean of a 1D array.

    Parameters
    ----------
    arr : array-like, 1D
        Values (float64 or coercible).

    Returns
    -------
    float
        Mean.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_mean expects a 1D array")
    if a.size == 0:
        raise ValueError("fast_mean: empty array")
    if _NATIVE_AVAILABLE:
        return float(_fast_mean_native(a))
    return float(np.mean(a))


def fast_variance(
    arr: Union[Sequence[float], np.ndarray],
    ddof: int = 0,
) -> float:
    """
    Variance of a 1D array. ddof=0 population variance, ddof=1 sample variance.

    Parameters
    ----------
    arr : array-like, 1D
        Values (float64 or coercible).
    ddof : int, optional
        Delta degrees of freedom (default 0).

    Returns
    -------
    float
        Variance.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_variance expects a 1D array")
    if a.size <= ddof:
        raise ValueError("fast_variance: n must be > ddof")
    if _NATIVE_AVAILABLE:
        return float(_fast_variance_native(a, ddof))
    return float(np.var(a, ddof=ddof))


def fast_argmax(arr: Union[Sequence[float], np.ndarray]) -> int:
    """
    Index of the maximum value in a 1D array.

    Parameters
    ----------
    arr : array-like, 1D
        Values (float64 or coercible).

    Returns
    -------
    int
        Index of first occurrence of maximum.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_argmax expects a 1D array")
    if a.size == 0:
        raise ValueError("fast_argmax: empty array")
    if _NATIVE_AVAILABLE:
        return int(_fast_argmax_native(a))
    return int(np.argmax(a))


def fast_argmin(arr: Union[Sequence[float], np.ndarray]) -> int:
    """
    Index of the minimum value in a 1D array.

    Parameters
    ----------
    arr : array-like, 1D
        Values (float64 or coercible).

    Returns
    -------
    int
        Index of first occurrence of minimum.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_argmin expects a 1D array")
    if a.size == 0:
        raise ValueError("fast_argmin: empty array")
    if _NATIVE_AVAILABLE:
        return int(_fast_argmin_native(a))
    return int(np.argmin(a))


def fast_min(arr: Union[Sequence[float], np.ndarray]) -> float:
    """Minimum of a 1D array."""
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_min expects a 1D array")
    if a.size == 0:
        raise ValueError("fast_min: empty array")
    if _NATIVE_AVAILABLE:
        return float(_fast_min_native(a))
    return float(np.min(a))


def fast_max(arr: Union[Sequence[float], np.ndarray]) -> float:
    """Maximum of a 1D array."""
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_max expects a 1D array")
    if a.size == 0:
        raise ValueError("fast_max: empty array")
    if _NATIVE_AVAILABLE:
        return float(_fast_max_native(a))
    return float(np.max(a))


def fast_norm1(arr: Union[Sequence[float], np.ndarray]) -> float:
    """
    L1 norm: sum of absolute values of a 1D array.

    Parameters
    ----------
    arr : array-like, 1D
        Vector (float64 or coercible).

    Returns
    -------
    float
        sum_i |x_i|.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_norm1 expects a 1D array")
    if _NATIVE_AVAILABLE:
        return float(_fast_norm1_native(a))
    return float(np.sum(np.abs(a)))


def fast_relu(arr: Union[Sequence[float], np.ndarray]) -> np.ndarray:
    """
    ReLU(x) = max(0, x) element-wise. Returns a new 1D float64 array.

    Parameters
    ----------
    arr : array-like, 1D
        Values (float64 or coercible).

    Returns
    -------
    np.ndarray
        1D array of same shape.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_relu expects a 1D array")
    if _NATIVE_AVAILABLE:
        return _fast_relu_native(a)
    return np.maximum(0.0, a)


def fast_softmax(arr: Union[Sequence[float], np.ndarray]) -> np.ndarray:
    """
    Numerically stable softmax over a 1D array. Returns a new float64 array.

    Parameters
    ----------
    arr : array-like, 1D
        Logits (float64 or coercible).

    Returns
    -------
    np.ndarray
        1D array of probabilities (sum = 1).
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_softmax expects a 1D array")
    if a.size == 0:
        raise ValueError("fast_softmax: empty array")
    if _NATIVE_AVAILABLE:
        return _fast_softmax_native(a)
    a = a - np.max(a)
    e = np.exp(a)
    return e / np.sum(e)


def fast_sigmoid(arr: Union[Sequence[float], np.ndarray]) -> np.ndarray:
    """
    Sigmoid 1 / (1 + exp(-x)) element-wise. Numerically stable; returns float64 copy.

    Parameters
    ----------
    arr : array-like, 1D
        Values (float64 or coercible).

    Returns
    -------
    np.ndarray
        1D array of same shape.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_sigmoid expects a 1D array")
    if _NATIVE_AVAILABLE:
        return _fast_sigmoid_native(a)
    pos = a >= 0.0
    out = np.empty_like(a)
    out[pos] = 1.0 / (1.0 + np.exp(-a[pos]))
    expx = np.exp(a[~pos])
    out[~pos] = expx / (1.0 + expx)
    return out


def fast_tanh(arr: Union[Sequence[float], np.ndarray]) -> np.ndarray:
    """Hyperbolic tangent element-wise. Returns a new 1D float64 array."""
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_tanh expects a 1D array")
    if _NATIVE_AVAILABLE:
        return _fast_tanh_native(a)
    return np.tanh(a)


def fast_clip(
    arr: Union[Sequence[float], np.ndarray],
    lo: float,
    hi: float,
) -> np.ndarray:
    """
    Clamp each element to ``[lo, hi]``. Returns a new float64 array.

    Parameters
    ----------
    arr : array-like, 1D
        Values (float64 or coercible).
    lo, hi : float
        Inclusive bounds; ``lo`` must be <= ``hi``.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_clip expects a 1D array")
    if lo > hi:
        raise ValueError("fast_clip: lo must be <= hi")
    if _NATIVE_AVAILABLE:
        return _fast_clip_native(a, lo, hi)
    return np.clip(a, lo, hi)


def fast_cumsum(arr: Union[Sequence[float], np.ndarray]) -> np.ndarray:
    """
    Cumulative sum of a 1D array. Returns a new float64 array.

    Parameters
    ----------
    arr : array-like, 1D
        Values (float64 or coercible).

    Returns
    -------
    np.ndarray
        1D cumulative sum.
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_cumsum expects a 1D array")
    if _NATIVE_AVAILABLE:
        return _fast_cumsum_native(a)
    return np.cumsum(a)


def fast_matrix_vector_mul(
    mat: Union[Sequence[Sequence[float]], np.ndarray],
    vec: Union[Sequence[float], np.ndarray],
) -> np.ndarray:
    """
    Matrix-vector product: (M, N) @ (N,) -> (M,). Returns a new float64 array.

    Parameters
    ----------
    mat : array-like, 2D
        Matrix (M, N).
    vec : array-like, 1D
        Vector (N,).

    Returns
    -------
    np.ndarray
        1D result (M,).
    """
    m = np.asarray(mat, dtype=np.float64)
    v = np.asarray(vec, dtype=np.float64)
    if m.ndim != 2 or v.ndim != 1:
        raise ValueError("fast_matrix_vector_mul expects 2D matrix and 1D vector")
    if m.shape[1] != v.shape[0]:
        raise ValueError("fast_matrix_vector_mul: matrix cols != vector size")
    if _NATIVE_AVAILABLE:
        return _fast_matrix_vector_mul_native(m, v)
    return np.dot(m, v)


def fast_lower_bound(arr: Union[Sequence[float], np.ndarray], value: float) -> int:
    """
    First index i where arr[i] >= value. Assumes ascending order (e.g. sorted).

    Parameters
    ----------
    arr : array-like, 1D
        Sorted ascending (float64 or coercible).
    value : float
        Search value.

    Returns
    -------
    int
        Smallest index i with arr[i] >= value (or len(arr) if none).
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_lower_bound expects a 1D array")
    if _NATIVE_AVAILABLE:
        return int(_fast_lower_bound_native(a, value))
    return int(np.searchsorted(a, value, side="left"))


def fast_upper_bound(arr: Union[Sequence[float], np.ndarray], value: float) -> int:
    """
    First index ``i`` where ``arr[i] > value``. Assumes ascending order (sorted).

    Parameters
    ----------
    arr : array-like, 1D
        Sorted ascending (float64 or coercible).
    value : float
        Search value.

    Returns
    -------
    int
        Smallest index ``i`` with ``arr[i] > value`` (or ``len(arr)`` if none).
    """
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError("fast_upper_bound expects a 1D array")
    if _NATIVE_AVAILABLE:
        return int(_fast_upper_bound_native(a, value))
    return int(np.searchsorted(a, value, side="right"))


def using_native_extension() -> bool:
    """Return True if the C++ extension is loaded."""
    return _NATIVE_AVAILABLE


__all__ = [
    "fast_sum",
    "fast_dot",
    "fast_norm2",
    "fast_norm1",
    "fast_mean",
    "fast_variance",
    "fast_argmax",
    "fast_argmin",
    "fast_min",
    "fast_max",
    "fast_relu",
    "fast_softmax",
    "fast_sigmoid",
    "fast_tanh",
    "fast_clip",
    "fast_cumsum",
    "fast_matrix_vector_mul",
    "fast_lower_bound",
    "fast_upper_bound",
    "using_native_extension",
]
