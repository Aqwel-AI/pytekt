"""Tests for aion.vision.transforms."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("PIL")

from aion.vision.transforms import center_crop, crop, flip, letterbox, pad, resize, rotate


def test_resize_shape():
    img = np.zeros((40, 60, 3), dtype=np.uint8)
    out = resize(img, (30, 20))
    assert out.shape == (20, 30, 3)


def test_resize_size_hw():
    img = np.zeros((40, 60, 3), dtype=np.uint8)
    out = resize(img, (20, 30), size_hw=True)
    assert out.shape == (20, 30, 3)


def test_crop_and_center():
    img = np.arange(100, dtype=np.uint8).reshape(10, 10)
    c = crop(img, (2, 2, 6, 7))
    assert c.shape == (5, 4)
    cc = center_crop(img, (4, 4))
    assert cc.shape == (4, 4)


def test_flip_pad_rotate_letterbox():
    img = np.zeros((20, 30, 3), dtype=np.uint8)
    img[0, 0] = (1, 2, 3)
    f = flip(img, horizontal=True)
    assert f.shape == img.shape
    assert tuple(f[0, -1]) == (1, 2, 3)
    p = pad(img, 2, value=7)
    assert p.shape == (24, 34, 3)
    r = rotate(img, 90)
    assert r.ndim == 3
    lb = letterbox(img, (64, 64))
    assert lb.shape == (64, 64, 3)
