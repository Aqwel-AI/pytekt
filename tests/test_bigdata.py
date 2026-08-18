"""Tests for the big-data helpers."""

import numpy as np

from pytekt import bigdata
from pytekt.algorithms.arrays import compute_prefix_sums, rolling_sum


def test_bigdata_prefix_sum_and_rolling_sum():
    values = [1.0, 2.0, 3.0, 4.0]
    assert np.allclose(bigdata.prefix_sum(values), [1.0, 3.0, 6.0, 10.0])
    assert np.allclose(bigdata.rolling_sum(values, 2), [3.0, 5.0, 7.0])
    assert np.allclose(bigdata.rolling_mean(values, 2), [1.5, 2.5, 3.5])


def test_bigdata_histogram_and_chunk_stats():
    values = [0.0, 0.1, 0.8, 1.5, 1.9, 2.2]
    hist = bigdata.histogram(values, bins=3, lo=0.0, hi=3.0)
    stats = bigdata.chunk_statistics(values, 2)
    assert hist.sum() == 6
    assert list(stats["mean"]) == [0.05, 1.15, 2.05]
    assert list(stats["min"]) == [0.0, 0.8, 1.9]
    assert list(stats["max"]) == [0.1, 1.5, 2.2]


def test_algorithms_use_native_bigdata_wrappers():
    values = [2, 3, 5, 7]
    assert compute_prefix_sums(values) == [2.0, 5.0, 10.0, 17.0]
    assert rolling_sum(values, 2) == [5.0, 8.0, 12.0]
