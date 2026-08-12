"""Synthetic data generators — create arbitrarily-sized datasets on the fly.

All ``make_*`` functions accept ``n_samples``, ``n_features`` (where applicable),
a ``seed`` for reproducibility, and return a :class:`Dataset`.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple, Union

import numpy as np

from ._base import Dataset


# ===================================================================
# make_classification
# ===================================================================

def make_classification(
    *,
    n_samples: int = 1000,
    n_features: int = 20,
    n_informative: int = 10,
    n_redundant: int = 5,
    n_classes: int = 2,
    class_sep: float = 1.0,
    flip_y: float = 0.01,
    weights: Optional[Sequence[float]] = None,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate a random multi-class classification dataset.

    Parameters
    ----------
    n_features : int
        Total number of features (informative + redundant + noise).
    n_informative : int
        Number of features that actually carry class-discriminating signal.
    n_redundant : int
        Number of features that are random linear combinations of informative
        features.
    n_classes : int
        Number of target classes.
    class_sep : float
        Factor multiplied into the cluster standard deviation; larger values
        make classes more separable.
    flip_y : float
        Fraction of labels randomly flipped (adds noise).
    weights : sequence of float, optional
        Class proportions. If ``None``, classes are balanced.
    """
    rng = np.random.RandomState(seed)

    n_informative = min(n_informative, n_features)
    n_redundant = min(n_redundant, n_features - n_informative)
    n_noise = n_features - n_informative - n_redundant

    if weights is None:
        weights_arr = np.ones(n_classes) / n_classes
    else:
        weights_arr = np.array(weights[:n_classes], dtype=np.float64)
        weights_arr /= weights_arr.sum()

    counts = (weights_arr * n_samples).astype(int)
    counts[-1] = n_samples - counts[:-1].sum()

    centroids = rng.randn(n_classes, n_informative) * class_sep * 2

    data_parts, target_parts = [], []
    for cls in range(n_classes):
        n = counts[cls]
        samples = rng.randn(n, n_informative) * (1.0 / class_sep) + centroids[cls]
        data_parts.append(samples)
        target_parts.append(np.full(n, cls, dtype=np.int64))

    informative = np.vstack(data_parts)
    target = np.concatenate(target_parts)

    if n_redundant > 0:
        mixing = rng.randn(n_informative, n_redundant)
        redundant = informative @ mixing
    else:
        redundant = np.zeros((n_samples, 0))

    if n_noise > 0:
        noise = rng.randn(n_samples, n_noise)
    else:
        noise = np.zeros((n_samples, 0))

    data = np.hstack([informative, redundant, noise])

    if flip_y > 0:
        n_flip = int(n_samples * flip_y)
        flip_idx = rng.choice(n_samples, n_flip, replace=False)
        target[flip_idx] = rng.randint(0, n_classes, n_flip)

    indices = np.arange(n_samples)
    rng.shuffle(indices)
    data, target = data[indices], target[indices]

    return Dataset(
        data=data,
        target=target,
        feature_names=[f"x{i}" for i in range(n_features)],
        target_names=[f"class_{i}" for i in range(n_classes)],
        description=(
            f"Synthetic classification dataset. {n_samples} samples, {n_features} features "
            f"({n_informative} informative, {n_redundant} redundant, {n_noise} noise), "
            f"{n_classes} classes."
        ),
        name="synthetic_classification",
        metadata={
            "task": "classification",
            "n_classes": n_classes,
            "n_informative": n_informative,
            "n_redundant": n_redundant,
            "n_noise": n_noise,
            "class_sep": class_sep,
            "flip_y": flip_y,
        },
    )


# ===================================================================
# make_regression
# ===================================================================

