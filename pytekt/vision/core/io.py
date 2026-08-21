#!/usr/bin/env python3
"""Image I/O helpers (Pillow → NumPy)."""

from __future__ import annotations

import io as _io
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np

from pytekt.vision.core.utils import as_hwc, ensure_uint8, require_pillow


def read_image(path: Union[str, Path], mode: Optional[str] = "RGB") -> np.ndarray:
    """
    Read an image from disk into a NumPy array.

    Args:
        path: File path to the image.
        mode: Optional PIL mode to convert into (e.g., ``"RGB"``, ``"L"``).
              Pass ``None`` to keep the file's native mode.

    Returns:
        ``np.ndarray`` with shape ``(H, W, C)`` for color or ``(H, W)`` for grayscale.
    """
    Image = require_pillow()
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    with Image.open(path) as img:
        if mode:
            img = img.convert(mode)
        return np.asarray(img)


def write_image(path: Union[str, Path], image: np.ndarray, *, format: Optional[str] = None) -> Path:
    """
    Write a NumPy image array to disk.

    Args:
        path: Output path.
        image: HW or HWC array (uint8 or float [0,1]).
        format: Optional Pillow format override (e.g. ``"PNG"``).

    Returns:
        Resolved output :class:`~pathlib.Path`.
    """
    Image = require_pillow()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    arr = ensure_uint8(image)
    if arr.ndim == 2:
        pil = Image.fromarray(arr)
    elif arr.shape[2] == 4:
        pil = Image.fromarray(arr)
    else:
        pil = Image.fromarray(arr[..., :3])
    save_kwargs: Dict[str, Any] = {}
    if format:
        save_kwargs["format"] = format
    pil.save(path, **save_kwargs)
    return path.resolve()


def image_info(path: Union[str, Path]) -> Dict[str, Any]:
    """Return basic metadata for an image file without fully decoding pixels."""
    Image = require_pillow()
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    with Image.open(path) as img:
        w, h = img.size
        return {
            "path": str(path.resolve()),
            "width": int(w),
            "height": int(h),
            "mode": img.mode,
            "format": img.format,
            "n_frames": int(getattr(img, "n_frames", 1) or 1),
        }


def encode_image(image: np.ndarray, *, format: str = "PNG") -> bytes:
    """Encode an image array to bytes (PNG/JPEG/…)."""
    Image = require_pillow()
    arr = ensure_uint8(as_hwc(image))
    if arr.ndim == 2:
        pil = Image.fromarray(arr)
    elif arr.shape[2] == 4:
        pil = Image.fromarray(arr)
    else:
        pil = Image.fromarray(arr[..., :3])
    buf = _io.BytesIO()
    pil.save(buf, format=format)
    return buf.getvalue()


def decode_image(data: bytes, mode: Optional[str] = "RGB") -> np.ndarray:
    """Decode image bytes into a NumPy array."""
    Image = require_pillow()
    with Image.open(_io.BytesIO(data)) as img:
        if mode:
            img = img.convert(mode)
        return np.asarray(img)
