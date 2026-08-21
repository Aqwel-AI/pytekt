"""
Vision Core Utilities & I/O
===========================

Provides image input/output, decoding/encoding, and array shape normalizations:
- Image reading and writing (JPEG, PNG, WebP)
- Array validation and channel normalization (HWC format)
- Float01 / Uint8 data type conversions
- Base64 encoding and decoding
"""

from __future__ import annotations

from .io import (
    decode_image,
    encode_image,
    image_info,
    read_image,
    write_image,
)
from .utils import (
    as_hwc,
    ensure_float01,
    ensure_uint8,
    image_shape,
    require_cv2,
    require_pillow,
)

__all__ = [
    "read_image",
    "write_image",
    "decode_image",
    "encode_image",
    "image_info",
    "as_hwc",
    "ensure_float01",
    "ensure_uint8",
    "image_shape",
    "require_pillow",
    "require_cv2",
]
