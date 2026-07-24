"""Two-pointer algorithms (stdlib only)."""

from __future__ import annotations

from typing import List, Tuple

from .catalog import register_algorithm


@register_algorithm(category="two_pointers", summary="Indices of two numbers summing to target in sorted array.")
def two_sum_sorted(nums: List[int], target: int) -> Tuple[int, int]:
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return left, right
        if total < target:
            left += 1
        else:
            right -= 1
    raise ValueError("no two-sum pair found")


@register_algorithm(category="two_pointers", summary="Unique triplets in array that sum to zero.")
def three_sum(nums: List[int]) -> List[List[int]]:
    nums.sort()
    out: List[List[int]] = []
    n = len(nums)
    for i in range(n):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                out.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return out


@register_algorithm(category="two_pointers", summary="Triplet sum closest to target.")
def three_sum_closest(nums: List[int], target: int) -> int:
    nums.sort()
    best = nums[0] + nums[1] + nums[2]
    n = len(nums)
    for i in range(n - 2):
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if abs(total - target) < abs(best - target):
                best = total
            if total < target:
                left += 1
            elif total > target:
                right -= 1
            else:
                return total
    return best


@register_algorithm(category="two_pointers", summary="Remove duplicates in-place from sorted array; return new length.")
def remove_duplicates_sorted(nums: List[int]) -> int:
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1
    return write


@register_algorithm(category="two_pointers", summary="Move all zeros to end while preserving order of non-zeros.")
def move_zeroes(nums: List[int]) -> List[int]:
    out = nums[:]
    write = 0
    for val in out:
        if val != 0:
            out[write] = val
            write += 1
    for i in range(write, len(out)):
        out[i] = 0
    return out


@register_algorithm(category="two_pointers", summary="Sort array of 0, 1, 2 in one pass (Dutch national flag).")
def sort_colors(nums: List[int]) -> List[int]:
    out = nums[:]
    low, mid, high = 0, 0, len(out) - 1
    while mid <= high:
        if out[mid] == 0:
            out[low], out[mid] = out[mid], out[low]
            low += 1
            mid += 1
        elif out[mid] == 1:
            mid += 1
        else:
            out[mid], out[high] = out[high], out[mid]
            high -= 1
    return out


@register_algorithm(category="two_pointers", summary="Maximum water contained between vertical lines.")
def container_with_most_water(heights: List[int]) -> int:
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        h = min(heights[left], heights[right])
        best = max(best, h * (right - left))
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    return best


@register_algorithm(category="two_pointers", summary="Trapped rainwater between elevation bars.")
def trap_rain_water(heights: List[int]) -> int:
    if len(heights) < 3:
        return 0
    left, right = 0, len(heights) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if heights[left] < heights[right]:
            left_max = max(left_max, heights[left])
            water += left_max - heights[left]
            left += 1
        else:
            right_max = max(right_max, heights[right])
            water += right_max - heights[right]
            right -= 1
    return water


@register_algorithm(category="two_pointers", summary="Check palindrome ignoring non-alphanumeric case.")
def is_palindrome_alphanumeric(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True


@register_algorithm(category="two_pointers", summary="Whether string is palindrome after deleting at most one char.")
def valid_palindrome_after_one_delete(s: str) -> bool:
    def check(lo: int, hi: int) -> bool:
        while lo < hi:
            if s[lo] != s[hi]:
                return False
            lo += 1
            hi -= 1
        return True

    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return check(left + 1, right) or check(left, right - 1)
        left += 1
        right -= 1
    return True


@register_algorithm(category="two_pointers", summary="Merge two sorted arrays into one sorted array.")
def merge_sorted_arrays(a: List[int], b: List[int]) -> List[int]:
    out: List[int] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


@register_algorithm(category="two_pointers", summary="Intersection of two sorted arrays.")
def intersection_sorted_arrays(a: List[int], b: List[int]) -> List[int]:
    out: List[int] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            if not out or out[-1] != a[i]:
                out.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out


@register_algorithm(category="two_pointers", summary="Union of two sorted arrays with duplicates removed.")
def union_sorted_arrays(a: List[int], b: List[int]) -> List[int]:
    out: List[int] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            if not out or out[-1] != a[i]:
                out.append(a[i])
            i += 1
        elif b[j] < a[i]:
            if not out or out[-1] != b[j]:
                out.append(b[j])
            j += 1
        else:
            if not out or out[-1] != a[i]:
                out.append(a[i])
            i += 1
            j += 1
    while i < len(a):
        if not out or out[-1] != a[i]:
            out.append(a[i])
        i += 1
    while j < len(b):
        if not out or out[-1] != b[j]:
            out.append(b[j])
        j += 1
    return out


@register_algorithm(category="two_pointers", summary="Square each number and return sorted result.")
def square_sorted_array(nums: List[int]) -> List[int]:
    out = [0] * len(nums)
    left, right = 0, len(nums) - 1
    pos = len(nums) - 1
    while left <= right:
        lsq = nums[left] * nums[left]
        rsq = nums[right] * nums[right]
        if lsq > rsq:
            out[pos] = lsq
            left += 1
        else:
            out[pos] = rsq
            right -= 1
        pos -= 1
    return out


@register_algorithm(category="two_pointers", summary="Partition array so elements < pivot come first.")
def partition_by_pivot(nums: List[int], pivot: int) -> List[int]:
    out = nums[:]
    left, right = 0, len(out) - 1
    i = 0
    while i <= right:
        if out[i] < pivot:
            out[left], out[i] = out[i], out[left]
            left += 1
            i += 1
        elif out[i] > pivot:
            out[right], out[i] = out[i], out[right]
            right -= 1
        else:
            i += 1
    return out


@register_algorithm(category="two_pointers", summary="Pair in sorted array with sum closest to target.")
def closest_pair_sum(nums: List[int], target: int) -> Tuple[int, int]:
    left, right = 0, len(nums) - 1
    best_pair = (nums[0], nums[-1])
    best_diff = abs(nums[0] + nums[-1] - target)
    while left < right:
        total = nums[left] + nums[right]
        diff = abs(total - target)
        if diff < best_diff:
            best_diff = diff
            best_pair = (nums[left], nums[right])
        if total < target:
            left += 1
        else:
            right -= 1
    return best_pair


@register_algorithm(category="two_pointers", summary="Count quadruplets from four arrays summing to zero.")
def four_sum_count(a: List[int], b: List[int], c: List[int], d: List[int]) -> int:
    from collections import Counter

    ab = Counter(x + y for x in a for y in b)
    count = 0
    for x in c:
        for y in d:
            count += ab.get(-(x + y), 0)
    return count


@register_algorithm(category="two_pointers", summary="Reverse a list of characters in-place style copy.")
def reverse_chars(chars: List[str]) -> List[str]:
    out = chars[:]
    left, right = 0, len(out) - 1
    while left < right:
        out[left], out[right] = out[right], out[left]
        left += 1
        right -= 1
    return out


@register_algorithm(category="two_pointers", summary="Whether subsequence s is subsequence of t.")
def is_subsequence(s: str, t: str) -> bool:
    i = 0
    for ch in t:
        if i < len(s) and s[i] == ch:
            i += 1
    return i == len(s)


@register_algorithm(category="two_pointers", summary="Minimum absolute difference between any two sorted elements.")
def min_difference_sorted(nums: List[int]) -> int:
    if len(nums) < 2:
        return 0
    best = nums[1] - nums[0]
    for i in range(1, len(nums)):
        best = min(best, nums[i] - nums[i - 1])
    return best


