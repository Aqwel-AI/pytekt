"""
Statistical Graphics & Themes (Seaborn)
=======================================

Provides statistical plots and consistent research styling:
- Custom research theme (set_pytekt_style)
- Boxplots, violin plots, strip/swarm plots
- KDE density plots, distribution (displot) charts
- Linear model (lmplot/regplot), joint distributions, pairplots, clustermaps
"""

from __future__ import annotations

from .seaborn_plots import (
    set_pytekt_style,
    sns_boxplot,
    sns_clustermap,
    sns_displot,
    sns_heatmap,
    sns_jointplot,
    sns_kdeplot,
    sns_lmplot,
    sns_pairplot,
    sns_regplot,
    sns_relplot,
    sns_stripplot,
    sns_swarmplot,
    sns_violinplot,
)

__all__ = [
    "set_pytekt_style",
    "sns_boxplot",
    "sns_clustermap",
    "sns_displot",
    "sns_heatmap",
    "sns_jointplot",
    "sns_kdeplot",
    "sns_lmplot",
    "sns_pairplot",
    "sns_regplot",
    "sns_relplot",
    "sns_stripplot",
    "sns_swarmplot",
    "sns_violinplot",
]
