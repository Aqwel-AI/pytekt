# Aion Vision

Computer vision helpers for **image arrays** (NumPy) — I/O, transforms, color, filters, drawing, metrics, and classic OpenCV ops.

> Not for charts/plots. Use [`pytekt.visualization`](../visualization/) for matplotlib/seaborn.

## Install

```bash
pip install 'pytekt[vision]'
# Pillow + opencv-python-headless
```

## Quick start

```python
from pytekt.vision import read_image, write_image, resize, canny, draw_box, psnr

img = read_image("photo.jpg")          # (H, W, 3) uint8 RGB
small = resize(img, (256, 256))
edges = canny(small)
boxed = draw_box(small, (10, 10, 100, 80), color=(255, 0, 0))
write_image("out.png", boxed)
print("PSNR vs self:", psnr(small, small))
```

## CLI

```bash
pytekt vision info photo.jpg
pytekt vision convert in.jpg out.png --mode RGB --size 256x256
pytekt vision edges in.jpg edges.png --t1 80 --t2 160
```

## Modules

| Module | Contents |
|--------|----------|
| `io` | `read_image`, `write_image`, `image_info`, encode/decode bytes |
| `utils` | `ensure_uint8`, `ensure_float01`, `as_hwc`, `image_shape` |
| `color` | gray/RGB/HSV, split/merge, invert |
| `transforms` | resize, crop, pad, flip, rotate, letterbox |
| `filters` | gaussian/box/median blur, sharpen, Sobel, Canny |
| `draw` | boxes, circles, polylines, text (Pillow) |
| `metrics` | MSE, PSNR, SSIM (NumPy) |
| `opencv_ops` | threshold, morphology, contours |

## Examples

```bash
python -m pytekt.vision.examples.demo_read_write
python -m pytekt.vision.examples.demo_transforms
python -m pytekt.vision.examples.demo_edges
```

See [`examples/README.md`](examples/README.md).

## Optional deps

- **Pillow** — I/O, transforms, drawing
- **OpenCV (headless)** — filters, HSV, morphology, contours

Deep-learning loaders / pretrained models stay under `[ai]` (torch / transformers), not this package.
