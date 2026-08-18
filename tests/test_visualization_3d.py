"""Tests for matplotlib 3D plots."""

import numpy as np

from pytekt.visualization.three_d import (
    plot_3d_contour,
    plot_3d_scatter,
    plot_3d_surface,
    plot_3d_wireframe,
)


def test_3d_scatter():
    fig = plot_3d_scatter([1, 2], [3, 4], [5, 6], show=False)
    assert fig is not None


def test_3d_surface():
    x = np.linspace(-1, 1, 10)
    y = np.linspace(-1, 1, 10)
    X, Y = np.meshgrid(x, y)
    Z = X ** 2 + Y ** 2
    fig = plot_3d_surface(x, y, Z, show=False)
    assert fig is not None


def test_3d_wireframe_and_contour():
    x = np.linspace(-1, 1, 8)
    y = np.linspace(-1, 1, 8)
    X, Y = np.meshgrid(x, y)
    Z = X * Y
    assert plot_3d_wireframe(x, y, Z, show=False) is not None
    assert plot_3d_contour(x, y, Z, show=False) is not None
