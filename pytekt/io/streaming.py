"""Streaming reads for large files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator, Union

PathLike = Union[str, os.PathLike[str]]


def iter_lines(
    path: PathLike,
    *,
    encoding: str = "utf-8",
    errors: str = "strict",
) -> Iterator[str]:
    """
    Yield text lines from a file without loading the whole file.

    Newlines are stripped from each yielded string.
    """
    p = Path(path)
    with p.open(encoding=encoding, errors=errors) as f:
        for line in f:
            yield line.rstrip("\n\r")


def read_chunks(path: PathLike, *, size: int = 65536) -> Iterator[bytes]:
    """
    Yield fixed-size byte chunks from a file (suitable for hashing or pipes).

    Parameters
    ----------
    path : str or path-like
    size : int, default 65536
        Chunk size in bytes.
    """
    p = Path(path)
    with p.open("rb") as f:
        while True:
            chunk = f.read(size)
            if not chunk:
                break
            yield chunk
