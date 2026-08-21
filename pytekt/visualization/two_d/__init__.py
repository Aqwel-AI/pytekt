"""
2D Matrix & Heatmap Visualization
==================================

Provides matrix, grid, and pairwise relation visualizations:
- Matrix heatmaps, annotated cell heatmaps, masked heatmaps
- Confusion matrices (raw counts and normalized percentages)
- Matrix 3D surface projections, 2D contour maps
- Correlation and similarity matrices (cosine, dot-product)
- Attention maps and matrix sparsity visualizations
"""

from __future__ import annotations

from .matrices import (
    plot_attention_map,
    plot_confusion_matrix,
    plot_confusion_matrix_normalized,
    plot_correlation_matrix,
    plot_masked_heatmap,
    plot_matrix_contour,
    plot_matrix_heatmap,
    plot_matrix_histogram,
    plot_matrix_sparsity,
    plot_matrix_surface,
    plot_matrix_with_values,
    plot_similarity_matrix,
)

__all__ = [
    "plot_attention_map",
    "plot_confusion_matrix",
    "plot_confusion_matrix_normalized",
    "plot_correlation_matrix",
    "plot_masked_heatmap",
    "plot_matrix_contour",
    "plot_matrix_heatmap",
    "plot_matrix_histogram",
    "plot_matrix_sparsity",
    "plot_matrix_surface",
    "plot_matrix_with_values",
    "plot_similarity_matrix",
]
