"""Classic OpenCV operations: threshold, morphology, contours."""

from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np

from .color import to_gray
from .utils import as_hwc, ensure_uint8, require_cv2


def threshold(
    image: np.ndarray,
    thresh: float = 127.0,
    maxval: float = 255.0,
    *,
    method: str = "binary",
) -> np.ndarray:
    """
    Threshold a grayscale (or converted) image.

    ``method``: ``binary``, ``binary_inv``, ``otsu``, ``tozero``, ``trunc``.
    """
    cv2 = require_cv2()
    gray = to_gray(image)
    methods = {
        "binary": cv2.THRESH_BINARY,
        "binary_inv": cv2.THRESH_BINARY_INV,
        "tozero": cv2.THRESH_TOZERO,
        "trunc": cv2.THRESH_TRUNC,
        "otsu": cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    }
    key = method.lower()
    if key not in methods:
        raise ValueError(f"Unknown threshold method: {method}")
    _, out = cv2.threshold(gray, thresh, maxval, methods[key])
    return out


def morph_open(image: np.ndarray, ksize: int = 3, iterations: int = 1) -> np.ndarray:
    """Morphological opening."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
    return cv2.morphologyEx(arr, cv2.MORPH_OPEN, kernel, iterations=iterations)


def morph_close(image: np.ndarray, ksize: int = 3, iterations: int = 1) -> np.ndarray:
    """Morphological closing."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
    return cv2.morphologyEx(arr, cv2.MORPH_CLOSE, kernel, iterations=iterations)


def dilate(image: np.ndarray, ksize: int = 3, iterations: int = 1) -> np.ndarray:
    """Dilate image."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
    return cv2.dilate(arr, kernel, iterations=iterations)


def erode(image: np.ndarray, ksize: int = 3, iterations: int = 1) -> np.ndarray:
    """Erode image."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
    return cv2.erode(arr, kernel, iterations=iterations)


def find_contours(
    image: np.ndarray,
    *,
    mode: str = "external",
    method: str = "simple",
) -> List[np.ndarray]:
    """
    Find contours on a binary/gray image.

    Returns a list of ``(N, 1, 2)`` or ``(N, 2)`` contour arrays (OpenCV format).
    """
    cv2 = require_cv2()
    gray = to_gray(image)
    # Ensure binary-ish
    if gray.max() > 1 and len(np.unique(gray)) > 2:
        gray = threshold(gray, method="otsu")
    modes = {
        "external": cv2.RETR_EXTERNAL,
        "list": cv2.RETR_LIST,
        "tree": cv2.RETR_TREE,
        "ccomp": cv2.RETR_CCOMP,
    }
    methods = {
        "none": cv2.CHAIN_APPROX_NONE,
        "simple": cv2.CHAIN_APPROX_SIMPLE,
    }
    if mode.lower() not in modes:
        raise ValueError(f"Unknown contour mode: {mode}")
    if method.lower() not in methods:
        raise ValueError(f"Unknown contour method: {method}")
    result = cv2.findContours(gray, modes[mode.lower()], methods[method.lower()])
    # OpenCV 3 vs 4 return signature
    contours = result[0] if len(result) == 2 else result[1]
    return list(contours)


def draw_contours(
    image: np.ndarray,
    contours: Sequence[np.ndarray],
    *,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray:
    """Draw contours onto a copy of ``image`` (converted to BGR for OpenCV)."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image))
    if arr.ndim == 2:
        canvas = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    else:
        canvas = cv2.cvtColor(arr[..., :3], cv2.COLOR_RGB2BGR)
    cv2.drawContours(canvas, list(contours), -1, color[::-1], thickness)
    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
