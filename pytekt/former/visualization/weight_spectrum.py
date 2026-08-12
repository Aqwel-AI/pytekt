"""
Weight spectrum: eigenvalue or singular-value distribution of weight matrices.

Useful for inspecting initialization and training dynamics (e.g. random
matrix theory). Accepts 2D NumPy arrays or aion.former.core.Tensor.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Union, List
from ..core.tensor import Tensor


# -----------------------------------------------------------------------------
# Spectrum plots
# -----------------------------------------------------------------------------

def _eigenvalues_of_matrix(W: np.ndarray) -> np.ndarray:
    """Eigenvalues of square matrix; singular values for non-square."""
    W = np.asarray(W)
    if W.shape[0] == W.shape[1]:
        return np.linalg.eigvalsh(W)
    return np.linalg.svd(W, compute_uv=False)


def plot_weight_spectrum(
    weight: Union[Tensor, np.ndarray],
    ax: Optional[plt.Axes] = None,
    title: str = "Weight spectrum",
    use_svd: bool = False,
) -> plt.Axes:
    """
    Plot eigenvalue (or singular value) distribution of a 2D weight matrix.

    Parameters
    ----------
    weight : Tensor or np.ndarray
        2D weight matrix; Tensor._data is used if Tensor.
    ax : matplotlib Axes, optional
        Axes to draw on; if None, a new figure is created.
    title : str, optional
        Plot title (default "Weight spectrum").
    use_svd : bool, optional
        If True, always use singular values; otherwise eigenvalues for square
        matrices, singular values for non-square (default False).

    Returns
    -------
    matplotlib.axes.Axes
        The axes used for the plot.

    Raises
    ------
    ValueError
        If weight is not 2D.
    """
    if isinstance(weight, Tensor):
        W = weight._data
    else:
        W = np.asarray(weight)
    if W.ndim != 2:
        raise ValueError("Weight must be 2D")
    if use_svd or W.shape[0] != W.shape[1]:
        values = np.linalg.svd(W, compute_uv=False)
        label = "Singular values"
    else:
        values = np.linalg.eigvalsh(W)
        values = np.real(values)
        label = "Eigenvalues"
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
    ax.hist(values, bins=50, density=True, alpha=0.7, edgecolor="black", label=label)
    ax.axvline(0, color="red", linestyle="--", alpha=0.7)
    ax.set_xlabel(label)
    ax.set_ylabel("Density")
    ax.set_title(title)
    ax.legend()
    return ax


def plot_weight_spectra(
    weights: List[Union[Tensor, np.ndarray]],
    labels: Optional[List[str]] = None,
    figsize: tuple = (12, 4),
) -> plt.Figure:
    """
    Plot spectra of multiple weight matrices in a single row.

    Parameters
    ----------
    weights : list of Tensor or np.ndarray
        List of 2D weight matrices.
    labels : list of str, optional
        Title for each subplot; default "W0", "W1", ...
    figsize : tuple, optional
        Figure size (default (12, 4)).

    Returns
    -------
    matplotlib.figure.Figure
        The figure containing the subplots.
    """
    n = len(weights)
    fig, axes = plt.subplots(1, n, figsize=figsize)
    if n == 1:
        axes = [axes]
    labels = labels or [f"W{i}" for i in range(n)]
    for ax, w, lab in zip(axes, weights, labels):
        plot_weight_spectrum(w, ax=ax, title=lab)
    plt.tight_layout()
    return fig
