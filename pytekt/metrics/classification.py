"""Classification metrics."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np

ArrayLike = Union[np.ndarray, Sequence[Any]]


def _check_lengths(y_true, y_pred) -> tuple:
    yt = np.asarray(y_true).ravel()
    yp = np.asarray(y_pred).ravel()
    if len(yt) != len(yp):
        raise ValueError("y_true and y_pred must have the same length")
    return yt, yp


def accuracy_score(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    yt, yp = _check_lengths(y_true, y_pred)
    return float(np.mean(yt == yp))


def confusion_matrix(
    y_true: ArrayLike,
    y_pred: ArrayLike,
    *,
    labels: Optional[Sequence[Any]] = None,
) -> np.ndarray:
    yt, yp = _check_lengths(y_true, y_pred)
    if labels is None:
        labels = sorted(set(yt.tolist()) | set(yp.tolist()))
    n = len(labels)
    label_to_idx = {lab: i for i, lab in enumerate(labels)}
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(yt, yp):
        if t in label_to_idx and p in label_to_idx:
            cm[label_to_idx[t], label_to_idx[p]] += 1
    return cm


def _precision_recall_f1(yt: np.ndarray, yp: np.ndarray, average: str) -> Dict[str, float]:
    labels = np.unique(np.concatenate([yt, yp]))
    precisions, recalls, f1s, supports = [], [], [], []
    for lab in labels:
        tp = np.sum((yp == lab) & (yt == lab))
        fp = np.sum((yp == lab) & (yt != lab))
        fn = np.sum((yp != lab) & (yt == lab))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        supports.append(np.sum(yt == lab))
    if average == "binary" and len(labels) == 2:
        return {"precision": precisions[1], "recall": recalls[1], "f1": f1s[1]}
    if average == "micro":
        cm = confusion_matrix(yt, yp, labels=labels)
        tp = np.trace(cm)
        fp = cm.sum(axis=0) - np.diag(cm)
        fn = cm.sum(axis=1) - np.diag(cm)
        tp, fp, fn = float(tp), float(fp.sum()), float(fn.sum())
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        return {"precision": prec, "recall": rec, "f1": f1}
    supports = np.array(supports, dtype=float)
    supports[supports == 0] = 1
    if average == "macro":
        return {
            "precision": float(np.mean(precisions)),
            "recall": float(np.mean(recalls)),
            "f1": float(np.mean(f1s)),
        }
    # weighted
    w = supports / supports.sum()
    return {
        "precision": float(np.average(precisions, weights=w)),
        "recall": float(np.average(recalls, weights=w)),
        "f1": float(np.average(f1s, weights=w)),
    }


def precision_score(y_true: ArrayLike, y_pred: ArrayLike, *, average: str = "binary") -> float:
    return _precision_recall_f1(*_check_lengths(y_true, y_pred), average)["precision"]


def recall_score(y_true: ArrayLike, y_pred: ArrayLike, *, average: str = "binary") -> float:
    return _precision_recall_f1(*_check_lengths(y_true, y_pred), average)["recall"]


def f1_score(y_true: ArrayLike, y_pred: ArrayLike, *, average: str = "binary") -> float:
    return _precision_recall_f1(*_check_lengths(y_true, y_pred), average)["f1"]


def matthews_corrcoef(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    yt, yp = _check_lengths(y_true, y_pred)
    cm = confusion_matrix(yt, yp)
    if cm.shape != (2, 2):
        labels = np.unique(np.concatenate([yt, yp]))
        if len(labels) != 2:
            raise ValueError("matthews_corrcoef requires binary classification")
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    denom = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    if denom == 0:
        return 0.0
    return float((tp * tn - fp * fn) / denom)


def _trapz(y: np.ndarray, x: np.ndarray) -> float:
    """Safe trapezoidal integration supporting NumPy 1.x and 2.x."""
    fn = getattr(np, "trapezoid", getattr(np, "trapz", None))
    if fn is not None:
        return float(fn(y, x))
    return float(np.sum((x[1:] - x[:-1]) * (y[:-1] + y[1:]) / 2.0))


def roc_curve(
    y_true: ArrayLike,
    y_score: ArrayLike,
    *,
    pos_label: Optional[Any] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute Receiver Operating Characteristic (ROC) curve.

    Returns
    -------
    fpr : ndarray
        Increasing false positive rates.
    tpr : ndarray
        Increasing true positive rates.
    thresholds : ndarray
        Decreasing thresholds on the decision function.
    """
    yt = np.asarray(y_true).ravel()
    scores = np.asarray(y_score, dtype=np.float64).ravel()
    labels = np.unique(yt)
    if pos_label is None:
        if len(labels) != 2:
            raise ValueError("roc_curve supports binary classification only")
        pos_label = labels[1]
    y_bin = (yt == pos_label).astype(np.int64)

    order = np.argsort(-scores)
    y_sorted = y_bin[order]
    scores_sorted = scores[order]

    # Find distinct thresholds where scores change
    distinct_idx = np.where(np.diff(scores_sorted))[0]
    threshold_idxs = np.concatenate([distinct_idx, [len(scores_sorted) - 1]])

    tps = np.cumsum(y_sorted)[threshold_idxs]
    fps = (threshold_idxs + 1) - tps
    total_pos = y_bin.sum()
    total_neg = len(y_bin) - total_pos

    if total_pos == 0 or total_neg == 0:
        return np.array([0.0, 1.0]), np.array([0.0, 1.0]), np.array([1.0, 0.0])

    tpr = np.concatenate([[0.0], tps / total_pos])
    fpr = np.concatenate([[0.0], fps / total_neg])
    thresholds = np.concatenate([[scores_sorted[0] + 1.0], scores_sorted[threshold_idxs]])
    return fpr, tpr, thresholds


