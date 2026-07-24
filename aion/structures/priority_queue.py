"""Heap-based priority queues (min-heap, max-heap, generic priority queue)."""

from __future__ import annotations

import heapq
from typing import Any, Generic, Iterator, List, Optional, Tuple, TypeVar

T = TypeVar("T")


class MinHeap(Generic[T]):
    """Min-heap: smallest element is popped first."""

    def __init__(self) -> None:
        self._data: List[T] = []

    def push(self, item: T) -> None:
        heapq.heappush(self._data, item)

    def pop(self) -> T:
        if not self._data:
            raise IndexError("pop from empty heap")
        return heapq.heappop(self._data)

    def peek(self) -> T:
        if not self._data:
            raise IndexError("peek at empty heap")
        return self._data[0]

    def pushpop(self, item: T) -> T:
        return heapq.heappushpop(self._data, item)

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(sorted(self._data))


class MaxHeap(Generic[T]):
    """Max-heap: largest element is popped first (negated min-heap)."""

    def __init__(self) -> None:
        self._data: List[Any] = []

    def push(self, item: T) -> None:
        heapq.heappush(self._data, _Negated(item))

    def pop(self) -> T:
        if not self._data:
            raise IndexError("pop from empty heap")
        return heapq.heappop(self._data).val

    def peek(self) -> T:
        if not self._data:
            raise IndexError("peek at empty heap")
        return self._data[0].val

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)


class _Negated:
    __slots__ = ("val",)

    def __init__(self, val: Any) -> None:
        self.val = val

    def __lt__(self, other: _Negated) -> bool:
        return self.val > other.val

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Negated):
            return self.val == other.val
        return NotImplemented

    def __le__(self, other: _Negated) -> bool:
        return self.val >= other.val


class PriorityQueue(Generic[T]):
    """
    Priority queue with ``(priority, item)`` pairs. Lower priority = higher urgency.
    Supports ``push``, ``pop``, ``peek``, and iteration.
    """

    def __init__(self) -> None:
        self._data: List[Tuple[float, int, T]] = []
        self._counter = 0

    def push(self, item: T, priority: float = 0.0) -> None:
        heapq.heappush(self._data, (priority, self._counter, item))
        self._counter += 1

    def pop(self) -> Tuple[float, T]:
        """Return ``(priority, item)``."""
        if not self._data:
            raise IndexError("pop from empty priority queue")
        pri, _, item = heapq.heappop(self._data)
        return pri, item

    def peek(self) -> Tuple[float, T]:
        if not self._data:
            raise IndexError("peek at empty priority queue")
        pri, _, item = self._data[0]
        return pri, item

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)
