"""Image quality metrics (NumPy, no scikit-image)."""

from __future__ import annotations

import numpy as np

from .color import to_gray
from .utils import as_hwc, ensure_float01


def mse(a: np.ndarray, b: np.ndarray) -> float:
    """Mean squared error between two images (float [0,1] scale)."""
    x = ensure_float01(as_hwc(a))
    y = ensure_float01(as_hwc(b))
    if x.shape != y.shape:
        raise ValueError(f"Shape mismatch: {x.shape} vs {y.shape}")
    return float(np.mean((x - y) ** 2))


def psnr(a: np.ndarray, b: np.ndarray, *, data_range: float = 1.0) -> float:
    """Peak signal-to-noise ratio in dB. Returns ``inf`` when images are identical."""
    err = mse(a, b)
    if err <= 0.0:
        return float("inf")
    return float(10.0 * np.log10((data_range ** 2) / err))


def _gaussian_kernel(size: int = 11, sigma: float = 1.5) -> np.ndarray:
    ax = np.arange(size) - size // 2
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    kernel /= kernel.sum()
    return kernel.astype(np.float64)


def _convolve2d(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Simple reflect-padded 2D convolution for single-channel images."""
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(img, ((pad_h, pad_h), (pad_w, pad_w)), mode="reflect")
    out = np.zeros_like(img, dtype=np.float64)
    # Fast-ish via as_strided when available
    try:
        from numpy.lib.stride_tricks import sliding_window_view

        windows = sliding_window_view(padded, (kh, kw))
        out = np.einsum("ijkl,kl->ij", windows, kernel)
    except Exception:
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                out[i, j] = np.sum(padded[i : i + kh, j : j + kw] * kernel)
    return out


def ssim(
    a: np.ndarray,
    b: np.ndarray,
    *,
    data_range: float = 1.0,
    win_size: int = 11,
    k1: float = 0.01,
    k2: float = 0.03,
) -> float:
    """
    Structural similarity (mean SSIM) for grayscale or RGB.

    RGB is converted to grayscale. Pure NumPy implementation (approximate vs skimage).
    """
    x = ensure_float01(to_gray(as_hwc(a))).astype(np.float64)
    y = ensure_float01(to_gray(as_hwc(b))).astype(np.float64)
    if x.shape != y.shape:
        raise ValueError(f"Shape mismatch: {x.shape} vs {y.shape}")
    if min(x.shape) < win_size:
        # Fallback: global stats
        mu_x, mu_y = x.mean(), y.mean()
        sig_x = x.var()
        sig_y = y.var()
        sig_xy = ((x - mu_x) * (y - mu_y)).mean()
        c1 = (k1 * data_range) ** 2
        c2 = (k2 * data_range) ** 2
        num = (2 * mu_x * mu_y + c1) * (2 * sig_xy + c2)
        den = (mu_x**2 + mu_y**2 + c1) * (sig_x + sig_y + c2)
        return float(num / den)

    kernel = _gaussian_kernel(win_size, 1.5)
    mu_x = _convolve2d(x, kernel)
    mu_y = _convolve2d(y, kernel)
    mu_x2 = mu_x**2
    mu_y2 = mu_y**2
    mu_xy = mu_x * mu_y
    sig_x = _convolve2d(x * x, kernel) - mu_x2
    sig_y = _convolve2d(y * y, kernel) - mu_y2
    sig_xy = _convolve2d(x * y, kernel) - mu_xy
    c1 = (k1 * data_range) ** 2
    c2 = (k2 * data_range) ** 2
    num = (2 * mu_xy + c1) * (2 * sig_xy + c2)
    den = (mu_x2 + mu_y2 + c1) * (sig_x + sig_y + c2)
    return float(np.mean(num / den))
