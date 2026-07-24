"""Standard ML benchmark suite for reproducible research baselines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np

from ..datasets import load_iris, load_wine, load_breast_cancer, load_digits
from ..metrics import accuracy_score
from ..models import GaussianNB, KNNClassifier, DecisionTreeClassifier


EstimatorFactory = Callable[[], Any]


@dataclass
class BenchmarkTask:
    """One dataset + metric for the suite."""

    name: str
    loader: Callable[..., Any]
    metric: str = "accuracy"
    supervised: bool = True


DEFAULT_TASKS: Dict[str, BenchmarkTask] = {
    "iris": BenchmarkTask("iris", load_iris),
    "wine": BenchmarkTask("wine", load_wine),
    "breast_cancer": BenchmarkTask("breast_cancer", load_breast_cancer),
    "digits": BenchmarkTask("digits", load_digits),
}


DEFAULT_ESTIMATORS: Dict[str, EstimatorFactory] = {
    "gaussian_nb": lambda: GaussianNB(),
    "knn_5": lambda: KNNClassifier(n_neighbors=5),
    "tree": lambda: DecisionTreeClassifier(max_depth=6),
}


@dataclass
class BenchmarkResult:
    task: str
    estimator: str
    seed: int
    score: float
    metric: str = "accuracy"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "estimator": self.estimator,
            "seed": self.seed,
            "score": self.score,
            "metric": self.metric,
        }


class BenchmarkSuite:
    """
    Run standard classification benchmarks with multiple seeds.

    Examples
    --------
    >>> suite = BenchmarkSuite(seeds=[0, 1, 2])
    >>> results = suite.run()
    >>> print(suite.leaderboard(results))
    """

    def __init__(
        self,
        *,
        tasks: Optional[Dict[str, BenchmarkTask]] = None,
        estimators: Optional[Dict[str, EstimatorFactory]] = None,
        seeds: Sequence[int] = (0, 1, 2, 3, 4),
    ) -> None:
        self.tasks = tasks or dict(DEFAULT_TASKS)
        self.estimators = estimators or dict(DEFAULT_ESTIMATORS)
        self.seeds = list(seeds)

    def run(
        self,
        *,
        task_names: Optional[Sequence[str]] = None,
        estimator_names: Optional[Sequence[str]] = None,
    ) -> List[BenchmarkResult]:
        """Evaluate all task × estimator × seed combinations."""
        tasks = task_names or list(self.tasks.keys())
        ests = estimator_names or list(self.estimators.keys())
        results: List[BenchmarkResult] = []

        for task_name in tasks:
            task = self.tasks[task_name]
            for est_name in ests:
                factory = self.estimators[est_name]
                for seed in self.seeds:
                    ds = task.loader(seed=seed)
                    X, y = ds.data, ds.target
                    est = factory()
                    est.fit(X, y)
                    pred = est.predict(X)
                    if task.metric == "accuracy":
                        score = float(accuracy_score(y, pred))
                    else:
                        raise ValueError(f"Unsupported metric: {task.metric}")
                    results.append(
                        BenchmarkResult(
                            task=task_name,
                            estimator=est_name,
                            seed=seed,
                            score=score,
                            metric=task.metric,
                        )
                    )
        return results

    def leaderboard(
        self,
        results: Sequence[BenchmarkResult],
    ) -> List[Dict[str, Any]]:
        """Aggregate mean ± std score per (task, estimator)."""
        buckets: Dict[tuple, List[float]] = {}
        for r in results:
            key = (r.task, r.estimator, r.metric)
            buckets.setdefault(key, []).append(r.score)
        rows = []
        for (task, est, metric), scores in sorted(buckets.items()):
            arr = np.array(scores)
            rows.append({
                "task": task,
                "estimator": est,
                "metric": metric,
                "mean": float(arr.mean()),
                "std": float(arr.std(ddof=0)),
                "n_seeds": len(scores),
            })
        return sorted(rows, key=lambda x: (-x["mean"], x["task"]))

    def leaderboard_markdown(self, results: Sequence[BenchmarkResult]) -> str:
        rows = self.leaderboard(results)
        if not rows:
            return ""
        headers = ["task", "estimator", "metric", "mean", "std", "n_seeds"]
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for r in rows:
            lines.append(
                "| {task} | {estimator} | {metric} | {mean:.4f} | {std:.4f} | {n_seeds} |".format(
                    **r
                )
            )
        return "\n".join(lines)
