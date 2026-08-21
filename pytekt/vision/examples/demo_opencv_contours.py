"""Demo: Classic OpenCV operations: thresholding, morphology, and contour detection."""

from __future__ import annotations

import numpy as np
from pytekt.vision.annotation.draw import draw_circle
from pytekt.vision.backends.opencv_ops import (
    dilate,
    draw_contours,
    erode,
    find_contours,
    morph_close,
    morph_open,
    threshold,
)


def main() -> None:
    print("=== PyTekt Vision: OpenCV Morphology & Contours Demo ===")

    # 1. Create a binary test image with two circles
    canvas = np.zeros((200, 300, 3), dtype=np.uint8)
    canvas = draw_circle(canvas, (80, 100), radius=40, color=(255, 255, 255), width=-1)
    canvas = draw_circle(canvas, (200, 100), radius=50, color=(255, 255, 255), width=-1)

    # 2. Binary Thresholding
    thresh = threshold(canvas, thresh=127, method="binary")
    print(f"Thresholded image shape: {thresh.shape}")

    # 3. Morphological Operations
    opened = morph_open(thresh, ksize=3)
    closed = morph_close(thresh, ksize=3)
    dilated = dilate(thresh, ksize=3)
    eroded = erode(thresh, ksize=3)
    print("Computed morphological open, close, dilate, and erode")

    # 4. Find Contours
    contours = find_contours(thresh, mode="external", method="simple")
    print(f"Detected {len(contours)} contours (expected 2 circles)")

    # 5. Draw Contours onto Canvas
    contour_img = draw_contours(canvas, contours, color=(0, 255, 0), thickness=2)
    print(f"Drawn contours onto image, output shape: {contour_img.shape}")

    print("\n[OK] demo_opencv_contours completed successfully.")


if __name__ == "__main__":
    main()
