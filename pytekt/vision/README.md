# PyTekt Vision — Computer Vision & Image Processing Toolkit

High-performance, NumPy-first computer vision toolkit for image processing, spatial geometry transforms, annotation drawing, quality metrics, and OpenCV hardware acceleration.

---

## 1. Architecture & Domain Taxonomy

The package is organized into 6 modular domain subpackages:

```
pytekt/vision/
├── core/                # Image I/O (read/write), format decoding, shape validation, type conversions
├── processing/          # Color space transforms (RGB/HSV/Gray) and spatial filters (Gaussian, Sobel, Canny)
├── geometry/            # Spatial transforms (resize, crop, center_crop, pad, flip, rotate, letterbox)
├── annotation/          # Drawing primitives on image arrays (bounding boxes, polygons, circles, text)
├── evaluation/          # Image fidelity & reconstruction metrics (MSE, PSNR, SSIM)
├── backends/            # Optional OpenCV accelerations (threshold, morphology, contours) & CLI
└── __init__.py          # Unified entry point & backward compatibility aliases
```

### Domain Subpackage Reference

| Subpackage | Key Exports | Primary Use Cases |
|---|---|---|
| **`pytekt.vision.core`** | `read_image`, `write_image`, `decode_image`, `encode_image`, `image_info`, `as_hwc`, `ensure_uint8` | Loading & saving images, type casting, array channel normalization |
| **`pytekt.vision.processing`** | `to_gray`, `to_rgb`, `rgb_to_hsv`, `hsv_to_rgb`, `gaussian_blur`, `canny`, `sobel`, `sharpen` | Color grading, edge detection, blurring, feature preprocessing |
| **`pytekt.vision.geometry`** | `resize`, `crop`, `center_crop`, `pad`, `flip`, `rotate`, `letterbox` | Dataset augmentation, model input preparation, aspect ratio handling |
| **`pytekt.vision.annotation`** | `draw_box`, `draw_boxes`, `draw_circle`, `draw_polyline`, `draw_text` | Visualizing object detections, keypoints, segmentation overlays |
| **`pytekt.vision.evaluation`** | `mse`, `psnr`, `ssim` | Model output fidelity, compression loss, image reconstruction evaluation |
| **`pytekt.vision.backends`** | `threshold`, `morph_open`, `morph_close`, `dilate`, `erode`, `find_contours`, `draw_contours`, `vision_main` | Binary mask operations, morphological filtering, contour extraction |

---

## 2. Quick Start

### 2.1 Domain Subpackage Imports (Recommended)

```python
from pytekt.vision.core import read_image, write_image
from pytekt.vision.geometry import resize, center_crop
from pytekt.vision.processing import to_gray, canny
from pytekt.vision.annotation import draw_box
from pytekt.vision.evaluation import psnr

# 1. Load image as (H, W, 3) uint8 NumPy array
img = read_image("sample.jpg")

# 2. Geometric transforms & cropping
small = resize(img, (256, 256))
cropped = center_crop(small, (224, 224))

# 3. Processing & Edge detection
edges = canny(cropped, 100, 200)

# 4. Draw bounding box annotation
boxed = draw_box(cropped, [20, 20, 100, 120], color=(255, 0, 0), thickness=2)
write_image("output_annotated.png", boxed)

# 5. Quality Metrics
print(f"Image Reconstruction PSNR: {psnr(cropped, cropped):.2f} dB")
```

---

## 3. CLI

```bash
# Get image metadata
pytekt vision info photo.jpg

# Convert format and resize
pytekt vision convert in.jpg out.png --mode RGB --size 256x256

# Edge detection
pytekt vision edges in.jpg edges.png --t1 80 --t2 160
```
