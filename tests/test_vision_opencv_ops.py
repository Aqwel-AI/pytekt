"""Tests for aion.vision OpenCV-backed ops."""

from __future__ import annotations

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from aion.vision.filters import canny, gaussian_blur
from aion.vision.opencv_ops import find_contours, morph_open, threshold


def test_blur_and_canny():
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    img[16:48, 16:48] = 255
    blurred = gaussian_blur(img, 5)
    assert blurred.shape == img.shape
    edges = canny(img, 50, 150)
    assert edges.shape == (64, 64)
    assert edges.dtype == np.uint8


def test_threshold_morph_contours():
    img = np.zeros((80, 80), dtype=np.uint8)
    img[20:60, 20:60] = 255
    binary = threshold(img, method="binary")
    opened = morph_open(binary, 3)
    contours = find_contours(opened)
    assert len(contours) >= 1
