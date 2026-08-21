"""
Strings & Compression Subpackage
================================

Provides string processing and data compression algorithms:
- strings: edit distance, longest common substring, anagram detection, palindrome checks, suffix utilities
- compression: Huffman coding, Run-Length Encoding (RLE), LZW compression, LZ77, Burrows-Wheeler Transform
"""

from __future__ import annotations

from . import compression, strings

__all__ = [
    "compression",
    "strings",
]
