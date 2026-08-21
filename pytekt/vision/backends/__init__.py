"""
Vision Backends & CLI
=====================

Provides OpenCV acceleration operations and command-line interfaces:
- Thresholding (binary, otsu, trunc, tozero)
- Morphological operations (morph_open, morph_close, dilate, erode)
- Contour finding and drawing
- CLI entry point
"""

from __future__ import annotations

from .cli import vision_main
from .opencv_ops import (
    dilate,
    draw_contours,
    erode,
    find_contours,
    morph_close,
    morph_open,
    threshold,
)

main = vision_main

__all__ = [
    "threshold",
    "morph_open",
    "morph_close",
    "dilate",
    "erode",
    "find_contours",
    "draw_contours",
    "vision_main",
    "main",
]
