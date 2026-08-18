"""String algorithms: palindromes, pattern matching, encoding, and parsing."""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Tuple

from .catalog import register_algorithm


@register_algorithm(category="strings", summary="Check if a string is a palindrome.")
def is_palindrome(s: str) -> bool:
    return s == s[::-1]


@register_algorithm(category="strings", summary="Palindrome check ignoring non-alphanumeric case.")
def is_palindrome_alnum(s: str) -> bool:
    filtered = [c.lower() for c in s if c.isalnum()]
    return filtered == filtered[::-1]


@register_algorithm(category="strings", summary="Longest palindromic substring via expand-around-center.")
def longest_palindrome_substring(s: str) -> str:
    if not s:
        return ""
    start, end = 0, 0

    def expand(left: int, right: int) -> Tuple[int, int]:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - 1

    for i in range(len(s)):
        l1, r1 = expand(i, i)
        l2, r2 = expand(i, i + 1)
        if r1 - l1 > end - start:
            start, end = l1, r1
        if r2 - l2 > end - start:
            start, end = l2, r2
    return s[start : end + 1]


@register_algorithm(category="strings", summary="Count distinct palindromic substrings.")
def count_palindromes(s: str) -> int:
    seen: set[str] = set()
    n = len(s)
    for i in range(n):
        for j in range(i, n):
            sub = s[i : j + 1]
            if sub == sub[::-1]:
                seen.add(sub)
    return len(seen)


@register_algorithm(category="strings", summary="Check if two strings are anagrams.")
def is_anagram(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)


@register_algorithm(category="strings", summary="Sorted-character key for anagram grouping.")
def group_anagrams_key(s: str) -> str:
    return "".join(sorted(s))


@register_algorithm(category="strings", summary="Run-length encode a string.")
def rle_encode(s: str) -> str:
    if not s:
        return ""
    parts: List[str] = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            parts.append(f"{count}{s[i - 1]}")
            count = 1
    parts.append(f"{count}{s[-1]}")
    return "".join(parts)


@register_algorithm(category="strings", summary="Decode run-length encoded string.")
def rle_decode(s: str) -> str:
    result: List[str] = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j].isdigit():
            j += 1
        if j == i:
            raise ValueError(f"Invalid RLE at position {i}")
        count = int(s[i:j])
        if j >= len(s):
            raise ValueError("Invalid RLE: missing character")
        result.append(s[j] * count)
        i = j + 1
    return "".join(result)


@register_algorithm(category="strings", summary="Longest palindrome substring via Manacher's algorithm.")
def manacher_longest_palindrome(s: str) -> str:
    if not s:
        return ""
    t = "#".join(s)
    n = len(t)
    p = [0] * n
    center = right = 0
    best_center = best_len = 0
    for i in range(n):
        mirror = 2 * center - i
        if i < right:
            p[i] = min(right - i, p[mirror])
        while (
            i + p[i] + 1 < n
            and i - p[i] - 1 >= 0
            and t[i + p[i] + 1] == t[i - p[i] - 1]
        ):
            p[i] += 1
        if i + p[i] > right:
            center, right = i, i + p[i]
        if p[i] > best_len:
            best_len = p[i]
            best_center = i
    start = (best_center - best_len) // 2
    return s[start : start + best_len]


@register_algorithm(category="strings", summary="KMP failure (prefix) function for a pattern.")
def kmp_failure(pattern: str) -> List[int]:
    n = len(pattern)
    fail = [0] * n
    length = 0
    i = 1
    while i < n:
        if pattern[i] == pattern[length]:
            length += 1
            fail[i] = length
            i += 1
        elif length:
            length = fail[length - 1]
        else:
            fail[i] = 0
            i += 1
    return fail


@register_algorithm(category="strings", summary="Z-function (prefix match lengths) for a string.")
def z_function(s: str) -> List[int]:
    n = len(s)
    if n == 0:
        return []
    z = [0] * n
    z[0] = n
    left = right = 0
    for i in range(1, n):
        if i <= right:
            z[i] = min(right - i + 1, z[i - left])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > right:
            left, right = i, i + z[i] - 1
    return z


