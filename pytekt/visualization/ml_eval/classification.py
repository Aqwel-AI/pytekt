"""
Classification and Evaluation Visualization
============================================

Provides diagnostic charts for evaluating machine learning models:
- ROC curves with AUC calculation
- Precision-Recall curves with Average Precision (AP)
- Calibration curves (Reliability diagrams)
- Class balance / distribution bar charts
- Residual analysis plots for regression/scoring
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Union
import math

import matplotlib.pyplot as plt  # type: ignore[import-untyped]
from pytekt.visualization.core.utils import finalize_plot


def plot_roc_curve(
    y_true: Sequence[int],
    y_score: Sequence[float],
    title: str = "Receiver Operating Characteristic (ROC)",
    show: bool = True,
) -> plt.Figure:
    """
    Plot Receiver Operating Characteristic (ROC) curve with AUC score.

    Parameters
    ----------
    y_true : Sequence[int]
        Binary ground truth labels (0 or 1).
    y_score : Sequence[float]
        Predicted probability scores for the positive class.
    title : str, default "Receiver Operating Characteristic (ROC)"
        Title for the plot.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The resulting figure.
    """
    if len(y_true) != len(y_score) or len(y_true) == 0:
        raise ValueError("y_true and y_score must be non-empty sequences of the same length.")

    # Sort scores descending
    desc_indices = sorted(range(len(y_score)), key=lambda i: y_score[i], reverse=True)
    y_true_sorted = [y_true[i] for i in desc_indices]
    y_score_sorted = [y_score[i] for i in desc_indices]

    n_pos = sum(1 for y in y_true if y == 1)
    n_neg = len(y_true) - n_pos

    if n_pos == 0 or n_neg == 0:
        raise ValueError("y_true must contain both positive (1) and negative (0) instances.")

    # Compute FPR and TPR points
    fpr = [0.0]
    tpr = [0.0]
    tp = 0
    fp = 0

    for i in range(len(y_true_sorted)):
        if y_true_sorted[i] == 1:
            tp += 1
        else:
            fp += 1
        fpr.append(fp / n_neg)
        tpr.append(tp / n_pos)

    # Compute AUC using trapezoidal rule
    auc = 0.0
    for i in range(1, len(fpr)):
        auc += (fpr[i] - fpr[i - 1]) * (tpr[i] + tpr[i - 1]) / 2.0

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="#2b5c8f", lw=2, label=f"ROC curve (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], color="#888888", lw=1.5, linestyle="--", label="Random Chance")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate (FPR)")
    ax.set_ylabel("True Positive Rate (TPR / Recall)")
    ax.legend(loc="lower right")

    finalize_plot(title, show)
    return fig


def plot_pr_curve(
    y_true: Sequence[int],
    y_score: Sequence[float],
    title: str = "Precision-Recall Curve",
    show: bool = True,
) -> plt.Figure:
    """
    Plot Precision-Recall curve with Average Precision score.

    Parameters
    ----------
    y_true : Sequence[int]
        Binary ground truth labels (0 or 1).
    y_score : Sequence[float]
        Predicted probabilities for the positive class.
    title : str, default "Precision-Recall Curve"
        Title for the plot.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The resulting figure.
    """
    if len(y_true) != len(y_score) or len(y_true) == 0:
        raise ValueError("y_true and y_score must be non-empty sequences of the same length.")

    desc_indices = sorted(range(len(y_score)), key=lambda i: y_score[i], reverse=True)
    y_true_sorted = [y_true[i] for i in desc_indices]

    n_pos = sum(1 for y in y_true if y == 1)
    if n_pos == 0:
        raise ValueError("y_true must contain at least one positive instance.")

    precision = []
    recall = []
    tp = 0
    fp = 0

    for i in range(len(y_true_sorted)):
        if y_true_sorted[i] == 1:
            tp += 1
        else:
            fp += 1
        precision.append(tp / (tp + fp))
        recall.append(tp / n_pos)

    # Average Precision approximation
    ap = sum(precision[i] * (recall[i] - (recall[i - 1] if i > 0 else 0.0)) for i in range(len(recall)))

    baseline = n_pos / len(y_true)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(recall, precision, color="#1b8a5a", lw=2, label=f"PR curve (AP = {ap:.3f})")
    ax.axhline(y=baseline, color="#888888", lw=1.5, linestyle="--", label=f"Baseline ({baseline:.2f})")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend(loc="lower left")

    finalize_plot(title, show)
    return fig


def plot_calibration_curve(
    y_true: Sequence[int],
    y_prob: Sequence[float],
    n_bins: int = 10,
    title: str = "Probability Calibration (Reliability Diagram)",
    show: bool = True,
) -> plt.Figure:
    """
    Plot calibration reliability diagram comparing predicted probabilities against empirical frequencies.

    Parameters
    ----------
    y_true : Sequence[int]
        Binary true labels (0 or 1).
    y_prob : Sequence[float]
        Predicted probability values in [0, 1].
    n_bins : int, default 10
        Number of equal-width bins between 0 and 1.
    title : str, default "Probability Calibration (Reliability Diagram)"
        Title for the plot.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The resulting figure.
    """
    if len(y_true) != len(y_prob) or len(y_true) == 0:
        raise ValueError("y_true and y_prob must be non-empty sequences of the same length.")

    bin_width = 1.0 / n_bins
    bin_true_frac = []
    bin_pred_mean = []

    for b in range(n_bins):
        low = b * bin_width
        high = (b + 1) * bin_width
        bin_items = [y_true[i] for i in range(len(y_prob)) if (low <= y_prob[i] < high) or (b == n_bins - 1 and y_prob[i] == high)]
        bin_probs = [y_prob[i] for i in range(len(y_prob)) if (low <= y_prob[i] < high) or (b == n_bins - 1 and y_prob[i] == high)]

        if bin_items:
            bin_true_frac.append(sum(bin_items) / len(bin_items))
            bin_pred_mean.append(sum(bin_probs) / len(bin_probs))

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot([0, 1], [0, 1], color="#888888", linestyle="--", lw=1.5, label="Perfect Calibration")
    ax.plot(bin_pred_mean, bin_true_frac, "s-", color="#c2410c", lw=2, label="Model Calibration")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    ax.legend(loc="upper left")

    finalize_plot(title, show)
    return fig


def plot_class_distribution(
    y: Sequence[Union[int, str]],
    labels: Optional[Sequence[str]] = None,
    title: str = "Class Distribution",
    show: bool = True,
) -> plt.Figure:
    """
    Plot class frequency distribution with sample counts and percentages.

    Parameters
    ----------
    y : Sequence[Union[int, str]]
        Class labels for dataset samples.
    labels : Optional[Sequence[str]], default None
        Human-readable category names.
    title : str, default "Class Distribution"
        Title for the plot.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The resulting figure.
    """
    counts: dict = {}
    for item in y:
        counts[item] = counts.get(item, 0) + 1

    classes = list(counts.keys())
    values = [counts[c] for c in classes]
    total = sum(values)

    display_labels = [labels[i] if labels and i < len(labels) else str(c) for i, c in enumerate(classes)]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(display_labels, values, color="#3b82f6", edgecolor="#1d4ed8", alpha=0.85)

    for bar, val in zip(bars, values):
        pct = (val / total) * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.02 * max(values),
            f"{val} ({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_ylabel("Count")
    ax.set_xlabel("Class")
    ax.set_ylim([0, max(values) * 1.18])

    finalize_plot(title, show)
    return fig


def plot_residuals(
    y_true: Sequence[float],
    y_pred: Sequence[float],
    title: str = "Residual Analysis",
    show: bool = True,
) -> plt.Figure:
    """
    Plot regression residuals (y_true - y_pred) against predicted values.

    Parameters
    ----------
    y_true : Sequence[float]
        Ground truth target values.
    y_pred : Sequence[float]
        Predicted values from the regression model.
    title : str, default "Residual Analysis"
        Title for the plot.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The resulting figure.
    """
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        raise ValueError("y_true and y_pred must be non-empty sequences of the same length.")

    residuals = [y_true[i] - y_pred[i] for i in range(len(y_true))]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.scatter(y_pred, residuals, color="#6366f1", alpha=0.7, edgecolors="none")
    ax.axhline(0, color="#ef4444", linestyle="--", lw=1.5)
    ax.set_xlabel("Predicted Values")
    ax.set_ylabel("Residuals (True - Predicted)")

    finalize_plot(title, show)
    return fig
