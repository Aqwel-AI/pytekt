"""
Matrix visualization utilities for AION.

This module provides visualization helpers for 2D numerical data,
commonly used in AI and machine learning research, such as:

- weight matrices
- correlation matrices
- attention maps
- confusion matrices

All functions return a matplotlib Figure object and optionally
display the plot.
"""

from typing import Sequence, Optional

import matplotlib.pyplot as plt  # type: ignore[import-untyped]
import numpy as np

from .utils import finalize_plot


def plot_matrix_heatmap(
    matrix: Sequence[Sequence[float]],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Visualize a 2D matrix as a heatmap.

    Heatmaps are useful for inspecting matrix structures such as
    correlations, learned weights, or attention scores.

    Parameters
    ----------
    matrix : Sequence[Sequence[float]]
        Two-dimensional numerical data structure (list of lists or array-like).
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
        If the input is not a 2D matrix.
    """

    # Convert input to NumPy array for validation and plotting
    mat = np.array(matrix)

    # Validate dimensionality
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")

    fig, ax = plt.subplots()

    # Render matrix as heatmap
    im = ax.imshow(mat)

    # Add colorbar for value reference
    fig.colorbar(im)

    finalize_plot(title, show)
    return fig


def plot_confusion_matrix(
    cm: Sequence[Sequence[int]],
    labels: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a confusion matrix for classification evaluation.

    Confusion matrices provide insight into classification performance
    by showing correct and incorrect predictions per class.

    Parameters
    ----------
    cm : Sequence[Sequence[int]]
        Confusion matrix values (2D array-like).
    labels : Sequence[str], optional
        Class labels for axes.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """

    # Convert input to NumPy array
    mat = np.array(cm)

    fig, ax = plt.subplots()

    # Display confusion matrix as heatmap
    im = ax.imshow(mat)

    # Add colorbar
    fig.colorbar(im)

    # Apply class labels if provided
    if labels:
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)

    # Axis labels follow ML convention
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")

    finalize_plot(title, show)
    return fig


def plot_matrix_surface(
    matrix: Sequence[Sequence[float]],
    title: Optional[str] = None,
    show: bool = True
):
    
    """
    Plot a 3D surface for a 2D matrix.

    Parameters
    ----------
    matrix : Sequence[Sequence[float]]
        Two-dimensional numerical data.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(matrix)
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")

    x = np.arange(mat.shape[1])
    y = np.arange(mat.shape[0])
    X, Y = np.meshgrid(x, y)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, mat, cmap="viridis")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    ax.set_zlabel("Value")

    finalize_plot(title, show)
    return fig

def plot_matrix_contour(
    matrix: Sequence[Sequence[float]],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a contour map for a 2D matrix.

    Parameters
    ----------
    matrix : Sequence[Sequence[float]]
        Two-dimensional numerical data.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(matrix)
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")

    fig, ax = plt.subplots()
    cs = ax.contourf(mat, cmap="viridis")
    fig.colorbar(cs)
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    finalize_plot(title, show)
    return fig


def plot_matrix_with_values(
    matrix: Sequence[Sequence[float]],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a heatmap with annotated cell values.

    Parameters
    ----------
    matrix : Sequence[Sequence[float]]
        Two-dimensional numerical data.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(matrix)
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")

    fig, ax = plt.subplots()
    im = ax.imshow(mat)
    fig.colorbar(im)

    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{mat[i, j]:.2f}",
                    ha="center", va="center", color="white")

    finalize_plot(title, show)
    return fig


def plot_correlation_matrix(
    data: Sequence[Sequence[float]],
    labels: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Compute and plot a correlation matrix.

    Parameters
    ----------
    data : Sequence[Sequence[float]]
        2D data (rows are samples, columns are features).
    labels : Sequence[str], optional
        Feature labels for axes.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(data)
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")

    corr = np.corrcoef(mat, rowvar=False)

    fig, ax = plt.subplots()
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
    fig.colorbar(im)

    if labels:
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)

    finalize_plot(title or "Correlation Matrix", show)
    return fig


def plot_similarity_matrix(
    data: Sequence[Sequence[float]],
    metric: str = "cosine",
    title: Optional[str] = None,
    show: bool = True
):
    """
    Compute and plot a similarity matrix.

    Parameters
    ----------
    data : Sequence[Sequence[float]]
        2D data (rows are vectors).
    metric : str, default "cosine"
        Similarity metric: "cosine" or "dot".
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(data, dtype=float)
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")
    if metric not in ("cosine", "dot"):
        raise ValueError("Metric must be 'cosine' or 'dot'")

    if metric == "cosine":
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = mat / norms
        sim = normalized @ normalized.T
    else:
        sim = mat @ mat.T

    fig, ax = plt.subplots()
    im = ax.imshow(sim, cmap="viridis")
    fig.colorbar(im)

    finalize_plot(title or "Similarity Matrix", show)
    return fig


