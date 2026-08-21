"""
Vision Package
==============

High-performance, NumPy-based computer vision toolkit for image processing,
spatial geometry transforms, array drawing, quality metrics, and OpenCV acceleration.

Subpackages
-----------
- ``pytekt.vision.core``        : Image I/O (read/write), format decoding, shape validation
- ``pytekt.vision.processing``  : Color space conversions (RGB/HSV/Gray) and spatial filters
- ``pytekt.vision.geometry``    : Array transforms (resize, crop, pad, flip, rotate, letterbox)
- ``pytekt.vision.annotation``  : Drawing primitives (boxes, polygons, circles, text)
- ``pytekt.vision.evaluation``  : Image fidelity & quality metrics (MSE, PSNR, SSIM)
- ``pytekt.vision.backends``    : Optional OpenCV accelerations and command-line tools
"""

from __future__ import annotations

import sys

# 1. Domain Subpackages
from . import (
    annotation,
    backends,
    core,
    evaluation,
    geometry,
    processing,
)

# 2. Subpackage Modules
from .annotation import draw
from .backends import cli, opencv_ops
from .core import io, utils
from .evaluation import metrics
from .geometry import transforms
from .processing import color, filters

# 3. Backward-compatible sys.modules aliasing
_MODULE_ALIASES = {
    "pytekt.vision.utils": utils,
    "pytekt.vision.io": io,
    "pytekt.vision.color": color,
    "pytekt.vision.filters": filters,
    "pytekt.vision.transforms": transforms,
    "pytekt.vision.draw": draw,
    "pytekt.vision.metrics": metrics,
    "pytekt.vision.opencv_ops": opencv_ops,
    "pytekt.vision.cli": cli,
}
for _mod_name, _mod_obj in _MODULE_ALIASES.items():
    sys.modules.setdefault(_mod_name, _mod_obj)

# 4. Top-level Curated Function Exports

# Processing (color & filters)
from .processing.color import (
    hsv_to_rgb,
    invert,
    merge_channels,
    rgb_to_hsv,
    split_channels,
    to_gray,
    to_rgb,
)
from .processing.filters import (
    blur,
    canny,
    gaussian_blur,
    median_blur,
    sharpen,
    sobel,
)

# Drawing & Annotation
from .annotation.draw import (
    draw_box,
    draw_boxes,
    draw_circle,
    draw_polyline,
    draw_text,
)

# I/O & Core
from .core.io import (
    decode_image,
    encode_image,
    image_info,
    read_image,
    write_image,
)
from .core.utils import (
    as_hwc,
    ensure_float01,
    ensure_uint8,
    image_shape,
)

# Evaluation Metrics
from .evaluation.metrics import (
    mse,
    psnr,
    ssim,
)

# OpenCV Ops
from .backends.opencv_ops import (
    dilate,
    draw_contours,
    erode,
    find_contours,
    morph_close,
    morph_open,
    threshold,
)

# Geometry Transforms
from .geometry.transforms import (
    center_crop,
    crop,
    flip,
    letterbox,
    pad,
    resize,
    rotate,
)

__all__ = [
    # Subpackages
    "core",
    "processing",
    "geometry",
    "annotation",
    "evaluation",
    "backends",
    # Modules
    "utils",
    "io",
    "color",
    "filters",
    "transforms",
    "draw",
    "metrics",
    "opencv_ops",
    "cli",
    # Core & I/O
    "read_image",
    "write_image",
    "decode_image",
    "encode_image",
    "image_info",
    "as_hwc",
    "ensure_float01",
    "ensure_uint8",
    "image_shape",
    # Color & Filters
    "to_gray",
    "to_rgb",
    "rgb_to_hsv",
    "hsv_to_rgb",
    "invert",
    "split_channels",
    "merge_channels",
    "blur",
    "gaussian_blur",
    "median_blur",
    "sobel",
    "canny",
    "sharpen",
    # Transforms
    "resize",
    "crop",
    "center_crop",
    "pad",
    "flip",
    "rotate",
    "letterbox",
    # Drawing
    "draw_box",
    "draw_boxes",
    "draw_circle",
    "draw_polyline",
    "draw_text",
    # Metrics
    "mse",
    "psnr",
    "ssim",
    # OpenCV
    "threshold",
    "morph_open",
    "morph_close",
    "dilate",
    "erode",
    "find_contours",
    "draw_contours",
]
