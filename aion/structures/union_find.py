"""Disjoint-set / Union-Find with path compression and union by rank."""

from __future__ import annotations

from typing import Dict, Generic, Hashable, List, Set, TypeVar

T = TypeVar("T", bound=Hashable)


class UnionFind(Generic[T]):
    """
    Union-Find (disjoint-set) with path compression and union by rank.

    Supports ``union``, ``find``, ``connected``, and enumeration of
    connected components. Amortized near-O(1) per operation.
    """

    def __init__(self) -> None:
        self._parent: Dict[T, T] = {}
        self._rank: Dict[T, int] = {}

    def _ensure(self, x: T) -> None:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0

    def find(self, x: T) -> T:
        """Return the root representative of the set containing *x*."""
        self._ensure(x)
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]
            x = self._parent[x]
        return x

    def union(self, x: T, y: T) -> bool:
        """Merge the sets containing *x* and *y*. Returns ``False`` if already same set."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1
        return True

    def connected(self, x: T, y: T) -> bool:
        return self.find(x) == self.find(y)

    def components(self) -> List[Set[T]]:
        """Return all disjoint sets as a list of sets."""
        groups: Dict[T, Set[T]] = {}
        for item in self._parent:
            root = self.find(item)
            groups.setdefault(root, set()).add(item)
        return list(groups.values())

    @property
    def num_components(self) -> int:
        return len({self.find(x) for x in self._parent})

    def __len__(self) -> int:
        return len(self._parent)

    def __contains__(self, x: T) -> bool:
        return x in self._parent
