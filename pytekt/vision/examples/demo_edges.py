"""Demo: Canny edges + contour count."""

from __future__ import annotations

import numpy as np

from pytekt.vision import canny, draw_box, find_contours, threshold


def main() -> None:
    img = np.zeros((128, 128, 3), dtype=np.uint8)
    img[30:90, 30:90] = (240, 240, 240)
    img = draw_box(img, (20, 20, 100, 100), color=(255, 0, 0), width=3)
    edges = canny(img, 50, 150)
    binary = threshold(edges, method="binary")
    contours = find_contours(binary)
    print(f"edges nonzero: {int(np.count_nonzero(edges))}")
    print(f"contours: {len(contours)}")
    print("demo_edges ok")


if __name__ == "__main__":
    main()
