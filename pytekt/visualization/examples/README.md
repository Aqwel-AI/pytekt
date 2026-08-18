# pytekt.visualization — Example Notebooks

This folder contains Jupyter notebooks that demonstrate the full **pytekt.visualization** API with detailed explanations and runnable examples. All plots return a matplotlib `Figure`; use `show=False` in scripts and `pytekt.visualization.utils.save_plot(fig, "path.png")` to save figures.

## Notebooks

| Notebook | Content |
|----------|---------|
| **01_array_visualization.ipynb** | 1D plots: array, histogram, scatter; multiple arrays, mean, running mean; boxplot, density, CDF; error bars, rolling std, min-max band; autocorrelation, quantiles, scatter with fit, dual axis. |
| **02_matrix_visualization.ipynb** | 2D plots: heatmap, confusion (raw and normalized), surface, contour; matrix with values, correlation matrix, similarity matrix; matrix histogram, masked heatmap; attention map, sparsity. |
| **03_training_visualization.ipynb** | Training plots: training history, single metric, train vs val, learning rate; metric with best, metrics grid; confidence band, early stopping; epoch time. |

## Dependencies

- **matplotlib** — required for all visualization.
- **numpy** — used in examples and by some plotting functions (e.g. density, correlation).

Install from project root:

```bash
pip install -e .
# or: pip install -e ".[full]"  if your project has optional deps
```

## How to run

From the project root:

```bash
jupyter notebook pytekt/visualization/examples/
```

Or open the notebooks in JupyterLab or VS Code. Use `show=True` (default) to display plots inline; use `show=False` and `save_plot(fig, "output.png")` to export without displaying.
