"""
Array and sequence processing utilities.

Flattening, chunking, windowing, deduplication, rolling sums, and related
helpers for list/sequence operations. Full package documentation:
pytekt/algorithms/README.md
"""
from typing import Any, Union, Iterator, List, Optional, Tuple, Dict
import random


def _native_bigdata():
    try:
        from pytekt import bigdata as native_bigdata

        if native_bigdata.using_native_extension():
            return native_bigdata
    except Exception:
        pass
    return None

def flatten_array(arr: List[List[Any]]) -> List[Any]:
    """Flatten a list of lists into a single list."""
    if not arr:
        return []
    return [item for sublist in arr for item in sublist]


def chunk_array(arr: List[Any], size: int) -> List[List[Any]]:
    """Split a list into smaller sublists (chunks) of a given size."""
    if not arr or size <= 0:
        return []
    return [arr[i:i + size] for i in range(0, len(arr), size)]


def remove_duplicates(arr: list[Any]) -> list[Any]:
    """
    Remove duplicate elements from a list while preserving order.

    The function returns a new list containing only the first
    occurrence of each element.

    Parameters
    ----------
    arr : list[Any]
        The input list that may contain duplicate values.

    Returns
    -------
    list[Any]
        A list without duplicate elements.

    Raises
    ------
    ValueError
        If the input list is empty.
    """

    # List that will store unique elements
    without_dupl = []

    # Validate input list
    if not arr:
        raise ValueError("List must not be empty")

    # Add only elements that were not seen before (O(n))
    seen = set()
    for item in arr:
        if item not in seen:
            without_dupl.append(item)
            seen.add(item)

    return without_dupl


def moving_average(arr: list[Union[int, float]]) -> float:
    """
    Calculate the arithmetic mean of a list of numbers.

    The function computes the average value of all numeric
    elements in the list.

    Parameters
    ----------
    arr : list[Union[int, float]]
        A list containing integer or floating-point numbers.

    Returns
    -------
    float
        The average value of the numbers in the list.

    Raises
    ------
    ValueError
        If the input list is empty.
    TypeError
        If the list contains non-numeric elements.
    """

    # Accumulator for the sum of elements
    total = 0.0

    # Validate input list
    if not arr:
        raise ValueError("List must not be empty")

    # Validate types and calculate sum
    for item in arr:
        if type(item) not in (int, float):
            raise TypeError("List must contain only int or float")
        total += item

    return total / len(arr)

def flatten_deep(arr: list[list[Any]]) -> list[Any]:
    """
    Recursively flatten a deeply nested list into a single list.

    This function takes a list that may contain other lists nested
    at any depth and returns a new flat list containing all elements
    in their original order.

    Parameters
    ----------
    arr : list[list[Any]]
        A list that may contain elements or other nested lists.

    Returns
    -------
    list[Any]
        A completely flattened list containing all values from the input.

    Raises
    ------
    ValueError
        If the input list is empty.
    """

    # Initialize an empty list to store the flattened result
    flat_array = list()

    # Validate input: list must not be empty
    if not arr:
        raise ValueError("List must not be empty")

    # Iterate over each element in the input list
    for item in arr:

        # If the current element is a list, flatten it recursively
        if isinstance(item, list):
            flat_array.extend(flatten_deep(item))

        # If the current element is not a list, append it directly
        else:
            flat_array.append(item)

    # Return the fully flattened list
    return flat_array


