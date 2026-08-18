"""Interactive Plotly 3D visualizations (optional [viz3d] extra)."""

from __future__ import annotations

from typing import Any, Optional, Sequence

import numpy as np

from .utils import require_plotly


def plotly_3d_scatter(
    x: Sequence[float],
    y: Sequence[float],
    z: Sequence[float],
    *,
    title: str = "3D scatter",
    color: Optional[Sequence[float]] = None,
):
    go = require_plotly()
    fig = go.Figure(data=[go.Scatter3d(
        x=list(x), y=list(y), z=list(z),
        mode="markers",
        marker=dict(size=4, color=color or list(z), colorscale="Viridis", showscale=True),
    )])
    fig.update_layout(title=title, template="plotly_dark")
    return fig


def plotly_3d_surface(
    x: Sequence[float],
    y: Sequence[float],
    z: np.ndarray,
    *,
    title: str = "Surface",
):
    go = require_plotly()
    fig = go.Figure(data=[go.Surface(x=list(x), y=list(y), z=z)])
    fig.update_layout(title=title, template="plotly_dark")
    return fig


def plotly_3d_mesh(
    x: Sequence[float],
    y: Sequence[float],
    z: Sequence[float],
    *,
    i: Sequence[int],
    j: Sequence[int],
    k: Sequence[int],
    title: str = "Mesh",
):
    go = require_plotly()
    fig = go.Figure(data=[go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, opacity=0.85)])
    fig.update_layout(title=title, template="plotly_dark")
    return fig


def plotly_3d_volume(
    values: np.ndarray,
    *,
    title: str = "Volume",
):
    go = require_plotly()
    fig = go.Figure(data=go.Volume(value=values.flatten(), opacity=0.2, surface_count=20))
    fig.update_layout(title=title, template="plotly_dark")
    return fig


def plotly_3d_cone(
    x: Sequence[float],
    y: Sequence[float],
    z: Sequence[float],
    u: Sequence[float],
    v: Sequence[float],
    w: Sequence[float],
    *,
    title: str = "Cone field",
):
    go = require_plotly()
    fig = go.Figure(data=go.Cone(x=x, y=y, z=z, u=u, v=v, w=w, colorscale="Blues"))
    fig.update_layout(title=title, template="plotly_dark")
    return fig


def plotly_3d_streamtube(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    w: np.ndarray,
    *,
    title: str = "Streamtube",
):
    go = require_plotly()
    fig = go.Figure(data=go.Streamtube(x=x, y=y, z=z, u=u, v=v, w=w))
    fig.update_layout(title=title, template="plotly_dark")
    return fig


def plotly_3d_isosurface(
    values: np.ndarray,
    *,
    isomin: Optional[float] = None,
    isomax: Optional[float] = None,
    title: str = "Isosurface",
):
    go = require_plotly()
    vmin, vmax = float(np.min(values)), float(np.max(values))
    fig = go.Figure(data=go.Isosurface(
        value=values.flatten(),
        isomin=isomin if isomin is not None else vmin + 0.25 * (vmax - vmin),
        isomax=isomax if isomax is not None else vmax,
        opacity=0.4,
        surface_count=3,
    ))
    fig.update_layout(title=title, template="plotly_dark")
    return fig


def show_plotly(fig: Any) -> None:
    fig.show()


def save_plotly_html(fig: Any, path: str) -> None:
    fig.write_html(path, include_plotlyjs="cdn")
