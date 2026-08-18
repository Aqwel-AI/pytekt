"""Hashing and checksum utilities (stdlib only)."""

from __future__ import annotations

import hashlib
import struct
from typing import Any, List, Tuple, Union

from .catalog import register_algorithm

HashableInput = Union[str, bytes, int]


def _to_bytes(data: HashableInput) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, int):
        return struct.pack(">q", data)
    return data.encode("utf-8")


@register_algorithm(category="hashing")
def djb2_hash(data: HashableInput) -> int:
    """DJB2 string hash."""
    h = 5381
    for byte in _to_bytes(data):
        h = ((h << 5) + h + byte) & 0xFFFFFFFFFFFFFFFF
    return h


@register_algorithm(category="hashing")
def fnv1a_hash(data: HashableInput) -> int:
    """FNV-1a 64-bit hash."""
    h = 0xCBF29CE484222325
    prime = 0x100000001B3
    for byte in _to_bytes(data):
        h ^= byte
        h = (h * prime) & 0xFFFFFFFFFFFFFFFF
    return h


@register_algorithm(category="hashing")
def sdbm_hash(data: HashableInput) -> int:
    """SDBM hash."""
    h = 0
    for byte in _to_bytes(data):
        h = (byte + (h << 6) + (h << 16) - h) & 0xFFFFFFFFFFFFFFFF
    return h


@register_algorithm(category="hashing")
def rolling_hash(
    text: str, base: int = 256, mod: int = 1_000_000_007
) -> List[int]:
    """Prefix rolling polynomial hashes for text."""
    hashes: List[int] = []
    h = 0
    for ch in text:
        h = (h * base + ord(ch)) % mod
        hashes.append(h)
    return hashes


@register_algorithm(category="hashing")
def polynomial_hash(text: str, base: int = 31, mod: int = 1_000_000_007) -> int:
    """Polynomial rolling hash of entire string."""
    h = 0
    for ch in text:
        h = (h * base + ord(ch)) % mod
    return h


@register_algorithm(category="hashing")
def hash_combine(seed: int, value: int) -> int:
    """Combine two hashes (boost-style mixing)."""
    seed ^= value + 0x9E3779B97F4A7C15 + ((seed << 6) & 0xFFFFFFFFFFFFFFFF) + (seed >> 2)
    return seed & 0xFFFFFFFFFFFFFFFF


@register_algorithm(category="hashing")
def murmur_mix64(k: int) -> int:
    """MurmurHash3-style 64-bit finalizer mix."""
    k &= 0xFFFFFFFFFFFFFFFF
    k ^= k >> 33
    k = (k * 0xFF51AFD7ED558CCD) & 0xFFFFFFFFFFFFFFFF
    k ^= k >> 33
    k = (k * 0xC4CEB9FE1A85EC53) & 0xFFFFFFFFFFFFFFFF
    k ^= k >> 33
    return k


@register_algorithm(category="hashing")
def checksum(data: bytes) -> int:
    """Simple additive checksum (sum of bytes mod 256)."""
    return sum(data) % 256


@register_algorithm(category="hashing")
def verify_checksum(data: bytes, expected: int) -> bool:
    """Verify additive checksum."""
    return checksum(data) == expected % 256


@register_algorithm(category="hashing")
def consistent_hash_bucket(key: HashableInput, num_buckets: int) -> int:
    """Map key to bucket index [0, num_buckets) via FNV-1a."""
    if num_buckets <= 0:
        raise ValueError("num_buckets must be positive")
    return fnv1a_hash(key) % num_buckets


@register_algorithm(category="hashing")
def string_to_bucket(text: str, num_buckets: int) -> int:
    """Map string to bucket using DJB2."""
    if num_buckets <= 0:
        raise ValueError("num_buckets must be positive")
    return djb2_hash(text) % num_buckets


@register_algorithm(category="hashing")
def hash_int(n: int) -> int:
    """Hash integer via splitmix64-style mixing."""
    z = (n + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9 & 0xFFFFFFFFFFFFFFFF
    z = (z ^ (z >> 27)) * 0x94D049BB133111EB & 0xFFFFFFFFFFFFFFFF
    return z ^ (z >> 31)


@register_algorithm(category="hashing")
def hash_tuple(values: Tuple[Any, ...]) -> int:
    """Hash a tuple by combining element hashes."""
    h = 0xCBF29CE484222325
    for v in values:
        h = hash_combine(h, hash(v) & 0xFFFFFFFFFFFFFFFF)
    return murmur_mix64(h)


@register_algorithm(category="hashing")
def hash_bytes(data: bytes, algorithm: str = "sha256") -> str:
    """Cryptographic hash digest as hex string."""
    return hashlib.new(algorithm, data).hexdigest()


@register_algorithm(category="hashing")
def double_hash(key: HashableInput, size: int) -> Tuple[int, int]:
    """Two hash values for double hashing in open addressing."""
    if size <= 0:
        raise ValueError("size must be positive")
    h1 = fnv1a_hash(key) % size
    h2 = 1 + (djb2_hash(key) % (size - 1)) if size > 1 else 1
    return h1, h2
