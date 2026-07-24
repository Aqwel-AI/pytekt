"""Array dtype/range helpers for vision pipelines."""

from __future__ import annotations

from typing import Tuple

import numpy as np


def as_hwc(image: np.ndarray) -> np.ndarray:
    """Ensure image is HWC (or HW for grayscale). Accepts CHW when C in {1,3,4}."""
    arr = np.asarray(image)
    if arr.ndim == 2:
        return arr
    if arr.ndim != 3:
        raise ValueError(f"Expected HW or HWC image, got shape {arr.shape}")
    h, w, c = arr.shape
    if c in (1, 3, 4):
        return arr
    # Likely CHW
    if arr.shape[0] in (1, 3, 4):
        return np.transpose(arr, (1, 2, 0))
    return arr


def ensure_uint8(image: np.ndarray) -> np.ndarray:
    """Convert float [0,1] or other arrays to uint8 [0,255]."""
    arr = as_hwc(np.asarray(image))
    if arr.dtype == np.uint8:
        return arr
    if np.issubdtype(arr.dtype, np.floating):
        mx = float(np.nanmax(arr)) if arr.size else 0.0
        if mx <= 1.0 + 1e-6:
            arr = arr * 255.0
        return np.clip(arr, 0, 255).astype(np.uint8)
    return np.clip(arr, 0, 255).astype(np.uint8)


def ensure_float01(image: np.ndarray) -> np.ndarray:
    """Convert image to float32 in [0, 1]."""
    arr = as_hwc(np.asarray(image)).astype(np.float32)
    if arr.size and float(np.nanmax(arr)) > 1.0 + 1e-6:
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def image_shape(image: np.ndarray) -> Tuple[int, int, int]:
    """Return (H, W, C) with C=1 for grayscale."""
    arr = as_hwc(image)
    if arr.ndim == 2:
        h, w = arr.shape
        return h, w, 1
    h, w, c = arr.shape
    return int(h), int(w), int(c)


def require_pillow():
    """Import Pillow or raise a helpful error."""
    try:
        from PIL import Image  # type: ignore

        return Image
    except ImportError as exc:
        raise ImportError(
            "Pillow is required for this vision operation. "
            "Install with: pip install 'aqwel-aion[vision]' or pip install pillow"
        ) from exc


def require_cv2():
    """Import OpenCV or raise a helpful error."""
    try:
        import cv2  # type: ignore

        return cv2
    except ImportError as exc:
        raise ImportError(
            "OpenCV is required for this vision operation. "
            "Install with: pip install 'aqwel-aion[vision]' "
            "or pip install opencv-python-headless"
        ) from exc