@register_algorithm(category="strings", summary="Naive suffix array: sorted start indices.")
def suffix_array_naive(s: str) -> List[int]:
    return sorted(range(len(s)), key=lambda i: s[i:])


@register_algorithm(category="strings", summary="LCP array from text and suffix array.")
def lcp_array(s: str, sa: List[int]) -> List[int]:
    n = len(sa)
    rank = [0] * len(s)
    for i, pos in enumerate(sa):
        rank[pos] = i
    lcp = [0] * n
    k = 0
    for i in range(len(s)):
        if rank[i] == n - 1:
            k = 0
            continue
        j = sa[rank[i] + 1]
        while i + k < len(s) and j + k < len(s) and s[i + k] == s[j + k]:
            k += 1
        lcp[rank[i]] = k
        if k:
            k -= 1
    return lcp


@register_algorithm(category="strings", summary="Longest repeated substring via suffix array and LCP.")
def longest_repeated_substring(s: str) -> str:
    if len(s) < 2:
        return ""
    sa = suffix_array_naive(s)
    lcp = lcp_array(s, sa)
    best_len = 0
    best_idx = 0
    for i, length in enumerate(lcp):
        if length > best_len:
            best_len = length
            best_idx = sa[i]
    return s[best_idx : best_idx + best_len]


@register_algorithm(category="strings", summary="Find first occurrence of needle in haystack (KMP).")
def str_str_find(haystack: str, needle: str) -> int:
    if needle == "":
        return 0
    fail = kmp_failure(needle)
    j = 0
    for i in range(len(haystack)):
        while j > 0 and haystack[i] != needle[j]:
            j = fail[j - 1]
        if haystack[i] == needle[j]:
            j += 1
            if j == len(needle):
                return i - j + 1
    return -1


@register_algorithm(category="strings", summary="Reverse order of words in a string.")
def reverse_words(s: str) -> str:
    return " ".join(s.split()[::-1])


@register_algorithm(category="strings", summary="Reverse characters in a string.")
def reverse_string(s: str) -> str:
    chars = list(s)
    left, right = 0, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1
        right -= 1
    return "".join(chars)


@register_algorithm(category="strings", summary="Rotate string left by k positions.")
def rotate_string(s: str, k: int) -> str:
    if not s:
        return s
    k %= len(s)
    return s[k:] + s[:k]


@register_algorithm(category="strings", summary="Check if s2 is a rotation of s1.")
def is_rotation(s1: str, s2: str) -> bool:
    return len(s1) == len(s2) and s2 in (s1 + s1)


@register_algorithm(category="strings", summary="Minimum window substring containing all of t.")
def min_window_substring(s: str, t: str) -> str:
    if not t or not s:
        return ""
    need = Counter(t)
    missing = len(t)
    left = 0
    best = (0, float("inf"))
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            if right - left < best[1] - best[0]:
                best = (left, right)
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return s[best[0] : best[1] + 1] if best[1] != float("inf") else ""


@register_algorithm(category="strings", summary="Length of longest substring without repeating characters.")
def longest_substring_no_repeat(s: str) -> int:
    last: Dict[str, int] = {}
    start = 0
    best = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best


@register_algorithm(category="strings", summary="Length of longest substring with at most k distinct chars.")
def longest_substring_k_distinct(s: str, k: int) -> int:
    if k == 0:
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


@register_algorithm(category="strings", summary="Count total substrings of a string.")
def count_substrings(s: str) -> int:
    n = len(s)
    return n * (n + 1) // 2


@register_algorithm(category="strings", summary="Count vowels in a string.")
def count_vowels(s: str) -> int:
    vowels = set("aeiouAEIOU")
    return sum(1 for c in s if c in vowels)


@register_algorithm(category="strings", summary="Remove duplicate characters preserving order.")
def remove_duplicates_string(s: str) -> str:
    seen: set[str] = set()
    out: List[str] = []
    for ch in s:
        if ch not in seen:
            seen.add(ch)
            out.append(ch)
    return "".join(out)


@register_algorithm(category="strings", summary="Compress string by replacing runs with char+count.")
def compress_string(s: str) -> str:
    if not s:
        return s
    parts: List[str] = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            parts.append(s[i - 1] + str(count))
            count = 1
    parts.append(s[-1] + str(count))
    compressed = "".join(parts)
    return compressed if len(compressed) < len(s) else s


