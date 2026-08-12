"""
Common visualization utilities for AION.

This module contains shared helper functions used across
visualization submodules (arrays, matrices, training).

The utilities here are designed to:
- standardize plot appearance
- handle backend differences safely
- support both interactive and non-interactive environments
"""

from typing import Optional

import matplotlib.pyplot as plt  # type: ignore[import-untyped]


def finalize_plot(title: Optional[str], show: bool):
    """
    Apply common formatting and optionally display a plot.

    This helper centralizes plot finalization logic such as
    applying titles, enabling grids, and safely showing plots
    across different matplotlib backends.

    Parameters
    ----------
    title : str, optional
        Title to apply to the plot.
    show : bool
        Whether to display the plot immediately.

    Notes
    -----
    In non-interactive environments (e.g. CLI, CI, servers),
    matplotlib may not support rendering windows. In such cases,
    this function safely ignores display errors.
    """

    if title:
        plt.title(title)

    # Enable grid for better readability
    plt.grid(True)

    # Safely attempt to display the plot
    if show:
        try:
            plt.show()
        except Exception:
            # Ignore backend-related display errors
            pass


def save_plot(fig, path: str, dpi: int = 300):
    """
    Save a matplotlib figure to disk.

    This function is intended for research workflows where plots
    need to be stored for reports, papers, or reproducibility.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure object to save.
    path : str
        Output file path (e.g. 'plot.png').
    dpi : int, default 300
        Resolution of the saved image.

    Notes
    -----
    The bounding box is tightened automatically to avoid
    unnecessary whitespace around the plot.
    """

    fig.savefig(
        path,
        dpi=dpi,
        bbox_inches="tight"
    )


def close_figure(fig):
    """
    Close a matplotlib figure to free memory.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to close.
    """
    plt.close(fig)


def require_seaborn():
    """Import seaborn or raise with install hint."""
    try:
        import seaborn as sns  # type: ignore[import-untyped]

        return sns
    except ImportError as e:
        raise ImportError(
            "seaborn is required. Install with: pip install pytekt[viz]"
        ) from e


def require_plotly():
    """Import plotly or raise with install hint."""
    try:
        import plotly.graph_objects as go  # type: ignore[import-untyped]

        return go
    except ImportError as e:
        raise ImportError(
            "plotly is required. Install with: pip install pytekt[viz3d]"
        ) from e


def safe_show(show: bool) -> None:
    if show:
        try:
            plt.show()
        except Exception:
            pass
