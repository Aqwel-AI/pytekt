"""Geometric image transforms (resize, crop, pad, flip, rotate)."""

from __future__ import annotations

from typing import Optional, Tuple, Union

import numpy as np

from .utils import as_hwc, ensure_uint8, require_pillow


Size = Tuple[int, int]  # (width, height) for Pillow; helpers also accept (h, w) via size_hw


def resize(
    image: np.ndarray,
    size: Size,
    *,
    size_hw: bool = False,
    resample: str = "bilinear",
) -> np.ndarray:
    """
    Resize image.

    Args:
        image: Input array.
        size: ``(width, height)`` by default, or ``(height, width)`` if ``size_hw=True``.
        size_hw: Interpret ``size`` as ``(H, W)``.
        resample: ``nearest``, ``bilinear``, ``bicubic``, or ``lanczos``.
    """
    Image = require_pillow()
    arr = ensure_uint8(as_hwc(image))
    if size_hw:
        h, w = size
    else:
        w, h = size
    if w < 1 or h < 1:
        raise ValueError(f"Invalid size: {(w, h)}")
    resample_map = {
        "nearest": Image.Resampling.NEAREST if hasattr(Image, "Resampling") else Image.NEAREST,
        "bilinear": Image.Resampling.BILINEAR if hasattr(Image, "Resampling") else Image.BILINEAR,
        "bicubic": Image.Resampling.BICUBIC if hasattr(Image, "Resampling") else Image.BICUBIC,
        "lanczos": Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS,
    }
    key = resample.lower()
    if key not in resample_map:
        raise ValueError(f"Unknown resample: {resample}")
    if arr.ndim == 2:
        pil = Image.fromarray(arr)
    elif arr.shape[2] == 4:
        pil = Image.fromarray(arr)
    else:
        pil = Image.fromarray(arr[..., :3])
    out = pil.resize((int(w), int(h)), resample=resample_map[key])
    return np.asarray(out)


def crop(
    image: np.ndarray,
    box: Tuple[int, int, int, int],
) -> np.ndarray:
    """Crop with ``box=(left, top, right, bottom)`` in pixel coords."""
    arr = as_hwc(image)
    left, top, right, bottom = box
    if right <= left or bottom <= top:
        raise ValueError(f"Invalid crop box: {box}")
    return arr[top:bottom, left:right].copy()


def center_crop(image: np.ndarray, size: Size, *, size_hw: bool = False) -> np.ndarray:
    """Center-crop to ``(width, height)`` (or H×W if ``size_hw``)."""
    arr = as_hwc(image)
    h, w = arr.shape[:2]
    if size_hw:
        th, tw = size
    else:
        tw, th = size
    if tw > w or th > h:
        raise ValueError(f"Crop size {(tw, th)} larger than image {(w, h)}")
    left = (w - tw) // 2
    top = (h - th) // 2
    return crop(arr, (left, top, left + tw, top + th))


def pad(
    image: np.ndarray,
    padding: Union[int, Tuple[int, int], Tuple[int, int, int, int]],
    *,
    value: int = 0,
) -> np.ndarray:
    """
    Pad image.

    ``padding`` is ``int``, ``(y, x)``, or ``(top, bottom, left, right)``.
    """
    arr = ensure_uint8(as_hwc(image))
    if isinstance(padding, int):
        top = bottom = left = right = padding
    elif len(padding) == 2:
        top = bottom = int(padding[0])
        left = right = int(padding[1])
    elif len(padding) == 4:
        top, bottom, left, right = (int(x) for x in padding)
    else:
        raise ValueError("padding must be int, (y,x), or (top,bottom,left,right)")
    if arr.ndim == 2:
        return np.pad(arr, ((top, bottom), (left, right)), constant_values=value)
    return np.pad(arr, ((top, bottom), (left, right), (0, 0)), constant_values=value)


def flip(image: np.ndarray, *, horizontal: bool = True, vertical: bool = False) -> np.ndarray:
    """Flip image horizontally and/or vertically."""
    arr = as_hwc(image)
    if horizontal:
        arr = np.ascontiguousarray(arr[:, ::-1])
    if vertical:
        arr = np.ascontiguousarray(arr[::-1, :])
    return arr


def rotate(image: np.ndarray, angle: float, *, expand: bool = True, fill: int = 0) -> np.ndarray:
    """Rotate counterclockwise by ``angle`` degrees (Pillow)."""
    Image = require_pillow()
    arr = ensure_uint8(as_hwc(image))
    if arr.ndim == 2:
        pil = Image.fromarray(arr)
    elif arr.shape[2] == 4:
        pil = Image.fromarray(arr)
    else:
        pil = Image.fromarray(arr[..., :3])
    out = pil.rotate(angle, expand=expand, fillcolor=fill)
    return np.asarray(out)


def letterbox(
    image: np.ndarray,
    size: Size,
    *,
    size_hw: bool = False,
    fill: int = 114,
) -> np.ndarray:
    """
    Resize keeping aspect ratio and pad to target size (YOLO-style letterbox).

    ``size`` is ``(width, height)`` unless ``size_hw=True``.
    """
    arr = ensure_uint8(as_hwc(image))
    h, w = arr.shape[:2]
    if size_hw:
        th, tw = size
    else:
        tw, th = size
    scale = min(tw / w, th / h)
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    resized = resize(arr, (nw, nh))
    canvas = np.full((th, tw) if resized.ndim == 2 else (th, tw, resized.shape[2]), fill, dtype=np.uint8)
    top = (th - nh) // 2
    left = (tw - nw) // 2
    canvas[top : top + nh, left : left + nw] = resized
    return canvas
