"""
Training and experiment visualization utilities for AION.

This module provides helpers for visualizing machine learning
training metrics over time, such as loss, accuracy, or any
custom scalar tracked per epoch or iteration.

The primary use case is plotting training histories produced
by ML frameworks or custom training loops.
"""

from typing import Dict, Sequence, Optional, Iterable

import matplotlib.pyplot as plt  # type: ignore[import-untyped]

from .utils import finalize_plot


def plot_training_history(
    history: Dict[str, Sequence[float]],
    show: bool = True
):
    """
    Plot training history metrics over epochs.

    This function visualizes one or more training metrics
    (e.g. loss, validation loss, accuracy) on the same figure.

    Parameters
    ----------
    history : dict[str, Sequence[float]]
        Dictionary mapping metric names to sequences of values.
        Example:
        {
            "loss": [1.0, 0.7, 0.4],
            "val_loss": [1.1, 0.8, 0.5],
            "accuracy": [0.5, 0.65, 0.78]
        }
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the history dictionary is empty.
    """

    # Validate input
    if not history:
        raise ValueError("History dictionary is empty")

    fig, ax = plt.subplots()

    # Plot each metric on the same axes
    for metric_name, values in history.items():
        ax.plot(values, label=metric_name)

    # Standard ML training axis labels
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Value")

    # Legend shows metric names
    ax.legend()

    # Apply common formatting and display logic
    finalize_plot("Training History", show)

    return fig


