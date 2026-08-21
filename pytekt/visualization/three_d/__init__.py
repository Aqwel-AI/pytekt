"""
3D Spatial & Mesh Visualization (Matplotlib)
===========================================

Provides 3D spatial, volumetric, and vector field visualization using Matplotlib:
- 3D scatter, surface, wireframe, and triangulated surface (trisurf) plots
- 3D contour, 3D bar, and 3D vector fields (quiver)
- 3D trajectories, voxel grids, 3D meshes, and 3D density projections
"""

from __future__ import annotations

from .three_d import (
    plot_3d_bar,
    plot_3d_contour,
    plot_3d_density,
    plot_3d_mesh,
    plot_3d_quiver,
    plot_3d_scatter,
    plot_3d_surface,
    plot_3d_trajectory,
    plot_3d_trisurf,
    plot_3d_voxels,
    plot_3d_wireframe,
)

__all__ = [
    "plot_3d_bar",
    "plot_3d_contour",
    "plot_3d_density",
    "plot_3d_mesh",
    "plot_3d_quiver",
    "plot_3d_scatter",
    "plot_3d_surface",
    "plot_3d_trajectory",
    "plot_3d_trisurf",
    "plot_3d_voxels",
    "plot_3d_wireframe",
]
