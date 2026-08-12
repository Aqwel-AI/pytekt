"""CLI smoke tests for aion vision."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("PIL")

from pytekt.vision.cli import build_vision_parser, vision_main
from pytekt.vision.io import write_image


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    build_vision_parser(p)
    return p


def test_vision_info_cli(tmp_path, capsys):
    img = np.zeros((12, 18, 3), dtype=np.uint8)
    path = tmp_path / "x.png"
    write_image(path, img)
    args = _parser().parse_args(["info", str(path)])
    vision_main(args)
    out = capsys.readouterr().out
    assert "width: 18" in out
    assert "height: 12" in out


def test_vision_convert_cli(tmp_path, capsys):
    img = np.zeros((40, 40, 3), dtype=np.uint8)
    src = tmp_path / "in.png"
    dst = tmp_path / "out.png"
    write_image(src, img)
    args = _parser().parse_args(["convert", str(src), str(dst), "--size", "20x10"])
    vision_main(args)
    assert dst.is_file()
    assert "wrote" in capsys.readouterr().out


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("cv2") is None,
    reason="OpenCV not installed",
)
def test_vision_edges_cli(tmp_path, capsys):
    img = np.zeros((32, 32, 3), dtype=np.uint8)
    img[8:24, 8:24] = 255
    src = tmp_path / "in.png"
    dst = tmp_path / "edges.png"
    write_image(src, img)
    args = _parser().parse_args(["edges", str(src), str(dst)])
    vision_main(args)
    assert Path(dst).is_file()
