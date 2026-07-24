"""Drawing primitives on images (Pillow)."""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple, Union

import numpy as np

from .utils import as_hwc, ensure_uint8, require_pillow

Color = Union[int, Tuple[int, ...]]
Box = Tuple[int, int, int, int]  # left, top, right, bottom


def _to_pil(image: np.ndarray):
    Image = require_pillow()
    arr = ensure_uint8(as_hwc(image))
    if arr.ndim == 2:
        return Image.fromarray(arr), arr
    if arr.shape[2] == 4:
        return Image.fromarray(arr), arr
    return Image.fromarray(arr[..., :3]), arr


def _normalize_color(color: Color, mode: str) -> Color:
    if mode == "L":
        if isinstance(color, tuple):
            return int(color[0])
        return int(color)
    if isinstance(color, int):
        return (color, color, color) if mode == "RGB" else (color, color, color, 255)
    if mode == "RGB":
        return tuple(int(c) for c in color[:3])  # type: ignore[return-value]
    # RGBA
    if len(color) == 3:
        return (int(color[0]), int(color[1]), int(color[2]), 255)
    return tuple(int(c) for c in color[:4])  # type: ignore[return-value]


def draw_box(
    image: np.ndarray,
    box: Box,
    *,
    color: Color = (255, 0, 0),
    width: int = 2,
) -> np.ndarray:
    """Draw an axis-aligned rectangle. ``box=(left, top, right, bottom)``."""
    from PIL import ImageDraw as ID  # type: ignore

    pil, _ = _to_pil(image)
    draw = ID.Draw(pil)
    c = _normalize_color(color, pil.mode)
    draw.rectangle(box, outline=c, width=max(1, int(width)))
    return np.asarray(pil)


def draw_boxes(
    image: np.ndarray,
    boxes: Sequence[Box],
    *,
    color: Color = (255, 0, 0),
    width: int = 2,
) -> np.ndarray:
    """Draw multiple rectangles."""
    out = image
    for box in boxes:
        out = draw_box(out, box, color=color, width=width)
    return out


def draw_circle(
    image: np.ndarray,
    center: Tuple[int, int],
    radius: int,
    *,
    color: Color = (0, 255, 0),
    width: int = 2,
    fill: Optional[Color] = None,
) -> np.ndarray:
    """Draw a circle. ``center=(x, y)``."""
    from PIL import ImageDraw as ID  # type: ignore

    pil, _ = _to_pil(image)
    draw = ID.Draw(pil)
    x, y = center
    r = int(radius)
    bbox = (x - r, y - r, x + r, y + r)
    outline = _normalize_color(color, pil.mode)
    fill_c = _normalize_color(fill, pil.mode) if fill is not None else None
    draw.ellipse(bbox, outline=outline, width=max(1, int(width)), fill=fill_c)
    return np.asarray(pil)


def draw_polyline(
    image: np.ndarray,
    points: Sequence[Tuple[int, int]],
    *,
    color: Color = (0, 0, 255),
    width: int = 2,
    closed: bool = False,
) -> np.ndarray:
    """Draw a polyline through ``points`` as ``(x, y)`` pairs."""
    from PIL import ImageDraw as ID  # type: ignore

    if len(points) < 2:
        return ensure_uint8(as_hwc(image))
    pil, _ = _to_pil(image)
    draw = ID.Draw(pil)
    c = _normalize_color(color, pil.mode)
    pts: List[Tuple[int, int]] = [(int(x), int(y)) for x, y in points]
    if closed:
        draw.polygon(pts, outline=c)
    else:
        draw.line(pts, fill=c, width=max(1, int(width)))
    return np.asarray(pil)


def draw_text(
    image: np.ndarray,
    text: str,
    xy: Tuple[int, int] = (5, 5),
    *,
    color: Color = (255, 255, 255),
    font_size: int = 16,
) -> np.ndarray:
    """Draw text at ``xy=(x, y)`` using a default bitmap/truetype font."""
    from PIL import ImageDraw as ID  # type: ignore
    from PIL import ImageFont  # type: ignore

    pil, _ = _to_pil(image)
    draw = ID.Draw(pil)
    c = _normalize_color(color, pil.mode)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except OSError:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
    draw.text(xy, text, fill=c, font=font)
    return np.asarray(pil)
