# pytekt.visualization — Example Notebooks

This folder contains runnable Jupyter notebooks demonstrating the **`pytekt.visualization`** suite across all domain categories: 1D distributions, 2D matrix analytics, model training, ML diagnostics, 3D spatial plots, Seaborn statistical styling, interactive Plotly charts, and report generation.

---

## 📚 Complete Notebook Catalog

| # | Notebook | Domain | Key Demonstrated Functions |
|---|---|---|---|
| **01** | [`01_array_visualization.ipynb`](01_array_visualization.ipynb) | **1D Sequences & Distributions** | `plot_array`, `plot_histogram`, `plot_scatter`, `plot_multiple_arrays`, `plot_running_mean`, `plot_boxplot`, `plot_density`, `plot_cdf`, `plot_error_bars`, `plot_rolling_std`, `plot_quantiles`, `plot_dual_axis` |
| **02** | [`02_matrix_visualization.ipynb`](02_matrix_visualization.ipynb) | **2D Matrix Analysis** | `plot_matrix_heatmap`, `plot_confusion_matrix`, `plot_confusion_matrix_normalized`, `plot_correlation_matrix`, `plot_similarity_matrix`, `plot_attention_map`, `plot_matrix_sparsity`, `plot_matrix_surface` |
| **03** | [`03_training_visualization.ipynb`](03_training_visualization.ipynb) | **ML Training & Optimization** | `plot_training_history`, `plot_metric`, `plot_train_vs_val`, `plot_learning_rate`, `plot_metric_with_best`, `plot_metrics_grid`, `plot_confidence_band`, `plot_early_stopping`, `plot_epoch_time` |
| **04** | [`04_seaborn_plots.ipynb`](04_seaborn_plots.ipynb) | **Statistical Graphics (Seaborn)** | `set_pytekt_style`, `sns_heatmap`, `sns_kdeplot`, `sns_boxplot`, `sns_violinplot`, `sns_jointplot`, `sns_pairplot`, `sns_clustermap`, `sns_regplot`, `sns_displot` |
| **05** | [`05_3d_matplotlib.ipynb`](05_3d_matplotlib.ipynb) | **3D Spatial (Matplotlib)** | `plot_3d_scatter`, `plot_3d_surface`, `plot_3d_wireframe`, `plot_3d_trisurf`, `plot_3d_contour`, `plot_3d_bar`, `plot_3d_quiver`, `plot_3d_trajectory`, `plot_3d_voxels`, `plot_3d_mesh` |
| **06** | [`06_3d_plotly.ipynb`](06_3d_plotly.ipynb) | **Interactive 3D (Plotly)** | `plotly_3d_scatter`, `plotly_3d_surface`, `plotly_3d_mesh`, `plotly_3d_volume`, `plotly_3d_cone`, `plotly_3d_streamtube`, `plotly_3d_isosurface`, `save_plotly_html` |
| **07** | [`07_classification_evaluation.ipynb`](07_classification_evaluation.ipynb) *(New)* | **Model Evaluation & Diagnostics** | `plot_roc_curve`, `plot_pr_curve`, `plot_calibration_curve`, `plot_class_distribution`, `plot_residuals` |
| **08** | [`08_pdf_html_reporting.ipynb`](08_pdf_html_reporting.ipynb) *(New)* | **Reporting & Export** | `save_figures_pdf`, `figures_to_html_img_tags`, `save_plot`, `close_figure` |

---

## 🚀 How to Run

```bash
# 1. Install pytekt with visualization dependencies
pip install pytekt[full]

# 2. Launch Jupyter Notebook
jupyter notebook pytekt/visualization/examples/
```

All plot functions return a `matplotlib.figure.Figure` object. In scripts or automated pipelines, use `show=False` and save via `save_plot(fig, "path.png")`.