def plot_metric(
    history: Dict[str, Sequence[float]],
    metric: str,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a single metric from a training history.

    Parameters
    ----------
    history : dict[str, Sequence[float]]
        Dictionary mapping metric names to sequences of values.
    metric : str
        Metric name to plot.
    title : str, optional
        Plot title.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the history is empty or metric is missing.
    """
    if not history:
        raise ValueError("History dictionary is empty")
    if metric not in history:
        raise ValueError(f"Metric '{metric}' not found in history")

    fig, ax = plt.subplots()
    ax.plot(history[metric], label=metric)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Value")
    ax.legend()

    finalize_plot(title or metric, show)
    return fig


def plot_train_vs_val(
    train: Sequence[float],
    val: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot training vs validation metrics on the same axes.

    Parameters
    ----------
    train : Sequence[float]
        Training metric values.
    val : Sequence[float]
        Validation metric values.
    title : str, optional
        Plot title.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If sequences are empty.
    """
    if not train or not val:
        raise ValueError("Train and validation sequences must not be empty")

    fig, ax = plt.subplots()
    ax.plot(train, label="train")
    ax.plot(val, label="val")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Value")
    ax.legend()

    finalize_plot(title or "Train vs Val", show)
    return fig


def plot_learning_rate(
    lr_values: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot learning rate values over steps or epochs.

    Parameters
    ----------
    lr_values : Sequence[float]
        Learning rate values.
    title : str, optional
        Plot title.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If lr_values is empty.
    """
    if not lr_values:
        raise ValueError("Learning rate values must not be empty")

    fig, ax = plt.subplots()
    ax.plot(lr_values, label="lr")
    ax.set_xlabel("Step")
    ax.set_ylabel("Learning Rate")
    ax.legend()

    finalize_plot(title or "Learning Rate", show)
    return fig


def plot_metric_with_best(
    history: Dict[str, Sequence[float]],
    metric: str,
    mode: str = "min",
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a metric and highlight its best value.

    Parameters
    ----------
    history : dict[str, Sequence[float]]
        Dictionary mapping metric names to sequences of values.
    metric : str
        Metric name to plot.
    mode : str, default "min"
        "min" for lowest value best, "max" for highest value best.
    title : str, optional
        Plot title.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If history is empty, metric missing, or mode invalid.
    """
    if not history:
        raise ValueError("History dictionary is empty")
    if metric not in history:
        raise ValueError(f"Metric '{metric}' not found in history")
    if mode not in ("min", "max"):
        raise ValueError("Mode must be 'min' or 'max'")

    values = history[metric]
    if not values:
        raise ValueError("Metric values must not be empty")

    if mode == "min":
        best_idx = int(min(range(len(values)), key=lambda i: values[i]))
    else:
        best_idx = int(max(range(len(values)), key=lambda i: values[i]))
    best_val = values[best_idx]

    fig, ax = plt.subplots()
    ax.plot(values, label=metric)
    ax.scatter([best_idx], [best_val], color="red", label=f"best ({mode})")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Value")
    ax.legend()

    finalize_plot(title or f"{metric} (best {mode})", show)
    return fig


def plot_metrics_grid(
    history: Dict[str, Sequence[float]],
    cols: int = 2,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot multiple metrics as a grid of subplots.

    Parameters
    ----------
    history : dict[str, Sequence[float]]
        Dictionary mapping metric names to sequences of values.
    cols : int, default 2
        Number of columns in the grid.
    title : str, optional
        Figure title.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If history is empty or cols is invalid.
    """
    if not history:
        raise ValueError("History dictionary is empty")
    if cols <= 0:
        raise ValueError("Cols must be positive")

    metrics = list(history.items())
    rows = (len(metrics) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 3 * rows))

    if isinstance(axes, Iterable):
        axes_flat = []
        for ax in axes:
            if isinstance(ax, Iterable):
                axes_flat.extend(list(ax))
            else:
                axes_flat.append(ax)
    else:
        axes_flat = [axes]

    for i, (metric, values) in enumerate(metrics):
        ax = axes_flat[i]
        ax.plot(values)
        ax.set_title(metric)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Value")

    for ax in axes_flat[len(metrics):]:
        ax.axis("off")

    if title:
        fig.suptitle(title)

    finalize_plot(None, show)
    return fig


def plot_confidence_band(
    mean: Sequence[float],
    std: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a mean curve with a +/- std confidence band.

    Parameters
    ----------
    mean : Sequence[float]
        Mean values.
    std : Sequence[float]
        Standard deviation values.
    title : str, optional
        Plot title.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If mean and std lengths do not match.
    """
    if len(mean) != len(std):
        raise ValueError("Mean and std must have the same length")

    x = list(range(len(mean)))
    upper = [m + s for m, s in zip(mean, std)]
    lower = [m - s for m, s in zip(mean, std)]

    fig, ax = plt.subplots()
    ax.plot(mean, label="mean")
    ax.fill_between(x, lower, upper, alpha=0.3, label="± std")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Value")
    ax.legend()

    finalize_plot(title or "Confidence Band", show)
    return fig


def plot_early_stopping(
    history: Dict[str, Sequence[float]],
    metric: str,
    patience: int,
    mode: str = "min",
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a metric and mark a simulated early stopping point.

    Parameters
    ----------
    history : dict[str, Sequence[float]]
        Dictionary mapping metric names to sequences of values.
    metric : str
        Metric name to plot.
    patience : int
        Number of epochs with no improvement before stopping.
    mode : str, default "min"
        "min" for lowest value best, "max" for highest value best.
    title : str, optional
        Plot title.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If inputs are invalid.
    """
    if not history:
        raise ValueError("History dictionary is empty")
    if metric not in history:
        raise ValueError(f"Metric '{metric}' not found in history")
    if patience <= 0:
        raise ValueError("Patience must be positive")
    if mode not in ("min", "max"):
        raise ValueError("Mode must be 'min' or 'max'")

    values = history[metric]
    if not values:
        raise ValueError("Metric values must not be empty")

    best_idx = 0
    best_val = values[0]
    wait = 0
    stop_idx = len(values) - 1

    for i in range(1, len(values)):
        improved = values[i] < best_val if mode == "min" else values[i] > best_val
        if improved:
            best_val = values[i]
            best_idx = i
            wait = 0
        else:
            wait += 1
            if wait >= patience:
                stop_idx = i
                break

    fig, ax = plt.subplots()
    ax.plot(values, label=metric)
    ax.axvline(stop_idx, color="red", linestyle="--", label="early stop")
    ax.scatter([best_idx], [best_val], color="green", label="best")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Value")
    ax.legend()

    finalize_plot(title or "Early Stopping", show)
    return fig


def plot_epoch_time(
    times: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot epoch duration over time.

    Parameters
    ----------
    times : Sequence[float]
        Per-epoch durations.
    title : str, optional
        Plot title.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If times is empty.
    """
    if not times:
        raise ValueError("Times must not be empty")

    fig, ax = plt.subplots()
    ax.plot(times, label="epoch_time")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Seconds")
    ax.legend()

    finalize_plot(title or "Epoch Time", show)
    return fig