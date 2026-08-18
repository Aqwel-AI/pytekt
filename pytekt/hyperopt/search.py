"""Grid and random hyperparameter search."""

from __future__ import annotations

import itertools
import random
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

import numpy as np

from ._cv import cross_val_score
from .early_stopping import EarlyStopping

ParamGrid = Dict[str, List[Any]]
ScoringFn = Callable[[Any, Any, Any], float]


def _default_scoring(estimator: Any, X: Any, y: Any) -> float:
    return float(estimator.score(X, y))


def _param_combinations(param_grid: ParamGrid) -> Iterator[Dict[str, Any]]:
    keys = list(param_grid.keys())
    for values in itertools.product(*(param_grid[k] for k in keys)):
        yield dict(zip(keys, values))


def _sample_params(param_grid: ParamGrid, rng: random.Random) -> Dict[str, Any]:
    return {k: rng.choice(v) for k, v in param_grid.items()}


class _BaseSearch:
    def __init__(
        self,
        estimator: Any,
        param_grid: ParamGrid,
        *,
        scoring: Optional[ScoringFn] = None,
        cv: int = 5,
        random_state: Optional[int] = None,
        tracker: Optional[Any] = None,
        tracker_run_name: str = "hyperopt",
        early_stopping: Optional[EarlyStopping] = None,
    ) -> None:
        self.estimator = estimator
        self.param_grid = param_grid
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

    def _evaluate(self, params: Dict[str, Any], X: np.ndarray, y: np.ndarray) -> Tuple[float, Any]:
        est = self.estimator.__class__(**{**self._base_params(), **params})
        score = cross_val_score(
            est,
            X,
            y,
            scoring=self.scoring,
            n_splits=self.cv,
            random_state=self.random_state,
        )
        return score, est

    def _base_params(self) -> Dict[str, Any]:
        return {
            k: v
            for k, v in vars(self.estimator).items()
            if not k.startswith("_") and not k.endswith("_") and not callable(v)
        }

    def _log_trial(
        self,
        run: Any,
        trial: int,
        params: Dict[str, Any],
        score: float,
    ) -> None:
        run.log_params(params)
        run.log_metric("cv_score", score, step=trial)
        run.set_tag("search", self.__class__.__name__)

    def _maybe_stop(self, score: float) -> bool:
        if self.early_stopping is None:
            return False
        return self.early_stopping.update(score)

    def _record(self, params: Dict[str, Any], score: float) -> None:
        self.cv_results_.append({"params": dict(params), "mean_score": score})
        if score > self.best_score_:
            self.best_score_ = score
            self.best_params_ = dict(params)

    def _fit_final(self, X: np.ndarray, y: np.ndarray) -> "_BaseSearch":
        assert self.best_params_ is not None
        self.best_estimator_ = self.estimator.__class__(
            **{**self._base_params(), **self.best_params_}
        )
        self.best_estimator_.fit(X, y)
        return self


class GridSearch(_BaseSearch):
    """Exhaustive search over a parameter grid with k-fold CV."""

    def fit(self, X, y) -> "GridSearch":
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        run = None
        if self.tracker is not None:
            run = self.tracker.start_run(self.tracker_run_name)
        for trial, params in enumerate(_param_combinations(self.param_grid)):
            score, _ = self._evaluate(params, X, y)
            self._record(params, score)
            if run is not None:
                self._log_trial(run, trial, params, score)
            if self._maybe_stop(score):
                break
        if run is not None:
            run.log_metric("best_cv_score", self.best_score_)
            run.log_params({"best": self.best_params_})
            run.end()
        return self._fit_final(X, y)


class RandomSearch(_BaseSearch):
    """Random search over a parameter grid with k-fold CV."""

    def __init__(
        self,
        estimator: Any,
        param_grid: ParamGrid,
        *,
        n_iter: int = 10,
        **kwargs: Any,
    ) -> None:
        super().__init__(estimator, param_grid, **kwargs)
        self.n_iter = n_iter

    def fit(self, X, y) -> "RandomSearch":
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        rng = random.Random(self.random_state)
        run = None
        if self.tracker is not None:
            run = self.tracker.start_run(self.tracker_run_name)
        for trial in range(self.n_iter):
            params = _sample_params(self.param_grid, rng)
            score, _ = self._evaluate(params, X, y)
            self._record(params, score)
            if run is not None:
                self._log_trial(run, trial, params, score)
            if self._maybe_stop(score):
                break
        if run is not None:
            run.log_metric("best_cv_score", self.best_score_)
            run.log_params({"best": self.best_params_})
            run.end()
        return self._fit_final(X, y)
