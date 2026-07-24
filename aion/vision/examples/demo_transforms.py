"""Demo: resize, flip, letterbox."""

from __future__ import annotations

import numpy as np

from aion.vision import flip, letterbox, resize


def main() -> None:
    img = np.random.randint(0, 255, (120, 200, 3), dtype=np.uint8)
    small = resize(img, (100, 60))
    flipped = flip(small, horizontal=True)
    boxed = letterbox(img, (128, 128))
    print(f"original: {img.shape}")
    print(f"resized:  {small.shape}")
    print(f"flipped:  {flipped.shape}")
    print(f"letterbox:{boxed.shape}")
    print("demo_transforms ok")


if __name__ == "__main__":
    main()
