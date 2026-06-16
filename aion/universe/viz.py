"""Cosmos visualizations (requires matplotlib / aqwel-aion[viz])."""

from __future__ import annotations

from typing import Any, List, Optional, Sequence


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError(
            "matplotlib required for aion.universe.viz. Install with: pip install aqwel-aion[viz]"
        ) from e
    return plt


def plot_sky_map(
    ra_hours: Sequence[float],
    dec_deg: Sequence[float],
    *,
    labels: Optional[Sequence[str]] = None,
    magnitudes: Optional[Sequence[float]] = None,
    title: str = "Sky map (equatorial)",
    save_path: Optional[str] = None,
) -> Any:
    """Stereographic-style RA/Dec scatter."""
    plt = _require_matplotlib()
    import numpy as np

    ra = np.asarray(ra_hours) * 15.0
    dec = np.asarray(dec_deg)
    sizes = 80.0
    if magnitudes is not None:
        mag = np.asarray(magnitudes)
        sizes = np.clip(200 - mag * 40, 20, 300)
    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"projection": "aitoff"})
    ax.scatter(np.radians(ra - 180), np.radians(dec), s=sizes, c="cyan", alpha=0.8)
    if labels:
        for r, d, lab in zip(ra, dec, labels):
            ax.text(np.radians(r - 180), np.radians(d), lab, fontsize=7, color="white")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    if save_path:
        fig.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig


def plot_hr_diagram(
    abs_mag: Sequence[float],
    color_index: Sequence[float],
    *,
    title: str = "Hertzsprung-Russell diagram",
    save_path: Optional[str] = None,
) -> Any:
    plt = _require_matplotlib()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(color_index, abs_mag, s=30, alpha=0.7)
    ax.set_xlabel("B - V")
    ax.set_ylabel("Absolute magnitude")
    ax.set_title(title)
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    if save_path:
        fig.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig


def plot_light_curve(
    times: Sequence[float],
    flux: Sequence[float],
    *,
    title: str = "Light curve",
    save_path: Optional[str] = None,
) -> Any:
    plt = _require_matplotlib()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(times, flux, "b.-")
    ax.set_xlabel("Time")
    ax.set_ylabel("Flux")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    if save_path:
        fig.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig


def plot_orbit_2d(
    xs: Sequence[float],
    ys: Sequence[float],
    *,
    title: str = "Orbit (xy plane)",
    save_path: Optional[str] = None,
) -> Any:
    plt = _require_matplotlib()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(xs, ys, "b-")
    ax.plot([0], [0], "yo", markersize=10, label="focus")
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    if save_path:
        fig.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig
