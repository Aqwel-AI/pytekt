"""
Experiment tracking: log runs, compare metrics, local storage.

A lightweight alternative to MLflow/W&B that stores everything locally
in JSON files. Integrates with :mod:`aion.former` for automatic training
run logging.

Examples
--------
>>> from aion.tracker import Tracker
>>> tracker = Tracker("experiments")
>>> run = tracker.start_run("baseline")
>>> run.log_params({"lr": 0.001, "epochs": 10})
>>> run.log_metric("loss", 0.42, step=1)
>>> run.end()
>>> tracker.compare_runs()
"""

from .core import Tracker, Run
from .compare import compare_runs, best_run

__all__ = [
    "Run",
    "Tracker",
    "best_run",
    "compare_runs",
]