def sliding_window(arr: list[Any], size: int) -> Iterator[list[Any]]:
    """
    Generate consecutive sublists (windows) of a specified size.

    This function produces overlapping slices of the input list,
    each containing exactly `size` elements.

    Example
    -------
    arr = [1, 2, 3, 4], size = 2
    Output: [1,2], [2,3], [3,4]

    Parameters
    ----------
    arr : list[Any]
        The input list to create windows from.
    size : int
        The size of each sliding window.

    Yields
    ------
    list[Any]
        Each window (sublist) of length `size`.

    Raises
    ------
    ValueError
        If the list is empty or size is invalid.
    TypeError
        If size is not an integer.
    """

    # Validate input list: must not be empty
    if not arr:
        raise ValueError("List must not be empty")

    # Validate that size is an integer
    if not isinstance(size, int):
        raise TypeError("size must be an integer")

    # Validate that size is greater than zero
    if size <= 0:
        raise ValueError("Size must be greater than 0")

    # Validate that window size does not exceed list length
    if size > len(arr):
        raise ValueError("Size cannot be greater than array length")

    # Generate each sliding window slice
    for i in range(len(arr) - size + 1):
        yield arr[i:i+size]


def pad_array(arr: list[Any], min_len: int, item: Any) -> list[Any]:
    """
    Extend a list until it reaches a minimum required length.

    This function appends the given `item` repeatedly to the list
    until its length becomes equal to `min_len`.

    Parameters
    ----------
    arr : list[Any]
        The input list to be padded.
    min_len : int
        The minimum desired length of the list.
    item : Any
        The element to append until the list reaches the target length.

    Returns
    -------
    list[Any]
        The padded list.

    Raises
    ------
    ValueError
        If the input list is empty.
    TypeError
        If min_len is not an integer.
    """

    # Validate input list: must not be empty
    if not arr:
        raise ValueError("List must not be empty")

    # Validate that min_len is an integer
    if not isinstance(min_len, int):
        raise TypeError("Size must be an integer")

    # Append the padding item until the list reaches the required length
    while len(arr) != min_len:
        arr.append(item)

    # Return the padded list
    return arr


def rolling_sum(arr: list[int], size: int) -> list[int]:
    """
    Compute rolling (moving) sums over a list of integers.

    This function calculates the sum of each consecutive window
    of length `size` in the list.

    Example
    -------
    arr = [1, 2, 3, 4], size = 2
    Output: [3, 5, 7]

    Parameters
    ----------
    arr : list[int]
        The input list of integers.
    size : int
        The size of each window used for summation.

    Returns
    -------
    list[int]
        A list of rolling sums.

    Raises
    ------
    ValueError
        If the list is empty or size is invalid.
    """

    # Validate input list: must not be empty
    if not arr:
        raise ValueError("List must not be empty")

    # Validate window size: must be greater than zero
    if size <= 0:
        raise ValueError("Size must be greater than 0")

    native_bigdata = _native_bigdata()
    if native_bigdata is not None:
        return native_bigdata.rolling_sum(arr, size).tolist()

    # List that will store all rolling sums
    roll_sum = list()

    # Iterate through all valid window starting positions
    for i in range(len(arr) - size + 1):

        # Compute sum of the current window and append it
        roll_sum.append(sum(arr[i:i+size]))

    # Return the list of rolling sums
    return roll_sum


def pairwise(arr: list[Any]) -> list[Any]:
    """
    Create pairs of consecutive elements in a list.

    This function returns a list of tuples where each tuple contains
    two neighboring elements from the input list.

    Example
    -------
    arr = [1, 2, 3, 4]
    Output: [(1,2), (2,3), (3,4)]

    Parameters
    ----------
    arr : list[Any]
        The input list containing at least two elements.

    Returns
    -------
    list[Any]
        A list of tuples representing consecutive pairs.

    Raises
    ------
    ValueError
        If the list contains fewer than two elements.
    """

    # Validate input, must contain at least two elements
    if len(arr) < 2:
        raise ValueError("List must contain at least 2 elements")

    # List that will store consecutive pairs
    pair = list()

    # Use zip to pair each element with the next one
    pair.extend(zip(arr, arr[1:]))

    # Return the list of pairs

    return pair


# --- Search & Selection ---

