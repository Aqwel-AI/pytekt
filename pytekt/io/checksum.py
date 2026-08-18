"""File checksums (SHA-256)."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Union

from .streaming import read_chunks

PathLike = Union[str, os.PathLike[str]]


def file_sha256(path: PathLike, *, chunk_size: int = 65536) -> str:
    """
    Compute hex SHA-256 of file contents.

    Parameters
    ----------
    path : str or path-like
    chunk_size : int
        Read buffer size.

    Returns
    -------
    str
        Lowercase hex digest.
    """
    h = hashlib.sha256()
    for chunk in read_chunks(path, size=chunk_size):
        h.update(chunk)
    return h.hexdigest()


def verify_sha256(path: PathLike, expected_hex: str, *, chunk_size: int = 65536) -> bool:
    """
    Return True if ``file_sha256(path)`` equals ``expected_hex`` (case-insensitive).
    """
    got = file_sha256(path, chunk_size=chunk_size)
    return got.lower() == expected_hex.strip().lower()
