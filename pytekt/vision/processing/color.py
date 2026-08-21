"""Color-space conversions and channel helpers."""

from __future__ import annotations

from typing import List

import numpy as np

from pytekt.vision.core.utils import as_hwc, ensure_uint8, require_cv2


def to_gray(image: np.ndarray) -> np.ndarray:
    """Convert RGB/RGBA/gray image to single-channel grayscale uint8."""
    arr = ensure_uint8(as_hwc(image))
    if arr.ndim == 2:
        return arr
    if arr.shape[2] == 1:
        return arr[..., 0]
    # ITU-R BT.601 luma
    rgb = arr[..., :3].astype(np.float32)
    gray = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    return np.clip(gray, 0, 255).astype(np.uint8)


def to_rgb(image: np.ndarray) -> np.ndarray:
    """Ensure 3-channel RGB uint8."""
    arr = ensure_uint8(as_hwc(image))
    if arr.ndim == 2:
        return np.stack([arr, arr, arr], axis=-1)
    if arr.shape[2] == 1:
        g = arr[..., 0]
        return np.stack([g, g, g], axis=-1)
    if arr.shape[2] >= 3:
        return arr[..., :3]
    raise ValueError(f"Unsupported channel count: {arr.shape}")


def rgb_to_hsv(image: np.ndarray) -> np.ndarray:
    """RGB uint8 → HSV uint8 (OpenCV convention)."""
    cv2 = require_cv2()
    rgb = to_rgb(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return hsv


def hsv_to_rgb(image: np.ndarray) -> np.ndarray:
    """HSV uint8 → RGB uint8 (OpenCV convention)."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image))
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError("HSV image must be HWC with 3 channels")
    bgr = cv2.cvtColor(arr, cv2.COLOR_HSV2BGR)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def split_channels(image: np.ndarray) -> List[np.ndarray]:
    """Split HWC image into a list of 2D channel arrays."""
    arr = as_hwc(image)
    if arr.ndim == 2:
        return [arr]
    return [arr[..., i] for i in range(arr.shape[2])]


def merge_channels(channels: List[np.ndarray]) -> np.ndarray:
    """Merge 2D channel arrays into an HWC image."""
    if not channels:
        raise ValueError("Need at least one channel")
    if len(channels) == 1:
        return np.asarray(channels[0])
    return np.stack([np.asarray(c) for c in channels], axis=-1)


def invert(image: np.ndarray) -> np.ndarray:
    """Photographic negative (uint8)."""
    arr = ensure_uint8(as_hwc(image))
    return (255 - arr).astype(np.uint8)
