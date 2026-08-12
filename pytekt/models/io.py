"""Save and load trained models for research reproducibility."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np

PathLike = Union[str, Path]


def _estimator_params(estimator: Any) -> Dict[str, Any]:
    params = {}
    for k, v in vars(estimator).items():
        if k.startswith("_") or callable(v):
            continue
        if isinstance(v, np.ndarray):
            params[k] = {"__ndarray__": True, "data": v.tolist(), "dtype": str(v.dtype)}
        elif isinstance(v, (str, int, float, bool, type(None), list)):
            params[k] = v
    return params


def _restore_params(estimator: Any, params: Dict[str, Any]) -> Any:
    for k, v in params.items():
        if isinstance(v, dict) and v.get("__ndarray__"):
            setattr(estimator, k, np.array(v["data"], dtype=v.get("dtype", "float64")))
        else:
            setattr(estimator, k, v)
    return estimator


def save_model(
    estimator: Any,
    path: PathLike,
    *,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Save an estimator to a directory (``meta.json`` + optional arrays).

    Parameters
    ----------
    estimator : object
        Fitted model (e.g. :class:`~pytekt.models.GaussianNB`).
    path : path
        Directory to create (e.g. ``runs/model_nb``).
    metadata : dict, optional
        Extra fields (dataset name, feature names, etc.).
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    payload = {
        "class": f"{estimator.__class__.__module__}.{estimator.__class__.__name__}",
        "params": _estimator_params(estimator),
        "metadata": metadata or {},
    }
    (path / "meta.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return str(path)


def load_model(path: PathLike) -> Any:
    """Load an estimator saved with :func:`save_model`."""
    path = Path(path)
    meta = json.loads((path / "meta.json").read_text(encoding="utf-8"))
    module_name, class_name = meta["class"].rsplit(".", 1)
    import importlib

    mod = importlib.import_module(module_name)
    cls = getattr(mod, class_name)
    est = cls()
    return _restore_params(est, meta["params"])
