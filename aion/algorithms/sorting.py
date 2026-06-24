"""Sorting algorithms for educational and research use."""

from __future__ import annotations

import math
import random
from typing import List, Optional, TypeVar

from .catalog import register_algorithm

T = TypeVar("T")


def _copy(arr: List[T]) -> List[T]:
    return list(arr)


@register_algorithm(category="sorting", summary="Exchange adjacent out-of-order pairs until sorted.")
def bubble_sort(arr: List[T]) -> List[T]:
    """Sort by repeatedly bubbling the largest element to the end."""
    a = _copy(arr)
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


@register_algorithm(category="sorting", summary="Repeatedly select the minimum and place it at the front.")
def selection_sort(arr: List[T]) -> List[T]:
    """Sort by selecting the minimum remaining element each pass."""
    a = _copy(arr)
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a


@register_algorithm(category="sorting", summary="Build a sorted prefix by inserting each next element.")
def insertion_sort(arr: List[T]) -> List[T]:
    """Sort by inserting each element into the sorted prefix."""
    a = _copy(arr)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def _merge(left: List[T], right: List[T]) -> List[T]:
    result: List[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def _merge_sort_rec(a: List[T]) -> List[T]:
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    return _merge(_merge_sort_rec(a[:mid]), _merge_sort_rec(a[mid:]))


@register_algorithm(category="sorting", summary="Divide the list in half, sort halves, then merge.")
def merge_sort(arr: List[T]) -> List[T]:
    """Stable divide-and-conquer merge sort."""
    return _merge_sort_rec(_copy(arr))


@register_algorithm(category="sorting", summary="Partition around a pivot and recurse on subarrays.")
def quick_sort(arr: List[T]) -> List[T]:
    """Classic Lomuto-style quicksort on a copied list."""
    a = _copy(arr)
    if len(a) <= 1:
        return a

    def _qs(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        _qs(lo, i - 1)
        _qs(i + 1, hi)

    _qs(0, len(a) - 1)
    return a


def _heapify(a: List[T], n: int, i: int) -> None:
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2
    if left < n and a[left] > a[largest]:
        largest = left
    if right < n and a[right] > a[largest]:
        largest = right
    if largest != i:
        a[i], a[largest] = a[largest], a[i]
        _heapify(a, n, largest)


@register_algorithm(category="sorting", summary="Build a max-heap and extract elements in descending order.")
def heap_sort(arr: List[T]) -> List[T]:
    """In-place heap sort on a copy."""
    a = _copy(arr)
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        _heapify(a, n, i)
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        _heapify(a, i, 0)
    return a


@register_algorithm(category="sorting", summary="Insertion sort with diminishing gap sequences (Shell gaps).")
def shell_sort(arr: List[T]) -> List[T]:
    """Shell sort using Knuth gap sequence."""
    a = _copy(arr)
    n = len(a)
    gap = 1
    while gap < n // 3:
        gap = gap * 3 + 1
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                j -= gap
            a[j] = temp
        gap //= 3
    return a


@register_algorithm(category="sorting", summary="Count occurrences of integer keys in a bounded range.")
def counting_sort(arr: List[int]) -> List[int]:
    """Non-comparison sort for integers in a modest value range."""
    if not arr:
        return []
    mn, mx = min(arr), max(arr)
    offset = mn
    counts = [0] * (mx - mn + 1)
    for x in arr:
        counts[x - offset] += 1
    out: List[int] = []
    for i, c in enumerate(counts):
        out.extend([i + offset] * c)
    return out


@register_algorithm(category="sorting", summary="Sort integers digit by digit using stable bucket passes.")
def radix_sort(arr: List[int]) -> List[int]:
    """Least-significant-digit radix sort for non-negative integers."""
    if not arr:
        return []
    a = _copy(arr)
    if min(a) < 0:
        raise ValueError("radix_sort expects non-negative integers")
    max_val = max(a)
    exp = 1
    while max_val // exp > 0:
        buckets: List[List[int]] = [[] for _ in range(10)]
        for x in a:
            buckets[(x // exp) % 10].append(x)
        a = [x for bucket in buckets for x in bucket]
        exp *= 10
    return a


@register_algorithm(category="sorting", summary="Distribute values into buckets, sort buckets, then concatenate.")
def bucket_sort(arr: List[float]) -> List[float]:
    """Bucket sort for floats in [0, 1); other values are scaled heuristically."""
    if not arr:
        return []
    a = _copy(arr)
    mn, mx = min(a), max(a)
    if mn == mx:
        return a
    num_buckets = max(1, len(a))
    buckets: List[List[float]] = [[] for _ in range(num_buckets)]
    span = mx - mn
    for x in a:
        idx = min(num_buckets - 1, int((x - mn) / span * num_buckets))
        buckets[idx].append(x)
    out: List[float] = []
    for bucket in buckets:
        out.extend(insertion_sort(bucket))
    return out


@register_algorithm(category="sorting", summary="Bidirectional bubble sort sweeping from both ends.")
def cocktail_sort(arr: List[T]) -> List[T]:
    """Cocktail shaker sort."""
    a = _copy(arr)
    lo, hi = 0, len(a) - 1
    while lo < hi:
        swapped = False
        for i in range(lo, hi):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
        if not swapped:
            break
        hi -= 1
        swapped = False
        for i in range(hi, lo, -1):
            if a[i] < a[i - 1]:
                a[i], a[i - 1] = a[i - 1], a[i]
                swapped = True
        if not swapped:
            break
        lo += 1
    return a


@register_algorithm(category="sorting", summary="Bubble sort with a shrinking gap factor (1.3).")
def comb_sort(arr: List[T]) -> List[T]:
    """Comb sort with gap shrink factor 1.3."""
    a = _copy(arr)
    n = len(a)
    gap = n
    shrink = 1.3
    sorted_flag = False
    while not sorted_flag:
        gap = max(1, int(gap / shrink))
        sorted_flag = True
        for i in range(n - gap):
            if a[i] > a[i + gap]:
                a[i], a[i + gap] = a[i + gap], a[i]
                sorted_flag = False
    return a


@register_algorithm(category="sorting", summary="Walk forward swapping like a garden gnome stepping back.")
def gnome_sort(arr: List[T]) -> List[T]:
    """Gnome sort (stupid sort)."""
    a = _copy(arr)
    i = 1
    while i < len(a):
        if a[i] >= a[i - 1]:
            i += 1
        else:
            a[i], a[i - 1] = a[i - 1], a[i]
            i = max(1, i - 1)
    return a


@register_algorithm(category="sorting", summary="Minimize writes by placing each element in its cycle.")
def cycle_sort(arr: List[T]) -> List[T]:
    """Cycle sort minimizing element writes."""
    a = _copy(arr)
    for start in range(len(a) - 1):
        item = a[start]
        pos = start
        for i in range(start + 1, len(a)):
            if a[i] < item:
                pos += 1
        if pos == start:
            continue
        while item == a[pos]:
            pos += 1
        a[pos], item = item, a[pos]
        while pos != start:
            pos = start
            for i in range(start + 1, len(a)):
                if a[i] < item:
                    pos += 1
            while item == a[pos]:
                pos += 1
            a[pos], item = item, a[pos]
    return a


def _flip(a: List[T], k: int) -> None:
    a[: k + 1] = reversed(a[: k + 1])


@register_algorithm(category="sorting", summary="Sort by flipping prefixes to move maxima into place.")
def pancake_sort(arr: List[T]) -> List[T]:
    """Pancake sort using prefix reversals."""
    a = _copy(arr)
    for size in range(len(a), 1, -1):
        max_idx = max(range(size), key=lambda i: a[i])
        if max_idx != size - 1:
            if max_idx != 0:
                _flip(a, max_idx)
            _flip(a, size - 1)
    return a


@register_algorithm(category="sorting", summary="Recursive exchange sort with three-way recursive calls.")
def stooge_sort(arr: List[T]) -> List[T]:
    """Stooge sort recursive variant."""
    a = _copy(arr)

    def _stooge(lo: int, hi: int) -> None:
        if a[lo] > a[hi]:
            a[lo], a[hi] = a[hi], a[lo]
        if hi - lo + 1 > 2:
            third = (hi - lo + 1) // 3
            _stooge(lo, hi - third)
            _stooge(lo + third, hi)
            _stooge(lo, hi - third)

    if a:
        _stooge(0, len(a) - 1)
    return a


@register_algorithm(category="sorting", summary="Randomly shuffle until sorted, stopping after max_iter.")
def bogo_sort(arr: List[T], max_iter: int = 10000) -> List[T]:
    """Bogosort with iteration guard to avoid infinite loops."""
    a = _copy(arr)
    if len(a) <= 1:
        return a
    for _ in range(max_iter):
        if all(a[i] <= a[i + 1] for i in range(len(a) - 1)):
            return a
        random.shuffle(a)
    raise RuntimeError(f"bogo_sort did not converge within {max_iter} iterations")


def _calc_min_run(n: int) -> int:
    r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r


@register_algorithm(category="sorting", summary="TimSort-style stable sort with min-runs and galloping merge.")
def tim_sort(arr: List[T]) -> List[T]:
    """Simplified TimSort using natural runs and merge."""
    a = _copy(arr)
    n = len(a)
    if n <= 1:
        return a
    min_run = max(_calc_min_run(n), 1)
    runs: List[List[T]] = []
    i = 0
    while i < n:
        end = min(i + min_run, n)
        run = a[i:end]
        runs.append(insertion_sort(run))
        i = end

    while len(runs) > 1:
        merged: List[List[T]] = []
        j = 0
        while j < len(runs):
            if j + 1 < len(runs):
                merged.append(_merge(runs[j], runs[j + 1]))
                j += 2
            else:
                merged.append(runs[j])
                j += 1
        runs = merged
    return runs[0]


@register_algorithm(category="sorting", summary="Introspective quicksort falling back to heapsort on deep recursion.")
def intro_sort(arr: List[T]) -> List[T]:
    """IntroSort: quicksort with depth limit and heap sort fallback."""
    a = _copy(arr)
    max_depth = 2 * int(math.log2(len(a))) if len(a) > 1 else 0

    def _partition(lo: int, hi: int) -> int:
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        return i

    def _heap_sort_range(lo: int, hi: int) -> None:
        sub = a[lo : hi + 1]
        sorted_sub = heap_sort(sub)
        a[lo : hi + 1] = sorted_sub

    def _is(lo: int, hi: int, depth: int) -> None:
        size = hi - lo + 1
        if size <= 1:
            return
        if depth == 0:
            _heap_sort_range(lo, hi)
            return
        p = _partition(lo, hi)
        _is(lo, p - 1, depth - 1)
        _is(p + 1, hi, depth - 1)

    if a:
        _is(0, len(a) - 1, max_depth)
    return a


@register_algorithm(category="sorting", summary="Quicksort with two pivots partitioning into three segments.")
def dual_pivot_quick_sort(arr: List[T]) -> List[T]:
    """Dual-pivot quicksort (Yaroslavskiy style)."""
    a = _copy(arr)

    def _sort(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        if a[lo] > a[hi]:
            a[lo], a[hi] = a[hi], a[lo]
        p, q = a[lo], a[hi]
        lt = lo + 1
        gt = hi - 1
        i = lt
        while i <= gt:
            if a[i] < p:
                a[i], a[lt] = a[lt], a[i]
                lt += 1
                i += 1
            elif a[i] > q:
                a[i], a[gt] = a[gt], a[i]
                gt -= 1
            else:
                i += 1
        a[lo], a[lt - 1] = a[lt - 1], a[lo]
        a[hi], a[gt + 1] = a[gt + 1], a[hi]
        _sort(lo, lt - 2)
        _sort(lt, gt)
        _sort(gt + 2, hi)

    if a:
        _sort(0, len(a) - 1)
    return a


@register_algorithm(category="sorting", summary="Dutch-national-flag quicksort for inputs with many duplicates.")
def three_way_quick_sort(arr: List[T]) -> List[T]:
    """Three-way partitioning quicksort."""
    a = _copy(arr)

    def _sort(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        pivot = a[lo + (hi - lo) // 2]
        lt = lo
        i = lo
        gt = hi
        while i <= gt:
            if a[i] < pivot:
                a[lt], a[i] = a[i], a[lt]
                lt += 1
                i += 1
            elif a[i] > pivot:
                a[i], a[gt] = a[gt], a[i]
                gt -= 1
            else:
                i += 1
        _sort(lo, lt - 1)
        _sort(gt + 1, hi)

    if a:
        _sort(0, len(a) - 1)
    return a


@register_algorithm(category="sorting", summary="Parallel-style odd-even transposition sort on a list.")
def odd_even_sort(arr: List[T]) -> List[T]:
    """Odd-even transposition sort."""
    a = _copy(arr)
    n = len(a)
    if n < 2:
        return a
    sorted_flag = False
    while not sorted_flag:
        sorted_flag = True
        for i in range(1, n - 1, 2):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                sorted_flag = False
        for i in range(0, n - 1, 2):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                sorted_flag = False
    return a


def _bitonic_merge(a: List[T], lo: int, cnt: int, direction: bool) -> None:
    if cnt <= 1:
        return
    k = cnt // 2
    for i in range(lo, lo + k):
        if (a[i] > a[i + k]) == direction:
            a[i], a[i + k] = a[i + k], a[i]
    _bitonic_merge(a, lo, k, True)
    _bitonic_merge(a, lo + k, k, False)
    _bitonic_merge(a, lo, cnt, True)


def _bitonic_sort_rec(a: List[T], lo: int, cnt: int, direction: bool) -> None:
    if cnt <= 1:
        return
    k = cnt // 2
    _bitonic_sort_rec(a, lo, k, True)
    _bitonic_sort_rec(a, lo + k, k, False)
    _bitonic_merge(a, lo, cnt, direction)


@register_algorithm(category="sorting", summary="Recursive bitonic merge network sort.")
def bitonic_sort(arr: List[T]) -> List[T]:
    """Bitonic sort for sequences whose length is a power of two."""
    a = _copy(arr)
    n = len(a)
    if n == 0 or (n & (n - 1)) != 0:
        raise ValueError("bitonic_sort requires length to be a power of two")
    _bitonic_sort_rec(a, 0, n, True)
    return a


@register_algorithm(category="sorting", summary="Like counting sort using pigeonhole indices for bounded ints.")
def pigeonhole_sort(arr: List[int]) -> List[int]:
    """Pigeonhole sort for integers in a compact range."""
    return counting_sort(arr)


@register_algorithm(category="sorting", summary="Distribution sort moving elements toward clustered positions.")
def flash_sort(arr: List[float]) -> List[float]:
    """Flash sort for uniformly distributed floats."""
    a = _copy(arr)
    n = len(a)
    if n <= 1:
        return a
    mn, mx = min(a), max(a)
    if mn == mx:
        return a
    num_classes = max(2, int(0.45 * n))
    class_min = [0] * num_classes
    count = [0] * num_classes
    for x in a:
        k = min(num_classes - 1, int((x - mn) / (mx - mn) * (num_classes - 1)))
        count[k] += 1
    for i in range(1, num_classes):
        count[i] += count[i - 1]
    for i in range(num_classes - 1, 0, -1):
        class_min[i] = count[i - 1]
    output: List[float] = [0.0] * n
    for x in a:
        k = min(num_classes - 1, int((x - mn) / (mx - mn) * (num_classes - 1)))
        output[class_min[k]] = x
        class_min[k] += 1
    start = 0
    for c in count:
        output[start:c] = insertion_sort(output[start:c])
        start = c
    return output


@register_algorithm(category="sorting", summary="Placeholder spreadsort using bucket distribution and merge.")
def spread_sort(arr: List[T]) -> List[T]:
    """Simplified spreadsort placeholder via range bucketing."""
    if len(arr) <= 1:
        return _copy(arr)
    a = _copy(arr)
    mn, mx = min(a), max(a)
    if mn == mx:
        return a
    num_buckets = max(2, int(math.sqrt(len(a))))
    buckets: List[List[T]] = [[] for _ in range(num_buckets)]
    span = mx - mn if mx != mn else 1
    for x in a:
        idx = min(num_buckets - 1, int((x - mn) / span * num_buckets))
        buckets[idx].append(x)
    out: List[T] = []
    for bucket in buckets:
        out.extend(merge_sort(bucket))
    return out


class _BSTNode:
    __slots__ = ("value", "left", "right")

    def __init__(self, value: T) -> None:
        self.value = value
        self.left: Optional[_BSTNode] = None
        self.right: Optional[_BSTNode] = None


def _bst_insert(root: Optional[_BSTNode], value: T) -> _BSTNode:
    if root is None:
        return _BSTNode(value)
    if value < root.value:
        root.left = _bst_insert(root.left, value)
    else:
        root.right = _bst_insert(root.right, value)
    return root


def _bst_inorder(node: Optional[_BSTNode], out: List[T]) -> None:
    if node is None:
        return
    _bst_inorder(node.left, out)
    out.append(node.value)
    _bst_inorder(node.right, out)


@register_algorithm(category="sorting", summary="Insert elements into a BST and emit in-order traversal.")
def tree_sort(arr: List[T]) -> List[T]:
    """Tree sort using binary search tree insertion."""
    root: Optional[_BSTNode] = None
    for x in arr:
        root = _bst_insert(root, x)
    out: List[T] = []
    _bst_inorder(root, out)
    return out


@register_algorithm(category="sorting", summary="Extract sorted runs from the input and merge them.")
def strand_sort(arr: List[T]) -> List[T]:
    """Strand sort building ascending runs then merging."""
    if not arr:
        return []
    a = _copy(arr)
    runs: List[List[T]] = []
    while a:
        run = [a.pop(0)]
        i = 0
        while i < len(a):
            if a[i] >= run[-1]:
                run.append(a.pop(i))
            else:
                i += 1
        runs.append(run)
    result: List[T] = []
    while len(runs) > 1:
        merged: List[List[T]] = []
        i = 0
        while i < len(runs):
            if i + 1 < len(runs):
                merged.append(_merge(runs[i], runs[i + 1]))
                i += 2
            else:
                merged.append(runs[i])
                i += 1
        runs = merged
    return runs[0] if runs else []


@register_algorithm(category="sorting", summary="Simplified smoothsort using a gap-based shell-like pass.")
def smooth_sort(arr: List[T]) -> List[T]:
    """Simplified smoothsort using Leonardo-gap inspired shell passes."""
    a = _copy(arr)
    n = len(a)
    gaps = [1, 4, 10, 23, 57, 132, 301, 701]
    gaps = [g for g in gaps if g < n]
    for gap in reversed(gaps):
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                j -= gap
            a[j] = temp
    return a


@register_algorithm(category="sorting", summary="American flag sort for bounded integers via counting passes.")
def american_flag_sort(arr: List[int]) -> List[int]:
    """American flag sort for non-negative integers in a modest range."""
    if not arr:
        return []
    if min(arr) < 0:
        raise ValueError("american_flag_sort expects non-negative integers")
    return counting_sort(arr)


@register_algorithm(category="sorting", summary="Insertion sort using binary search to find insert position.")
def binary_insertion_sort(arr: List[T]) -> List[T]:
    """Binary insertion sort."""
    a = _copy(arr)
    for i in range(1, len(a)):
        key = a[i]
        lo, hi = 0, i
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] > key:
                hi = mid
            else:
                lo = mid + 1
        a[lo + 1 : i + 1] = a[lo:i]
        a[lo] = key
    return a


@register_algorithm(category="sorting", summary="Bubble sort implemented recursively on the tail.")
def recursive_bubble_sort(arr: List[T]) -> List[T]:
    """Recursive bubble sort."""
    a = _copy(arr)
    n = len(a)

    def _bubble(end: int) -> None:
        if end <= 1:
            return
        for i in range(end - 1):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
        _bubble(end - 1)

    _bubble(n)
    return a


@register_algorithm(category="sorting", summary="Bottom-up iterative merge sort without recursion.")
def iterative_merge_sort(arr: List[T]) -> List[T]:
    """Iterative merge sort using doubling window sizes."""
    a = _copy(arr)
    n = len(a)
    if n <= 1:
        return a
    width = 1
    while width < n:
        for start in range(0, n, 2 * width):
            mid = min(start + width, n)
            end = min(start + 2 * width, n)
            left = a[start:mid]
            right = a[mid:end]
            merged = _merge(left, right)
            a[start:end] = merged
        width *= 2
    return a


def _rotate(a: List[T], lo: int, mid: int, hi: int) -> None:
    a[lo:hi] = a[mid:hi] + a[lo:mid]


@register_algorithm(category="sorting", summary="In-place merge sort using rotations on subranges.")
def in_place_merge_sort(arr: List[T]) -> List[T]:
    """In-place merge sort via rotate-based merging."""
    a = _copy(arr)

    def _sort(lo: int, hi: int) -> None:
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        _sort(lo, mid)
        _sort(mid, hi)
        if a[mid - 1] <= a[mid]:
            return
        i, j = lo, mid
        while i < j and j < hi:
            if a[i] <= a[j]:
                i += 1
            else:
                k = j
                while k < hi and a[k] < a[i]:
                    k += 1
                _rotate(a, i, j, k)
                j = k

    _sort(0, len(a))
    return a


@register_algorithm(category="sorting", summary="Simplified block sort merging fixed-size sorted blocks.")
def block_sort(arr: List[T]) -> List[T]:
    """Simplified block sort using fixed-size insertion-sorted blocks."""
    a = _copy(arr)
    n = len(a)
    if n <= 1:
        return a
    block = max(1, int(math.sqrt(n)))
    for start in range(0, n, block):
        end = min(start + block, n)
        chunk = insertion_sort(a[start:end])
        a[start:end] = chunk
    width = block
    while width < n:
        for start in range(0, n, 2 * width):
            mid = min(start + width, n)
            end = min(start + 2 * width, n)
            a[start:end] = _merge(a[start:mid], a[mid:end])
        width *= 2
    return a