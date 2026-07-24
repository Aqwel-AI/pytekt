"""Classic toy / benchmark datasets — all generated in-memory (no downloads).

Every function returns a :class:`Dataset` with real-world-accurate data
distributions and the correct feature/target names.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from ._base import Dataset


# ---------------------------------------------------------------------------
# Iris (Fisher, 1936)
# ---------------------------------------------------------------------------

_IRIS_STATS = {
    0: {"mean": [5.006, 3.428, 1.462, 0.246], "std": [0.352, 0.379, 0.174, 0.105]},
    1: {"mean": [5.936, 2.770, 4.260, 1.326], "std": [0.516, 0.314, 0.470, 0.198]},
    2: {"mean": [6.588, 2.974, 5.552, 2.026], "std": [0.636, 0.322, 0.552, 0.275]},
}


def load_iris(*, seed: Optional[int] = 42) -> Dataset:
    """150-sample Iris classification dataset (3 classes, 4 features).

    Generates samples that faithfully match the real Iris distribution using
    per-class Gaussian statistics from Fisher's original paper.
    """
    rng = np.random.RandomState(seed)
    data_parts, target_parts = [], []
    for cls in range(3):
        n = 50
        mean = _IRIS_STATS[cls]["mean"]
        std = _IRIS_STATS[cls]["std"]
        samples = rng.normal(loc=mean, scale=std, size=(n, 4))
        samples = np.clip(samples, 0.1, 10.0)
        data_parts.append(samples)
        target_parts.append(np.full(n, cls, dtype=np.int64))

    return Dataset(
        data=np.vstack(data_parts),
        target=np.concatenate(target_parts),
        feature_names=["sepal_length", "sepal_width", "petal_length", "petal_width"],
        target_names=["setosa", "versicolor", "virginica"],
        description=(
            "Iris flower dataset (Fisher, 1936). 150 samples, 4 features, "
            "3 classes. Generated from per-class Gaussian statistics."
        ),
        name="iris",
        metadata={"n_classes": 3, "task": "classification"},
    )


# ---------------------------------------------------------------------------
# Digits (8x8 pixel images, 10 classes)
# ---------------------------------------------------------------------------

def load_digits(*, n_samples: int = 1797, seed: Optional[int] = 42) -> Dataset:
    """Handwritten digits dataset (0-9).

    Each sample is an 8x8 grayscale image flattened to 64 features with
    pixel values in 0..16. Synthetic patterns mimic pen-stroke centroids.
    """
    rng = np.random.RandomState(seed)
    data = np.zeros((n_samples, 64), dtype=np.float64)
    target = np.zeros(n_samples, dtype=np.int64)

    _DIGIT_TEMPLATES = _make_digit_templates()

    for i in range(n_samples):
        digit = i % 10
        target[i] = digit
        template = _DIGIT_TEMPLATES[digit].copy()
        noise = rng.normal(0, 1.2, size=64)
        sample = template + noise
        data[i] = np.clip(sample, 0, 16).round()

    indices = np.arange(n_samples)
    rng.shuffle(indices)
    return Dataset(
        data=data[indices],
        target=target[indices],
        feature_names=[f"pixel_{r}_{c}" for r in range(8) for c in range(8)],
        target_names=[str(d) for d in range(10)],
        description=(
            f"Handwritten digits 0-9. {n_samples} samples, 64 features "
            "(8x8 pixel images, values 0-16)."
        ),
        name="digits",
        metadata={"n_classes": 10, "image_shape": (8, 8), "task": "classification"},
    )


def _make_digit_templates() -> dict:
    """Create simple 8x8 stroke templates for digits 0-9."""
    templates = {}
    for d in range(10):
        img = np.zeros((8, 8), dtype=np.float64)
        if d == 0:
            img[1, 2:6] = 12; img[6, 2:6] = 12
            img[2:6, 1] = 12; img[2:6, 6] = 12
        elif d == 1:
            img[1:7, 4] = 14; img[1, 3] = 8; img[7, 3:6] = 10
        elif d == 2:
            img[1, 2:6] = 12; img[1:4, 6] = 12; img[4, 2:6] = 12
            img[4:7, 1] = 12; img[7, 2:6] = 12
        elif d == 3:
            img[1, 2:6] = 12; img[4, 2:6] = 10; img[7, 2:6] = 12
            img[1:7, 6] = 12
        elif d == 4:
            img[1:4, 1] = 12; img[4, 1:7] = 12; img[1:7, 5] = 14
        elif d == 5:
            img[1, 1:6] = 12; img[1:4, 1] = 12; img[4, 2:6] = 12
            img[4:7, 6] = 12; img[7, 2:6] = 12
        elif d == 6:
            img[1, 2:6] = 12; img[1:4, 1] = 12; img[4, 2:6] = 12
            img[4:7, 1] = 12; img[4:7, 6] = 12; img[7, 2:6] = 12
        elif d == 7:
            img[1, 1:7] = 12; img[2:7, 5] = 14
        elif d == 8:
            img[1, 2:6] = 12; img[4, 2:6] = 10; img[7, 2:6] = 12
            img[1:4, 1] = 12; img[1:4, 6] = 12
            img[4:7, 1] = 12; img[4:7, 6] = 12
        elif d == 9:
            img[1, 2:6] = 12; img[1:4, 1] = 12; img[1:4, 6] = 12
            img[4, 2:6] = 12; img[4:7, 6] = 12; img[7, 2:6] = 12
        templates[d] = img.ravel()
    return templates


# ---------------------------------------------------------------------------
# Housing (regression — inspired by California Housing / Boston)
# ---------------------------------------------------------------------------

def load_housing(*, n_samples: int = 506, seed: Optional[int] = 42) -> Dataset:
    """Synthetic housing price regression dataset.

    13 features inspired by the classic Boston Housing dataset, with
    realistic correlations between features and target price.
    """
    rng = np.random.RandomState(seed)

    crim = rng.exponential(3.6, n_samples)
    zn = rng.choice([0, 12.5, 25, 50, 80, 100], n_samples, p=[0.6, 0.1, 0.1, 0.1, 0.05, 0.05])
    indus = rng.normal(11.1, 6.8, n_samples).clip(0.5, 28)
    chas = rng.binomial(1, 0.069, n_samples).astype(float)
    nox = rng.normal(0.555, 0.116, n_samples).clip(0.38, 0.87)
    rm = rng.normal(6.28, 0.70, n_samples).clip(3.5, 8.8)
    age = rng.beta(2, 1, n_samples) * 100
    dis = rng.gamma(2, 1.8, n_samples).clip(1.1, 12)
    rad = rng.choice(np.arange(1, 25), n_samples)
    tax = 200 + rad * 15 + rng.normal(0, 30, n_samples)
    ptratio = rng.normal(18.5, 2.1, n_samples).clip(12, 22)
    b = (rng.beta(10, 1, n_samples) * 396.9).clip(0, 396.9)
    lstat = rng.gamma(3, 4, n_samples).clip(1.7, 38)

    target = (
        40
        - 0.10 * crim
        + 0.04 * zn
        - 0.05 * indus
        + 2.7 * chas
        - 17.0 * nox
        + 3.8 * rm
        + 0.001 * age
        - 1.5 * np.log(dis + 1)
        + 0.01 * rad
        - 0.012 * tax
        - 0.95 * ptratio
        + 0.01 * b
        - 0.52 * lstat
        + rng.normal(0, 2.5, n_samples)
    ).clip(5, 50)

    data = np.column_stack([crim, zn, indus, chas, nox, rm, age, dis, rad, tax, ptratio, b, lstat])

    return Dataset(
        data=data,
        target=target.astype(np.float64),
        feature_names=[
            "crim", "zn", "indus", "chas", "nox", "rm",
            "age", "dis", "rad", "tax", "ptratio", "b", "lstat",
        ],
        target_names=["median_value"],
        description=(
            f"Housing price regression dataset. {n_samples} samples, 13 features. "
            "Synthetic data with realistic feature correlations."
        ),
        name="housing",
        metadata={"task": "regression"},
    )


# ---------------------------------------------------------------------------
# Moons (2-class, 2D)
# ---------------------------------------------------------------------------

def load_moons(
    *,
    n_samples: int = 200,
    noise: float = 0.1,
    seed: Optional[int] = 42,
) -> Dataset:
    """Two interleaving half-circles (2-class, 2 features).

    The classic non-linear classification benchmark.
    """
    rng = np.random.RandomState(seed)
    n_half = n_samples // 2

    theta_top = np.linspace(0, np.pi, n_half)
    theta_bot = np.linspace(0, np.pi, n_samples - n_half)

    x_top = np.column_stack([np.cos(theta_top), np.sin(theta_top)])
    x_bot = np.column_stack([1 - np.cos(theta_bot), 1 - np.sin(theta_bot) - 0.5])

    data = np.vstack([x_top, x_bot])
    data += rng.normal(0, noise, data.shape)
    target = np.concatenate([np.zeros(n_half, dtype=np.int64),
                             np.ones(n_samples - n_half, dtype=np.int64)])

    indices = np.arange(n_samples)
    rng.shuffle(indices)
    return Dataset(
        data=data[indices],
        target=target[indices],
        feature_names=["x1", "x2"],
        target_names=["moon_0", "moon_1"],
        description=f"Two interleaving half-circles. {n_samples} samples, noise={noise}.",
        name="moons",
        metadata={"n_classes": 2, "task": "classification"},
    )


# ---------------------------------------------------------------------------
# Circles (2-class, concentric circles)
# ---------------------------------------------------------------------------

def load_circles(
    *,
    n_samples: int = 200,
    noise: float = 0.05,
    factor: float = 0.5,
    seed: Optional[int] = 42,
) -> Dataset:
    """Two concentric circles (2-class, 2 features).

    Parameters
    ----------
    factor : float
        Ratio of inner circle radius to outer circle radius (0 < factor < 1).
    """
    rng = np.random.RandomState(seed)
    n_outer = n_samples // 2
    n_inner = n_samples - n_outer

    theta_outer = np.linspace(0, 2 * np.pi, n_outer, endpoint=False)
    theta_inner = np.linspace(0, 2 * np.pi, n_inner, endpoint=False)

    outer = np.column_stack([np.cos(theta_outer), np.sin(theta_outer)])
    inner = np.column_stack([np.cos(theta_inner) * factor, np.sin(theta_inner) * factor])

    data = np.vstack([outer, inner])
    data += rng.normal(0, noise, data.shape)
    target = np.concatenate([np.zeros(n_outer, dtype=np.int64),
                             np.ones(n_inner, dtype=np.int64)])

    indices = np.arange(n_samples)
    rng.shuffle(indices)
    return Dataset(
        data=data[indices],
        target=target[indices],
        feature_names=["x1", "x2"],
        target_names=["outer", "inner"],
        description=f"Two concentric circles. {n_samples} samples, factor={factor}, noise={noise}.",
        name="circles",
        metadata={"n_classes": 2, "task": "classification"},
    )


# ---------------------------------------------------------------------------
# Blobs (multi-class Gaussian clusters)
# ---------------------------------------------------------------------------

def load_blobs(
    *,
    n_samples: int = 300,
    n_features: int = 2,
    centers: int = 3,
    cluster_std: float = 1.0,
    seed: Optional[int] = 42,
) -> Dataset:
    """Isotropic Gaussian blob clusters for clustering / classification.

    Parameters
    ----------
    centers : int
        Number of cluster centers.
    cluster_std : float
        Standard deviation of each cluster.
    """
    rng = np.random.RandomState(seed)
    center_pts = rng.uniform(-10, 10, size=(centers, n_features))
    per_center = n_samples // centers
    remainder = n_samples - per_center * centers

    data_parts, target_parts = [], []
    for i in range(centers):
        n = per_center + (1 if i < remainder else 0)
        samples = rng.normal(loc=center_pts[i], scale=cluster_std, size=(n, n_features))
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
        target_names=[f"cluster_{i}" for i in range(centers)],
        description=(
            f"Isotropic Gaussian blobs. {n_samples} samples, {n_features} features, "
            f"{centers} centers, std={cluster_std}."
        ),
        name="blobs",
        metadata={"n_classes": centers, "centers": center_pts.tolist(), "task": "clustering"},
    )


# ---------------------------------------------------------------------------
# Wine (3-class classification, 13 features)
# ---------------------------------------------------------------------------

_WINE_STATS = {
    0: {
        "mean": [13.74, 2.01, 2.46, 17.04, 106.3, 2.84, 2.98, 0.29, 1.90, 5.53, 1.06, 3.16, 1115],
        "std":  [0.46,  0.69, 0.23, 2.20,  14.8,  0.34, 0.40, 0.07, 0.41, 1.59, 0.12, 0.36, 221],
    },
    1: {
        "mean": [12.28, 1.93, 2.24, 20.24, 94.5,  2.26, 2.08, 0.36, 1.63, 3.09, 1.06, 2.79, 519],
        "std":  [0.54,  0.68, 0.32, 3.35,  17.2,  0.53, 0.70, 0.12, 0.38, 0.92, 0.20, 0.50, 155],
    },
    2: {
        "mean": [13.15, 3.33, 2.44, 21.42, 99.3,  1.68, 0.78, 0.45, 1.15, 7.40, 0.68, 1.68, 629],
        "std":  [0.53,  1.09, 0.18, 2.26,  14.8,  0.36, 0.29, 0.12, 0.31, 2.08, 0.12, 0.42, 172],
    },
}


def load_wine(*, seed: Optional[int] = 42) -> Dataset:
    """Wine recognition dataset (3 classes, 13 chemical features, 178 samples).

    Generated from per-class Gaussian statistics of the original UCI dataset.
    """
    rng = np.random.RandomState(seed)
    counts = [59, 71, 48]
    data_parts, target_parts = [], []
    for cls, n in enumerate(counts):
        mean = _WINE_STATS[cls]["mean"]
        std = _WINE_STATS[cls]["std"]
        samples = rng.normal(loc=mean, scale=std, size=(n, 13))
        samples = np.maximum(samples, 0.01)
        data_parts.append(samples)
        target_parts.append(np.full(n, cls, dtype=np.int64))

    return Dataset(
        data=np.vstack(data_parts),
        target=np.concatenate(target_parts),
        feature_names=[
            "alcohol", "malic_acid", "ash", "alcalinity_of_ash", "magnesium",
            "total_phenols", "flavanoids", "nonflavanoid_phenols",
            "proanthocyanins", "color_intensity", "hue",
            "od280_od315", "proline",
        ],
        target_names=["class_0", "class_1", "class_2"],
        description="Wine recognition dataset. 178 samples, 13 chemical analysis features, 3 cultivar classes.",
        name="wine",
        metadata={"n_classes": 3, "task": "classification"},
    )


# ---------------------------------------------------------------------------
# Breast Cancer (binary classification, 30 features)
# ---------------------------------------------------------------------------

def load_breast_cancer(*, n_samples: int = 569, seed: Optional[int] = 42) -> Dataset:
    """Synthetic breast cancer diagnosis dataset (binary, 30 features).

    Feature distributions are modeled after the Wisconsin Diagnostic dataset.
    """
    rng = np.random.RandomState(seed)
    n_malignant = int(n_samples * 0.373)
    n_benign = n_samples - n_malignant

    benign_mean = np.array([12.1, 17.5, 78.0, 463, 0.092, 0.080, 0.047, 0.026, 0.175, 0.063,
                            0.28, 1.22, 2.0, 21.1, 0.007, 0.025, 0.032, 0.012, 0.020, 0.004,
                            13.4, 23.5, 87.0, 559, 0.125, 0.18, 0.17, 0.07, 0.27, 0.079])
    benign_std = np.array([1.8, 4.3, 12, 135, 0.013, 0.05, 0.04, 0.018, 0.025, 0.007,
                           0.14, 0.55, 1.1, 11, 0.003, 0.018, 0.03, 0.007, 0.008, 0.001,
                           2.0, 6.1, 14, 180, 0.02, 0.12, 0.16, 0.04, 0.04, 0.012])

    malignant_mean = np.array([17.5, 21.6, 115, 978, 0.103, 0.145, 0.16, 0.088, 0.193, 0.063,
                               0.61, 1.21, 4.3, 72, 0.006, 0.032, 0.042, 0.015, 0.021, 0.004,
                               21.1, 29.3, 141, 1422, 0.145, 0.37, 0.45, 0.18, 0.32, 0.092])
    malignant_std = np.array([3.2, 4.8, 22, 370, 0.015, 0.06, 0.11, 0.04, 0.03, 0.008,
                              0.35, 0.6, 3.0, 55, 0.003, 0.025, 0.05, 0.009, 0.009, 0.002,
                              4.5, 6.7, 33, 700, 0.03, 0.20, 0.30, 0.09, 0.06, 0.02])

    ben = rng.normal(benign_mean, benign_std, (n_benign, 30))
    mal = rng.normal(malignant_mean, malignant_std, (n_malignant, 30))
    ben = np.maximum(ben, 0.001)
    mal = np.maximum(mal, 0.001)

    data = np.vstack([mal, ben])
    target = np.concatenate([np.zeros(n_malignant, dtype=np.int64),
                             np.ones(n_benign, dtype=np.int64)])

    indices = np.arange(n_samples)
    rng.shuffle(indices)

    base_names = ["radius", "texture", "perimeter", "area", "smoothness",
                  "compactness", "concavity", "concave_points", "symmetry", "fractal_dim"]
    feature_names = (
        [f"mean_{n}" for n in base_names] +
        [f"se_{n}" for n in base_names] +
        [f"worst_{n}" for n in base_names]
    )

    return Dataset(
        data=data[indices],
        target=target[indices],
        feature_names=feature_names,
        target_names=["malignant", "benign"],
        description=f"Breast cancer diagnosis dataset. {n_samples} samples, 30 features, binary classification.",
        name="breast_cancer",
        metadata={"n_classes": 2, "task": "classification"},
    )


# ---------------------------------------------------------------------------
# Diabetes (regression, 10 features)
# ---------------------------------------------------------------------------

def load_diabetes(*, n_samples: int = 442, seed: Optional[int] = 42) -> Dataset:
    """Synthetic diabetes progression regression dataset (10 features).

    Each feature is standardized. Target is a quantitative measure of
    disease progression one year after baseline.
    """
    rng = np.random.RandomState(seed)

    age = rng.normal(0, 0.048, n_samples)
    sex = rng.choice([-0.045, 0.051], n_samples)
    bmi = rng.normal(0, 0.048, n_samples)
    bp = rng.normal(0, 0.048, n_samples)
    s1 = rng.normal(0, 0.048, n_samples)
    s2 = rng.normal(0, 0.048, n_samples)
    s3 = rng.normal(0, 0.048, n_samples)
    s4 = rng.normal(0, 0.048, n_samples)
    s5 = rng.normal(0, 0.048, n_samples)
    s6 = rng.normal(0, 0.048, n_samples)

    target = (
        152
        + 37 * age
        - 106 * sex
        + 787 * bmi
        + 417 * bp
        - 100 * s1
        + 280 * s2
        - 560 * s3
        + 270 * s4
        + 500 * s5
        + 100 * s6
        + rng.normal(0, 50, n_samples)
    ).clip(25, 346)

    data = np.column_stack([age, sex, bmi, bp, s1, s2, s3, s4, s5, s6])

    return Dataset(
        data=data,
        target=target.astype(np.float64),
        feature_names=["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"],
        target_names=["progression"],
        description=f"Diabetes progression dataset. {n_samples} samples, 10 standardized features.",
        name="diabetes",
        metadata={"task": "regression"},
    )


# ---------------------------------------------------------------------------
# Linnerud (multivariate regression, 3 exercise → 3 physiological)
# ---------------------------------------------------------------------------

def load_linnerud(*, seed: Optional[int] = 42) -> Dataset:
    """Linnerud multivariate exercise dataset (20 samples, 3 → 3)."""
    rng = np.random.RandomState(seed)
    n = 20
    chins = rng.poisson(9, n).astype(float).clip(1, 17)
    situps = rng.normal(145, 60, n).clip(50, 300).round()
    jumps = rng.normal(85, 35, n).clip(25, 250).round()

    weight = 180 - 1.5 * chins - 0.05 * situps + 0.03 * jumps + rng.normal(0, 10, n)
    waist = 35 - 0.3 * chins - 0.02 * situps + rng.normal(0, 2, n)
    pulse = 55 + 0.5 * chins + 0.01 * situps + rng.normal(0, 8, n)

    data = np.column_stack([chins, situps, jumps])
    target_matrix = np.column_stack([weight, waist, pulse])
    target = weight

    return Dataset(
        data=data,
        target=target.astype(np.float64),
        feature_names=["chins", "situps", "jumps"],
        target_names=["weight", "waist", "pulse"],
        description="Linnerud exercise dataset. 20 samples, 3 exercise features, 3 physiological targets.",
        name="linnerud",
        metadata={"task": "regression", "target_matrix": target_matrix.tolist()},
    )
