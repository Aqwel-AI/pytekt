"""
Interactive Web & 3D Visualization (Plotly)
===========================================

Provides interactive web-ready 3D charts powered by Plotly:
- Interactive 3D scatter, surface, and mesh plots
- 3D volume rendering, vector cones, streamtubes, and isosurfaces
- HTML export and interactive notebook rendering
"""

from __future__ import annotations

from .plotly_viz import (
    plotly_3d_cone,
    plotly_3d_isosurface,
    plotly_3d_mesh,
    plotly_3d_scatter,
    plotly_3d_streamtube,
    plotly_3d_surface,
    plotly_3d_volume,
    save_plotly_html,
    show_plotly,
)

__all__ = [
    "plotly_3d_cone",
    "plotly_3d_isosurface",
    "plotly_3d_mesh",
    "plotly_3d_scatter",
    "plotly_3d_streamtube",
    "plotly_3d_surface",
    "plotly_3d_volume",
    "save_plotly_html",
    "show_plotly",
]
