"""Early stopping for hyperparameter search loops."""

from __future__ import annotations


class EarlyStopping:
    """
    Stop search when the monitored score fails to improve for ``patience`` trials.

    Parameters
    ----------
    patience:
        Number of trials without improvement before stopping.
    min_delta:
        Minimum absolute improvement to count as progress.
    mode:
        ``max`` if higher scores are better (default for ``estimator.score``),
        ``min`` for loss-style metrics.
    """

    def __init__(
        self,
        *,
        patience: int = 5,
        min_delta: float = 0.0,
        mode: str = "max",
    ) -> None:
        if mode not in ("max", "min"):
            raise ValueError("mode must be 'max' or 'min'")
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: float | None = None
        self.counter = 0
        self.stopped = False

    def update(self, score: float) -> bool:
        """Record *score*; return True if search should stop."""
        if self.best is None:
            self.best = score
            return False
        improved = (
            score > self.best + self.min_delta
            if self.mode == "max"
            else score < self.best - self.min_delta
        )
        if improved:
            self.best = score
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.stopped = True
                return True
        return False

    def reset(self) -> None:
        self.best = None
        self.counter = 0
        self.stopped = False
