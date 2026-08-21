"""
Vision Image Annotation & Drawing
=================================

Provides drawing primitives directly on NumPy image arrays:
- Bounding boxes (single and batch)
- Polylines, circles, and shapes
- Text rendering on image arrays
"""

from __future__ import annotations

from .draw import (
    draw_box,
    draw_boxes,
    draw_circle,
    draw_polyline,
    draw_text,
)

__all__ = [
    "draw_box",
    "draw_boxes",
    "draw_circle",
    "draw_polyline",
    "draw_text",
]
