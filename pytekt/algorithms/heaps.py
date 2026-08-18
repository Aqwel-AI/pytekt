"""Heap algorithms: heapify, priority-queue ops, and top-k problems."""

from __future__ import annotations

import heapq
from collections import Counter
from typing import Any, Callable, List, Optional, Tuple

from .catalog import register_algorithm


@register_algorithm(category="heaps", summary="Heapify a list in-place into a min-heap.")
def heapify_list(items: List[Any], key: Optional[Callable[[Any], Any]] = None) -> List[Any]:
    if key is None:
        heapq.heapify(items)
        return items
    wrapped = [(key(x), x) for x in items]
    heapq.heapify(wrapped)
    items[:] = [x for _, x in wrapped]
    return items


@register_algorithm(category="heaps", summary="Push item onto a min-heap list.")
def heappush_wrapper(heap: List[Any], item: Any) -> None:
    heapq.heappush(heap, item)


@register_algorithm(category="heaps", summary="Pop smallest item from a min-heap list.")
def heappop_wrapper(heap: List[Any]) -> Any:
    return heapq.heappop(heap)


@register_algorithm(category="heaps", summary="Push then pop; more efficient than separate push/pop.")
def heappushpop_wrapper(heap: List[Any], item: Any) -> Any:
    return heapq.heappushpop(heap, item)


@register_algorithm(category="heaps", summary="Pop smallest then push item onto heap.")
def heapreplace_wrapper(heap: List[Any], item: Any) -> Any:
    return heapq.heapreplace(heap, item)


@register_algorithm(category="heaps", summary="K largest elements from an iterable.")
def nlargest_k(items: List[Any], k: int, key: Optional[Callable[[Any], Any]] = None) -> List[Any]:
    if key is None:
        return heapq.nlargest(k, items)
    return heapq.nlargest(k, items, key=key)


@register_algorithm(category="heaps", summary="K smallest elements from an iterable.")
def nsmallest_k(items: List[Any], k: int, key: Optional[Callable[[Any], Any]] = None) -> List[Any]:
    if key is None:
        return heapq.nsmallest(k, items)
    return heapq.nsmallest(k, items, key=key)


@register_algorithm(category="heaps", summary="Merge k sorted lists into one sorted list.")
def merge_k_sorted_lists(lists: List[List[int]]) -> List[int]:
    heap: List[Tuple[int, int, int]] = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))
    result: List[int] = []
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        next_idx = elem_idx + 1
        if next_idx < len(lists[list_idx]):
            heapq.heappush(heap, (lists[list_idx][next_idx], list_idx, next_idx))
    return result


@register_algorithm(category="heaps", summary="Running median after each value using two heaps.")
def running_median(nums: List[int]) -> List[float]:
    lower: List[int] = []
    upper: List[int] = []
    medians: List[float] = []
    for num in nums:
        if not upper or num <= upper[0]:
            heapq.heappush(lower, -num)
        else:
            heapq.heappush(upper, num)
        if len(lower) > len(upper) + 1:
            heapq.heappush(upper, -heapq.heappop(lower))
        elif len(upper) > len(lower):
            heapq.heappush(lower, -heapq.heappop(upper))
        if len(lower) == len(upper):
            medians.append((upper[0] - lower[0]) / 2)
        else:
            medians.append(float(-lower[0]))
    return medians


@register_algorithm(category="heaps", summary="Top k most frequent elements.")
def top_k_frequent(nums: List[int], k: int) -> List[int]:
    counts = Counter(nums)
    return [item for item, _ in heapq.nlargest(k, counts.items(), key=lambda x: x[1])]


@register_algorithm(category="heaps", summary="Kth largest element in an unsorted array.")
def kth_largest(nums: List[int], k: int) -> int:
    heap = nums[:k]
    heapq.heapify(heap)
    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)
    return heap[0]


@register_algorithm(category="heaps", summary="Build max-heap representation from a list.")
def build_max_heap(nums: List[int]) -> List[int]:
    heap = [-x for x in nums]
    heapq.heapify(heap)
    return heap


@register_algorithm(category="heaps", summary="Sort a list using heap sort (returns new sorted list).")
def heap_sort(nums: List[int]) -> List[int]:
    heap = nums[:]
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(len(heap))]


@register_algorithm(category="heaps", summary="Check if a list satisfies the min-heap property.")
def is_min_heap(nums: List[int]) -> bool:
    n = len(nums)
    for i in range(n):
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and nums[left] < nums[i]:
            return False
        if right < n and nums[right] < nums[i]:
            return False
    return True


@register_algorithm(category="heaps", summary="Sift down at index in a min-heap array representation.")
def sift_down(nums: List[int], start: int, end: int) -> None:
    root = start
    while True:
        child = 2 * root + 1
        if child > end:
            break
        if child + 1 <= end and nums[child + 1] < nums[child]:
            child += 1
        if nums[root] <= nums[child]:
            break
        nums[root], nums[child] = nums[child], nums[root]
        root = child


@register_algorithm(category="heaps", summary="Sift up at index in a min-heap array representation.")
def sift_up(nums: List[int], index: int) -> None:
    while index > 0:
        parent = (index - 1) // 2
        if nums[index] >= nums[parent]:
            break
        nums[index], nums[parent] = nums[parent], nums[index]
        index = parent


@register_algorithm(category="heaps", summary="Last stone weight after repeated smash (max-heap).")
def last_stone_weight(stones: List[int]) -> int:
    heap = [-s for s in stones]
    heapq.heapify(heap)
    while len(heap) > 1:
        first = -heapq.heappop(heap)
        second = -heapq.heappop(heap)
        if first != second:
            heapq.heappush(heap, -(first - second))
    return -heap[0] if heap else 0


@register_algorithm(category="heaps", summary="Minimum idle intervals to schedule tasks with cooldown.")
def schedule_tasks(tasks: List[str], n: int) -> int:
    counts = Counter(tasks)
    max_count = max(counts.values())
    max_count_tasks = sum(1 for c in counts.values() if c == max_count)
    return max(len(tasks), (max_count - 1) * (n + 1) + max_count_tasks)


@register_algorithm(category="heaps", summary="Reorganize string so no two adjacent chars are equal.")
def reorganize_string(s: str) -> str:
    counts = Counter(s)
    max_heap: List[Tuple[int, str]] = [(-cnt, ch) for ch, cnt in counts.items()]
    heapq.heapify(max_heap)
    result: List[str] = []
    prev_count = 0
    prev_char = ""
    while max_heap:
        count, ch = heapq.heappop(max_heap)
        result.append(ch)
        if prev_count:
            heapq.heappush(max_heap, (prev_count, prev_char))
        prev_count = count + 1
        prev_char = ch
    return "".join(result) if len(result) == len(s) else ""


@register_algorithm(category="heaps", summary="K closest points to origin using a max-heap of size k.")
def k_closest_points(points: List[Tuple[int, int]], k: int) -> List[Tuple[int, int]]:
    def dist_sq(p: Tuple[int, int]) -> int:
        return p[0] * p[0] + p[1] * p[1]

    heap: List[Tuple[int, Tuple[int, int]]] = []
    for p in points:
        d = dist_sq(p)
        if len(heap) < k:
            heapq.heappush(heap, (-d, p))
        elif d < -heap[0][0]:
            heapq.heapreplace(heap, (-d, p))
    return [p for _, p in heap]
