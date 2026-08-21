"""Tests for pytekt.visualization package and subpackages."""

import pytest
import matplotlib.pyplot as plt

from pytekt.visualization import (
    # Subpackages
    core,
    one_d,
    two_d,
    ml_eval,
    three_d_pkg,
    reporting,
    # Functions
    plot_array,
    plot_histogram,
    plot_scatter,
    plot_matrix_heatmap,
    plot_confusion_matrix,
    plot_training_history,
    plot_roc_curve,
    plot_pr_curve,
    plot_calibration_curve,
    plot_class_distribution,
    plot_residuals,
    plot_3d_scatter,
    save_plot,
    close_figure,
)


def test_subpackages_existence():
    assert hasattr(core, "utils")
    assert hasattr(one_d, "arrays")
    assert hasattr(two_d, "matrices")
    assert hasattr(ml_eval, "training")
    assert hasattr(ml_eval, "classification")
    assert hasattr(three_d_pkg, "three_d")
    assert hasattr(reporting, "report")


def test_1d_plots():
    fig = plot_array([1, 4, 2, 8, 5], title="Test Array", show=False)
    assert isinstance(fig, plt.Figure)
    close_figure(fig)

    fig = plot_histogram([1, 2, 2, 3, 3, 3, 4], bins=4, show=False)
    assert isinstance(fig, plt.Figure)
    close_figure(fig)

    fig = plot_scatter([1, 2, 3], [3, 2, 1], show=False)
    assert isinstance(fig, plt.Figure)
    close_figure(fig)


def test_2d_plots():
    fig = plot_matrix_heatmap([[1, 2], [3, 4]], show=False)
    assert isinstance(fig, plt.Figure)
    close_figure(fig)

    fig = plot_confusion_matrix([[10, 2], [1, 15]], labels=["A", "B"], show=False)
    assert isinstance(fig, plt.Figure)
    close_figure(fig)


def test_ml_training_plots():
    history = {"loss": [0.8, 0.5, 0.3], "val_loss": [0.9, 0.6, 0.4]}
    fig = plot_training_history(history, show=False)
    assert isinstance(fig, plt.Figure)
    close_figure(fig)


def test_ml_classification_diagnostics():
    y_true = [0, 0, 1, 1, 1, 0, 1, 0]
    y_score = [0.1, 0.2, 0.8, 0.9, 0.6, 0.4, 0.7, 0.3]

    # ROC curve
    fig_roc = plot_roc_curve(y_true, y_score, show=False)
    assert isinstance(fig_roc, plt.Figure)
    close_figure(fig_roc)

    # PR curve
    fig_pr = plot_pr_curve(y_true, y_score, show=False)
    assert isinstance(fig_pr, plt.Figure)
    close_figure(fig_pr)

    # Calibration curve
    fig_cal = plot_calibration_curve(y_true, y_score, n_bins=5, show=False)
    assert isinstance(fig_cal, plt.Figure)
    close_figure(fig_cal)

    # Class distribution
    fig_dist = plot_class_distribution([0, 1, 1, 0, 1, 2], labels=["Cat", "Dog", "Bird"], show=False)
    assert isinstance(fig_dist, plt.Figure)
    close_figure(fig_dist)

    # Residuals
    fig_res = plot_residuals([10.0, 20.0, 30.0], [9.5, 20.8, 29.2], show=False)
    assert isinstance(fig_res, plt.Figure)
    close_figure(fig_res)


def test_3d_plots():
    fig = plot_3d_scatter([1, 2, 3], [4, 5, 6], [7, 8, 9], show=False)
    assert isinstance(fig, plt.Figure)
    close_figure(fig)
