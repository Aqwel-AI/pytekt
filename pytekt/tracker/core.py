"""Experiment tracker: runs, metrics, params, artifacts."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MetricEntry:
    name: str
    value: float
    step: int
    timestamp: float


class Run:
    """
    A single experiment run that logs parameters, metrics, and artifacts.

    Do not instantiate directly; use :meth:`Tracker.start_run`.
    """

    def __init__(self, run_id: str, name: str, run_dir: str) -> None:
        self.id = run_id
        self.name = name
        self._dir = run_dir
        self.params: Dict[str, Any] = {}
        self.metrics: Dict[str, List[MetricEntry]] = {}
        self.tags: Dict[str, str] = {}
        self.status: str = "running"
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None
        self._step_counters: Dict[str, int] = {}

        os.makedirs(run_dir, exist_ok=True)
        self._save_meta()

    def log_param(self, key: str, value: Any) -> None:
        self.params[key] = value
        self._save_meta()

    def log_params(self, params: Dict[str, Any]) -> None:
        self.params.update(params)
        self._save_meta()

    def log_metric(self, name: str, value: float, *, step: Optional[int] = None) -> None:
        """Log a single metric value. Auto-increments step if not provided."""
        if step is None:
            step = self._step_counters.get(name, 0)
            self._step_counters[name] = step + 1
        entry = MetricEntry(name, value, step, time.time())
        self.metrics.setdefault(name, []).append(entry)
        self._save_metrics()

    def log_metrics(self, metrics: Dict[str, float], *, step: Optional[int] = None) -> None:
        for name, value in metrics.items():
            self.log_metric(name, value, step=step)

    def log_artifact(self, name: str, data: Any) -> None:
        """Save an artifact (JSON-serializable) to the run directory."""
        path = os.path.join(self._dir, f"artifact_{name}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def set_tag(self, key: str, value: str) -> None:
        self.tags[key] = value
        self._save_meta()

    def end(self, status: str = "completed") -> None:
        self.status = status
        self.end_time = time.time()
        self._save_meta()
        self._save_metrics()

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def get_metric_history(self, name: str) -> List[Dict[str, Any]]:
        return [
            {"value": e.value, "step": e.step, "timestamp": e.timestamp}
            for e in self.metrics.get(name, [])
        ]

    def latest_metrics(self) -> Dict[str, float]:
        """Return the last recorded value for each metric."""
        return {
            name: entries[-1].value
            for name, entries in self.metrics.items()
            if entries
        }

    def summary(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "params": self.params,
            "metrics": self.latest_metrics(),
            "tags": self.tags,
            "duration_s": self.duration_seconds,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    def _save_meta(self) -> None:
        path = os.path.join(self._dir, "meta.json")
        with open(path, "w") as f:
            json.dump(self.summary(), f, indent=2, default=str)

    def _save_metrics(self) -> None:
        path = os.path.join(self._dir, "metrics.json")
        data = {}
        for name, entries in self.metrics.items():
            data[name] = [
                {"value": e.value, "step": e.step, "timestamp": e.timestamp}
                for e in entries
            ]
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


class Tracker:
    """
    Experiment tracker that manages runs in a local directory.

    Parameters
    ----------
    base_dir : str
        Root directory for storing experiment data.
    """

    def __init__(self, base_dir: str = ".aion_experiments") -> None:
        self._base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def start_run(self, name: str = "", *, tags: Optional[Dict[str, str]] = None) -> Run:
        """Create and return a new :class:`Run`."""
        run_id = uuid.uuid4().hex[:10]
        run_dir = os.path.join(self._base_dir, run_id)
        run = Run(run_id, name or run_id, run_dir)
        if tags:
            for k, v in tags.items():
                run.set_tag(k, v)
        return run

    def list_runs(self) -> List[Dict[str, Any]]:
        """List all runs with their summaries."""
        runs = []
        if not os.path.exists(self._base_dir):
            return runs
        for entry in sorted(os.listdir(self._base_dir)):
            meta_path = os.path.join(self._base_dir, entry, "meta.json")
            if os.path.isfile(meta_path):
                with open(meta_path) as f:
                    runs.append(json.load(f))
        return runs

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Load a run's summary by id."""
        meta_path = os.path.join(self._base_dir, run_id, "meta.json")
        if not os.path.isfile(meta_path):
            return None
        with open(meta_path) as f:
            return json.load(f)

    def get_run_metrics(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Load full metric histories for a run."""
        metrics_path = os.path.join(self._base_dir, run_id, "metrics.json")
        if not os.path.isfile(metrics_path):
            return None
        with open(metrics_path) as f:
            return json.load(f)

    def delete_run(self, run_id: str) -> bool:
        """Delete a run and all its data."""
        import shutil
        run_dir = os.path.join(self._base_dir, run_id)
        if os.path.isdir(run_dir):
            shutil.rmtree(run_dir)
            return True
        return False

    def compare_runs(
        self, metric_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all runs sorted by a metric (descending). Uses ``compare_runs``."""
        from .compare import compare_runs as _compare
        return _compare(self.list_runs(), metric_name)
