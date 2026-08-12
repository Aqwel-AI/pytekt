"""Big-data helpers with optional C++ acceleration.

This module keeps the public API simple while allowing the hot paths to
run in the native extension when available.
"""

from __future__ import annotations

from typing import Dict, Sequence

import numpy as np

try:
    from pytekt._pytekt_bigdata import (
        chunk_statistics as _chunk_statistics_native,
        histogram as _histogram_native,
        prefix_sum as _prefix_sum_native,
        rolling_mean as _rolling_mean_native,
        rolling_sum as _rolling_sum_native,
    )

    _NATIVE_AVAILABLE = True
except ImportError:
    _chunk_statistics_native = None
    _histogram_native = None
    _prefix_sum_native = None
    _rolling_mean_native = None
    _rolling_sum_native = None
    _NATIVE_AVAILABLE = False


def using_native_extension() -> bool:
    """Return True when the native big-data backend is active."""
    return _NATIVE_AVAILABLE


def _as_float_array(arr: Sequence[float] | np.ndarray) -> np.ndarray:
    values = np.asarray(arr, dtype=np.float64)
    if values.ndim != 1:
        raise ValueError("expected a 1D numeric array")
    return values


def prefix_sum(arr: Sequence[float] | np.ndarray) -> np.ndarray:
    """Compute prefix sums for large numeric sequences."""
    values = _as_float_array(arr)
    if _NATIVE_AVAILABLE:
        return np.asarray(_prefix_sum_native(values))
    return np.cumsum(values)


def rolling_sum(arr: Sequence[float] | np.ndarray, window: int) -> np.ndarray:
    """Compute rolling sums over a 1D numeric sequence."""
    values = _as_float_array(arr)
    if window <= 0:
        raise ValueError("window must be > 0")
    if _NATIVE_AVAILABLE:
        return np.asarray(_rolling_sum_native(values, window))
    if values.size == 0 or window > values.size:
        return np.asarray([], dtype=np.float64)
    out = np.array([values[i : i + window].sum() for i in range(values.size - window + 1)])
    return out


def rolling_mean(arr: Sequence[float] | np.ndarray, window: int) -> np.ndarray:
    """Compute rolling means over a 1D numeric sequence."""
    values = _as_float_array(arr)
    if window <= 0:
        raise ValueError("window must be > 0")
    if _NATIVE_AVAILABLE:
        return np.asarray(_rolling_mean_native(values, window))
    sums = rolling_sum(values, window)
    return sums / float(window)


def histogram(
    arr: Sequence[float] | np.ndarray,
    bins: int,
    lo: float,
    hi: float,
) -> np.ndarray:
    """Compute histogram counts for a 1D numeric sequence."""
    values = _as_float_array(arr)
    if bins <= 0:
        raise ValueError("bins must be > 0")
    if hi <= lo:
        raise ValueError("hi must be greater than lo")
    if _NATIVE_AVAILABLE:
        return np.asarray(_histogram_native(values, bins, lo, hi))
    counts, _ = np.histogram(values, bins=bins, range=(lo, hi))
    return counts.astype(np.int64, copy=False)


def chunk_statistics(arr: Sequence[float] | np.ndarray, chunk_size: int) -> Dict[str, np.ndarray]:
    """Return per-chunk mean/min/max statistics for a 1D numeric sequence."""
    values = _as_float_array(arr)
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if _NATIVE_AVAILABLE:
        native = _chunk_statistics_native(values, chunk_size)
        return {
            "mean": np.asarray(native["mean"]),
            "min": np.asarray(native["min"]),
            "max": np.asarray(native["max"]),
        }
    if values.size == 0:
        empty = np.asarray([], dtype=np.float64)
        return {"mean": empty, "min": empty, "max": empty}
    chunks = []
    mins = []
    maxs = []
    for start in range(0, values.size, chunk_size):
        chunk = values[start : start + chunk_size]
        chunks.append(chunk.mean())
        mins.append(chunk.min())
        maxs.append(chunk.max())
    return {
        "mean": np.asarray(chunks),
        "min": np.asarray(mins),
        "max": np.asarray(maxs),
    }


__all__ = [
    "chunk_statistics",
    "histogram",
    "prefix_sum",
    "rolling_mean",
    "rolling_sum",
    "using_native_extension",
]
