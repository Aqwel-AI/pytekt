"""Bounded LRU (Least Recently Used) cache with O(1) get/set."""

from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Any, Generic, Hashable, Iterator, Optional, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    """
    Thread-safe LRU cache backed by ``OrderedDict``.

    Parameters
    ----------
    capacity : int
        Maximum number of items. Oldest item is evicted on overflow.
    """

    def __init__(self, capacity: int = 128) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._capacity = capacity
        self._store: OrderedDict[K, V] = OrderedDict()
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
                self.hits += 1
                return self._store[key]
            self.misses += 1
            return default

    def set(self, key: K, value: V) -> None:
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
                self._store[key] = value
            else:
                if len(self._store) >= self._capacity:
                    self._store.popitem(last=False)
                self._store[key] = value

    def delete(self, key: K) -> bool:
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self.hits = 0
            self.misses = 0

    def peek(self, key: K) -> Optional[V]:
        """Get value without promoting the key."""
        with self._lock:
            return self._store.get(key)

    def __contains__(self, key: K) -> bool:
        return key in self._store

    def __len__(self) -> int:
        return len(self._store)

    def __iter__(self) -> Iterator[K]:
        return iter(self._store)

    def __getitem__(self, key: K) -> V:
        val = self.get(key)
        if val is None and key not in self._store:
            raise KeyError(key)
        return val  # type: ignore[return-value]

    def __setitem__(self, key: K, value: V) -> None:
        self.set(key, value)

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0
