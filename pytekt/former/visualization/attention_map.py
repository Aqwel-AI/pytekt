"""
Attention weight visualization.

Heatmaps for a single head or all heads of one layer. Optional token
labels on axes. Uses matplotlib.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, List


# -----------------------------------------------------------------------------
# Attention heatmaps
# -----------------------------------------------------------------------------

def plot_attention_map(
    attention_weights: np.ndarray,
    tokens: Optional[List[str]] = None,
    layer: int = 0,
    head: int = 0,
    ax: Optional[plt.Axes] = None,
    title: Optional[str] = None,
    cmap: str = "viridis",
) -> plt.Axes:
    """
    Plot attention matrix for one layer and one head.

    Parameters
    ----------
    attention_weights : np.ndarray
        Shape (batch, num_heads, seq, seq) or (num_heads, seq, seq); first batch
        or single array is used.
    tokens : list of str, optional
        Token strings for axis labels.
    layer, head : int, optional
        Layer and head index for title (default 0, 0).
    ax : matplotlib Axes, optional
        Axes to draw on; if None, a new figure is created.
    title : str, optional
        Plot title; if None, default title includes layer and head.
    cmap : str, optional
        Colormap name (default "viridis").

    Returns
    -------
    matplotlib.axes.Axes
        The axes used for the plot.
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    if attention_weights.ndim == 4:
        attn = attention_weights[0, head]
    else:
        attn = attention_weights[head]
    im = ax.imshow(attn, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    if tokens:
        ax.set_xticks(range(len(tokens)))
        ax.set_yticks(range(len(tokens)))
        ax.set_xticklabels(tokens, rotation=45, ha="right")
        ax.set_yticklabels(tokens)
    ax.set_xlabel("Key position")
    ax.set_ylabel("Query position")
    if title:
        ax.set_title(title)
    else:
        ax.set_title(f"Attention (layer {layer}, head {head})")
    plt.colorbar(im, ax=ax, label="Weight")
    return ax


def plot_multi_head_attention(
    attention_weights: np.ndarray,
    layer: int = 0,
    tokens: Optional[List[str]] = None,
    figsize: Optional[tuple] = None,
) -> plt.Figure:
    """
    Plot all heads for one layer in a grid of subplots.

    Parameters
    ----------
    attention_weights : np.ndarray
        Shape (batch, num_heads, seq, seq) or (num_heads, seq, seq).
    layer : int, optional
        Layer index for title (default 0).
    tokens : list of str, optional
        Token labels on bottom row of subplots.
    figsize : tuple, optional
        Figure size; default scales with number of heads.

    Returns
    -------
    matplotlib.figure.Figure
        The figure containing the grid.
    """
    if attention_weights.ndim == 4:
        attn = attention_weights[0]
    else:
        attn = attention_weights
    num_heads = attn.shape[0]
    ncol = min(4, num_heads)
    nrow = (num_heads + ncol - 1) // ncol
    figsize = figsize or (4 * ncol, 4 * nrow)
    fig, axes = plt.subplots(nrow, ncol, figsize=figsize)
    axes = np.atleast_2d(axes)
    for h in range(num_heads):
        ax = axes.flat[h]
        im = ax.imshow(attn[h], aspect="auto", cmap="viridis", vmin=0, vmax=1)
        ax.set_title(f"Head {h}")
        if tokens and h >= num_heads - ncol:
            ax.set_xticks(range(len(tokens)))
            ax.set_xticklabels(tokens, rotation=45, ha="right")
    for h in range(num_heads, axes.size):
        axes.flat[h].set_visible(False)
    fig.suptitle(f"Layer {layer} attention heads")
    plt.tight_layout()
    return fig
