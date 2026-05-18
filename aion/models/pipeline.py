"""End-to-end ML pipeline: preprocessing + estimator."""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

import numpy as np

from ..preprocessing._base import TransformerMixin, _as_2d


class MLPipeline:
    """
    Chain preprocessing step(s) and a supervised estimator.

    Examples
    --------
    >>> from aion.models import MLPipeline, GaussianNB
    >>> from aion.preprocessing import StandardScaler
    >>> pipe = MLPipeline(StandardScaler(), GaussianNB())
    >>> pipe.fit(X, y).predict(X)
    """

    def __init__(
        self,
        preprocessor: Optional[TransformerMixin],
        estimator: Any,
        *,
        steps: Optional[Sequence[Tuple[str, Any]]] = None,
    ) -> None:
        if steps is not None:
            if len(steps) < 1:
                raise ValueError("steps must include at least an estimator as the last step")
            self.steps: List[Tuple[str, Any]] = list(steps)
            self.preprocessor = None
            self.estimator = steps[-1][1]
        else:
            self.steps = []
            self.preprocessor = preprocessor
            self.estimator = estimator

    def _fit_transform_steps(self, X, y, *, fit: bool) -> np.ndarray:
        for name, step in self.steps[:-1]:
            if fit:
                if hasattr(step, "fit_transform"):
                    X = step.fit_transform(X, y)
                else:
                    step.fit(X, y)
                    X = step.transform(X)
            else:
                X = step.transform(X)
        return _as_2d(X)

    def fit(self, X, y) -> "MLPipeline":
        X = _as_2d(X)
        if self.steps:
            Xt = self._fit_transform_steps(X, y, fit=True)
            self.estimator.fit(Xt, y)
            return self
        if self.preprocessor is not None:
            if hasattr(self.preprocessor, "fit_transform"):
                X = self.preprocessor.fit_transform(X, y)
            else:
                self.preprocessor.fit(X, y)
                X = self.preprocessor.transform(X)
        self.estimator.fit(X, y)
        return self

    def _transform(self, X) -> np.ndarray:
        X = _as_2d(X)
        if self.steps:
            return self._fit_transform_steps(X, None, fit=False)
        if self.preprocessor is not None:
            return self.preprocessor.transform(X)
        return X

    def predict(self, X) -> np.ndarray:
        return self.estimator.predict(self._transform(X))

    def score(self, X, y) -> float:
        return float(self.estimator.score(self._transform(X), y))
