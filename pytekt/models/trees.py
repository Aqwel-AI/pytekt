"""Decision tree models."""

from __future__ import annotations

from typing import Any, Optional, Tuple

import numpy as np

from ._base import BaseEstimator, _as_1d, _as_2d


class _TreeNode:
    __slots__ = ("feature", "threshold", "left", "right", "value", "is_leaf")

    def __init__(
        self,
        feature: int = -1,
        threshold: float = 0.0,
        left: Optional["_TreeNode"] = None,
        right: Optional["_TreeNode"] = None,
        value: Any = None,
        is_leaf: bool = False,
    ) -> None:
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value
        self.is_leaf = is_leaf


def _gini(y: np.ndarray) -> float:
    if len(y) == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    p = counts / counts.sum()
    return 1.0 - np.sum(p ** 2)


def _mse(y: np.ndarray) -> float:
    if len(y) == 0:
        return 0.0
    return float(np.var(y))


class DecisionTreeClassifier(BaseEstimator):
    """CART decision tree classifier."""

    def __init__(self, *, max_depth: int = 5, min_samples_split: int = 2) -> None:
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree_: Optional[_TreeNode] = None
        self.classes_: Optional[np.ndarray] = None

    def _best_split(self, X: np.ndarray, y: np.ndarray) -> Tuple[int, float, float]:
        best_feat, best_thr, best_gain = -1, 0.0, -1.0
        parent_imp = _gini(y)
        n, d = X.shape
        for feat in range(d):
            thresholds = np.unique(X[:, feat])
            for thr in thresholds:
                left = y[X[:, feat] <= thr]
                right = y[X[:, feat] > thr]
                if len(left) == 0 or len(right) == 0:
                    continue
                gain = parent_imp - (len(left) * _gini(left) + len(right) * _gini(right)) / n
                if gain > best_gain:
                    best_gain, best_feat, best_thr = gain, feat, thr
        return best_feat, best_thr, best_gain

    def _build(self, X: np.ndarray, y: np.ndarray, depth: int) -> _TreeNode:
        if depth >= self.max_depth or len(y) < self.min_samples_split or len(np.unique(y)) == 1:
            vals, counts = np.unique(y, return_counts=True)
            return _TreeNode(value=vals[np.argmax(counts)], is_leaf=True)
        feat, thr, gain = self._best_split(X, y)
        if feat < 0 or gain <= 0:
            vals, counts = np.unique(y, return_counts=True)
            return _TreeNode(value=vals[np.argmax(counts)], is_leaf=True)
        left_mask = X[:, feat] <= thr
        return _TreeNode(
            feature=feat,
            threshold=thr,
            left=self._build(X[left_mask], y[left_mask], depth + 1),
            right=self._build(X[~left_mask], y[~left_mask], depth + 1),
            is_leaf=False,
        )

    def fit(self, X, y) -> "DecisionTreeClassifier":
        X = _as_2d(X)
        y = _as_1d(y)
        self.classes_ = np.unique(y)
        self.tree_ = self._build(X, y, 0)
        return self

    def _predict_one(self, x: np.ndarray, node: _TreeNode) -> Any:
        if node.is_leaf:
            return node.value
        if x[node.feature] <= node.threshold:
            return self._predict_one(x, node.left)
        return self._predict_one(x, node.right)

    def predict(self, X) -> np.ndarray:
        X = _as_2d(X)
        return np.array([self._predict_one(X[i], self.tree_) for i in range(X.shape[0])])


class DecisionTreeRegressor(BaseEstimator):
    """CART decision tree regressor."""

    def __init__(self, *, max_depth: int = 5, min_samples_split: int = 2) -> None:
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree_: Optional[_TreeNode] = None

    def _best_split(self, X: np.ndarray, y: np.ndarray) -> Tuple[int, float, float]:
        best_feat, best_thr, best_gain = -1, 0.0, -1.0
        parent_imp = _mse(y)
        n, d = X.shape
        for feat in range(d):
            for thr in np.unique(X[:, feat]):
                left = y[X[:, feat] <= thr]
                right = y[X[:, feat] > thr]
                if len(left) == 0 or len(right) == 0:
                    continue
                gain = parent_imp - (len(left) * _mse(left) + len(right) * _mse(right)) / n
                if gain > best_gain:
                    best_gain, best_feat, best_thr = gain, feat, thr
        return best_feat, best_thr, best_gain

    def _build(self, X: np.ndarray, y: np.ndarray, depth: int) -> _TreeNode:
        if depth >= self.max_depth or len(y) < self.min_samples_split:
            return _TreeNode(value=float(np.mean(y)), is_leaf=True)
        feat, thr, gain = self._best_split(X, y)
        if feat < 0 or gain <= 0:
            return _TreeNode(value=float(np.mean(y)), is_leaf=True)
        left_mask = X[:, feat] <= thr
        return _TreeNode(
            feature=feat,
            threshold=thr,
            left=self._build(X[left_mask], y[left_mask], depth + 1),
            right=self._build(X[~left_mask], y[~left_mask], depth + 1),
            is_leaf=False,
        )

    def fit(self, X, y) -> "DecisionTreeRegressor":
        X = _as_2d(X)
        y = _as_1d(y)
        self.tree_ = self._build(X, y, 0)
        return self

    def _predict_one(self, x: np.ndarray, node: _TreeNode) -> float:
        if node.is_leaf:
            return node.value
        if x[node.feature] <= node.threshold:
            return self._predict_one(x, node.left)
        return self._predict_one(x, node.right)

    def predict(self, X) -> np.ndarray:
        X = _as_2d(X)
        return np.array([self._predict_one(X[i], self.tree_) for i in range(X.shape[0])])
