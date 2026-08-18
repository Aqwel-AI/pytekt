"""Atomic writes via temp file + replace."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Union

PathLike = Union[str, os.PathLike[str]]


def atomic_write(
    path: PathLike,
    data: str,
    *,
    encoding: str = "utf-8",
    mode: str = "w",
) -> None:
    """
    Write text to ``path`` atomically: write to a temp file in the same
    directory, then ``os.replace`` into place.

    Raises
    ------
    OSError
        If the temp file cannot be written or replaced.
    """
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(dest.parent),
        prefix=f".{dest.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, mode, encoding=encoding, newline="") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, dest)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def save_automatically(data: Any, path: PathLike, **json_kwargs: Any) -> None:
    """
    Write ``data`` as JSON to ``path`` atomically (temp file + ``os.replace``).

    Same idea as writing to ``path + ".tmp"`` then renaming: readers never see a
    half-written file. Extra keyword arguments are passed to :func:`json.dump`
    (e.g. ``indent=2``, ``ensure_ascii=False``).

    Parameters
    ----------
    data : Any
        JSON-serializable object (dict, list, etc.).
    path : str or path-like
        Destination file path.
    **json_kwargs
        Forwarded to :func:`json.dump`.
    """
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(dest.parent),
        prefix=f".{dest.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            json.dump(data, f, **json_kwargs)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, dest)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def atomic_write_bytes(path: PathLike, data: bytes) -> None:
    """Write bytes to ``path`` atomically (same strategy as ``atomic_write``)."""
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(dest.parent),
        prefix=f".{dest.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, dest)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
