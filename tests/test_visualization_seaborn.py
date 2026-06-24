"""Tests for seaborn visualization wrappers."""

import numpy as np
import pytest

pytest.importorskip("seaborn")

from aion.visualization.seaborn_plots import sns_heatmap, sns_kdeplot, sns_regplot


def test_sns_heatmap_returns_figure():
    data = np.arange(16).reshape(4, 4)
    fig = sns_heatmap(data, show=False)
    assert fig is not None


def test_sns_kdeplot():
    x = np.linspace(0, 1, 50)
    fig = sns_kdeplot(x, show=False)
    assert fig is not None


def test_sns_regplot():
    x = np.arange(10.0)
    y = x * 2 + 1
    fig = sns_regplot(x, y, show=False)
    assert fig is not None
