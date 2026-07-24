"""
Advanced data structures: Trie, Bloom filter, LRU cache, priority queue, Union-Find.

Pure-Python implementations with no external dependencies beyond the stdlib.

Examples
--------
>>> from aion.structures import Trie
>>> t = Trie()
>>> t.insert("hello")
>>> t.search("hello")
True
>>> t.starts_with("hel")
['hello']
"""

from .bloom_filter import BloomFilter
from .lru import LRUCache
from .priority_queue import MinHeap, MaxHeap, PriorityQueue
from .trie import Trie
from .union_find import UnionFind

__all__ = [
    "BloomFilter",
    "LRUCache",
    "MaxHeap",
    "MinHeap",
    "PriorityQueue",
    "Trie",
    "UnionFind",
]
