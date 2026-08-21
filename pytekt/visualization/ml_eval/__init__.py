"""
Machine Learning Training & Diagnostics Visualization
=====================================================

Provides comprehensive training progression and model evaluation charts:
- Training history, metric evolution, train vs. validation curves
- Learning rate schedules, metric with best checkpoint marker, metrics grid
- Confidence bands, early stopping indicators, epoch duration plots
- ROC curves with AUC calculation, Precision-Recall curves (AP)
- Reliability calibration curves, class distribution, residual analysis
"""

from __future__ import annotations

from .classification import (
    plot_calibration_curve,
    plot_class_distribution,
    plot_pr_curve,
    plot_residuals,
    plot_roc_curve,
)
from .training import (
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

__all__ = [
    # Training Curves
    "plot_training_history",
    "plot_metric",
    "plot_train_vs_val",
    "plot_learning_rate",
    "plot_metric_with_best",
    "plot_metrics_grid",
    "plot_confidence_band",
    "plot_early_stopping",
    "plot_epoch_time",
    # Classification & Evaluation Diagnostics
    "plot_roc_curve",
    "plot_pr_curve",
    "plot_calibration_curve",
    "plot_class_distribution",
    "plot_residuals",
]