def plot_matrix_histogram(
    matrix: Sequence[Sequence[float]],
    bins: int = 30,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a histogram of matrix values.

    Parameters
    ----------
    matrix : Sequence[Sequence[float]]
        Two-dimensional numerical data.
    bins : int, default 30
        Number of histogram bins.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(matrix)
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")
    if bins <= 0:
        raise ValueError("Bins must be positive")

    fig, ax = plt.subplots()
    ax.hist(mat.ravel(), bins=bins)
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")

    finalize_plot(title or "Matrix Histogram", show)
    return fig


def plot_masked_heatmap(
    matrix: Sequence[Sequence[float]],
    mask: Sequence[Sequence[bool]],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a heatmap with a boolean mask.

    Parameters
    ----------
    matrix : Sequence[Sequence[float]]
        Two-dimensional numerical data.
    mask : Sequence[Sequence[bool]]
        Boolean mask, same shape as matrix (True = hidden).
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(matrix, dtype=float)
    msk = np.array(mask, dtype=bool)
    if mat.ndim != 2 or msk.ndim != 2:
        raise ValueError("Inputs must be 2D matrices")
    if mat.shape != msk.shape:
        raise ValueError("Mask must match matrix shape")

    masked = np.ma.array(mat, mask=msk)
    fig, ax = plt.subplots()
    im = ax.imshow(masked)
    fig.colorbar(im)

    finalize_plot(title, show)
    return fig


def plot_confusion_matrix_normalized(
    cm: Sequence[Sequence[int]],
    labels: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot a normalized confusion matrix.

    Parameters
    ----------
    cm : Sequence[Sequence[int]]
        Confusion matrix values (2D array-like).
    labels : Sequence[str], optional
        Class labels for axes.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(cm, dtype=float)
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")

    row_sums = mat.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    norm = mat / row_sums

    fig, ax = plt.subplots()
    im = ax.imshow(norm, vmin=0, vmax=1, cmap="Blues")
    fig.colorbar(im)

    if labels:
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)

    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")

    finalize_plot(title or "Normalized Confusion Matrix", show)
    return fig


def plot_attention_map(
    weights: Sequence[Sequence[float]],
    tokens: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    show: bool = True
):
    """
    Plot an attention weight matrix with optional token labels.

    Parameters
    ----------
    weights : Sequence[Sequence[float]]
        Attention weights (2D array-like).
    tokens : Sequence[str], optional
        Token labels for axes.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(weights)
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")

    fig, ax = plt.subplots()
    im = ax.imshow(mat, cmap="viridis")
    fig.colorbar(im)

    if tokens:
        if len(tokens) != mat.shape[0] or len(tokens) != mat.shape[1]:
            raise ValueError("Token labels must match matrix shape")
        ax.set_xticks(range(len(tokens)))
        ax.set_yticks(range(len(tokens)))
        ax.set_xticklabels(tokens, rotation=90)
        ax.set_yticklabels(tokens)

    finalize_plot(title or "Attention Map", show)
    return fig


def plot_matrix_sparsity(
    matrix: Sequence[Sequence[float]],
    title: Optional[str] = None,
    show: bool = True
):
    """
    Visualize matrix sparsity (non-zero pattern).

    Parameters
    ----------
    matrix : Sequence[Sequence[float]]
        Two-dimensional numerical data.
    title : str, optional
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    mat = np.array(matrix)
    if mat.ndim != 2:
        raise ValueError("Input must be a 2D matrix")

    fig, ax = plt.subplots()
    ax.spy(mat, markersize=2)
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    finalize_plot(title or "Matrix Sparsity", show)
    return fig





def plot_calibration_curve(
    y_true,           
    y_prob,           
    n_bins=10,
    ax=None,
    title="Calibration curve",
    show=True
):
    """
    Plot a calibration curve (reliability diagram).

    Bins predicted probabilities and plots mean predicted value vs
    fraction of positives in each bin. A well-calibrated model lies
    along the diagonal.

    Parameters
    ----------
    y_true : array-like
        True binary labels (0 or 1).
    y_prob : array-like
        Predicted probabilities for the positive class.
    n_bins : int, default 10
        Number of bins for the calibration curve.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, a new figure is created.
    title : str, default "Calibration curve"
        Title of the plot.
    show : bool, default True
        Whether to display the plot.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    if y_true.shape != y_prob.shape:
        raise ValueError("y_true and y_prob must have the same shape")

    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.clip(
        np.digitize(y_prob, bin_edges[1:-1], right=False), 0, n_bins - 1
    )
    bin_means = np.array(
        [y_prob[bin_indices == i].mean() if (bin_indices == i).any() else np.nan
         for i in range(n_bins)]
    )
    bin_freqs = np.array(
        [y_true[bin_indices == i].mean() if (bin_indices == i).any() else np.nan
         for i in range(n_bins)]
    )
    valid = ~(np.isnan(bin_means) | np.isnan(bin_freqs))

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    ax.plot([0, 1], [0, 1], "k--", label="Perfectly calibrated")
    ax.plot(bin_means[valid], bin_freqs[valid], "s-", label="Model")
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Fraction of positives")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right")

    finalize_plot(title, show)
    return fig