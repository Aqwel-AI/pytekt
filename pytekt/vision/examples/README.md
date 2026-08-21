# PyTekt Vision — Examples

Runnable examples demonstrating image I/O, geometric transformations, spatial filtering, bounding box and text annotation, quantitative quality metrics, and OpenCV contour operations.

---

## 📚 Example Demos

| Script | Domain | Description | Run Command |
|---|---|---|---|
| [`demo_read_write.py`](demo_read_write.py) | **Core / I/O** | Image file read/write, base64 encoding/decoding, and format inspection. | `python -m pytekt.vision.examples.demo_read_write` |
| [`demo_transforms.py`](demo_transforms.py) | **Geometry** | Resizing, center cropping, padding, flipping, rotating, and letterboxing. | `python -m pytekt.vision.examples.demo_transforms` |
| [`demo_edges.py`](demo_edges.py) | **Processing** | Canny edge detection, Sobel gradients, and Gaussian blurring. | `python -m pytekt.vision.examples.demo_edges` |
| [`demo_annotations.py`](demo_annotations.py) | **Annotation** | Drawing bounding boxes, text labels, circles, and polylines on NumPy arrays. | `python -m pytekt.vision.examples.demo_annotations` |
| [`demo_metrics_evaluation.py`](demo_metrics_evaluation.py) | **Evaluation** | Measuring image fidelity with MSE, PSNR, and SSIM under noise and blur. | `python -m pytekt.vision.examples.demo_metrics_evaluation` |
| [`demo_opencv_contours.py`](demo_opencv_contours.py) | **Backends** | Otsu thresholding, morphological filtering (open, close, dilate, erode), and contour extraction. | `python -m pytekt.vision.examples.demo_opencv_contours` |

---

## 🚀 Running All Vision Demos

```bash
python -m pytekt.vision.examples.demo_read_write
python -m pytekt.vision.examples.demo_transforms
python -m pytekt.vision.examples.demo_edges
python -m pytekt.vision.examples.demo_annotations
python -m pytekt.vision.examples.demo_metrics_evaluation
python -m pytekt.vision.examples.demo_opencv_contours
```