def binary_search(arr: List[int], target: int) -> int:
    """Find the index of target in a sorted array using binary search. Returns -1 if not found."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def kth_largest_element(arr: List[int], k: int) -> int:
    """Find the kth largest element using the Quickselect algorithm."""
    if not arr:
        return -1
    pivot = random.choice(arr)
    left = [x for x in arr if x > pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x < pivot]
    
    L, M = len(left), len(mid)
    if k <= L:
        return kth_largest_element(left, k)
    elif k <= L + M:
        return pivot
    else:
        return kth_largest_element(right, k - L - M)


def find_peak_element(arr: List[int]) -> int:
    """Find a peak element (greater than its neighbors) in O(log n) time."""
    left, right = 0, len(arr) - 1
    while left < right:
        mid = (left + right) // 2
        if arr[mid] > arr[mid + 1]:
            right = mid
        else:
            left = mid + 1
    return left


def majority_element(arr: List[int]) -> int:
    """Boyer-Moore Voting Algorithm: Find the element that appears more than n/2 times."""
    candidate, count = None, 0
    for num in arr:
        if count == 0:
            candidate = num
        count += (1 if num == candidate else -1)
    return candidate


def find_missing_number(arr: List[int]) -> int:
    """Find the missing number in an array containing n unique numbers from 0 to n."""
    n = len(arr)
    expected_sum = n * (n + 1) // 2
    return expected_sum - sum(arr)


def find_all_duplicates(arr: List[int]) -> List[int]:
    """Find all duplicates in an array where elements are in range [1, n]. O(n) time, O(1) space."""
    res = []
    for x in arr:
        idx = abs(x) - 1
        if arr[idx] < 0:
            res.append(abs(x))
        else:
            arr[idx] *= -1
    # Cleanup: restore array
    for i in range(len(arr)):
        arr[i] = abs(arr[i])
    return res


# --- Optimization ---

def max_subarray_sum(arr: List[int]) -> int:
    """Kadane's Algorithm: Find the maximum sum of a contiguous subarray."""
    if not arr:
        return 0
    max_so_far = -float('inf')
    current_max = 0
    for x in arr:
        current_max += x
        if max_so_far < current_max:
            max_so_far = current_max
        if current_max < 0:
            current_max = 0
    return int(max_so_far)


def max_product_subarray(arr: List[int]) -> int:
    """Find the contiguous subarray within an array which has the largest product."""
    if not arr:
        return 0
    res = max(arr)
    cur_min, cur_max = 1, 1
    for n in arr:
        if n == 0:
            cur_min, cur_max = 1, 1
            continue
        tmp = cur_max * n
        cur_max = max(n * cur_max, n * cur_min, n)
        cur_min = min(tmp, n * cur_min, n)
        res = max(res, cur_max)
    return res


def longest_consecutive_sequence(arr: List[int]) -> int:
    """Find the length of the longest consecutive elements sequence in O(n) time."""
    num_set = set(arr)
    longest = 0
    for n in arr:
        if (n - 1) not in num_set:
            length = 0
            while (n + length) in num_set:
                length += 1
            longest = max(length, longest)
    return longest


def subarray_with_given_sum(arr: List[int], target: int) -> List[int]:
    """Find a contiguous subarray that sums to target. Returns [start_index, end_index]."""
    lookup = {0: -1}
    cur_sum = 0
    for i, n in enumerate(arr):
        cur_sum += n
        if (cur_sum - target) in lookup:
            return [lookup[cur_sum - target] + 1, i]
        lookup[cur_sum] = i
    return []


def longest_increasing_subsequence_length(arr: List[int]) -> int:
    """Find the length of the longest increasing subsequence in O(n log n) time."""
    import bisect
    tails = []
    for x in arr:
        idx = bisect.bisect_left(tails, x)
        if idx < len(tails):
            tails[idx] = x
        else:
            tails.append(x)
    return len(tails)


def count_subarrays_with_sum(arr: List[int], k: int) -> int:
    """Count the number of subarrays that sum to k."""
    count = 0
    cur_sum = 0
    lookup = {0: 1}
    for n in arr:
        cur_sum += n
        count += lookup.get(cur_sum - k, 0)
        lookup[cur_sum] = lookup.get(cur_sum, 0) + 1
    return count


