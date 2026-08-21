"""Demo: Drawing annotations (bounding boxes, circles, polylines, text) on NumPy image arrays."""

from __future__ import annotations

import numpy as np
from pytekt.vision.annotation import (
    draw_box,
    draw_boxes,
    draw_circle,
    draw_polyline,
    draw_text,
)


def main() -> None:
    print("=== PyTekt Vision: Annotations & Drawing Demo ===")

    # 1. Create a dark slate background canvas (H=300, W=400, C=3)
    canvas = np.zeros((300, 400, 3), dtype=np.uint8)
    canvas[:] = [30, 35, 45]

    # 2. Draw single bounding box (left, top, right, bottom)
    box = (40, 40, 180, 160)
    canvas = draw_box(canvas, box, color=(59, 130, 246), width=3)
    print(f"Drew bounding box at {box}")

    # 3. Draw text label
    canvas = draw_text(canvas, "Object: Class A (0.95)", (45, 20), color=(255, 255, 255))
    print("Rendered text label above bounding box")

    # 4. Draw batch boxes
    batch_boxes = [
        (220, 50, 350, 140),
        (100, 180, 260, 270),
    ]
    canvas = draw_boxes(canvas, batch_boxes, color=(16, 185, 129), width=2)
    print(f"Drew batch of {len(batch_boxes)} bounding boxes")

    # 5. Draw circle
    canvas = draw_circle(canvas, (320, 220), radius=35, color=(239, 68, 68), width=3)
    print("Drew circle marker at (320, 220) with radius 35")

    # 6. Draw polyline
    points = [(50, 260), (120, 220), (180, 280), (220, 240)]
    canvas = draw_polyline(canvas, points, color=(245, 158, 11), width=2)
    print(f"Drew polyline connecting {len(points)} vertices")

    print(f"\nFinal annotated image shape: {canvas.shape}, dtype: {canvas.dtype}")
    print("[OK] demo_annotations completed successfully.")


if __name__ == "__main__":
    main()
