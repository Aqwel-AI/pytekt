"""Tests for pytekt.vision.io."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("PIL")

from pytekt.vision.io import decode_image, encode_image, image_info, read_image, write_image


def test_write_read_roundtrip(tmp_path):
    img = np.zeros((32, 48, 3), dtype=np.uint8)
    img[..., 0] = 200
    path = tmp_path / "t.png"
    write_image(path, img)
    loaded = read_image(path)
    assert loaded.shape == (32, 48, 3)
    assert loaded.dtype == np.uint8
    np.testing.assert_array_equal(loaded, img)


def test_image_info(tmp_path):
    img = np.zeros((10, 20), dtype=np.uint8)
    path = tmp_path / "g.png"
    write_image(path, img)
    info = image_info(path)
    assert info["width"] == 20
    assert info["height"] == 10
    assert info["mode"] in ("L", "RGB", "RGBA")


def test_encode_decode():
    img = np.random.randint(0, 255, (16, 16, 3), dtype=np.uint8)
    blob = encode_image(img, format="PNG")
    assert isinstance(blob, (bytes, bytearray))
    out = decode_image(blob)
    assert out.shape == (16, 16, 3)


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_image(tmp_path / "nope.png")
