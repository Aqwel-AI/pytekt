"""
Algorithmic Paradigms & Techniques Subpackage
============================================

Provides classical algorithm design techniques and problem-solving patterns:
- dynamic_programming: 0/1 knapsack, LCS, LIS, edit distance, matrix chain, coin change, interval DP, bitmask DP
- greedy: activity selection, fractional knapsack, interval scheduling, Huffman coding, gas station
- backtracking: N-queens, Sudoku solver, subsets, permutations, combinations, word search, subset sum
- sliding_window: maximum sum subarray, longest substring without repeats, min window substring
- two_pointers: 2-sum sorted, 3-sum, container with most water, trapping rain water, remove duplicates
- bit_manipulation: single number, count set bits, power of two, bitmask subsets, reverse bits
"""

from __future__ import annotations

from . import (
    backtracking,
    bit_manipulation,
    dynamic_programming,
    greedy,
    sliding_window,
    two_pointers,
)

__all__ = [
    "backtracking",
    "bit_manipulation",
    "dynamic_programming",
    "greedy",
    "sliding_window",
    "two_pointers",
]
