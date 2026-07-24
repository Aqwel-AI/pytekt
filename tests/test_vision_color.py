"""Tests for aion.vision.color."""

from __future__ import annotations

import numpy as np
import pytest

from aion.vision.color import invert, merge_channels, split_channels, to_gray, to_rgb


def test_to_gray_and_rgb():
    rgb = np.zeros((8, 8, 3), dtype=np.uint8)
    rgb[..., 0] = 255
    g = to_gray(rgb)
    assert g.shape == (8, 8)
    assert g.dtype == np.uint8
    back = to_rgb(g)
    assert back.shape == (8, 8, 3)


def test_split_merge_invert():
    img = np.zeros((4, 4, 3), dtype=np.uint8)
    img[..., 1] = 100
    chans = split_channels(img)
    assert len(chans) == 3
    merged = merge_channels(chans)
    np.testing.assert_array_equal(merged, img)
    inv = invert(img)
    assert inv[0, 0, 1] == 155


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("cv2") is None,
    reason="OpenCV not installed",
)
def test_hsv_roundtrip():
    from aion.vision.color import hsv_to_rgb, rgb_to_hsv

    rgb = np.zeros((5, 5, 3), dtype=np.uint8)
    rgb[..., 0] = 200
    rgb[..., 1] = 50
    rgb[..., 2] = 50
    hsv = rgb_to_hsv(rgb)
    back = hsv_to_rgb(hsv)
    assert back.shape == rgb.shape
