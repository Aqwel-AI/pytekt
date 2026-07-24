"""Tests for algorithm catalog."""

from aion.algorithms import count_algorithms, categories, get_algorithm, list_algorithms


def test_catalog_count_at_least_420():
    assert count_algorithms() >= 420


def test_catalog_categories():
    cats = categories()
    assert "sorting" in cats
    assert "dynamic_programming" in cats
    assert "search" in cats


def test_get_algorithm():
    fn = get_algorithm("binary_search")
    assert fn([1, 2, 3], 2) == 1


def test_list_algorithms_filter():
    sorting = list_algorithms("sorting")
    assert len(sorting) >= 30
    assert all(e.category == "sorting" for e in sorting)
