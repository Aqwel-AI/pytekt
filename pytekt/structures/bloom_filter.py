"""Bloom filter for probabilistic membership testing."""

from __future__ import annotations

import hashlib
import math
from typing import Iterable


class BloomFilter:
    """
    Space-efficient probabilistic set. Supports ``add`` and ``might_contain``
    (no false negatives, tunable false-positive rate).

    Parameters
    ----------
    expected_items : int
        Anticipated number of items.
    fp_rate : float
        Desired false-positive rate (default 1 %).
    """

    def __init__(self, expected_items: int = 10_000, fp_rate: float = 0.01) -> None:
        self._n = expected_items
        self._fp = fp_rate
        self._size = self._optimal_size(expected_items, fp_rate)
        self._hashes = self._optimal_hashes(self._size, expected_items)
        self._bits = bytearray(math.ceil(self._size / 8))
        self._count = 0

    @staticmethod
    def _optimal_size(n: int, p: float) -> int:
        return max(1, int(-n * math.log(p) / (math.log(2) ** 2)))

    @staticmethod
    def _optimal_hashes(m: int, n: int) -> int:
        return max(1, int((m / max(n, 1)) * math.log(2)))

    def _get_indices(self, item: str) -> list[int]:
        h1 = int(hashlib.md5(item.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha1(item.encode()).hexdigest(), 16)
        return [(h1 + i * h2) % self._size for i in range(self._hashes)]

    def add(self, item: str) -> None:
        for idx in self._get_indices(item):
            self._bits[idx // 8] |= 1 << (idx % 8)
        self._count += 1

    def add_all(self, items: Iterable[str]) -> None:
        for item in items:
            self.add(item)

    def might_contain(self, item: str) -> bool:
        """``True`` if *item* is probably in the set (never false negatives)."""
        return all(
            self._bits[idx // 8] & (1 << (idx % 8))
            for idx in self._get_indices(item)
        )

    def __contains__(self, item: str) -> bool:
        return self.might_contain(item)

    @property
    def count(self) -> int:
        return self._count

    @property
    def estimated_fp_rate(self) -> float:
        """Current estimated false-positive rate given items inserted so far."""
        if self._count == 0:
            return 0.0
        return (1 - math.exp(-self._hashes * self._count / self._size)) ** self._hashes
