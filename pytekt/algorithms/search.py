"""
Search Algorithms
=================

This module contains classical search algorithms used for locating elements
or traversal states within ordered sequences and discrete structures. The
implementations are designed for research and educational use, emphasizing
correctness, clarity, and predictable behavior.

Scope
-----
The algorithms in this module focus on:
- Searching within sorted sequences
- Boundary search operations (lower and upper bounds)
- Graph and state-space traversal where applicable

Design principles
-----------------
- Deterministic behavior under well-defined input assumptions
- Clear and readable implementations suitable for inspection and study
- Minimal abstraction to preserve algorithmic transparency
- Stable function interfaces intended for direct use in experiments

Intended usage
--------------
These search utilities are provided to reduce boilerplate in research code
while keeping standard search logic explicit and easy to reason about.

See also: aion/algorithms/README.md for full package documentation.
"""

from typing import List, Optional, TypeVar, Union, Tuple, Dict, Callable
import math
import random
from collections import deque

T = TypeVar("T")


def binary_search(arr: List[T], target: T) -> Optional[int]:
    """
    Perform binary search on a sorted sequence.

    This function searches for a target value in a sorted list using
    the binary search algorithm. If the target is found, its index is
    returned. If the target is not present, None is returned.

    Parameters
    ----------
    arr : List[T]
        A list of elements sorted in ascending order.
    target : T
        The value to search for.

    Returns
    -------
    Optional[int]
        The index of the target if found, otherwise None.

    Notes
    -----
    - The input list must be sorted in ascending order.
    - The algorithm runs in O(log n) time complexity.
    """

    # Initialize search boundaries
    left, right = 0, len(arr) - 1

    # Continue searching while the interval is valid
    while left <= right:
        # Compute middle index
        mid = (left + right) // 2

        # Check if the middle element is the target
        if arr[mid] == target:
            return mid

        # If target is greater, ignore the left half
        elif arr[mid] < target:
            left = mid + 1

        # If target is smaller, ignore the right half
        else:
            right = mid - 1

    # Target not found
    return None


def lower_bound(arr: List[T], target: T) -> int:
    """
    Find the first index at which `target` can be inserted in a sorted list.

    This function returns the index of the first element in `arr` that is
    greater than or equal to `target`. If all elements in the list are less
    than `target`, the function returns the length of the list.

    Parameters
    ----------
    arr : List[T]
        A list of elements sorted in ascending order.
    target : T
        The value to locate.

    Returns
    -------
    int
        The index of the first position where `target` can be inserted
        without violating the sort order.

    Notes
    -----
    - The input list must be sorted in ascending order.
    - The algorithm runs in O(log n) time complexity.
    - This function does not check for the presence of `target`; it only
      determines the insertion position.
    """

    # Initialize the search interval [left, right)
    left = 0
    right = len(arr)

    # Continue until the search space is empty
    while left < right:
        # Compute middle index
        mid = (left + right) // 2

        # If middle element is less than target,
        # narrow search to the right half
        if arr[mid] < target:
            left = mid + 1
        else:
            # Otherwise, target belongs to the left half
            right = mid

    # Left is the first index where arr[left] >= target
    return left


def upper_bound(arr: List[T], target: T) -> int:
    """
    Find the first index at which an element greater than `target` appears.

    This function returns the index of the first element in `arr` that is
    strictly greater than `target`. If no such element exists, the function
    returns the length of the list.

    Parameters
    ----------
    arr : List[T]
        A list of elements sorted in ascending order.
    target : T
        The value to locate.

    Returns
    -------
    int
        The index of the first position where an element greater than
        `target` can be found or inserted.

    Notes
    -----
    - The input list must be sorted in ascending order.
    - The algorithm runs in O(log n) time complexity.
    - This function is equivalent to C++ std::upper_bound.
    """

    # Initialize the search interval [left, right)
    left = 0
    right = len(arr)

    # Continue until the search space is empty
    while left < right:
        # Compute middle index
        mid = (left + right) // 2

        # If middle element is less than or equal to target,
        # narrow search to the right half
        if arr[mid] <= target:
            left = mid + 1
        else:
            # Otherwise, element greater than target is in the left half
            right = mid

    # Left is the first index where arr[left] > target
    return left