# --- Two-Pointer & Sliding Window ---

def two_sum_sorted(arr: List[int], target: int) -> Optional[Tuple[int, int]]:
    """Find two numbers in a sorted array that sum to target. Returns indices."""
    left, right = 0, len(arr) - 1
    while left < right:
        s = arr[left] + arr[right]
        if s == target:
            return (left, right)
        elif s < target:
            left += 1
        else:
            right -= 1
    return None


def three_sum(arr: List[int]) -> List[List[int]]:
    """Find all unique triplets that sum to zero."""
    res = []
    arr.sort()
    for i, a in enumerate(arr):
        if i > 0 and a == arr[i - 1]:
            continue
        left, right = i + 1, len(arr) - 1
        while left < right:
            s = a + arr[left] + arr[right]
            if s > 0:
                right -= 1
            elif s < 0:
                left += 1
            else:
                res.append([a, arr[left], arr[right]])
                left += 1
                while left < right and arr[left] == arr[left - 1]:
                    left += 1
    return res


def container_with_most_water(arr: List[int]) -> int:
    """Find two lines that together with the x-axis form a container containing the most water."""
    left, right = 0, len(arr) - 1
    res = 0
    while left < right:
        area = (right - left) * min(arr[left], arr[right])
        res = max(res, area)
        if arr[left] < arr[right]:
            left += 1
        else:
            right -= 1
    return res


def trapping_rain_water(arr: List[int]) -> int:
    """Calculate how much water can be trapped after raining."""
    if not arr:
        return 0
    left, right = 0, len(arr) - 1
    left_max, right_max = arr[left], arr[right]
    res = 0
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, arr[left])
            res += left_max - arr[left]
        else:
            right -= 1
            right_max = max(right_max, arr[right])
            res += right_max - arr[right]
    return res


def remove_duplicates_inplace(arr: List[int]) -> int:
    """Remove duplicates from a sorted array in-place. Returns the new length."""
    if not arr:
        return 0
    left = 1
    for r in range(1, len(arr)):
        if arr[r] != arr[r - 1]:
            arr[left] = arr[r]
            left += 1
    return left


def move_zeros_to_end(arr: List[int]) -> None:
    """Move all zeros to the end of the array in-place while maintaining relative order."""
    left = 0
    for r in range(len(arr)):
        if arr[r]:
            arr[left], arr[r] = arr[r], arr[left]
            left += 1


# --- Rearrangement & Sorting-like ---

def dutch_national_flag(arr: List[int]) -> None:
    """Sort an array of 0s, 1s, and 2s in one pass (Dutch National Flag Algorithm)."""
    low, mid, high = 0, 0, len(arr) - 1
    while mid <= high:
        if arr[mid] == 0:
            arr[low], arr[mid] = arr[mid], arr[low]
            low += 1
            mid += 1
        elif arr[mid] == 1:
            mid += 1
        else:
            arr[mid], arr[high] = arr[high], arr[mid]
            high -= 1


def next_permutation(arr: List[int]) -> None:
    """Rearrange numbers into the lexicographically next greater permutation of numbers."""
    i = len(arr) - 2
    while i >= 0 and arr[i] >= arr[i + 1]:
        i -= 1
    if i >= 0:
        j = len(arr) - 1
        while arr[j] <= arr[i]:
            j -= 1
        arr[i], arr[j] = arr[j], arr[i]
    arr[i+1:] = reversed(arr[i+1:])


def rotate_array(arr: List[Any], k: int) -> None:
    """Rotate the array to the right by k steps in-place."""
    n = len(arr)
    k %= n
    def reverse(left, right):
        while left < right:
            arr[left], arr[right] = arr[right], arr[left]
            left, right = left + 1, right - 1
    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)


def shuffle_array(arr: List[Any]) -> None:
    """Shuffle an array in-place using the Fisher-Yates algorithm."""
    for i in range(len(arr) - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]


