"""Bit manipulation and bitwise arithmetic utilities."""

from __future__ import annotations

from typing import List

from pytekt.algorithms.catalog import register_algorithm


@register_algorithm(category="bit")
def popcount(n: int) -> int:
    """Count set bits (population count)."""
    n = abs(n)
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count


@register_algorithm(category="bit")
def is_power_of_two(n: int) -> bool:
    """Return True if n is a positive power of two."""
    return n > 0 and (n & (n - 1)) == 0


@register_algorithm(category="bit")
def next_power_of_two(n: int) -> int:
    """Smallest power of two >= n."""
    if n <= 1:
        return 1
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    return n + 1


@register_algorithm(category="bit")
def prev_power_of_two(n: int) -> int:
    """Largest power of two <= n."""
    if n <= 0:
        return 0
    p = next_power_of_two(n)
    return p if p == n else p // 2


@register_algorithm(category="bit")
def highest_set_bit(n: int) -> int:
    """Index of highest set bit (0-based), or -1 if n==0."""
    if n == 0:
        return -1
    n = abs(n)
    pos = 0
    while n > 1:
        n >>= 1
        pos += 1
    return pos


@register_algorithm(category="bit")
def lowest_set_bit(n: int) -> int:
    """Value of lowest set bit (n & -n), or 0 if n==0."""
    return n & -n if n else 0


@register_algorithm(category="bit")
def set_bit(n: int, pos: int) -> int:
    """Set bit at position pos."""
    return n | (1 << pos)


@register_algorithm(category="bit")
def clear_bit(n: int, pos: int) -> int:
    """Clear bit at position pos."""
    return n & ~(1 << pos)


@register_algorithm(category="bit")
def toggle_bit(n: int, pos: int) -> int:
    """Toggle bit at position pos."""
    return n ^ (1 << pos)


@register_algorithm(category="bit")
def get_bit(n: int, pos: int) -> int:
    """Return 0 or 1 for bit at position pos."""
    return (n >> pos) & 1


@register_algorithm(category="bit")
def parity(n: int) -> int:
    """Parity of n: 0 for even number of set bits, 1 for odd."""
    result = 0
    while n:
        result ^= 1
        n &= n - 1
    return result


@register_algorithm(category="bit")
def reverse_bits(n: int, width: int = 32) -> int:
    """Reverse the lowest `width` bits."""
    result = 0
    for i in range(width):
        if n & (1 << i):
            result |= 1 << (width - 1 - i)
    return result


@register_algorithm(category="bit")
def count_trailing_zeros(n: int) -> int:
    """Count trailing zero bits."""
    if n == 0:
        return 0
    count = 0
    while (n & 1) == 0:
        count += 1
        n >>= 1
    return count


@register_algorithm(category="bit")
def count_leading_zeros(n: int, width: int = 32) -> int:
    """Count leading zero bits in a `width`-bit representation."""
    if n == 0:
        return width
    count = 0
    for i in range(width - 1, -1, -1):
        if n & (1 << i):
            break
        count += 1
    return count


@register_algorithm(category="bit")
def rotate_left(n: int, k: int, width: int = 32) -> int:
    """Rotate n left by k bits within `width` bits."""
    k %= width
    mask = (1 << width) - 1
    n &= mask
    return ((n << k) | (n >> (width - k))) & mask


@register_algorithm(category="bit")
def rotate_right(n: int, k: int, width: int = 32) -> int:
    """Rotate n right by k bits within `width` bits."""
    k %= width
    mask = (1 << width) - 1
    n &= mask
    return ((n >> k) | (n << (width - k))) & mask


@register_algorithm(category="bit")
def subsets_mask(n: int) -> List[int]:
    """All subset bitmasks for a set of size n (0..2^n-1)."""
    return list(range(1 << n))


@register_algorithm(category="bit")
def gray_code(n: int) -> List[int]:
    """Generate n-bit Gray code sequence (2^n values)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return [0]
    prev = gray_code(n - 1)
    return prev + [x | (1 << (n - 1)) for x in reversed(prev)]


@register_algorithm(category="bit")
def hamming_distance(a: int, b: int) -> int:
    """Number of bit positions where a and b differ."""
    return popcount(a ^ b)


@register_algorithm(category="bit")
def xor_from_1_to_n(n: int) -> int:
    """XOR of all integers from 1 to n."""
    rem = n % 4
    if rem == 0:
        return n
    if rem == 1:
        return 1
    if rem == 2:
        return n + 1
    return 0


@register_algorithm(category="bit")
def find_missing_number(nums: List[int], n: int) -> int:
    """Find missing number in [0..n] using XOR."""
    xor_all = xor_from_1_to_n(n)
    for x in nums:
        xor_all ^= x
    return xor_all


@register_algorithm(category="bit")
def single_number(nums: List[int]) -> int:
    """Element appearing once when all others appear twice."""
    result = 0
    for x in nums:
        result ^= x
    return result


@register_algorithm(category="bit")
def swap_without_temp(a: int, b: int) -> tuple[int, int]:
    """Swap two integers using XOR."""
    a = a ^ b
    b = a ^ b
    a = a ^ b
    return a, b


@register_algorithm(category="bit")
def bitwise_add(a: int, b: int) -> int:
    """Add two integers without using + operator."""
    mask = 0xFFFFFFFF
    while b:
        carry = (a & b) << 1
        a = (a ^ b) & mask
        b = carry & mask
    if a > 0x7FFFFFFF:
        a = ~(a ^ mask)
    return a


@register_algorithm(category="bit")
def bitwise_subtract(a: int, b: int) -> int:
    """Subtract b from a using bitwise operations."""
    return bitwise_add(a, bitwise_add(~b, 1))
