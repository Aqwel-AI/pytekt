"""
Visualization Package
=====================

Domain-structured, high-performance visualization suite for scientific computing,
machine learning diagnostics, matrix analysis, 3D rendering, statistical plots,
and publication reports.

Subpackages
-----------
- ``pytekt.visualization.one_d``        : 1D sequence, distribution, uncertainty, and rolling statistical plots
- ``pytekt.visualization.two_d``        : 2D matrix analysis, heatmaps, attention maps, and confusion matrices
- ``pytekt.visualization.ml_eval``      : Model training curves, learning rate, ROC, PR, calibration, residuals
- ``pytekt.visualization.three_d``      : Matplotlib 3D spatial, volumetric, and vector field visualizations
- ``pytekt.visualization.interactive``  : Interactive Web 3D charts with Plotly
- ``pytekt.visualization.statistical``  : Statistical plots and research styling with Seaborn
- ``pytekt.visualization.reporting``    : Multi-page PDF generation and HTML dashboard embedding
- ``pytekt.visualization.core``         : Figure management, display safety, and backend utilities
"""

from __future__ import annotations

import sys

# 1. Domain Subpackages
from . import (
    core,
    interactive,
    ml_eval,
    one_d,
    reporting,
    statistical,
    three_d as three_d_pkg,
    two_d,
)

# 2. Subpackage Modules
from .core import utils
from .interactive import plotly_viz
from .ml_eval import classification, training
from .one_d import arrays
from .reporting import report
from .statistical import seaborn_plots
from .three_d import three_d as three_d_module
from .two_d import matrices

# 3. Backward-compatible sys.modules aliasing
_MODULE_ALIASES = {
    "pytekt.visualization.utils": utils,
    "pytekt.visualization.arrays": arrays,
    "pytekt.visualization.matrices": matrices,
    "pytekt.visualization.training": training,
    "pytekt.visualization.classification": classification,
    "pytekt.visualization.three_d": three_d_module,
    "pytekt.visualization.plotly_viz": plotly_viz,
    "pytekt.visualization.seaborn_plots": seaborn_plots,
    "pytekt.visualization.report": report,
}
for _mod_name, _mod_obj in _MODULE_ALIASES.items():
    sys.modules.setdefault(_mod_name, _mod_obj)

# 4. Top-level Curated Exports

# One-dimensional Plots (arrays)
from .one_d.arrays import (
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

# Two-dimensional Matrix Plots (matrices)
from .two_d.matrices import (
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

# ML Training & Diagnostics (training & classification)
from .ml_eval.training import (
    plot_confidence_band,
    plot_early_stopping,
    plot_epoch_time,
    plot_learning_rate,
    plot_metric,
    plot_metric_with_best,
    plot_metrics_grid,
    plot_train_vs_val,
    plot_training_history,
)
from .ml_eval.classification import (
    plot_calibration_curve,
    plot_class_distribution,
    plot_pr_curve,
    plot_residuals,
    plot_roc_curve,
)

# Matplotlib 3D Plots
from .three_d.three_d import (
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

# Reporting & Export
from .reporting.report import (
    figures_to_html_img_tags,
    save_figures_pdf,
)

# Core Helpers
from .core.utils import (
    close_figure,
    finalize_plot,
    safe_show,
    save_plot,
)

# Optional Seaborn Visualizations
try:
    from .statistical.seaborn_plots import (
        set_pytekt_style,
        sns_boxplot,
        sns_clustermap,
        sns_displot,
        sns_heatmap,
        sns_jointplot,
        sns_kdeplot,
        sns_lmplot,
        sns_pairplot,
        sns_regplot,
        sns_relplot,
        sns_stripplot,
        sns_swarmplot,
        sns_violinplot,
    )
    _HAS_SEABORN = True
except ImportError:
    _HAS_SEABORN = False

# Optional Plotly Interactive Visualizations
try:
    from .interactive.plotly_viz import (
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
    _HAS_PLOTLY = True
except ImportError:
    _HAS_PLOTLY = False

__all__ = [
    # Subpackages
    "core",
    "one_d",
    "two_d",
    "ml_eval",
    "three_d_pkg",
    "interactive",
    "statistical",
    "reporting",
    # Modules
    "utils",
    "arrays",
    "matrices",
    "training",
    "classification",
    "three_d_module",
    "plotly_viz",
    "seaborn_plots",
    "report",
    # Core Helpers
    "save_plot",
    "close_figure",
    "finalize_plot",
    "safe_show",
    # 1D Plots
    "plot_array",
    "plot_histogram",
    "plot_scatter",
    "plot_multiple_arrays",
    "plot_array_with_mean",
    "plot_running_mean",
    "plot_boxplot",
    "plot_density",
    "plot_cdf",
    "plot_error_bars",
    "plot_rolling_std",
    "plot_min_max_band",
    "plot_autocorrelation",
    "plot_quantiles",
    "plot_scatter_with_fit",
    "plot_dual_axis",
    # 2D Matrix Plots
    "plot_matrix_heatmap",
    "plot_confusion_matrix",
    "plot_matrix_surface",
    "plot_matrix_contour",
    "plot_matrix_with_values",
    "plot_correlation_matrix",
    "plot_similarity_matrix",
    "plot_matrix_histogram",
    "plot_masked_heatmap",
    "plot_confusion_matrix_normalized",
    "plot_attention_map",
    "plot_matrix_sparsity",
    # ML & Diagnostics
    "plot_training_history",
    "plot_metric",
    "plot_train_vs_val",
    "plot_learning_rate",
    "plot_metric_with_best",
    "plot_metrics_grid",
    "plot_confidence_band",
    "plot_early_stopping",
    "plot_epoch_time",
    "plot_roc_curve",
    "plot_pr_curve",
    "plot_calibration_curve",
    "plot_class_distribution",
    "plot_residuals",
    # 3D Plots
    "plot_3d_scatter",
    "plot_3d_surface",
    "plot_3d_wireframe",
    "plot_3d_trisurf",
    "plot_3d_contour",
    "plot_3d_bar",
    "plot_3d_quiver",
    "plot_3d_trajectory",
    "plot_3d_voxels",
    "plot_3d_mesh",
    "plot_3d_density",
    # Reporting
    "save_figures_pdf",
    "figures_to_html_img_tags",
]

if _HAS_SEABORN:
    __all__ += [
        "set_pytekt_style",
        "sns_heatmap",
        "sns_kdeplot",
        "sns_boxplot",
        "sns_violinplot",
        "sns_stripplot",
        "sns_swarmplot",
        "sns_regplot",
        "sns_jointplot",
        "sns_pairplot",
        "sns_clustermap",
        "sns_displot",
        "sns_relplot",
        "sns_lmplot",
    ]

if _HAS_PLOTLY:
    __all__ += [
        "plotly_3d_scatter",
        "plotly_3d_surface",
        "plotly_3d_mesh",
        "plotly_3d_volume",
        "plotly_3d_cone",
        "plotly_3d_streamtube",
        "plotly_3d_isosurface",
        "show_plotly",
        "save_plotly_html",
    ]
