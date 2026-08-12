"""Statistical helpers for research comparisons."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

ArrayLike = Union[np.ndarray, Sequence[Any]]


def bootstrap_ci(
    values: ArrayLike,
    *,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    seed: Optional[int] = None,
) -> Tuple[float, float, float]:
    """
    Bootstrap confidence interval for the mean.

    Returns
    -------
    mean, lower, upper
    """
    arr = np.asarray(values, dtype=np.float64).ravel()
    if len(arr) == 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n_bootstrap):
        sample = rng.choice(arr, size=len(arr), replace=True)
        means.append(float(np.mean(sample)))
    means_arr = np.array(means)
    alpha = (1 - ci) / 2
    return (
        float(np.mean(arr)),
        float(np.quantile(means_arr, alpha)),
        float(np.quantile(means_arr, 1 - alpha)),
    )


def mcnemar_test(y_true: ArrayLike, pred_a: ArrayLike, pred_b: ArrayLike) -> Dict[str, float]:
    """
    McNemar test for paired classifier comparison (binary labels).

    Returns chi2 statistic and approximate p-value (no scipy required).
    """
    yt = np.asarray(y_true).ravel()
    a = np.asarray(pred_a).ravel()
    b = np.asarray(pred_b).ravel()
    # Contingency: b correct & a wrong vs a correct & b wrong
    b_right_a_wrong = np.sum((b == yt) & (a != yt))
    a_right_b_wrong = np.sum((a == yt) & (b != yt))
    if b_right_a_wrong + a_right_b_wrong == 0:
        return {"chi2": 0.0, "p_value": 1.0}
    chi2 = (abs(b_right_a_wrong - a_right_b_wrong) - 1) ** 2 / (
        b_right_a_wrong + a_right_b_wrong
    )
    # Wilson-Hilferty approx for df=1 — rough p-value
    from math import erfc, sqrt

    p = erfc(sqrt(chi2 / 2))
    return {"chi2": float(chi2), "p_value": float(p)}


def compare_models(
    y_true: ArrayLike,
    pred_a: ArrayLike,
    pred_b: ArrayLike,
    *,
    labels: Tuple[str, str] = ("model_a", "model_b"),
) -> Dict[str, Any]:
    """
    Compare two classifiers on the same test set.

    Returns accuracies and McNemar test when labels are binary.
    """
    from .classification import accuracy_score

    yt = np.asarray(y_true).ravel()
    a = np.asarray(pred_a).ravel()
    b = np.asarray(pred_b).ravel()
    acc_a = float(accuracy_score(yt, a))
    acc_b = float(accuracy_score(yt, b))
    out: Dict[str, Any] = {
        labels[0]: {"accuracy": acc_a},
        labels[1]: {"accuracy": acc_b},
        "delta_accuracy": acc_b - acc_a,
    }
    if len(np.unique(yt)) == 2:
        out["mcnemar"] = mcnemar_test(yt, a, b)
    return out
