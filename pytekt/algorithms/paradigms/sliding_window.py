"""Sliding-window algorithms (stdlib only)."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Deque, Dict, List, Tuple

from pytekt.algorithms.catalog import register_algorithm


@register_algorithm(category="sliding_window", summary="Maximum sum of any contiguous subarray of size k.")
def max_sum_subarray_size_k(nums: List[int], k: int) -> int:
    if k <= 0 or len(nums) < k:
        return 0
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best


@register_algorithm(category="sliding_window", summary="Minimum sum of any contiguous subarray of size k.")
def min_sum_subarray_size_k(nums: List[int], k: int) -> int:
    if k <= 0 or len(nums) < k:
        return 0
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = min(best, window)
    return best


@register_algorithm(category="sliding_window", summary="Length of longest substring without repeating characters.")
def longest_substring_without_repeating(s: str) -> int:
    last: Dict[str, int] = {}
    best = 0
    left = 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best


@register_algorithm(category="sliding_window", summary="Longest substring with at most k distinct characters.")
def longest_substring_at_most_k_distinct(s: str, k: int) -> int:
    if k <= 0:
        return 0
    counts: Dict[str, int] = {}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            left_ch = s[left]
            counts[left_ch] -= 1
            if counts[left_ch] == 0:
                del counts[left_ch]
            left += 1
        best = max(best, right - left + 1)
    return best


@register_algorithm(category="sliding_window", summary="Minimum window substring containing all characters of t.")
def min_window_substring(s: str, t: str) -> str:
    if not t or not s:
        return ""
    need = Counter(t)
    missing = len(t)
    left = 0
    best_len = len(s) + 1
    best_start = 0
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            if right - left + 1 < best_len:
                best_len = right - left + 1
                best_start = left
            left_ch = s[left]
            need[left_ch] += 1
            if need[left_ch] > 0:
                missing += 1
            left += 1
    return "" if best_len > len(s) else s[best_start : best_start + best_len]


@register_algorithm(category="sliding_window", summary="Longest subarray of 1s after flipping at most k zeros.")
def max_consecutive_ones_with_k_flips(nums: List[int], k: int) -> int:
    left = 0
    zeros = 0
    best = 0
    for right, val in enumerate(nums):
        if val == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


@register_algorithm(category="sliding_window", summary="Longest subarray containing at most two distinct values.")
def longest_subarray_two_distinct(nums: List[int]) -> int:
    counts: Dict[int, int] = {}
    left = 0
    best = 0
    for right, val in enumerate(nums):
        counts[val] = counts.get(val, 0) + 1
        while len(counts) > 2:
            counts[nums[left]] -= 1
            if counts[nums[left]] == 0:
                del counts[nums[left]]
            left += 1
        best = max(best, right - left + 1)
    return best


@register_algorithm(category="sliding_window", summary="Longest substring with same letter after at most k replacements.")
def longest_repeating_character_replacement(s: str, k: int) -> int:
    counts: Dict[str, int] = {}
    left = 0
    best = 0
    max_freq = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        max_freq = max(max_freq, counts[ch])
        while (right - left + 1) - max_freq > k:
            counts[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


@register_algorithm(category="sliding_window", summary="Count substrings of s that are anagrams of p.")
def count_anagram_substrings(s: str, p: str) -> int:
    if len(p) > len(s) or not p:
        return 0
    k = len(p)
    need = Counter(p)
    window = Counter(s[:k])
    count = 1 if window == need else 0
    for i in range(k, len(s)):
        outgoing = s[i - k]
        incoming = s[i]
        window[incoming] += 1
        window[outgoing] -= 1
        if window[outgoing] == 0:
            del window[outgoing]
        if window == need:
            count += 1
    return count


@register_algorithm(category="sliding_window", summary="Start indices of anagram substrings of p in s.")
def find_anagram_indices(s: str, p: str) -> List[int]:
    if len(p) > len(s) or not p:
        return []
    k = len(p)
    need = Counter(p)
    window = Counter(s[:k])
    out: List[int] = []
    if window == need:
        out.append(0)
    for i in range(k, len(s)):
        outgoing = s[i - k]
        incoming = s[i]
        window[incoming] += 1
        window[outgoing] -= 1
        if window[outgoing] == 0:
            del window[outgoing]
        if window == need:
            out.append(i - k + 1)
    return out


@register_algorithm(category="sliding_window", summary="Maximum average value of subarray of length k.")
def max_average_subarray(nums: List[int], k: int) -> float:
    if k <= 0 or len(nums) < k:
        return 0.0
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best / k


@register_algorithm(category="sliding_window", summary="Count subarrays whose sum equals k (handles negatives).")
def subarray_sum_equals_k(nums: List[int], k: int) -> int:
    prefix = 0
    freq: Dict[int, int] = {0: 1}
    count = 0
    for x in nums:
        prefix += x
        count += freq.get(prefix - k, 0)
        freq[prefix] = freq.get(prefix, 0) + 1
    return count


@register_algorithm(category="sliding_window", summary="Length of longest subarray with sum at most k (non-negative nums).")
def longest_subarray_sum_at_most_k(nums: List[int], k: int) -> int:
    left = 0
    total = 0
    best = 0
    for right, val in enumerate(nums):
        total += val
        while total > k and left <= right:
            total -= nums[left]
            left += 1
        best = max(best, right - left + 1)
    return best


@register_algorithm(category="sliding_window", summary="Minimum length subarray with sum at least target (positive ints).")
def smallest_subarray_sum_at_least(nums: List[int], target: int) -> int:
    left = 0
    total = 0
    best = len(nums) + 1
    for right, val in enumerate(nums):
        total += val
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best > len(nums) else best


@register_algorithm(category="sliding_window", summary="Maximum number of distinct values in any window of size k.")
def max_distinct_in_window(nums: List[int], k: int) -> int:
    if k <= 0 or len(nums) < k:
        return 0
    counts: Dict[int, int] = {}
    for x in nums[:k]:
        counts[x] = counts.get(x, 0) + 1
    best = len(counts)
    for i in range(k, len(nums)):
        outgoing = nums[i - k]
        counts[outgoing] -= 1
        if counts[outgoing] == 0:
            del counts[outgoing]
        incoming = nums[i]
        counts[incoming] = counts.get(incoming, 0) + 1
        best = max(best, len(counts))
    return best


@register_algorithm(category="sliding_window", summary="Distinct element counts for each sliding window of size k.")
def distinct_counts_per_window(nums: List[int], k: int) -> List[int]:
    if k <= 0 or len(nums) < k:
        return []
    counts: Dict[int, int] = {}
    for x in nums[:k]:
        counts[x] = counts.get(x, 0) + 1
    out = [len(counts)]
    for i in range(k, len(nums)):
        outgoing = nums[i - k]
        counts[outgoing] -= 1
        if counts[outgoing] == 0:
            del counts[outgoing]
        incoming = nums[i]
        counts[incoming] = counts.get(incoming, 0) + 1
        out.append(len(counts))
    return out


@register_algorithm(category="sliding_window", summary="Maximum in each sliding window of size k.")
def sliding_window_maximum(nums: List[int], k: int) -> List[int]:
    if k <= 0 or not nums:
        return []
    dq: Deque[int] = deque()
    out: List[int] = []
    for i, val in enumerate(nums):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] <= val:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


@register_algorithm(category="sliding_window", summary="Median of each sliding window of size k.")
def sliding_window_median(nums: List[int], k: int) -> List[float]:
    if k <= 0 or len(nums) < k:
        return []
    window = sorted(nums[:k])
    out: List[float] = []
    mid = k // 2
    for i in range(k - 1, len(nums)):
        if k % 2:
            out.append(float(window[mid]))
        else:
            out.append((window[mid - 1] + window[mid]) / 2.0)
        if i + 1 < len(nums):
            outgoing = nums[i - k + 1]
            incoming = nums[i + 1]
            lo = 0
            hi = k - 1
            while lo < hi:
                m = (lo + hi) // 2
                if window[m] < outgoing:
                    lo = m + 1
                else:
                    hi = m
            window.pop(lo)
            lo = 0
            hi = len(window)
            while lo < hi:
                m = (lo + hi) // 2
                if window[m] < incoming:
                    lo = m + 1
                else:
                    hi = m
            window.insert(lo, incoming)
    return out


@register_algorithm(category="sliding_window", summary="Count subarrays with at most k odd numbers.")
def count_subarrays_at_most_k_odds(nums: List[int], k: int) -> int:
    left = 0
    odds = 0
    total = 0
    for right, val in enumerate(nums):
        if val % 2:
            odds += 1
        while odds > k:
            if nums[left] % 2:
                odds -= 1
            left += 1
        total += right - left + 1
    return total


@register_algorithm(category="sliding_window", summary="Longest subarray where max minus min is at most limit.")
def longest_subarray_bounded_range(nums: List[int], limit: int) -> int:
    maxdq: Deque[int] = deque()
    mindq: Deque[int] = deque()
    left = 0
    best = 0
    for right, val in enumerate(nums):
        while maxdq and nums[maxdq[-1]] <= val:
            maxdq.pop()
        maxdq.append(right)
        while mindq and nums[mindq[-1]] >= val:
            mindq.pop()
        mindq.append(right)
        while nums[maxdq[0]] - nums[mindq[0]] > limit:
            left += 1
            if maxdq[0] < left:
                maxdq.popleft()
            if mindq[0] < left:
                mindq.popleft()
        best = max(best, right - left + 1)
    return best


