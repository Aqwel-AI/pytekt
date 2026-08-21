"""
Core Visualization Utilities
============================

Shared formatting, figure management, backend safety, and environment check helpers.
"""

from __future__ import annotations

from .utils import (
    close_figure,
    finalize_plot,
    require_plotly,
    require_seaborn,
    safe_show,
    save_plot,
)

__all__ = [
    "close_figure",
    "finalize_plot",
    "require_plotly",
    "require_seaborn",
    "safe_show",
    "save_plot",
]
