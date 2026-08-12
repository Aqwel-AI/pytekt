"""Smoke tests for dynamic programming algorithms."""

from pytekt.algorithms import get_algorithm


def test_lcs_length():
    assert get_algorithm("lcs_length")("abcde", "ace") == 3


def test_knapsack_01():
    val = get_algorithm("knapsack_01_max_value")([1, 2, 3], [6, 10, 12], 5)
    assert val == 22


def test_edit_distance():
    assert get_algorithm("edit_distance")("kitten", "sitting") == 3
