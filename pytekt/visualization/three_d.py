"""3D plots for ML / teaching (matplotlib; optional [viz] extra)."""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

from .utils import safe_show


def _make_3d_axes(
    figsize: Tuple[float, float] = (8.0, 6.0),
    *,
    elev: float = 25.0,
    azim: float = -60.0,
):
    import matplotlib.pyplot as plt  # pyright: ignore [reportMissingImports]

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    ax.view_init(elev=elev, azim=azim)
    return fig, ax


def plot_3d_scatter(
    x: Sequence[float],
    y: Sequence[float],
    z: Sequence[float],
    *,
    title: str = "3D scatter",
    xlabel: str = "x",
    ylabel: str = "y",
    zlabel: str = "z",
    show: bool = True,
):
    """Scatter in 3D; returns matplotlib Figure."""
    fig, ax = _make_3d_axes()
    ax.scatter(np.asarray(x), np.asarray(y), np.asarray(z))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    safe_show(show)
    return fig


def plot_3d_surface(
    x: Sequence[float],
    y: Sequence[float],
    z: np.ndarray,
    *,
    title: str = "Surface",
    show: bool = True,
):
    """Plot a surface from meshgrid-compatible arrays."""
    xv = np.asarray(x, dtype=float).ravel()
    yv = np.asarray(y, dtype=float).ravel()
    Z = np.asarray(z, dtype=float)
    X, Y = np.meshgrid(xv, yv)
    if Z.shape != X.shape:
        raise ValueError(f"z shape {Z.shape} must match meshgrid {X.shape}")
    fig, ax = _make_3d_axes()
    ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.9)
    ax.set_title(title)
    safe_show(show)
    return fig


def plot_3d_wireframe(
    x: Sequence[float],
    y: Sequence[float],
    z: np.ndarray,
    *,
    title: str = "Wireframe",
    show: bool = True,
):
    xv = np.asarray(x, dtype=float).ravel()
    yv = np.asarray(y, dtype=float).ravel()
    Z = np.asarray(z, dtype=float)
    X, Y = np.meshgrid(xv, yv)
    fig, ax = _make_3d_axes()
    ax.plot_wireframe(X, Y, Z, color="cyan", linewidth=0.5)
    ax.set_title(title)
    safe_show(show)
    return fig


def plot_3d_trisurf(
    x: Sequence[float],
    y: Sequence[float],
    z: Sequence[float],
    *,
    title: str = "Trisurf",
    show: bool = True,
):
    fig, ax = _make_3d_axes()
    ax.plot_trisurf(np.asarray(x), np.asarray(y), np.asarray(z), cmap="viridis", alpha=0.85)
    ax.set_title(title)
    safe_show(show)
    return fig


def plot_3d_contour(
    x: Sequence[float],
    y: Sequence[float],
    z: np.ndarray,
    *,
    title: str = "3D contour",
    show: bool = True,
):
    xv = np.asarray(x, dtype=float).ravel()
    yv = np.asarray(y, dtype=float).ravel()
    Z = np.asarray(z, dtype=float)
    X, Y = np.meshgrid(xv, yv)
    fig, ax = _make_3d_axes()
    ax.contour3D(X, Y, Z, 50, cmap="viridis")
    ax.set_title(title)
    safe_show(show)
    return fig


def plot_3d_bar(
    x: Sequence[float],
    y: Sequence[float],
    z: np.ndarray,
    *,
    title: str = "3D bars",
    show: bool = True,
):
    fig, ax = _make_3d_axes()
    xv = np.asarray(x)
    yv = np.asarray(y)
    Z = np.asarray(z)
    dx = dy = 0.4
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            ax.bar3d(xv[j], yv[i], 0, dx, dy, Z[i, j], shade=True)
    ax.set_title(title)
    safe_show(show)
    return fig


def plot_3d_quiver(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    w: np.ndarray,
    *,
    title: str = "Vector field",
    show: bool = True,
):
    fig, ax = _make_3d_axes()
    ax.quiver(x, y, z, u, v, w, length=0.15, normalize=True)
    ax.set_title(title)
    safe_show(show)
    return fig


def plot_3d_trajectory(
    x: Sequence[float],
    y: Sequence[float],
    z: Sequence[float],
    *,
    colors: Optional[Sequence[float]] = None,
    title: str = "Trajectory",
    show: bool = True,
):
    fig, ax = _make_3d_axes()
    xs, ys, zs = np.asarray(x), np.asarray(y), np.asarray(z)
    if colors is not None:
        ax.scatter(xs, ys, zs, c=colors, cmap="plasma")
    ax.plot(xs, ys, zs, color="white", alpha=0.6)
    ax.set_title(title)
    safe_show(show)
    return fig


def plot_3d_voxels(
    filled: np.ndarray,
    *,
    title: str = "Voxels",
    show: bool = True,
):
    fig, ax = _make_3d_axes()
    ax.voxels(filled.astype(bool), edgecolors="gray")
    ax.set_title(title)
    safe_show(show)
    return fig


def plot_3d_mesh(
    vertices: np.ndarray,
    faces: np.ndarray,
    *,
    title: str = "Mesh",
    show: bool = True,
):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig, ax = _make_3d_axes()
    polys = [[vertices[i] for i in face] for face in faces]
    mesh = Poly3DCollection(polys, alpha=0.7, facecolor="cyan", edgecolor="gray")
    ax.add_collection3d(mesh)
    ax.auto_scale_xyz(vertices[:, 0], vertices[:, 1], vertices[:, 2])
    ax.set_title(title)
    safe_show(show)
    return fig


def plot_3d_density(
    x: Sequence[float],
    y: Sequence[float],
    z: Sequence[float],
    *,
    bins: int = 12,
    title: str = "3D histogram",
    show: bool = True,
):
    fig, ax = _make_3d_axes()
    h, xedges, yedges = np.histogram2d(x, y, bins=bins)
    xpos, ypos = np.meshgrid(xedges[:-1], yedges[:-1], indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = np.zeros_like(xpos)
    dx = dy = (xedges[1] - xedges[0]) * 0.8
    dz = h.ravel()
    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, shade=True)
    ax.set_title(title)
    safe_show(show)
    return fig
