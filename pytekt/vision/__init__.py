#!/usr/bin/env python3
"""
Computer vision utilities for Aion.

Image arrays (NumPy) — not plotting. For matplotlib charts see ``aion.visualization``.

Install: ``pip install 'pytekt[vision]'``
"""

from .color import hsv_to_rgb, invert, merge_channels, rgb_to_hsv, split_channels, to_gray, to_rgb
from .draw import draw_box, draw_boxes, draw_circle, draw_polyline, draw_text
from .filters import blur, canny, gaussian_blur, median_blur, sharpen, sobel
from .io import decode_image, encode_image, image_info, read_image, write_image
from .metrics import mse, psnr, ssim
from .opencv_ops import (
    dilate,
    draw_contours,
    erode,
    find_contours,
    morph_close,
    morph_open,
    threshold,
)
from .transforms import center_crop, crop, flip, letterbox, pad, resize, rotate
from .utils import as_hwc, ensure_float01, ensure_uint8, image_shape

__all__ = [
    # io
    "read_image",
    "write_image",
    "image_info",
    "encode_image",
    "decode_image",
    # utils
    "as_hwc",
    "ensure_uint8",
    "ensure_float01",
    "image_shape",
    # color
    "to_gray",
    "to_rgb",
    "rgb_to_hsv",
    "hsv_to_rgb",
    "split_channels",
    "merge_channels",
    "invert",
    # transforms
    "resize",
    "crop",
    "center_crop",
    "pad",
    "flip",
    "rotate",
    "letterbox",
    # filters
    "gaussian_blur",
    "blur",
    "sharpen",
    "sobel",
    "canny",
    "median_blur",
    # draw
    "draw_box",
    "draw_boxes",
    "draw_circle",
    "draw_polyline",
    "draw_text",
    # metrics
    "mse",
    "psnr",
    "ssim",
    # opencv
    "threshold",
    "morph_open",
    "morph_close",
    "dilate",
    "erode",
    "find_contours",
    "draw_contours",
]
