"""
Array visualization utilities for AION.

This module provides research-friendly plotting helpers for
one-dimensional numerical data. The functions are designed to be:

- lightweight
- backend-safe (CLI, notebooks, CI)
- suitable for AI/ML research and data analysis

All functions return a matplotlib Figure object and optionally
display the plot.
"""

from typing import Sequence, List, Optional

import matplotlib.pyplot as plt  # type: ignore[import-untyped]
import numpy as np

from .utils import finalize_plot


def plot_array(
    array: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a 1D numerical array as a line chart.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical sequence (list, tuple, or array-like).
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot immediately.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty.
    """

    # Validate input
    if not array:
        raise ValueError("Array must not be empty")

    # Create figure and axis
    fig, ax = plt.subplots()

    # Plot values against their indices
    ax.plot(range(len(array)), array)

    # Axis labels
    ax.set_xlabel("Index")
    ax.set_ylabel("Value")

    # Apply common formatting and display logic
    finalize_plot(title, show)

    return fig


def plot_histogram(
    array: Sequence[float],
    bins: int = 10,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a histogram representing the distribution of values.

    Useful for analyzing feature distributions, weights,
    residuals, or any numeric data spread.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    bins : int, default 10
        Number of histogram bins.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty.
    """

    if not array:
        raise ValueError("Array must not be empty")

    fig, ax = plt.subplots()

    # Histogram plot
    ax.hist(array, bins=bins)

    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")

    finalize_plot(title, show)
    return fig


def plot_scatter(
    x: Sequence[float],
    y: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a scatter diagram showing the relationship between two variables.

    Common use cases include correlation analysis, embeddings inspection,
    and prediction vs. ground truth comparison.

    Parameters
    ----------
    x : Sequence[float]
        Values for the x-axis.
    y : Sequence[float]
        Values for the y-axis.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If x and y have different lengths.
    """

    if len(x) != len(y):
        raise ValueError("x and y must have the same length")

    fig, ax = plt.subplots()

    ax.scatter(x, y)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    finalize_plot(title, show)
    return fig


def plot_multiple_arrays(
    arrays: List[Sequence[float]],
    labels: Optional[List[str]] = None,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot multiple 1D arrays on the same figure.

    Useful for comparing multiple signals or experiment curves,
    such as training vs. validation loss.

    Parameters
    ----------
    arrays : list of Sequence[float]
        List of numerical arrays to plot.
    labels : list of str, optional
        Labels corresponding to each array.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If no arrays are provided.
    """

    if not arrays:
        raise ValueError("No arrays provided")

    fig, ax = plt.subplots()

    # Plot each array
    for i, arr in enumerate(arrays):
        label = labels[i] if labels and i < len(labels) else None
        ax.plot(arr, label=label)

    if labels:
        ax.legend()

    ax.set_xlabel("Index")
    ax.set_ylabel("Value")

    finalize_plot(title, show)
    return fig


def plot_array_with_mean(
    array: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a 1D array with its mean value shown as a horizontal line.

    This visualization is useful for statistical inspection
    and quick anomaly detection.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty.
    """

    if not array:
        raise ValueError("Array must not be empty")

    # Compute mean value
    mean_val = float(np.mean(array))

    fig, ax = plt.subplots()

    ax.plot(array, label="Values")
    ax.axhline(
        mean_val,
        linestyle="--",
        label=f"Mean = {mean_val:.3f}"
    )

    ax.legend()

    ax.set_xlabel("Index")
    ax.set_ylabel("Value")

    finalize_plot(title, show)
    return fig



def plot_running_mean(
    array: Sequence[float],
    window_size: int = 10,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a running mean of a 1D array.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    window_size : int, default 10
        Size of the moving window for the running mean.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty or window_size is invalid.
    """
    """
    Plot a running mean of a 1D array.
    """
    if not array:
        raise ValueError("Array must not be empty")
    
    if window_size <= 0:
        raise ValueError("Window size must be positive")

    if window_size > len(array):
        raise ValueError("Window size must not exceed array length")

    window = np.ones(window_size) / window_size
    running_mean = np.convolve(array, window, mode="valid")

    fig, ax = plt.subplots()

    ax.plot(running_mean, label="Running Mean")

    ax.set_xlabel("Index")
    ax.set_ylabel("Value")

    finalize_plot(title, show)
    return fig


def plot_boxplot(
    array: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a boxplot for a 1D numerical array.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty.
    """
    if not array:
        raise ValueError("Array must not be empty")

    fig, ax = plt.subplots()
    ax.boxplot(array, vert=True)
    ax.set_ylabel("Value")

    finalize_plot(title, show)
    return fig


def plot_density(
    array: Sequence[float],
    bins: int = 30,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a density curve using a normalized histogram.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    bins : int, default 30
        Number of histogram bins used to approximate the density.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty or bins is invalid.
    """
    if not array:
        raise ValueError("Array must not be empty")
    if bins <= 0:
        raise ValueError("Bins must be positive")

    hist, edges = np.histogram(array, bins=bins, density=True)
    centers = (edges[:-1] + edges[1:]) / 2

    fig, ax = plt.subplots()
    ax.plot(centers, hist)
    ax.set_xlabel("Value")
    ax.set_ylabel("Density")

    finalize_plot(title, show)
    return fig


def plot_cdf(
    array: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot the cumulative distribution function (CDF).

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty.
    """
    if not array:
        raise ValueError("Array must not be empty")

    values = np.sort(np.asarray(array))
    cdf = np.arange(1, len(values) + 1) / len(values)

    fig, ax = plt.subplots()
    ax.plot(values, cdf)
    ax.set_xlabel("Value")
    ax.set_ylabel("CDF")

    finalize_plot(title, show)
    return fig


def plot_error_bars(
    x: Sequence[float],
    y: Sequence[float],
    yerr: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a line with error bars.

    Parameters
    ----------
    x : Sequence[float]
        Values for the x-axis.
    y : Sequence[float]
        Values for the y-axis.
    yerr : Sequence[float]
        Error values for each y point.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If input lengths do not match.
    """
    if len(x) != len(y) or len(y) != len(yerr):
        raise ValueError("x, y, and yerr must have the same length")

    fig, ax = plt.subplots()
    ax.errorbar(x, y, yerr=yerr, fmt="-o", capsize=3)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    finalize_plot(title, show)
    return fig


def plot_rolling_std(
    array: Sequence[float],
    window_size: int = 10,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a rolling standard deviation of a 1D array.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    window_size : int, default 10
        Size of the moving window.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty or window_size is invalid.
    """
    if not array:
        raise ValueError("Array must not be empty")
    if window_size <= 0:
        raise ValueError("Window size must be positive")
    if window_size > len(array):
        raise ValueError("Window size must not exceed array length")

    arr = np.asarray(array, dtype=float)
    rolling = [
        float(np.std(arr[i:i + window_size]))
        for i in range(len(arr) - window_size + 1)
    ]

    fig, ax = plt.subplots()
    ax.plot(rolling, label="Rolling Std")
    ax.set_xlabel("Index")
    ax.set_ylabel("Std")

    finalize_plot(title, show)
    return fig


def plot_min_max_band(
    array: Sequence[float],
    window_size: int = 10,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a rolling min/max band for a 1D array.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    window_size : int, default 10
        Size of the moving window.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty or window_size is invalid.
    """
    if not array:
        raise ValueError("Array must not be empty")
    if window_size <= 0:
        raise ValueError("Window size must be positive")
    if window_size > len(array):
        raise ValueError("Window size must not exceed array length")

    arr = np.asarray(array, dtype=float)
    rolling_min = [
        float(np.min(arr[i:i + window_size]))
        for i in range(len(arr) - window_size + 1)
    ]
    rolling_max = [
        float(np.max(arr[i:i + window_size]))
        for i in range(len(arr) - window_size + 1)
    ]

    fig, ax = plt.subplots()
    ax.fill_between(
        range(len(rolling_min)),
        rolling_min,
        rolling_max,
        alpha=0.3,
        label="Min/Max Band"
    )
    ax.set_xlabel("Index")
    ax.set_ylabel("Value")

    finalize_plot(title, show)
    return fig


def plot_autocorrelation(
    array: Sequence[float],
    max_lag: int = 40,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot autocorrelation for a 1D array.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    max_lag : int, default 40
        Maximum lag to compute.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty or max_lag is invalid.
    """
    if not array:
        raise ValueError("Array must not be empty")
    if max_lag <= 0:
        raise ValueError("Max lag must be positive")

    arr = np.asarray(array, dtype=float)
    arr = arr - np.mean(arr)
    n = len(arr)
    max_lag = min(max_lag, n - 1)

    corr = np.correlate(arr, arr, mode="full")[n - 1:n + max_lag]
    corr = corr / corr[0]

    fig, ax = plt.subplots()
    ax.stem(range(len(corr)), corr)
    ax.set_xlabel("Lag")
    ax.set_ylabel("Autocorrelation")

    finalize_plot(title, show)
    return fig


def plot_quantiles(
    array: Sequence[float],
    qs: Sequence[float] = (0.25, 0.5, 0.75),
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot selected quantiles as horizontal lines.

    Parameters
    ----------
    array : Sequence[float]
        Input numerical data.
    qs : Sequence[float], default (0.25, 0.5, 0.75)
        Quantiles to compute, between 0 and 1.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If the input array is empty or quantiles are invalid.
    """
    if not array:
        raise ValueError("Array must not be empty")
    if not qs:
        raise ValueError("Quantiles must not be empty")
    if any(q < 0 or q > 1 for q in qs):
        raise ValueError("Quantiles must be between 0 and 1")

    values = np.asarray(array, dtype=float)
    quantiles = np.quantile(values, qs)

    fig, ax = plt.subplots()
    ax.plot(values, label="Values")
    for q, val in zip(qs, quantiles):
        ax.axhline(val, linestyle="--", label=f"q={q:.2f}")
    ax.set_xlabel("Index")
    ax.set_ylabel("Value")
    ax.legend()

    finalize_plot(title, show)
    return fig


def plot_scatter_with_fit(
    x: Sequence[float],
    y: Sequence[float],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot scatter points with a linear regression fit line.

    Parameters
    ----------
    x : Sequence[float]
        Values for the x-axis.
    y : Sequence[float]
        Values for the y-axis.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If x and y have different lengths or not enough points.
    """
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if len(x) < 2:
        raise ValueError("At least two points are required")

    xs = np.asarray(x, dtype=float)
    ys = np.asarray(y, dtype=float)

    coeffs = np.polyfit(xs, ys, 1)
    fit = coeffs[0] * xs + coeffs[1]

    fig, ax = plt.subplots()
    ax.scatter(xs, ys, label="Data")
    ax.plot(xs, fit, label="Fit")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()

    finalize_plot(title, show)
    return fig


def plot_dual_axis(
    x: Sequence[float],
    y1: Sequence[float],
    y2: Sequence[float],
    label1: str = "Series 1",
    label2: str = "Series 2",
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot two series against the same x-axis with dual y-axes.

    Parameters
    ----------
    x : Sequence[float]
        Values for the x-axis.
    y1 : Sequence[float]
        Values for the left y-axis.
    y2 : Sequence[float]
        Values for the right y-axis.
    label1 : str, default "Series 1"
        Label for the left axis series.
    label2 : str, default "Series 2"
        Label for the right axis series.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ValueError
        If input lengths do not match.
    """
    if len(x) != len(y1) or len(x) != len(y2):
        raise ValueError("x, y1, and y2 must have the same length")

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(x, y1, color="tab:blue", label=label1)
    ax2.plot(x, y2, color="tab:orange", label=label2)

    ax1.set_xlabel("X")
    ax1.set_ylabel(label1, color="tab:blue")
    ax2.set_ylabel(label2, color="tab:orange")

    finalize_plot(title, show)
    return fig