"""Research experiment context: tracker + seed + reproducibility manifest."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

import numpy as np

from ..tracker import Run, Tracker
from .manifest import build_manifest, save_manifest


class Experiment:
    """
    High-level experiment wrapper for ML research workflows.

    Combines fixed random seeds, :class:`~aion.tracker.Run` logging, and a
    reproducibility manifest (``manifest.json``) in the run directory.

    Examples
    --------
    >>> from pytekt.experiments import Experiment
    >>> from pytekt.datasets import load_iris
    >>> from pytekt.models import GaussianNB
    >>> from pytekt.metrics import accuracy_score
    >>> exp = Experiment("iris_nb", seed=42)
    >>> with exp:
    ...     ds = load_iris(seed=42)
    ...     clf = GaussianNB().fit(ds.data, ds.target)
    ...     acc = accuracy_score(ds.target, clf.predict(ds.data))
    ...     exp.log_metrics(accuracy=acc)
    """

    def __init__(
        self,
        name: str,
        *,
        seed: int = 42,
        tracker_dir: str = ".aion_experiments",
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        self.name = name
        self.seed = seed
        self.tracker_dir = tracker_dir
        self.tags = tags or {}
        self._tracker = Tracker(tracker_dir)
        self.run: Optional[Run] = None
        self.manifest: Dict[str, Any] = {}

    def __enter__(self) -> "Experiment":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            self.end(status="failed")
        else:
            self.end(status="completed")

    def start(self, *, extra_manifest: Optional[Dict[str, Any]] = None) -> Run:
        """Begin the experiment run."""
        np.random.seed(self.seed)
        self.run = self._tracker.start_run(self.name, tags=self.tags)
        self.manifest = build_manifest(
            experiment_name=self.name,
            seed=self.seed,
            extra=extra_manifest,
        )
        self.run.log_params({"seed": self.seed, "experiment": self.name})
        self.run.log_params(
            {k: v for k, v in self.manifest.items() if isinstance(v, (str, int, float))}
        )
        save_manifest(os.path.join(self.run._dir, "manifest.json"), self.manifest)
        return self.run

    def end(self, status: str = "completed") -> None:
        if self.run is not None:
            self.run.end(status=status)

    def log_param(self, key: str, value: Any) -> None:
        if self.run is None:
            raise RuntimeError("Experiment not started; use 'with Experiment(...)' or start()")
        self.run.log_param(key, value)

    def log_params(self, params: Dict[str, Any]) -> None:
        if self.run is None:
            raise RuntimeError("Experiment not started")
        self.run.log_params(params)

    def log_metric(self, name: str, value: float, *, step: Optional[int] = None) -> None:
        if self.run is None:
            raise RuntimeError("Experiment not started")
        self.run.log_metric(name, value, step=step)

    def log_metrics(
        self,
        metrics: Optional[Dict[str, float]] = None,
        *,
        step: Optional[int] = None,
        **kwargs: float,
    ) -> None:
        if self.run is None:
            raise RuntimeError("Experiment not started")
        combined: Dict[str, float] = {}
        if metrics:
            combined.update(metrics)
        combined.update(kwargs)
        self.run.log_metrics(combined, step=step)

    def log_artifact(self, name: str, data: Any) -> None:
        if self.run is None:
            raise RuntimeError("Experiment not started")
        self.run.log_artifact(name, data)

    @property
    def run_id(self) -> Optional[str]:
        return self.run.id if self.run else None

    @property
    def run_dir(self) -> Optional[str]:
        return self.run._dir if self.run else None


@contextmanager
def experiment(
    name: str,
    *,
    seed: int = 42,
    tracker_dir: str = ".aion_experiments",
    tags: Optional[Dict[str, str]] = None,
) -> Iterator[Experiment]:
    """Context manager alias for :class:`Experiment`."""
    exp = Experiment(name, seed=seed, tracker_dir=tracker_dir, tags=tags)
    with exp:
        yield exp
