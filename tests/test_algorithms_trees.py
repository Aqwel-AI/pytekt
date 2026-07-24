"""Smoke tests for tree algorithms."""

from aion.algorithms import get_algorithm
from aion.algorithms.trees import TrieNode


def test_bst_search():
    search = get_algorithm("bst_search")
    root = get_algorithm("bst_insert")(None, 5)
    root = get_algorithm("bst_insert")(root, 3)
    root = get_algorithm("bst_insert")(root, 7)
    assert search(root, 3) is not None
    assert search(root, 8) is None


def test_trie_insert_search():
    root = TrieNode()
    get_algorithm("trie_insert")(root, "cat")
    get_algorithm("trie_insert")(root, "car")
    assert get_algorithm("trie_search")(root, "cat")
    assert not get_algorithm("trie_search")(root, "ca")
