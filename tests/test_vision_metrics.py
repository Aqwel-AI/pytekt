"""Tests for aion.vision.metrics."""

from __future__ import annotations

import numpy as np

from aion.vision.metrics import mse, psnr, ssim


def test_mse_psnr_identical():
    a = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
    assert mse(a, a) == 0.0
    assert psnr(a, a) == float("inf")


def test_mse_different():
    a = np.zeros((16, 16), dtype=np.uint8)
    b = np.full((16, 16), 255, dtype=np.uint8)
    assert mse(a, b) > 0.5
    assert psnr(a, b) < 10.0


def test_ssim_self():
    a = np.random.randint(0, 255, (48, 48), dtype=np.uint8)
    score = ssim(a, a)
    assert score > 0.99
