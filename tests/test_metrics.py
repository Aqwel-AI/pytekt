"""Tests for pytekt.metrics."""

import numpy as np

from pytekt.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    matthews_corrcoef,
    mean_squared_error,
    root_mean_squared_error,
    mean_absolute_error,
    r2_score,
    silhouette_score,
    adjusted_rand_score,
    bleu_score,
    rouge_l_score,
    perplexity,
    ndcg_score,
    mrr_score,
    classification_report,
)


def test_classification_metrics():
    y_true = [0, 1, 1, 0, 1]
    y_pred = [0, 1, 0, 0, 1]
    assert 0.0 <= accuracy_score(y_true, y_pred) <= 1.0
    assert precision_score(y_true, y_pred, average="binary") > 0
    assert recall_score(y_true, y_pred, average="binary") > 0
    assert f1_score(y_true, y_pred, average="binary") > 0
    cm = confusion_matrix(y_true, y_pred)
    assert cm.shape == (2, 2)
    assert matthews_corrcoef(y_true, y_pred) >= -1.0
    report = classification_report(y_true, y_pred)
    assert "accuracy" in report


def test_regression_metrics():
    y_true = [1.0, 2.0, 3.0]
    y_pred = [1.1, 2.0, 2.8]
    assert mean_squared_error(y_true, y_pred) >= 0
    assert root_mean_squared_error(y_true, y_pred) >= 0
    assert mean_absolute_error(y_true, y_pred) >= 0
    assert r2_score(y_true, y_pred) > 0.9


def test_clustering_metrics():
    X = np.array([[0, 0], [1, 1], [5, 5], [6, 6]])
    labels = [0, 0, 1, 1]
    assert -1.0 <= silhouette_score(X, labels) <= 1.0
    assert adjusted_rand_score([0, 0, 1, 1], labels) > 0.9


def test_nlp_metrics():
    ref = "the cat sat on the mat"
    hyp = "the cat sat on the mat"
    assert bleu_score(ref, hyp) > 0.9
    assert rouge_l_score(ref, hyp) > 0.9
    assert perplexity([-0.1, -0.2, -0.1]) > 0


def test_ranking_metrics():
    assert 0.0 <= ndcg_score([3, 2, 1], [0.9, 0.8, 0.1]) <= 1.0
    assert mrr_score([[0, 1, 0], [0, 0, 1]]) > 0


def test_roc_and_pr_curves():
    from pytekt.metrics import (
        average_precision_score,
        precision_recall_curve,
        roc_auc_score,
        roc_curve,
    )

    y_true = np.array([0, 0, 1, 1, 1])
    y_score = np.array([0.1, 0.4, 0.35, 0.8, 0.9])

    # ROC curve
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    assert len(fpr) == len(tpr) == len(thresholds)
    assert fpr[0] == 0.0 and tpr[0] == 0.0
    assert fpr[-1] == 1.0 and tpr[-1] == 1.0

    # ROC AUC
    auc = roc_auc_score(y_true, y_score)
    assert 0.5 <= auc <= 1.0

    # PR curve
    precision, recall, pr_thresh = precision_recall_curve(y_true, y_score)
    assert len(precision) == len(recall)
    assert precision[-1] == 1.0 and recall[-1] == 0.0

    # Average precision
    ap = average_precision_score(y_true, y_score)
    assert 0.5 <= ap <= 1.0