@register_algorithm(category="strings", summary="Decompress char+count compressed string.")
def decompress_string(s: str) -> str:
    result: List[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        i += 1
        j = i
        while j < len(s) and s[j].isdigit():
            j += 1
        count = int(s[i:j]) if j > i else 1
        result.append(ch * count)
        i = j
    return "".join(result)


@register_algorithm(category="strings", summary="Check if two strings are isomorphic.")
def is_isomorphic(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    s_to_t: Dict[str, str] = {}
    t_to_s: Dict[str, str] = {}
    for a, b in zip(s, t):
        if a in s_to_t and s_to_t[a] != b:
            return False
        if b in t_to_s and t_to_s[b] != a:
            return False
        s_to_t[a] = b
        t_to_s[b] = a
    return True


@register_algorithm(category="strings", summary="Check if s follows the word pattern.")
def word_pattern(pattern: str, s: str) -> bool:
    words = s.split()
    if len(pattern) != len(words):
        return False
    p_to_w: Dict[str, str] = {}
    w_to_p: Dict[str, str] = {}
    for p, w in zip(pattern, words):
        if p in p_to_w and p_to_w[p] != w:
            return False
        if w in w_to_p and w_to_p[w] != p:
            return False
        p_to_w[p] = w
        w_to_p[w] = p
    return True


@register_algorithm(category="strings", summary="Check if s is built by repeating a substring.")
def repeated_substring(s: str) -> bool:
    if not s:
        return False
    z = z_function(s)
    n = len(s)
    for length in range(1, n // 2 + 1):
        if n % length == 0 and z[length] >= n - length:
            return True
    return False


@register_algorithm(category="strings", summary="Shortest palindrome by prepending characters to s.")
def shortest_palindrome_prefix(s: str) -> str:
    if not s:
        return ""
    rev = s[::-1]
    combined = s + "#" + rev
    z = z_function(combined)
    overlap = z[-1]
    return rev[: len(s) - overlap] + s


@register_algorithm(category="strings", summary="Parse string to integer (atoi).")
def atoi(s: str) -> int:
    s = s.strip()
    if not s:
        return 0
    sign = 1
    i = 0
    if s[0] in "+-":
        sign = -1 if s[0] == "-" else 1
        i = 1
    result = 0
    while i < len(s) and s[i].isdigit():
        result = result * 10 + int(s[i])
        i += 1
    result *= sign
    return max(-(2**31), min(2**31 - 1, result))


@register_algorithm(category="strings", summary="Add two non-negative integer strings.")
def add_strings(num1: str, num2: str) -> str:
    i, j = len(num1) - 1, len(num2) - 1
    carry = 0
    digits: List[str] = []
    while i >= 0 or j >= 0 or carry:
        d1 = int(num1[i]) if i >= 0 else 0
        d2 = int(num2[j]) if j >= 0 else 0
        total = d1 + d2 + carry
        digits.append(str(total % 10))
        carry = total // 10
        i -= 1
        j -= 1
    return "".join(reversed(digits)) or "0"


@register_algorithm(category="strings", summary="Multiply two non-negative integer strings.")
def multiply_strings(num1: str, num2: str) -> str:
    if num1 == "0" or num2 == "0":
        return "0"
    m, n = len(num1), len(num2)
    prod = [0] * (m + n)
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            mul = int(num1[i]) * int(num2[j])
            p1, p2 = i + j, i + j + 1
            total = mul + prod[p2]
            prod[p2] = total % 10
            prod[p1] += total // 10
    start = 0
    while start < len(prod) - 1 and prod[start] == 0:
        start += 1
    return "".join(str(d) for d in prod[start:])


@register_algorithm(category="strings", summary="Compare dotted version strings.")
def compare_version(version1: str, version2: str) -> int:
    v1 = [int(x) for x in version1.split(".")]
    v2 = [int(x) for x in version2.split(".")]
    length = max(len(v1), len(v2))
    v1.extend([0] * (length - len(v1)))
    v2.extend([0] * (length - len(v2)))
    for a, b in zip(v1, v2):
        if a < b:
            return -1
        if a > b:
            return 1
    return 0
