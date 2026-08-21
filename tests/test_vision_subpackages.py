"""Tests for pytekt.vision domain subpackages."""

import numpy as np
import pytest
from pytekt.vision import (
    # Subpackages
    core,
    processing,
    geometry,
    annotation,
    evaluation,
    backends,
    # Functions
    to_gray,
    to_rgb,
    gaussian_blur,
    resize,
    crop,
    center_crop,
    draw_box,
    draw_circle,
    mse,
    psnr,
    ssim,
)


def test_vision_subpackages_structure():
    assert hasattr(core, "utils")
    assert hasattr(core, "io")
    assert hasattr(processing, "color")
    assert hasattr(processing, "filters")
    assert hasattr(geometry, "transforms")
    assert hasattr(annotation, "draw")
    assert hasattr(evaluation, "metrics")
    assert hasattr(backends, "opencv_ops")
    assert hasattr(backends, "cli")


def test_processing_color_and_filters():
    img = np.zeros((20, 20, 3), dtype=np.uint8)
    img[5:15, 5:15] = [255, 128, 64]
    
    gray = to_gray(img)
    assert gray.shape == (20, 20, 1) or gray.shape == (20, 20)
    
    blurred = gaussian_blur(img, ksize=3, sigma=1.0)
    assert blurred.shape == (20, 20, 3)


def test_geometry_transforms():
    img = np.ones((40, 60, 3), dtype=np.uint8) * 100
    resized = resize(img, (30, 20))
    assert resized.shape[:2] == (20, 30)
    
    cropped = center_crop(img, (20, 20))
    assert cropped.shape[:2] == (20, 20)


def test_annotation_drawing():
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    annotated = draw_box(img, (10, 10, 30, 30), color=(255, 0, 0), width=2)
    assert annotated.shape == (50, 50, 3)
    
    circle_img = draw_circle(img, (25, 25), radius=10, color=(0, 255, 0))
    assert circle_img.shape == (50, 50, 3)


def test_evaluation_metrics():
    a = np.ones((20, 20, 3), dtype=np.uint8) * 128
    b = np.ones((20, 20, 3), dtype=np.uint8) * 128
    
    assert mse(a, b) == 0.0
    assert psnr(a, b) > 50.0
    assert ssim(a, b) == pytest.approx(1.0)
