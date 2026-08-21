# pytekt.visualization — Scientific Visualization Suite

Research-grade plotting and diagnostic suite for 1D/2D data, machine learning evaluation, 3D rendering, statistical distributions, and multi-page publication reports.

---

## 1. Architecture & Domain Taxonomy

The package is organized into 8 clean domain subpackages with top-level curated access and full backward compatibility:

```
pytekt/visualization/
├── one_d/               # 1D Sequence, distributions, time series, error bands, quantiles
├── two_d/               # 2D Matrix analysis, heatmaps, attention maps, confusion matrices
├── ml_eval/             # Model training curves, ROC/PR curves, calibration, residuals
├── three_d/             # 3D spatial plots (scatter, surface, wireframe, quiver, voxels)
├── interactive/         # Interactive web-based 3D visualizations (Plotly)
├── statistical/         # High-level statistical distributions & multi-variate plots (Seaborn)
├── reporting/           # Report generation, HTML embedding & multi-page PDF export
├── core/                # Styling, figure management, display safety, backend helpers
└── __init__.py          # Unified entry point and backward compatibility aliases
```

### Domain Categories

| Subpackage | Key Visualizations | Primary Use Cases |
|---|---|---|
| **`pytekt.visualization.one_d`** | `plot_array`, `plot_histogram`, `plot_scatter`, `plot_density`, `plot_boxplot`, `plot_error_bars`, `plot_rolling_std`, `plot_quantiles`, `plot_dual_axis` | Sequence data, rolling statistics, distributions, uncertainty bands |
| **`pytekt.visualization.two_d`** | `plot_matrix_heatmap`, `plot_confusion_matrix`, `plot_correlation_matrix`, `plot_similarity_matrix`, `plot_attention_map`, `plot_matrix_sparsity` | Correlation analysis, transformer attention, weights, confusion matrices |
| **`pytekt.visualization.ml_eval`** | `plot_training_history`, `plot_train_vs_val`, `plot_learning_rate`, `plot_roc_curve`, `plot_pr_curve`, `plot_calibration_curve`, `plot_residuals` | Model training dynamics, classification performance, probability reliability |
| **`pytekt.visualization.three_d`** | `plot_3d_scatter`, `plot_3d_surface`, `plot_3d_wireframe`, `plot_3d_quiver`, `plot_3d_trajectory`, `plot_3d_voxels` | 3D scientific geometry, trajectories, vector fields, optimization surfaces |
| **`pytekt.visualization.interactive`** | `plotly_3d_scatter`, `plotly_3d_surface`, `plotly_3d_mesh`, `plotly_3d_volume`, `save_plotly_html` | Interactive 3D charts, web dashboards, rotatable models |
| **`pytekt.visualization.statistical`** | `sns_boxplot`, `sns_violinplot`, `sns_kdeplot`, `sns_pairplot`, `sns_clustermap`, `set_pytekt_style` | Multivariate exploration, publication styling, density estimates |
| **`pytekt.visualization.reporting`** | `save_figures_pdf`, `figures_to_html_img_tags` | Multi-page PDF report generation, HTML report embedding |
| **`pytekt.visualization.core`** | `save_plot`, `close_figure`, `finalize_plot`, `safe_show` | Figure lifetime management, safe headless rendering |

---

## 2. Installation

```bash
# Base visualization (Matplotlib + NumPy)
pip install pytekt[viz]

# Interactive 3D (Plotly)
pip install pytekt[viz3d]

# Full suite (Matplotlib + Seaborn + Plotly + ReportLab)
pip install pytekt[full]
```

---

## 3. Usage & Import Styles

### 3.1 Domain Subpackage Imports (Recommended)

```python
# 1D plots
from pytekt.visualization.one_d import plot_array, plot_density, plot_quantiles

# 2D & Matrix analysis
from pytekt.visualization.two_d import plot_matrix_heatmap, plot_attention_map

# Machine Learning & Diagnostics
from pytekt.visualization.ml_eval import (
    plot_training_history,
    plot_roc_curve,
    plot_pr_curve,
    plot_calibration_curve,
)

# 3D Visualization
from pytekt.visualization.three_d import plot_3d_surface, plot_3d_scatter

# Figure utilities
from pytekt.visualization.core import save_plot, close_figure
```

### 3.2 Top-Level Curated Imports

```python
from pytekt.visualization import (
    plot_array,
    plot_matrix_heatmap,
    plot_training_history,
    plot_roc_curve,
    plot_3d_surface,
    save_plot,
    close_figure,
)

# 1. Plot sequence with mean overlay
fig = plot_array([10, 14, 12, 18, 16, 22], title="Sensor Readings", show=False)
save_plot(fig, "sensor_readings.png")
close_figure(fig)

# 2. Classification ROC curve with AUC
y_true = [0, 0, 1, 1, 0, 1, 1, 0]
y_score = [0.1, 0.2, 0.85, 0.9, 0.3, 0.7, 0.95, 0.15]
fig = plot_roc_curve(y_true, y_score, title="Model Evaluation ROC", show=False)
save_plot(fig, "roc_curve.png")
close_figure(fig)
```

---

## 4. Design Principles

- **Headless & Backend-Safe**: Safe in CI, Jupyter, and remote SSH environments without X11.
- **Consistent Figure Lifecycle**: All plotting functions return a standard `matplotlib.figure.Figure`.
- **Zero-Friction Saving**: `save_plot(fig, path, dpi=300)` automatically sets `bbox_inches="tight"`.
- **100% Backward Compatibility**: Legacy imports like `from pytekt.visualization.arrays import ...` and `from pytekt.visualization.utils import save_plot` continue to work seamlessly.