def precision_recall_curve(
    y_true: ArrayLike,
    y_score: ArrayLike,
    *,
    pos_label: Optional[Any] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute Precision-Recall curve.

    Returns
    -------
    precision : ndarray
        Precision values such that element i is the precision of predictions with
        score >= thresholds[i] and the last element is 1.
    recall : ndarray
        Decreasing recall values such that element i is the recall of predictions with
        score >= thresholds[i] and the last element is 0.
    thresholds : ndarray
        Increasing thresholds on the decision function used to compute precision and recall.
    """
    yt = np.asarray(y_true).ravel()
    scores = np.asarray(y_score, dtype=np.float64).ravel()
    labels = np.unique(yt)
    if pos_label is None:
        if len(labels) != 2:
            raise ValueError("precision_recall_curve supports binary classification only")
        pos_label = labels[1]
    y_bin = (yt == pos_label).astype(np.int64)

    thresholds = np.sort(np.unique(scores))
    total_pos = int(y_bin.sum())
    if total_pos == 0:
        return np.array([1.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0])

    precisions = []
    recalls = []
    for th in thresholds:
        yp = (scores >= th).astype(np.int64)
        tp = np.sum((yp == 1) & (y_bin == 1))
        fp = np.sum((yp == 1) & (y_bin == 0))
        prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 1.0
        rec = float(tp / total_pos)
        precisions.append(prec)
        recalls.append(rec)

    precisions.append(1.0)
    recalls.append(0.0)
    return np.array(precisions), np.array(recalls), thresholds


def average_precision_score(
    y_true: ArrayLike,
    y_score: ArrayLike,
    *,
    pos_label: Optional[Any] = None,
) -> float:
    """Compute Average Precision (AP) from prediction scores."""
    precision, recall, _ = precision_recall_curve(y_true, y_score, pos_label=pos_label)
    # recall is decreasing from 1.0 down to 0.0: sum_{n} (R_n - R_{n-1}) * P_n
    return float(np.sum(-np.diff(recall) * precision[:-1]))


def roc_auc_score(
    y_true: ArrayLike,
    y_score: ArrayLike,
) -> float:
    """Binary ROC AUC from scores (higher = more positive class)."""
    yt = np.asarray(y_true).ravel()
    scores = np.asarray(y_score, dtype=np.float64).ravel()
    labels = np.unique(yt)
    if len(labels) != 2:
        raise ValueError("roc_auc_score supports binary classification only")
    pos = labels[1]
    y_bin = (yt == pos).astype(np.int64)
    order = np.argsort(-scores)
    y_sorted = y_bin[order]
    n_pos = y_bin.sum()
    n_neg = len(y_bin) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    tpr = np.cumsum(y_sorted) / n_pos
    fpr = np.cumsum(1 - y_sorted) / n_neg
    return _trapz(tpr, fpr)


def classification_report(
    y_true: ArrayLike,
    y_pred: ArrayLike,
) -> str:
    """Text summary of precision, recall, and F1 per class."""
    yt, yp = _check_lengths(y_true, y_pred)
    labels = np.unique(np.concatenate([yt, yp]))
    lines = [f"{'':>12} {'precision':>10} {'recall':>10} {'f1':>10} {'support':>10}"]
    for lab in labels:
        mask_true = yt == lab
        mask_pred = yp == lab
        tp = np.sum(mask_true & mask_pred)
        fp = np.sum(~mask_true & mask_pred)
        fn = np.sum(mask_true & ~mask_pred)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        sup = int(mask_true.sum())
        lines.append(f"{str(lab):>12} {prec:10.4f} {rec:10.4f} {f1:10.4f} {sup:10d}")
    lines.append(f"\naccuracy: {accuracy_score(yt, yp):.4f}")
    return "\n".join(lines)
