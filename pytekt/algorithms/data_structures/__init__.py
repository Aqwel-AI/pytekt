"""
Data Structures Subpackage
==========================

Provides foundational and advanced data structures and array manipulation utilities:
- arrays: array transformations, windowing, deduplication, rolling stats, matrix operations
- heaps: binary heap, min/max heap, priority queues, median finding
- queues_stacks: stack, monotonic stack, queue, circular queue, deque, min/max queue
- trees: binary tree, BST, AVL tree, segment tree, Fenwick tree (BIT), trie, traversal
- union_find: Disjoint Set Union (DSU) with path compression and union by rank/size
- hashing: hash map, hash set, bloom filter, consistent hashing, LRU/LFU cache helpers
"""

from __future__ import annotations

from . import arrays, hashing, heaps, queues_stacks, trees, union_find

__all__ = [
    "arrays",
    "hashing",
    "heaps",
    "queues_stacks",
    "trees",
    "union_find",
]
