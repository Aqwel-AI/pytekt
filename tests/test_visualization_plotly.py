"""Tests for Plotly 3D visualization."""

import numpy as np
import pytest

plotly = pytest.importorskip("plotly")

from aion.visualization.plotly_viz import (
    plotly_3d_isosurface,
    plotly_3d_scatter,
    plotly_3d_surface,
    save_plotly_html,
)


def test_plotly_3d_scatter():
    fig = plotly_3d_scatter([1, 2, 3], [4, 5, 6], [7, 8, 9])
    assert fig is not None


def test_plotly_3d_surface():
    x = np.linspace(0, 1, 5)
    y = np.linspace(0, 1, 5)
    X, Y = np.meshgrid(x, y)
    fig = plotly_3d_surface(x, y, X + Y)
    assert fig is not None


def test_save_plotly_html(tmp_path):
    fig = plotly_3d_scatter([1], [2], [3])
    path = tmp_path / "out.html"
    save_plotly_html(fig, str(path))
    assert path.is_file()
