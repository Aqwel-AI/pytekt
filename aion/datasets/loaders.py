"""Convenience loaders: fetch any built-in dataset by name, list available
datasets, and load with automatic train/test splitting.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from ._base import Dataset, train_test_split_dataset

# Registry maps short names → loader callables (populated at import time).
_REGISTRY: Dict[str, Callable[..., Dataset]] = {}


def _register(name: str, fn: Callable[..., Dataset]) -> None:
    _REGISTRY[name] = fn


def _ensure_registry() -> None:
    """Lazy-populate the registry on first use."""
    if _REGISTRY:
        return

    from .toy import (
        load_iris, load_digits, load_housing, load_moons,
        load_circles, load_blobs, load_wine, load_breast_cancer,
        load_diabetes, load_linnerud,
    )
    from .text import load_sentiment, load_topics, load_ner, load_spam, load_qa
    from .generators import (
        make_classification, make_regression, make_clusters,
        make_moons, make_circles, make_blobs,
        make_sparse_classification, make_time_series, make_multilabel,
    )

    for name, fn in [
        ("iris", load_iris),
        ("digits", load_digits),
        ("housing", load_housing),
        ("moons", load_moons),
        ("circles", load_circles),
        ("blobs", load_blobs),
        ("wine", load_wine),
        ("breast_cancer", load_breast_cancer),
        ("diabetes", load_diabetes),
        ("linnerud", load_linnerud),
        ("sentiment", load_sentiment),
        ("topics", load_topics),
        ("ner", load_ner),
        ("spam", load_spam),
        ("qa", load_qa),
    ]:
        _register(name, fn)

    for name, fn in [
        ("make_classification", make_classification),
        ("make_regression", make_regression),
        ("make_clusters", make_clusters),
        ("make_moons", make_moons),
        ("make_circles", make_circles),
        ("make_blobs", make_blobs),
        ("make_sparse_classification", make_sparse_classification),
        ("make_time_series", make_time_series),
        ("make_multilabel", make_multilabel),
    ]:
        _register(name, fn)


# ===================================================================
# Public helpers
# ===================================================================

def list_datasets() -> List[Dict[str, str]]:
    """Return a list of all available dataset names with their task types.

    >>> from aion.datasets import list_datasets
    >>> for ds in list_datasets():
    ...     print(ds["name"], "—", ds["task"])
    """
    _ensure_registry()
    result = []
    for name, fn in _REGISTRY.items():
        doc = (fn.__doc__ or "").split("\n")[0].strip()
        task = "unknown"
        try:
            ds = fn(seed=0) if "seed" in fn.__code__.co_varnames else fn()
            task = ds.metadata.get("task", "unknown")
        except Exception:
            pass
        result.append({"name": name, "description": doc, "task": task})
    return result


def fetch(
    name: str,
    *,
    return_split: bool = False,
    test_ratio: float = 0.2,
    seed: Optional[int] = 42,
    **kwargs: Any,
) -> Any:
    """Load a dataset by name, optionally split into train/test.

    Parameters
    ----------
    name : str
        Dataset identifier (e.g. ``"iris"``, ``"make_classification"``).
    return_split : bool
        If ``True``, return ``(train_dataset, test_dataset)`` instead of
        the full dataset.
    test_ratio : float
        Fraction for the test set when ``return_split=True``.
    **kwargs
        Extra keyword arguments forwarded to the underlying loader/generator.

    Examples
    --------
    >>> ds = fetch("iris")
    >>> train, test = fetch("iris", return_split=True)
    >>> ds = fetch("make_classification", n_samples=5000, n_features=30)
    """
    _ensure_registry()
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(f"Unknown dataset {name!r}. Available: {available}")

    loader = _REGISTRY[name]
    if "seed" in (loader.__code__.co_varnames if hasattr(loader, "__code__") else []):
        kwargs.setdefault("seed", seed)
    ds = loader(**kwargs)

    if return_split:
        return train_test_split_dataset(ds, test_ratio=test_ratio, seed=seed)
    return ds


def summary(name: str, **kwargs: Any) -> str:
    """Print a concise summary of a dataset.

    >>> print(summary("iris"))
    """
    ds = fetch(name, **kwargs)
    lines = [
        f"Dataset: {ds.name}",
        f"  Samples:  {ds.n_samples}",
        f"  Features: {ds.n_features}",
        f"  Targets:  {', '.join(ds.target_names) if ds.target_names else 'N/A'}",
        f"  Task:     {ds.metadata.get('task', 'unknown')}",
        f"  {ds.description}",
    ]
    if ds.data.dtype.kind in ("f", "i", "u") and ds.data.ndim == 2:
        lines.append(f"  Feature ranges:")
        for i, fname in enumerate(ds.feature_names[:10]):
            col = ds.data[:, i]
            lines.append(f"    {fname}: [{col.min():.4g}, {col.max():.4g}]  mean={col.mean():.4g}")
        if len(ds.feature_names) > 10:
            lines.append(f"    ... and {len(ds.feature_names) - 10} more features")
    return "\n".join(lines)
