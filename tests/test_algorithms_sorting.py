"""Smoke tests for sorting algorithms."""

import pytest

from pytekt.algorithms import get_algorithm


@pytest.mark.parametrize("name", ["bubble_sort", "merge_sort", "quick_sort", "heap_sort"])
def test_sorting_produces_sorted(name):
    fn = get_algorithm(name)
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    assert fn(data) == sorted(data)
