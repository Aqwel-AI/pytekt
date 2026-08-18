"""
Training loss and metrics plots.

Plot one or more metrics (e.g. loss, accuracy) over epochs. Uses matplotlib.
"""

import matplotlib.pyplot as plt
from typing import List, Dict, Optional


# -----------------------------------------------------------------------------
# Training curves
# -----------------------------------------------------------------------------

def plot_training_metrics(
    history: List[Dict[str, float]],
    metrics: Optional[List[str]] = None,
    ax: Optional[plt.Axes] = None,
    title: str = "Training metrics",
) -> plt.Axes:
    """
    Plot metrics over epochs (e.g. loss from Trainer.history).

    Parameters
    ----------
    history : list of dict
        One dict per epoch, e.g. [{"loss": 0.5}, {"loss": 0.4}, ...].
    metrics : list of str, optional
        Keys to plot; default is all keys from the first epoch.
    ax : matplotlib Axes, optional
        Axes to draw on; if None, a new figure is created.
    title : str, optional
        Plot title (default "Training metrics").

    Returns
    -------
    matplotlib.axes.Axes
        The axes used for the plot.
    """
    if not history:
        if ax is None:
            _, ax = plt.subplots(1, 1)
        return ax
    metrics = metrics or list(history[0].keys())
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    epochs = range(1, len(history) + 1)
    for key in metrics:
        if key in history[0]:
            values = [h[key] for h in history]
            ax.plot(epochs, values, label=key, marker="o", markersize=3)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Value")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    return ax
