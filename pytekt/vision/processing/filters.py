"""Image filters: blur, sharpen, edges."""

from __future__ import annotations

import numpy as np

from pytekt.vision.processing.color import to_gray
from pytekt.vision.core.utils import as_hwc, ensure_uint8, require_cv2


def gaussian_blur(image: np.ndarray, ksize: int = 5, sigma: float = 0.0) -> np.ndarray:
    """Gaussian blur via OpenCV. ``ksize`` must be odd and positive."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image))
    k = int(ksize)
    if k < 1 or k % 2 == 0:
        raise ValueError("ksize must be a positive odd integer")
    return cv2.GaussianBlur(arr, (k, k), sigmaX=float(sigma))


def blur(image: np.ndarray, ksize: int = 5) -> np.ndarray:
    """Box blur via OpenCV."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image))
    k = max(1, int(ksize))
    return cv2.blur(arr, (k, k))


def sharpen(image: np.ndarray, amount: float = 1.0) -> np.ndarray:
    """Unsharp-mask style sharpening."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image)).astype(np.float32)
    blurred = cv2.GaussianBlur(arr, (0, 0), 1.0)
    out = cv2.addWeighted(arr, 1.0 + amount, blurred, -amount, 0)
    return np.clip(out, 0, 255).astype(np.uint8)


def sobel(image: np.ndarray, *, dx: int = 1, dy: int = 0, ksize: int = 3) -> np.ndarray:
    """Sobel derivative magnitude (uint8)."""
    cv2 = require_cv2()
    gray = to_gray(image)
    grad = cv2.Sobel(gray, cv2.CV_64F, dx, dy, ksize=ksize)
    mag = np.abs(grad)
    if mag.max() > 0:
        mag = mag / mag.max() * 255.0
    return mag.astype(np.uint8)


def canny(
    image: np.ndarray,
    threshold1: float = 100.0,
    threshold2: float = 200.0,
    *,
    aperture_size: int = 3,
) -> np.ndarray:
    """Canny edge detection (uint8 binary edges)."""
    cv2 = require_cv2()
    gray = to_gray(image)
    return cv2.Canny(gray, threshold1, threshold2, apertureSize=aperture_size)


def median_blur(image: np.ndarray, ksize: int = 5) -> np.ndarray:
    """Median blur (odd ksize)."""
    cv2 = require_cv2()
    arr = ensure_uint8(as_hwc(image))
    k = int(ksize)
    if k < 1 or k % 2 == 0:
        raise ValueError("ksize must be a positive odd integer")
    return cv2.medianBlur(arr, k)