def merge_sorted_arrays(arr1: List[int], arr2: List[int]) -> List[int]:
    """Merge two sorted arrays into a single sorted array."""
    res = []
    i, j = 0, 0
    while i < len(arr1) and j < len(arr2):
        if arr1[i] < arr2[j]:
            res.append(arr1[i])
            i += 1
        else:
            res.append(arr2[j])
            j += 1
    res.extend(arr1[i:])
    res.extend(arr2[j:])
    return res


def intersection_of_arrays(arr1: List[Any], arr2: List[Any]) -> List[Any]:
    """Find the intersection of two arrays while preserving unique elements."""
    return list(set(arr1) & set(arr2))


# --- Mathematical & Statistical ---

def product_except_self(arr: List[int]) -> List[int]:
    """Return an array such that res[i] is the product of all elements except arr[i]."""
    n = len(arr)
    res = [1] * n
    prefix = 1
    for i in range(n):
        res[i] = prefix
        prefix *= arr[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        res[i] *= suffix
        suffix *= arr[i]
    return res


def find_equilibrium_index(arr: List[int]) -> int:
    """Find the index where the sum of elements to the left equals the sum of elements to the right."""
    total = sum(arr)
    left_sum = 0
    for i, x in enumerate(arr):
        total -= x
        if left_sum == total:
            return i
        left_sum += x
    return -1


def compute_prefix_sums(arr: List[Union[int, float]]) -> List[Union[int, float]]:
    """Compute the prefix sums of an array."""
    native_bigdata = _native_bigdata()
    if native_bigdata is not None:
        return native_bigdata.prefix_sum(arr).tolist()
    res = [0] * len(arr)
    cur = 0
    for i, x in enumerate(arr):
        cur += x
        res[i] = cur
    return res


def compute_suffix_sums(arr: List[Union[int, float]]) -> List[Union[int, float]]:
    """Compute the suffix sums of an array."""
    res = [0] * len(arr)
    cur = 0
    for i in range(len(arr) - 1, -1, -1):
        cur += arr[i]
        res[i] = cur
    return res


def find_min_difference(arr: List[int]) -> int:
    """Find the minimum absolute difference between any two elements in the array."""
    arr.sort()
    min_diff = float('inf')
    for i in range(1, len(arr)):
        min_diff = min(min_diff, arr[i] - arr[i-1])
    return int(min_diff)


def median_of_two_sorted_arrays(arr1: List[int], arr2: List[int]) -> float:
    """Find the median of two sorted arrays in O(log(min(m, n))) time."""
    A, B = arr1, arr2
    if len(B) < len(A):
        A, B = B, A
    total = len(A) + len(B)
    half = total // 2
    left, right = 0, len(A) - 1
    while True:
        i = (left + right) // 2
        j = half - i - 2
        Aleft = A[i] if i >= 0 else -float('inf')
        Aright = A[i + 1] if (i + 1) < len(A) else float('inf')
        Bleft = B[j] if j >= 0 else -float('inf')
        Bright = B[j + 1] if (j + 1) < len(B) else float('inf')
        if Aleft <= Bright and Bleft <= Aright:
            if total % 2:
                return min(Aright, Bright)
            return (max(Aleft, Bleft) + min(Aright, Bright)) / 2
        elif Aleft > Bright:
            right = i - 1
        else:
            left = i + 1


# --- Utility ---

def is_monotonic(arr: List[Union[int, float]]) -> bool:
    """Check if an array is monotonic (either entirely non-increasing or non-decreasing)."""
    return (all(arr[i] <= arr[i+1] for i in range(len(arr)-1)) or
            all(arr[i] >= arr[i+1] for i in range(len(arr)-1)))


def find_common_elements_three_sorted(a: List[int], b: List[int], c: List[int]) -> List[int]:
    """Find common elements in three sorted arrays using three pointers."""
    i, j, k = 0, 0, 0
    res = []
    while i < len(a) and j < len(b) and k < len(c):
        if a[i] == b[j] == c[k]:
            res.append(a[i])
            i, j, k = i + 1, j + 1, k + 1
        elif a[i] < b[j]:
            i += 1
        elif b[j] < c[k]:
            j += 1
        else:
            k += 1
    return res


def get_frequencies(arr: List[Any]) -> Dict[Any, int]:
    """Return a dictionary mapping each element to its frequency in the array."""
    res = {}
    for x in arr:
        res[x] = res.get(x, 0) + 1
    return res


def find_first_missing_positive(arr: List[int]) -> int:
    """Find the smallest missing positive integer in an unsorted array in O(n) time."""
    n = len(arr)
    for i in range(n):
        while 1 <= arr[i] <= n and arr[arr[i] - 1] != arr[i]:
            arr[arr[i] - 1], arr[i] = arr[i], arr[arr[i] - 1]
    for i in range(n):
        if arr[i] != i + 1:
            return i + 1
    return n + 1


def difference_between_arrays(arr1: List[Any], arr2: List[Any]) -> List[Any]:
    """Return elements present in arr1 but not in arr2."""
    s2 = set(arr2)
    return [x for x in arr1 if x not in s2]


def symmetric_difference(arr1: List[Any], arr2: List[Any]) -> List[Any]:
    """Return elements present in either arr1 or arr2 but not both."""
    return list(set(arr1) ^ set(arr2))


def rotate_matrix_90(matrix: List[List[Any]]) -> None:
    """Rotate an n x n matrix 90 degrees clockwise in-place."""
    n = len(matrix)
    for i in range(n // 2):
        for j in range(i, n - i - 1):
            tmp = matrix[i][j]
            matrix[i][j] = matrix[n - j - 1][i]
            matrix[n - j - 1][i] = matrix[n - i - 1][n - j - 1]
            matrix[n - i - 1][n - j - 1] = matrix[j][n - i - 1]
            matrix[j][n - i - 1] = tmp


def spiral_order_traversal(matrix: List[List[Any]]) -> List[Any]:
    """Return all elements of an m x n matrix in spiral order."""
    res = []
    if not matrix:
        return res
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for i in range(left, right + 1):
            res.append(matrix[top][i])
        top += 1
        for i in range(top, bottom + 1):
            res.append(matrix[i][right])
        right -= 1
        if top <= bottom:
            for i in range(right, left - 1, -1):
                res.append(matrix[bottom][i])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                res.append(matrix[i][left])
            left += 1
    return res


def matrix_transpose(matrix: List[List[Any]]) -> List[List[Any]]:
    """Transpose a 2D matrix (swap rows and columns)."""
    if not matrix or not matrix[0]:
        return []
    rows, cols = len(matrix), len(matrix[0])
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]


def matrix_multiply(a: List[List[Union[int, float]]], b: List[List[Union[int, float]]]) -> List[List[float]]:
    """Multiply two 2D matrices and return the result."""
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])
    if cols_a != rows_b:
        raise ValueError(f"Incompatible shapes: ({rows_a}x{cols_a}) x ({rows_b}x{cols_b})")
    result: List[List[float]] = [[0.0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    return result


def z_score_normalization(arr: List[Union[int, float]]) -> List[float]:
    """Normalize values to z-scores (mean=0, std=1)."""
    n = len(arr)
    if n == 0:
        return []
    mean = sum(arr) / n
    variance = sum((x - mean) ** 2 for x in arr) / n
    std = variance ** 0.5
    if std == 0:
        return [0.0] * n
    return [(x - mean) / std for x in arr]


def min_max_scaling(arr: List[Union[int, float]], low: float = 0.0, high: float = 1.0) -> List[float]:
    """Scale values to the range [low, high] using min-max normalization."""
    if not arr:
        return []
    mn, mx = min(arr), max(arr)
    if mn == mx:
        return [(low + high) / 2] * len(arr)
    return [low + (x - mn) / (mx - mn) * (high - low) for x in arr]