def is_sorted(ulist: List[T]) -> bool:
    """
    Check whether a list is sorted in ascending or descending order.

    The function performs a single pass to verify non-decreasing or
    non-increasing order without allocating sorted copies.

    Parameters
    ----------
    ulist : List[T]
        Input list to check.

    Returns
    -------
    bool
        True if the list is sorted ascending or descending, otherwise False.

    Raises
    ------
    TypeError
        If the input is not a list.
    """
    # Validate type
    if not isinstance(ulist, list):
        raise TypeError("Input must be a list")

    # Fast linear checks (O(n)) for ascending or descending order
    if len(ulist) < 2:
        return True

    ascending = True
    descending = True

    for i in range(1, len(ulist)):
        if ulist[i] < ulist[i - 1]:
            ascending = False
        if ulist[i] > ulist[i - 1]:
            descending = False
        if not ascending and not descending:
            return False

    return True
    
def jump_search(slist: List[T], step: int, target: T) -> Optional[int]:
    """
    Search for a target in a sorted list using jump search.

    The list is scanned in fixed-size jumps to find a block that may
    contain the target, then linearly searched within that block.

    Parameters
    ----------
    slist : List[T]
        Sorted list to search.
    step : int
        Jump size. Must be a positive integer.
    target : T
        Value to find in the list.

    Returns
    -------
    Optional[int]
        Index of the target if found, otherwise None.

    Raises
    ------
    TypeError
        If inputs are invalid types.
    ValueError
        If step is not a positive integer.
    """
    if not isinstance(slist, list):
        raise TypeError("Input must be a list")
    if not isinstance(step, int):
        raise TypeError("Step must be an integer")
    if step <= 0:
        raise ValueError("Step must be a positive integer")
    if not slist:
        return None

    # Find the block where target may be present
    n = len(slist)
    prev = 0
    curr = 0
    while curr < n and slist[curr] < target:
        prev = curr
        curr = min(curr + step, n - 1)
        if prev == curr:
            break

    # Linear search within the block
    for idx in range(prev, min(curr + 1, n)):
        if slist[idx] == target:
            return idx
        if slist[idx] > target:
            break

    return None

def find_all_peaks(ulist: List[T]) -> List[int]:
    """Find indices of all peak elements in a list. O(n)."""
    if not isinstance(ulist, list):
        raise TypeError("Input must be a list")
    n = len(ulist)
    if n == 0:
        return []
    if n == 1:
        return [0]
    
    result = []
    if ulist[0] > ulist[1]:
        result.append(0)
    for i in range(1, n - 1):
        if ulist[i-1] < ulist[i] > ulist[i+1]:
            result.append(i)
    if ulist[-1] > ulist[-2]:
        result.append(n - 1)
    return result
            

def exponential_search(slist: List[T], target: T) -> Optional[int]:
    """
    Search for a target in a sorted list using exponential search.

    The function expands the search range exponentially, then performs
    a binary search within that range.

    Parameters
    ----------
    slist : List[T]
        Sorted list to search.
    target : T
        Value to find in the list.

    Returns
    -------
    Optional[int]
        Index of the target if found, otherwise None.

    Raises
    ------
    TypeError
        If inputs are invalid types.
    """
    # Validate input
    if not isinstance(slist, list):
        raise TypeError("Input must be a list")

    # Handle empty list and first-element match
    if len(slist) == 0:
        return None
    if slist[0] == target:
        return 0

    # Find range where target could be
    i = 1
    while i < len(slist) and slist[i] < target:
        i *= 2
    low = i // 2
    high = min(i, len(slist) - 1)

    # Binary search within range
    while low <= high:
        mid = (low + high) // 2
        if slist[mid] == target:
            return mid
        if slist[mid] < target:
            low = mid + 1
        if slist[mid] > target:
            high = mid - 1

    return None


