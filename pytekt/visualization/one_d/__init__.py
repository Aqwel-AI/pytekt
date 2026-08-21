"""
1D Sequence & Distribution Visualization
=========================================

Provides 1D sequence, distribution, uncertainty, and rolling statistical plots:
- Line plots, histograms, scatter plots, multi-array plots
- Running mean, boxplots, density (KDE), CDF
- Error bars, rolling standard deviation, min-max bands
- Autocorrelation, quantiles, scatter with linear fit, dual y-axis
"""

from __future__ import annotations

from .arrays import (
    plot_array,
    plot_array_with_mean,
    plot_autocorrelation,
    plot_boxplot,
    plot_cdf,
    plot_density,
    plot_dual_axis,
    plot_error_bars,
    plot_histogram,
    plot_min_max_band,
    plot_multiple_arrays,
    plot_quantiles,
    plot_rolling_std,
    plot_running_mean,
    plot_scatter,
    plot_scatter_with_fit,
)

__all__ = [
    "plot_array",
    "plot_array_with_mean",
    "plot_autocorrelation",
    "plot_boxplot",
    "plot_cdf",
    "plot_density",
    "plot_dual_axis",
    "plot_error_bars",
    "plot_histogram",
    "plot_min_max_band",
    "plot_multiple_arrays",
    "plot_quantiles",
    "plot_rolling_std",
    "plot_running_mean",
    "plot_scatter",
    "plot_scatter_with_fit",
]
