"""Demo: synthesize, write, read, and compare images."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from aion.vision import decode_image, encode_image, image_info, mse, read_image, write_image


def main() -> None:
    img = np.zeros((64, 96, 3), dtype=np.uint8)
    img[:, :32] = (220, 40, 40)
    img[:, 32:64] = (40, 180, 60)
    img[:, 64:] = (40, 80, 220)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "demo.png"
        write_image(path, img)
        info = image_info(path)
        loaded = read_image(path)
        blob = encode_image(loaded, format="PNG")
        again = decode_image(blob)
        print(f"wrote {path.name}: {info['width']}x{info['height']} mode={info['mode']}")
        print(f"roundtrip MSE: {mse(img, again):.6f}")
        print("demo_read_write ok")


if __name__ == "__main__":
    main()