def linear_search(ulist: List[T], target: T) -> Optional[int]:
    """Basic sequential search. Returns index or None."""
    for i, x in enumerate(ulist):
        if x == target:
            return i
    return None

def first_occurrence(ulist: List[T], target: T) -> Optional[int]:
    """Find the first index of target in ulist."""
    return linear_search(ulist, target)
    
def last_occurrence(ulist: List[T], target: T) -> Optional[int]:
    """Find the last index of target in ulist."""
    for i in range(len(ulist) - 1, -1, -1):
        if ulist[i] == target:
            return i
    return None

def first_last_occurrence(ulist: List[T], target: T) -> Tuple[Optional[int], Optional[int]]:
    """Return (first_index, last_index) of target."""
    return first_occurrence(ulist, target), last_occurrence(ulist, target)

def rotated_search(ulist: List[T], target: T) -> Optional[int]:
    """Search for target in a rotated sorted list. O(log n)."""
    low, high = 0, len(ulist) - 1
    while low <= high:
        mid = (low + high) // 2
        if ulist[mid] == target:
            return mid
        if ulist[low] <= ulist[mid]:
            if ulist[low] <= target < ulist[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if ulist[mid] < target <= ulist[high]:
                low = mid + 1
            else:
                high = mid - 1
    return None


def ternary_search(slist: List[T], target: T) -> Optional[int]:
    """Divide-and-conquer search splitting list into three segments. O(log3 n)."""
    low, high = 0, len(slist) - 1
    while low <= high:
        m1 = low + (high - low) // 3
        m2 = high - (high - low) // 3
        if slist[m1] == target:
            return m1
        if slist[m2] == target:
            return m2
        if target < slist[m1]:
            high = m1 - 1
        elif target > slist[m2]:
            low = m2 + 1
        else:
            low, high = m1 + 1, m2 - 1
    return None

def interpolation_search(slist: List[Union[int, float]], target: Union[int, float]) -> Optional[int]:
    """Estimate position based on value distribution. O(log log n) for uniform data."""
    low, high = 0, len(slist) - 1
    while low <= high and slist[low] <= target <= slist[high]:
        if low == high:
            return low if slist[low] == target else None
        pos = low + int(((float(high - low) / (slist[high] - slist[low])) * (target - slist[low])))
        if slist[pos] == target:
            return pos
        if slist[pos] < target:
            low = pos + 1
        else:
            high = pos - 1
    return None


# --- Binary Search on Answer & Optimization ---

def integer_sqrt(n: int) -> int:
    """Find the floor of the square root of n using binary search. O(log n)."""
    if n < 0:
        raise ValueError("Negative input")
    if n < 2:
        return n
    low, high = 1, n // 2
    res = 1
    while low <= high:
        mid = (low + high) // 2
        if mid * mid == n:
            return mid
        if mid * mid < n:
            res = mid
            low = mid + 1
        else:
            high = mid - 1
    return res


def nth_root(n: int, r: int) -> int:
    """Find the floor of the r-th root of n using binary search. O(log n)."""
    if n < 0 and r % 2 == 0:
        raise ValueError("Even root of negative number")
    if n == 0:
        return 0
    if n == 1:
        return 1
    low, high = 1, n
    res = 1
    while low <= high:
        mid = (low + high) // 2
        if pow(mid, r) <= n:
            res = mid
            low = mid + 1
        else:
            high = mid - 1
    return res


def koko_eating_bananas(piles: List[int], h: int) -> int:
    """Find the minimum integer k such that Koko can eat all bananas within h hours."""
    def can_eat(k):
        return sum((p + k - 1) // k for p in piles) <= h

    low, high = 1, max(piles)
    res = high
    while low <= high:
        mid = (low + high) // 2
        if can_eat(mid):
            res = mid
            high = mid - 1
        else:
            low = mid + 1
    return res


def ship_capacity(weights: List[int], days: int) -> int:
    """Find the minimum ship capacity to transport all weights within 'days' days."""
    def can_ship(cap):
        d, cur = 1, 0
        for w in weights:
            if cur + w > cap:
                d += 1
                cur = w
            else:
                cur += w
        return d <= days

    low, high = max(weights), sum(weights)
    res = high
    while low <= high:
        mid = (low + high) // 2
        if can_ship(mid):
            res = mid
            high = mid - 1
        else:
            low = mid + 1
    return res


def split_array_max_sum(nums: List[int], k: int) -> int:
    """Split array into k non-empty subarrays such that the largest sum is minimized."""
    def can_split(max_sum):
        count, cur = 1, 0
        for n in nums:
            if cur + n > max_sum:
                count += 1
                cur = n
            else:
                cur += n
        return count <= k

    low, high = max(nums), sum(nums)
    res = high
    while low <= high:
        mid = (low + high) // 2
        if can_split(mid):
            res = mid
            high = mid - 1
        else:
            low = mid + 1
    return res


def find_k_closest_elements(arr: List[int], k: int, x: int) -> List[int]:
    """Find k closest elements to x in a sorted array using binary search. O(log(n-k) + k)."""
    low, high = 0, len(arr) - k
    while low < high:
        mid = (low + high) // 2
        if x - arr[mid] > arr[mid + k] - x:
            low = mid + 1
        else:
            high = mid
    return arr[low : low + k]


# --- String & Pattern Searching ---

def kmp_search(text: str, pattern: str) -> List[int]:
    """Knuth-Morris-Pratt string matching. Returns all starting indices. O(n + m)."""
    if not pattern:
        return []
    def compute_lps(pat):
        lps = [0] * len(pat)
        length = 0
        i = 1
        while i < len(pat):
            if pat[i] == pat[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    lps = compute_lps(pattern)
    res = []
    i = j = 0
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == len(pattern):
            res.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return res


def rabin_karp(text: str, pattern: str) -> List[int]:
    """Rabin-Karp string matching using rolling hash. O(n + m) average."""
    if not pattern:
        return []
    n, m = len(text), len(pattern)
    h_pat = hash(pattern)
    res = []
    for i in range(n - m + 1):
        if hash(text[i : i + m]) == h_pat:
            if text[i : i + m] == pattern:
                res.append(i)
    return res


def boyer_moore_simple(text: str, pattern: str) -> List[int]:
    """Simplified Boyer-Moore string matching (Bad Character Rule)."""
    if not pattern:
        return []
    m, n = len(pattern), len(text)
    bad_char = {c: i for i, c in enumerate(pattern)}
    res = []
    s = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            res.append(s)
            s += (m - bad_char.get(text[s + m], -1)) if s + m < n else 1
        else:
            s += max(1, j - bad_char.get(text[s + j], -1))
    return res


def z_algorithm(text: str, pattern: str) -> List[int]:
    """Find all occurrences of pattern in text using the Z-algorithm. O(n + m)."""
    S = pattern + "$" + text
    n = len(S)
    z = [0] * n
    left, r, k = 0, 0, 0
    for i in range(1, n):
        if i > r:
            left, r = i, i
            while r < n and S[r - left] == S[r]:
                r += 1
            z[i] = r - left
            r -= 1
        else:
            k = i - left
            if z[k] < r - i + 1:
                z[i] = z[k]
            else:
                left = i
                while r < n and S[r - left] == S[r]:
                    r += 1
                z[i] = r - left
                r -= 1
    m = len(pattern)
    return [i - m - 1 for i, val in enumerate(z) if val == m]


def wildcard_match(text: str, pattern: str) -> bool:
    """Check if text matches pattern containing '?' and '*'."""
    n, m = len(text), len(pattern)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    for j in range(1, m + 1):
        if pattern[j-1] == '*':
            dp[0][j] = dp[0][j-1]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if pattern[j-1] == '?' or pattern[j-1] == text[i-1]:
                dp[i][j] = dp[i-1][j-1]
            elif pattern[j-1] == '*':
                dp[i][j] = dp[i-1][j] or dp[i][j-1]
    return dp[n][m]


# --- Spatial & Geometric Searching ---

def search_2d_matrix(matrix: List[List[int]], target: int) -> bool:
    """Search for target in an m x n matrix where each row and column is sorted. O(m + n)."""
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    row, col = 0, n - 1
    while row < m and col >= 0:
        if matrix[row][col] == target:
            return True
        if matrix[row][col] > target:
            col -= 1
        else:
            row += 1
    return False


def range_search_1d(arr: List[int], low: int, high: int) -> List[int]:
    """Find all elements in a sorted array within [low, high]. O(log n + count)."""
    left = lower_bound(arr, low)
    right = upper_bound(arr, high)
    return arr[left:right]


# --- Optimization & Meta-heuristics ---

def hill_climbing(func: Callable[[float], float], start: float, step: float = 0.01, iterations: int = 1000) -> float:
    """Simple hill climbing to find a local maximum of func."""
    curr = start
    for _ in range(iterations):
        next_val = curr + step
        prev_val = curr - step
        if func(next_val) > func(curr):
            curr = next_val
        elif func(prev_val) > func(curr):
            curr = prev_val
        else:
            break
    return curr


def simulated_annealing_search(
    func: Callable[[float], float], 
    start: float, 
    temp: float = 1.0, 
    cooling_rate: float = 0.99, 
    iterations: int = 1000
) -> float:
    """Simulated annealing to find the maximum of a function."""
    curr = start
    curr_val = func(curr)
    best = curr
    best_val = curr_val

    for _ in range(iterations):
        next_x = curr + random.uniform(-1, 1)
        next_val = func(next_x)
        if next_val > curr_val or random.random() < math.exp((next_val - curr_val) / temp):
            curr, curr_val = next_x, next_val
            if curr_val > best_val:
                best, best_val = curr, curr_val
        temp *= cooling_rate
    return best


# --- Miscellaneous Utilities ---

def count_occurrences_sorted(arr: List[T], target: T) -> int:
    """Count occurrences of target in a sorted array. O(log n)."""
    left = lower_bound(arr, target)
    if left == len(arr) or arr[left] != target:
        return 0
    right = upper_bound(arr, target)
    return right - left


def find_single_element_sorted(arr: List[int]) -> int:
    """Find the single element in a sorted array where every other element appears twice. O(log n)."""
    low, high = 0, len(arr) - 1
    while low < high:
        mid = 2 * ((low + high) // 4)
        if arr[mid] == arr[mid + 1]:
            low = mid + 2
        else:
            high = mid
    return arr[low]


def peak_index_mountain_array(arr: List[int]) -> int:
    """Find the index of the peak in a mountain array. O(log n)."""
    low, high = 0, len(arr) - 1
    while low < high:
        mid = (low + high) // 2
        if arr[mid] < arr[mid + 1]:
            low = mid + 1
        else:
            high = mid
    return low


def search_bitonic_array(arr: List[int], target: int) -> Optional[int]:
    """Search for target in a bitonic array (increasing then decreasing). O(log n)."""
    peak = peak_index_mountain_array(arr)
    # Search in increasing part
    res = binary_search(arr[:peak + 1], target)
    if res is not None:
        return res
    # Search in decreasing part
    low, high = peak + 1, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] > target:
            low = mid + 1
        else:
            high = mid - 1
    return None


def search_infinite_array(reader: Callable[[int], int], target: int) -> Optional[int]:
    """Search for target in an array of unknown size. O(log index)."""
    if reader(0) == target:
        return 0
    high = 1
    while reader(high) < target:
        high *= 2
    low = high // 2
    while low <= high:
        mid = (low + high) // 2
        val = reader(mid)
        if val == target:
            return mid
        if val < target:
            low = mid + 1
        else:
            high = mid - 1
    return None


def fibonacci_search(arr: List[int], target: int) -> Optional[int]:
    """Fibonacci search for a target in a sorted array. O(log n)."""
    n = len(arr)
    fib2, fib1 = 0, 1
    fibM = fib2 + fib1
    while fibM < n:
        fib2, fib1 = fib1, fibM
        fibM = fib2 + fib1
    
    offset = -1
    while fibM > 1:
        i = min(offset + fib2, n - 1)
        if arr[i] < target:
            fibM, fib1 = fib1, fib2
            fib2 = fibM - fib1
            offset = i
        elif arr[i] > target:
            fibM = fib2
            fib1 = fib1 - fib2
            fib2 = fibM - fib1
        else:
            return i
    if fib1 and offset + 1 < n and arr[offset + 1] == target:
        return offset + 1
    return None


# --- Selection & Advanced Optimization ---

def quickselect(arr: List[T], k: int) -> T:
    """Find the k-th smallest element in an unordered list. O(n) average."""
    if not arr:
        raise ValueError("Empty list")
    if k < 0 or k >= len(arr):
        raise ValueError("Index out of bounds")
    
    def partition(left, right, pivot_idx):
        pivot_val = arr[pivot_idx]
        arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
        store_idx = left
        for i in range(left, right):
            if arr[i] < pivot_val:
                arr[i], arr[store_idx] = arr[store_idx], arr[i]
                store_idx += 1
        arr[store_idx], arr[right] = arr[right], arr[store_idx]
        return store_idx

    def select(left, right, k_idx):
        if left == right:
            return arr[left]
        pivot_idx = random.randint(left, right)
        pivot_idx = partition(left, right, pivot_idx)
        if k_idx == pivot_idx:
            return arr[k_idx]
        if k_idx < pivot_idx:
            return select(left, pivot_idx - 1, k_idx)
        return select(pivot_idx + 1, right, k_idx)

    return select(0, len(arr) - 1, k)


def find_median_unordered(arr: List[Union[int, float]]) -> float:
    """Find the median of an unordered list in O(n) average time."""
    n = len(arr)
    if n % 2 == 1:
        return float(quickselect(arr, n // 2))
    return (quickselect(arr, n // 2 - 1) + quickselect(arr, n // 2)) / 2.0


def binary_search_rotated_duplicates(arr: List[int], target: int) -> bool:
    """Check if target exists in a rotated sorted array with duplicates. O(n) worst case."""
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return True
        if arr[low] == arr[mid] == arr[high]:
            low += 1
            high -= 1
        elif arr[low] <= arr[mid]:
            if arr[low] <= target < arr[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if arr[mid] < target <= arr[high]:
                low = mid + 1
            else:
                high = mid - 1
    return False


def find_kth_smallest_matrix(matrix: List[List[int]], k: int) -> int:
    """Find the k-th smallest element in a row-column sorted matrix. O(n log(max-min))."""
    n = len(matrix)
    def count_less_equal(mid):
        count, j = 0, n - 1
        for i in range(n):
            while j >= 0 and matrix[i][j] > mid:
                j -= 1
            count += (j + 1)
        return count

    low, high = matrix[0][0], matrix[n-1][n-1]
    res = low
    while low <= high:
        mid = (low + high) // 2
        if count_less_equal(mid) >= k:
            res = mid
            high = mid - 1
        else:
            low = mid + 1
    return res


def search_in_sparse_array(arr: List[str], target: str) -> Optional[int]:
    """Search for a string in a sorted array interspersed with empty strings."""
    if not target:
        return None
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if not arr[mid]:
            left, right = mid - 1, mid + 1
            while True:
                if left < low and right > high:
                    return None
                if left >= low and arr[left]:
                    mid = left
                    break
                if right <= high and arr[right]:
                    mid = right
                    break
                left -= 1
                right += 1
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return None


def find_local_minimum_2d(matrix: List[List[int]]) -> Tuple[int, int]:
    """Find a local minimum in a 2D matrix. O(n log m)."""
    rows = len(matrix)
    cols = len(matrix[0])
    
    def get_min_in_col(col):
        min_val = float('inf')
        min_row = -1
        for i in range(rows):
            if matrix[i][col] < min_val:
                min_val = matrix[i][col]
                min_row = i
        return min_row

    low_col, high_col = 0, cols - 1
    while low_col <= high_col:
        mid_col = (low_col + high_col) // 2
        min_row = get_min_in_col(mid_col)
        
        is_left_smaller = mid_col > 0 and matrix[min_row][mid_col-1] < matrix[min_row][mid_col]
        is_right_smaller = mid_col < cols - 1 and matrix[min_row][mid_col+1] < matrix[min_row][mid_col]
        
        if not is_left_smaller and not is_right_smaller:
            return (min_row, mid_col)
        if is_left_smaller:
            high_col = mid_col - 1
        else:
            low_col = mid_col + 1
    return (-1, -1)


def bitap_search(text: str, pattern: str) -> Optional[int]:
    """Bitap algorithm for exact string matching (Shift-or)."""
    m = len(pattern)
    if m == 0:
        return 0
    if m > 64:
        raise ValueError("Pattern too long for bitap")
    
    pattern_mask = [~0] * 256
    for i in range(m):
        pattern_mask[ord(pattern[i])] &= ~(1 << i)
    
    R = ~1
    for i in range(len(text)):
        R |= pattern_mask[ord(text[i])]
        R <<= 1
        if (R & (1 << m)) == 0:
            return i - m + 1
    return None


def aho_corasick_simple(text: str, patterns: List[str]) -> Dict[str, List[int]]:
    """A simplified Aho-Corasick implementation for multi-pattern matching."""
    trie = [{'next': {}, 'fail': 0, 'output': []}]
    for pattern in patterns:
        node = 0
        for char in pattern:
            if char not in trie[node]['next']:
                trie[node]['next'][char] = len(trie)
                trie.append({'next': {}, 'fail': 0, 'output': []})
            node = trie[node]['next'][char]
        trie[node]['output'].append(pattern)

    queue = deque()
    for char, node in trie[0]['next'].items():
        queue.append(node)
    
    while queue:
        u = queue.popleft()
        for char, v in trie[u]['next'].items():
            f = trie[u]['fail']
            while char not in trie[f]['next'] and f != 0:
                f = trie[f]['fail']
            trie[v]['fail'] = trie[f]['next'][char] if char in trie[f]['next'] else 0
            trie[v]['output'] += trie[trie[v]['fail']]['output']
            queue.append(v)

    results = {p: [] for p in patterns}
    node = 0
    for i, char in enumerate(text):
        while char not in trie[node]['next'] and node != 0:
            node = trie[node]['fail']
        node = trie[node]['next'][char] if char in trie[node]['next'] else 0
        for pattern in trie[node]['output']:
            results[pattern].append(i - len(pattern) + 1)
    return results


def geometric_median_search(points: List[Tuple[float, float]], eps: float = 1e-7) -> Tuple[float, float]:
    """Weiszfeld's algorithm to find the geometric median of a set of 2D points."""
    x = sum(p[0] for p in points) / len(points)
    y = sum(p[1] for p in points) / len(points)
    
    while True:
        num_x, num_y, den = 0.0, 0.0, 0.0
        for px, py in points:
            d = math.sqrt((x - px)**2 + (y - py)**2)
            if d < eps:
                continue
            num_x += px / d
            num_y += py / d
            den += 1 / d
        if den == 0:
            return (x, y)
        nx, ny = num_x / den, num_y / den
        if math.sqrt((x - nx)**2 + (y - ny)**2) < eps:
            return (nx, ny)
        x, y = nx, ny
