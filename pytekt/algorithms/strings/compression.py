"""Compression and encoding algorithms (stdlib only)."""

from __future__ import annotations

import base64
import heapq
from typing import Dict, List, Tuple

from pytekt.algorithms.catalog import register_algorithm


@register_algorithm(category="compression", summary="Run-length encode string to (char, count) pairs.")
def run_length_encode(s: str) -> List[Tuple[str, int]]:
    if not s:
        return []
    out: List[Tuple[str, int]] = []
    cur = s[0]
    count = 1
    for ch in s[1:]:
        if ch == cur:
            count += 1
        else:
            out.append((cur, count))
            cur = ch
            count = 1
    out.append((cur, count))
    return out


@register_algorithm(category="compression", summary="Decode run-length encoded pairs to string.")
def run_length_decode(encoded: List[Tuple[str, int]]) -> str:
    return "".join(ch * count for ch, count in encoded)


@register_algorithm(category="compression", summary="LZ77-style compression to (offset, length, next_char) tokens.")
def lz77_compress(data: str, window: int = 4096) -> List[Tuple[int, int, str]]:
    if not data:
        return []
    tokens: List[Tuple[int, int, str]] = []
    i = 0
    while i < len(data):
        best_len = 0
        best_offset = 0
        start = max(0, i - window)
        for j in range(start, i):
            length = 0
            while (
                i + length < len(data)
                and data[j + length] == data[i + length]
                and length < 255
            ):
                length += 1
            if length > best_len:
                best_len = length
                best_offset = i - j
        if best_len >= 3:
            nxt = data[i + best_len] if i + best_len < len(data) else ""
            tokens.append((best_offset, best_len, nxt))
            i += best_len + (1 if nxt else 0)
        else:
            tokens.append((0, 0, data[i]))
            i += 1
    return tokens


@register_algorithm(category="compression", summary="Decompress LZ77 tokens produced by lz77_compress.")
def lz77_decompress(tokens: List[Tuple[int, int, str]]) -> str:
    out: List[str] = []
    for offset, length, nxt in tokens:
        if length == 0:
            out.append(nxt)
        else:
            start = len(out) - offset
            for k in range(length):
                out.append(out[start + k])
            if nxt:
                out.append(nxt)
    return "".join(out)


@register_algorithm(category="compression", summary="Huffman-compress bytes to bitstring using frequencies.")
def huffman_compress_bytes(data: bytes) -> Tuple[Dict[int, str], str]:
    if not data:
        return {}, ""
    freq: Dict[int, int] = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    if len(freq) == 1:
        byte = next(iter(freq))
        return {byte: "0"}, "0" * len(data)
    heap: List[Tuple[int, int, object]] = []
    uid = 0
    for byte, count in freq.items():
        heapq.heappush(heap, (count, uid, byte))
        uid += 1
    while len(heap) > 1:
        c1, _, n1 = heapq.heappop(heap)
        c2, _, n2 = heapq.heappop(heap)
        heapq.heappush(heap, (c1 + c2, uid, (n1, n2)))
        uid += 1
    root = heap[0][2]
    codes: Dict[int, str] = {}

    def walk(node: object, prefix: str) -> None:
        if isinstance(node, int):
            codes[node] = prefix or "0"
            return
        left, right = node
        walk(left, prefix + "0")
        walk(right, prefix + "1")

    walk(root, "")
    bits = "".join(codes[b] for b in data)
    return codes, bits


@register_algorithm(category="compression", summary="Huffman-decompress bitstring using code table.")
def huffman_decompress_bytes(codes: Dict[int, str], bits: str) -> bytes:
    if not bits:
        return b""
    rev = {v: k for k, v in codes.items()}
    out: List[int] = []
    cur = ""
    for bit in bits:
        cur += bit
        if cur in rev:
            out.append(rev[cur])
            cur = ""
    if cur:
        raise ValueError("invalid Huffman bitstream")
    return bytes(out)


@register_algorithm(category="compression", summary="Delta encode integer sequence.")
def delta_encode(values: List[int]) -> List[int]:
    if not values:
        return []
    out = [values[0]]
    for i in range(1, len(values)):
        out.append(values[i] - values[i - 1])
    return out


@register_algorithm(category="compression", summary="Delta decode integer sequence.")
def delta_decode(deltas: List[int]) -> List[int]:
    if not deltas:
        return []
    out = [deltas[0]]
    for d in deltas[1:]:
        out.append(out[-1] + d)
    return out


@register_algorithm(category="compression", summary="Pack booleans into bytes.")
def pack_bools(flags: List[bool]) -> bytes:
    out = bytearray()
    byte = 0
    for i, flag in enumerate(flags):
        if flag:
            byte |= 1 << (i % 8)
        if i % 8 == 7:
            out.append(byte)
            byte = 0
    if len(flags) % 8:
        out.append(byte)
    return bytes(out)


@register_algorithm(category="compression", summary="Unpack booleans from bytes.")
def unpack_bools(data: bytes, count: int) -> List[bool]:
    out: List[bool] = []
    for i in range(count):
        byte = data[i // 8]
        out.append(bool(byte & (1 << (i % 8))))
    return out


@register_algorithm(category="compression", summary="Base64-encode bytes to ASCII string.")
def base64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


@register_algorithm(category="compression", summary="Base64-decode ASCII string to bytes.")
def base64_decode(encoded: str) -> bytes:
    return base64.b64decode(encoded.encode("ascii"))
