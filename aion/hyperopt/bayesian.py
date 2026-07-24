"""Lightweight Bayesian-style hyperparameter search."""

from __future__ import annotations

import math
import random
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from ._cv import cross_val_score
from .early_stopping import EarlyStopping
from .search import ParamGrid, ScoringFn, _default_scoring, _sample_params


def _encode_params(params: Dict[str, Any], param_grid: ParamGrid) -> np.ndarray:
    """Encode categorical params as indices in [0, 1] per dimension."""
    vec = []
    for key in sorted(param_grid.keys()):
        choices = param_grid[key]
        val = params[key]
        idx = choices.index(val) if val in choices else 0
        vec.append(idx / max(len(choices) - 1, 1))
    return np.array(vec, dtype=np.float64)


class BayesianSearch:
    """
    Simple Bayesian optimization over discrete grids.

  Uses a Gaussian-process-style weighting over past trials to pick the next
  candidate (exploration via random probes). Suitable for small grids and
  fast estimators.
    """

    def __init__(
        self,
        estimator: Any,
        param_grid: ParamGrid,
        *,
        n_iter: int = 15,
        n_initial: int = 3,
        scoring: Optional[ScoringFn] = None,
        cv: int = 5,
        random_state: Optional[int] = None,
        tracker: Optional[Any] = None,
        tracker_run_name: str = "bayesian_search",
        early_stopping: Optional[EarlyStopping] = None,
    ) -> None:
        self.estimator = estimator
        self.param_grid = param_grid
        self.n_iter = n_iter
        self.n_initial = n_initial
        self.scoring = scoring or _default_scoring
        self.cv = cv
        self.random_state = random_state
        self.tracker = tracker
        self.tracker_run_name = tracker_run_name
        self.early_stopping = early_stopping
        self.best_params_: Optional[Dict[str, Any]] = None
        self.best_score_: float = -np.inf
        self.best_estimator_: Any = None
        self.cv_results_: List[Dict[str, Any]] = []

    def _base_params(self) -> Dict[str, Any]:
        return {
            k: v
            for k, v in vars(self.estimator).items()
            if not k.startswith("_") and not k.endswith("_") and not callable(v)
        }

    def _evaluate(self, params: Dict[str, Any], X: np.ndarray, y: np.ndarray) -> float:
        est = self.estimator.__class__(**{**self._base_params(), **params})
        return cross_val_score(
            est, X, y, scoring=self.scoring, n_splits=self.cv, random_state=self.random_state
        )

    def _acquisition(
        self,
        candidate: Dict[str, Any],
        X_hist: List[np.ndarray],
        y_hist: List[float],
    ) -> float:
        if not X_hist:
            return 0.0
        x = _encode_params(candidate, self.param_grid)
        best = max(y_hist)
        scores = []
        for xi, yi in zip(X_hist, y_hist):
            dist = np.linalg.norm(x - xi)
            kernel = math.exp(-dist * 5.0)
            scores.append(kernel * (yi - best))
        mu = sum(scores) / len(scores) if scores else 0.0
        return mu + 0.1 * random.random()

    def fit(self, X, y) -> "BayesianSearch":
        X = np.asarray(X)
        y_arr = np.asarray(y).ravel()
        rng = random.Random(self.random_state)
        run = None
        if self.tracker is not None:
            run = self.tracker.start_run(self.tracker_run_name)
        X_hist: List[np.ndarray] = []
        y_hist: List[float] = []
        tried: List[Dict[str, Any]] = []

        for trial in range(self.n_iter):
            if trial < self.n_initial:
                params = _sample_params(self.param_grid, rng)
            else:
                candidates = [_sample_params(self.param_grid, rng) for _ in range(20)]
                params = max(
                    candidates,
                    key=lambda c: self._acquisition(c, X_hist, y_hist),
                )
            if params in tried:
                params = _sample_params(self.param_grid, rng)
            tried.append(params)
            score = self._evaluate(params, X, y_arr)
            X_hist.append(_encode_params(params, self.param_grid))
            y_hist.append(score)
            self.cv_results_.append({"params": dict(params), "mean_score": score})
            if score > self.best_score_:
                self.best_score_ = score
                self.best_params_ = dict(params)
            if run is not None:
                run.log_params(params)
                run.log_metric("cv_score", score, step=trial)
            if self.early_stopping and self.early_stopping.update(score):
                break
        if run is not None:
            run.log_metric("best_cv_score", self.best_score_)
            run.end()
        assert self.best_params_ is not None
        self.best_estimator_ = self.estimator.__class__(
            **{**self._base_params(), **self.best_params_}
        )
        self.best_estimator_.fit(X, y_arr)
        return self
