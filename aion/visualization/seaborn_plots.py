"""Seaborn plot wrappers with Aion conventions."""

from __future__ import annotations

from typing import Any, List, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .utils import require_seaborn, safe_show


def set_aion_style() -> None:
    """Apply a dark research theme for seaborn/matplotlib."""
    sns = require_seaborn()
    sns.set_theme(style="darkgrid", palette="deep")
    plt.rcParams.update({
        "figure.facecolor": "#0d1117",
        "axes.facecolor": "#161b22",
        "axes.edgecolor": "#30363d",
        "text.color": "#e6edf3",
        "axes.labelcolor": "#e6edf3",
        "xtick.color": "#8b949e",
        "ytick.color": "#8b949e",
        "grid.color": "#30363d",
    })


def sns_heatmap(
    data: Any,
    *,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    fig, ax = plt.subplots()
    sns.heatmap(data, ax=ax, **kwargs)
    if title:
        ax.set_title(title)
    safe_show(show)
    return fig


def sns_kdeplot(
    x: Sequence[float],
    *,
    y: Optional[Sequence[float]] = None,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    fig, ax = plt.subplots()
    if y is not None:
        sns.kdeplot(x=x, y=y, ax=ax, fill=True, **kwargs)
    else:
        sns.kdeplot(x=x, ax=ax, fill=True, **kwargs)
    if title:
        ax.set_title(title)
    safe_show(show)
    return fig


def sns_boxplot(
    data: Any,
    *,
    x: Optional[str] = None,
    y: Optional[str] = None,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    fig, ax = plt.subplots()
    sns.boxplot(data=data, x=x, y=y, ax=ax, **kwargs)
    if title:
        ax.set_title(title)
    safe_show(show)
    return fig


def sns_violinplot(
    data: Any,
    *,
    x: Optional[str] = None,
    y: Optional[str] = None,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    fig, ax = plt.subplots()
    sns.violinplot(data=data, x=x, y=y, ax=ax, **kwargs)
    if title:
        ax.set_title(title)
    safe_show(show)
    return fig


def sns_stripplot(
    data: Any,
    *,
    x: Optional[str] = None,
    y: Optional[str] = None,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    fig, ax = plt.subplots()
    sns.stripplot(data=data, x=x, y=y, ax=ax, **kwargs)
    if title:
        ax.set_title(title)
    safe_show(show)
    return fig


def sns_swarmplot(
    data: Any,
    *,
    x: Optional[str] = None,
    y: Optional[str] = None,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    fig, ax = plt.subplots()
    sns.swarmplot(data=data, x=x, y=y, ax=ax, **kwargs)
    if title:
        ax.set_title(title)
    safe_show(show)
    return fig


def sns_regplot(
    x: Sequence[float],
    y: Sequence[float],
    *,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    fig, ax = plt.subplots()
    sns.regplot(x=x, y=y, ax=ax, **kwargs)
    if title:
        ax.set_title(title)
    safe_show(show)
    return fig


def sns_jointplot(
    x: Sequence[float],
    y: Sequence[float],
    *,
    kind: str = "scatter",
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    g = sns.jointplot(x=x, y=y, kind=kind, **kwargs)
    if title:
        g.figure.suptitle(title)
    safe_show(show)
    return g.figure


def sns_pairplot(
    data: Any,
    *,
    hue: Optional[str] = None,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    g = sns.pairplot(data, hue=hue, **kwargs)
    if title:
        g.figure.suptitle(title)
    safe_show(show)
    return g.figure


def sns_clustermap(
    data: Any,
    *,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    g = sns.clustermap(data, **kwargs)
    if title:
        g.fig.suptitle(title)
    safe_show(show)
    return g.fig


def sns_displot(
    data: Any,
    *,
    x: Optional[str] = None,
    kind: str = "hist",
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    g = sns.displot(data=data, x=x, kind=kind, **kwargs)
    if title:
        g.figure.suptitle(title)
    safe_show(show)
    return g.figure


def sns_relplot(
    data: Any,
    *,
    x: Optional[str] = None,
    y: Optional[str] = None,
    kind: str = "scatter",
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    g = sns.relplot(data=data, x=x, y=y, kind=kind, **kwargs)
    if title:
        g.figure.suptitle(title)
    safe_show(show)
    return g.figure


def sns_lmplot(
    data: Any,
    *,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: Optional[str] = None,
    show: bool = True,
    **kwargs: Any,
):
    sns = require_seaborn()
    g = sns.lmplot(data=data, x=x, y=y, hue=hue, **kwargs)
    if title:
        g.figure.suptitle(title)
    safe_show(show)
    return g.figure
