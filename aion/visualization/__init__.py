from .arrays import (
    plot_array,
    plot_histogram,
    plot_scatter,
    plot_multiple_arrays,
    plot_array_with_mean,
    plot_running_mean,
    plot_boxplot,
    plot_density,
    plot_cdf,
    plot_error_bars,
    plot_rolling_std,
    plot_min_max_band,
    plot_autocorrelation,
    plot_quantiles,
    plot_scatter_with_fit,
    plot_dual_axis,
)

from .matrices import (
    plot_matrix_heatmap,
    plot_confusion_matrix,
    plot_matrix_surface,
    plot_matrix_contour,
    plot_matrix_with_values,
    plot_correlation_matrix,
    plot_similarity_matrix,
    plot_matrix_histogram,
    plot_masked_heatmap,
    plot_confusion_matrix_normalized,
    plot_attention_map,
    plot_matrix_sparsity,
)

from .training import (
    plot_training_history,
    plot_metric,
    plot_train_vs_val,
    plot_learning_rate,
    plot_metric_with_best,
    plot_metrics_grid,
    plot_confidence_band,
    plot_early_stopping,
    plot_epoch_time,
)

from .three_d import (
    plot_3d_scatter,
    plot_3d_surface,
    plot_3d_wireframe,
    plot_3d_trisurf,
    plot_3d_contour,
    plot_3d_bar,
    plot_3d_quiver,
    plot_3d_trajectory,
    plot_3d_voxels,
    plot_3d_mesh,
    plot_3d_density,
)

try:
    from .seaborn_plots import (
        set_aion_style,
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

try:
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
    _HAS_PLOTLY = True
except ImportError:
    _HAS_PLOTLY = False

from .report import figures_to_html_img_tags, save_figures_pdf

__all__ = [
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
    "plot_training_history",
    "plot_metric",
    "plot_train_vs_val",
    "plot_learning_rate",
    "plot_metric_with_best",
    "plot_metrics_grid",
    "plot_confidence_band",
    "plot_early_stopping",
    "plot_epoch_time",
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
    "save_figures_pdf",
    "figures_to_html_img_tags",
]

if _HAS_SEABORN:
    __all__ += [
        "set_aion_style",
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