def make_regression(
    *,
    n_samples: int = 1000,
    n_features: int = 10,
    n_informative: int = 5,
    noise: float = 1.0,
    bias: float = 0.0,
    effective_rank: Optional[int] = None,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate a random regression dataset.

    Parameters
    ----------
    n_informative : int
        Number of features with non-zero coefficients.
    noise : float
        Standard deviation of Gaussian noise added to the target.
    bias : float
        Bias (intercept) term.
    effective_rank : int, optional
        If set, the feature matrix has approximately this many significant
        singular values (creates collinear features).
    """
    rng = np.random.RandomState(seed)
    n_informative = min(n_informative, n_features)

    if effective_rank is not None:
        singular_values = np.zeros(n_features)
        singular_values[:effective_rank] = rng.uniform(1, 10, effective_rank)
        singular_values[effective_rank:] = rng.uniform(0.001, 0.1, n_features - effective_rank)
        U = np.linalg.qr(rng.randn(n_samples, n_features))[0][:, :n_features]
        V = np.linalg.qr(rng.randn(n_features, n_features))[0]
        data = U * singular_values @ V.T
    else:
        data = rng.randn(n_samples, n_features)

    coef = np.zeros(n_features)
    coef[:n_informative] = rng.uniform(-5, 5, n_informative)
    coef[:n_informative] *= 100.0 / (np.abs(coef[:n_informative]).sum() + 1e-12)

    target = data @ coef + bias + rng.normal(0, noise, n_samples)

    return Dataset(
        data=data,
        target=target.astype(np.float64),
        feature_names=[f"x{i}" for i in range(n_features)],
        target_names=["y"],
        description=(
            f"Synthetic regression dataset. {n_samples} samples, {n_features} features "
            f"({n_informative} informative), noise={noise}, bias={bias}."
        ),
        name="synthetic_regression",
        metadata={
            "task": "regression",
            "n_informative": n_informative,
            "noise": noise,
            "bias": bias,
            "coefficients": coef.tolist(),
        },
    )


# ===================================================================
# make_clusters
# ===================================================================

def make_clusters(
    *,
    n_samples: int = 500,
    n_features: int = 2,
    n_clusters: int = 5,
    cluster_std: Union[float, Sequence[float]] = 1.0,
    center_range: Tuple[float, float] = (-10.0, 10.0),
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate isotropic Gaussian clusters for clustering tasks.

    Parameters
    ----------
    n_clusters : int
        Number of cluster centers.
    cluster_std : float or sequence of float
        Per-cluster standard deviation.  If scalar, the same value is used
        for all clusters.
    center_range : tuple of float
        Range ``(low, high)`` for random center placement.
    """
    rng = np.random.RandomState(seed)
    centers = rng.uniform(center_range[0], center_range[1], size=(n_clusters, n_features))

    if isinstance(cluster_std, (float, int)):
        stds = np.full(n_clusters, float(cluster_std))
    else:
        stds = np.array(cluster_std[:n_clusters], dtype=np.float64)

    per_cluster = n_samples // n_clusters
    remainder = n_samples - per_cluster * n_clusters

    data_parts, target_parts = [], []
    for i in range(n_clusters):
        n = per_cluster + (1 if i < remainder else 0)
        samples = rng.normal(loc=centers[i], scale=stds[i], size=(n, n_features))
        data_parts.append(samples)
        target_parts.append(np.full(n, i, dtype=np.int64))

    data = np.vstack(data_parts)
    target = np.concatenate(target_parts)

    indices = np.arange(len(target))
    rng.shuffle(indices)

    return Dataset(
        data=data[indices],
        target=target[indices],
        feature_names=[f"x{i}" for i in range(n_features)],
        target_names=[f"cluster_{i}" for i in range(n_clusters)],
        description=(
            f"Synthetic clustering dataset. {n_samples} samples, {n_features} features, "
            f"{n_clusters} clusters."
        ),
        name="synthetic_clusters",
        metadata={
            "task": "clustering",
            "n_clusters": n_clusters,
            "centers": centers.tolist(),
        },
    )


# ===================================================================
# make_moons (parametric)
# ===================================================================

def make_moons(
    *,
    n_samples: int = 500,
    noise: float = 0.1,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate two interleaving half-circles at arbitrary scale.

    This is the parametric version — ``load_moons`` gives the classic 200-sample
    variant.
    """
    rng = np.random.RandomState(seed)
    n_half = n_samples // 2
    n_other = n_samples - n_half

    theta_0 = np.linspace(0, np.pi, n_half)
    theta_1 = np.linspace(0, np.pi, n_other)

    x0 = np.column_stack([np.cos(theta_0), np.sin(theta_0)])
    x1 = np.column_stack([1 - np.cos(theta_1), 1 - np.sin(theta_1) - 0.5])

    data = np.vstack([x0, x1]) + rng.normal(0, noise, (n_samples, 2))
    target = np.concatenate([np.zeros(n_half, dtype=np.int64),
                             np.ones(n_other, dtype=np.int64)])
    idx = np.arange(n_samples)
    rng.shuffle(idx)

    return Dataset(
        data=data[idx],
        target=target[idx],
        feature_names=["x1", "x2"],
        target_names=["moon_0", "moon_1"],
        description=f"Synthetic moons dataset. {n_samples} samples, noise={noise}.",
        name="synthetic_moons",
        metadata={"task": "classification", "n_classes": 2},
    )


# ===================================================================
# make_circles (parametric)
# ===================================================================

def make_circles(
    *,
    n_samples: int = 500,
    noise: float = 0.05,
    factor: float = 0.5,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate two concentric circles at arbitrary scale."""
    rng = np.random.RandomState(seed)
    n_outer = n_samples // 2
    n_inner = n_samples - n_outer

    theta_o = np.linspace(0, 2 * np.pi, n_outer, endpoint=False)
    theta_i = np.linspace(0, 2 * np.pi, n_inner, endpoint=False)

    outer = np.column_stack([np.cos(theta_o), np.sin(theta_o)])
    inner = np.column_stack([np.cos(theta_i) * factor, np.sin(theta_i) * factor])

    data = np.vstack([outer, inner]) + rng.normal(0, noise, (n_samples, 2))
    target = np.concatenate([np.zeros(n_outer, dtype=np.int64),
                             np.ones(n_inner, dtype=np.int64)])
    idx = np.arange(n_samples)
    rng.shuffle(idx)

    return Dataset(
        data=data[idx],
        target=target[idx],
        feature_names=["x1", "x2"],
        target_names=["outer", "inner"],
        description=f"Synthetic circles dataset. {n_samples} samples, factor={factor}, noise={noise}.",
        name="synthetic_circles",
        metadata={"task": "classification", "n_classes": 2},
    )


# ===================================================================
# make_blobs (parametric)
# ===================================================================

def make_blobs(
    *,
    n_samples: int = 500,
    n_features: int = 2,
    centers: Optional[Union[int, np.ndarray]] = 3,
    cluster_std: float = 1.0,
    center_range: Tuple[float, float] = (-10.0, 10.0),
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate Gaussian blobs with optional explicit centers.

    Parameters
    ----------
    centers : int or ndarray
        If int, that many centers are generated randomly.  If an ndarray of
        shape ``(k, n_features)``, those exact centers are used.
    """
    rng = np.random.RandomState(seed)

    if isinstance(centers, (int, type(None))):
        k = centers or 3
        center_pts = rng.uniform(center_range[0], center_range[1], (k, n_features))
    else:
        center_pts = np.asarray(centers)
        k = center_pts.shape[0]
        n_features = center_pts.shape[1]

    per = n_samples // k
    remainder = n_samples - per * k

    data_parts, target_parts = [], []
    for i in range(k):
        n = per + (1 if i < remainder else 0)
        samples = rng.normal(center_pts[i], cluster_std, (n, n_features))
        data_parts.append(samples)
        target_parts.append(np.full(n, i, dtype=np.int64))

    data = np.vstack(data_parts)
    target = np.concatenate(target_parts)
    idx = np.arange(len(target))
    rng.shuffle(idx)

    return Dataset(
        data=data[idx],
        target=target[idx],
        feature_names=[f"x{i}" for i in range(n_features)],
        target_names=[f"blob_{i}" for i in range(k)],
        description=f"Synthetic blobs. {n_samples} samples, {n_features} features, {k} centers.",
        name="synthetic_blobs",
        metadata={"task": "clustering", "n_clusters": k, "centers": center_pts.tolist()},
    )


# ===================================================================
# make_sparse_classification
# ===================================================================

def make_sparse_classification(
    *,
    n_samples: int = 500,
    n_features: int = 50,
    n_informative: int = 5,
    density: float = 0.3,
    n_classes: int = 2,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate a sparse classification dataset.

    Most feature entries are zero, mimicking text bag-of-words or one-hot
    encoded data.

    Parameters
    ----------
    density : float
        Approximate fraction of non-zero entries per sample.
    """
    rng = np.random.RandomState(seed)
    mask = rng.rand(n_samples, n_features) < density
    values = rng.randn(n_samples, n_features) * mask
    data = values

    coef = np.zeros(n_features)
    coef[:n_informative] = rng.randn(n_informative) * 3

    logits = data @ coef
    probs = 1 / (1 + np.exp(-logits))

    if n_classes == 2:
        target = (probs > 0.5).astype(np.int64)
    else:
        target = np.digitize(probs, np.linspace(0, 1, n_classes + 1)[1:-1]).astype(np.int64)

    return Dataset(
        data=data,
        target=target,
        feature_names=[f"x{i}" for i in range(n_features)],
        target_names=[f"class_{i}" for i in range(n_classes)],
        description=(
            f"Sparse classification dataset. {n_samples} samples, {n_features} features, "
            f"density={density}, {n_classes} classes."
        ),
        name="sparse_classification",
        metadata={"task": "classification", "n_classes": n_classes, "density": density},
    )


# ===================================================================
# make_time_series
# ===================================================================

def make_time_series(
    *,
    n_samples: int = 200,
    n_steps: int = 50,
    n_features: int = 1,
    trend: float = 0.02,
    seasonality: float = 1.0,
    noise: float = 0.3,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate synthetic time-series data with trend + seasonality + noise.

    Returns a dataset where ``data`` is shape ``(n_samples, n_steps * n_features)``
    and ``target`` is the next-step value (simple forecasting target).
    """
    rng = np.random.RandomState(seed)
    t = np.arange(n_steps + 1, dtype=np.float64)

    all_series = []
    targets = []
    for _ in range(n_samples):
        phase = rng.uniform(0, 2 * np.pi)
        amp = rng.uniform(0.5, 1.5) * seasonality
        tr = rng.uniform(0.5, 1.5) * trend
        series = tr * t + amp * np.sin(2 * np.pi * t / 12 + phase)
        if n_features > 1:
            extra = np.column_stack([
                rng.randn(n_steps + 1) * noise for _ in range(n_features - 1)
            ])
            full = np.column_stack([series.reshape(-1, 1), extra])
        else:
            full = series.reshape(-1, 1)
        full += rng.normal(0, noise, full.shape)
        all_series.append(full[:n_steps].ravel())
        targets.append(full[n_steps, 0])

    data = np.array(all_series)
    target = np.array(targets, dtype=np.float64)

    feature_names = []
    for step in range(n_steps):
        for f in range(n_features):
            feature_names.append(f"t{step}_f{f}" if n_features > 1 else f"t{step}")

    return Dataset(
        data=data,
        target=target,
        feature_names=feature_names,
        target_names=["next_value"],
        description=(
            f"Synthetic time-series dataset. {n_samples} series of {n_steps} steps, "
            f"{n_features} features each."
        ),
        name="synthetic_timeseries",
        metadata={"task": "regression", "n_steps": n_steps},
    )


# ===================================================================
# make_multilabel
# ===================================================================

def make_multilabel(
    *,
    n_samples: int = 500,
    n_features: int = 20,
    n_labels: int = 5,
    n_active: int = 2,
    seed: Optional[int] = 42,
) -> Dataset:
    """Generate a multi-label classification dataset.

    Each sample can have multiple active labels simultaneously.

    Parameters
    ----------
    n_labels : int
        Total number of possible labels.
    n_active : int
        Average number of active labels per sample.
    """
    rng = np.random.RandomState(seed)
    data = rng.randn(n_samples, n_features)

    coef = rng.randn(n_features, n_labels) * 2
    logits = data @ coef
    probs = 1 / (1 + np.exp(-logits))

    threshold = 1 - (n_active / n_labels)
    target_matrix = (probs > threshold).astype(np.int64)

    target = np.array([
        np.where(row == 1)[0].tolist() for row in target_matrix
    ], dtype=object)

    return Dataset(
        data=data,
        target=target,
        feature_names=[f"x{i}" for i in range(n_features)],
        target_names=[f"label_{i}" for i in range(n_labels)],
        description=(
            f"Multi-label classification dataset. {n_samples} samples, "
            f"{n_features} features, {n_labels} labels, ~{n_active} active per sample."
        ),
        name="synthetic_multilabel",
        metadata={
            "task": "multilabel_classification",
            "n_labels": n_labels,
            "target_matrix": target_matrix,
        },
    )
