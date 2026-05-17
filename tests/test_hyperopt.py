"""Tests for aion.hyperopt."""

import numpy as np

from aion.datasets import load_iris
from aion.hyperopt import (
    GridSearch,
    RandomSearch,
    BayesianSearch,
    EarlyStopping,
    cross_val_score,
    kfold_indices,
)
from aion.models import KNNClassifier, GaussianNB


def test_kfold_indices():
    splits = kfold_indices(10, n_splits=5, shuffle=False)
    assert len(splits) == 5
    for train, test in splits:
        assert len(set(train) & set(test)) == 0


def test_cross_val_score():
    ds = load_iris()
    score = cross_val_score(
        GaussianNB(),
        ds.data,
        ds.target,
        scoring=lambda est, X, y: est.score(X, y),
        n_splits=3,
        random_state=0,
    )
    assert score > 0.7


def test_grid_search():
    ds = load_iris()
    search = GridSearch(
        KNNClassifier(),
        {"n_neighbors": [3, 5]},
        cv=3,
        random_state=0,
    )
    search.fit(ds.data, ds.target)
    assert search.best_params_ is not None
    assert search.best_estimator_ is not None
    assert search.best_score_ > 0.5
    assert len(search.cv_results_) == 2


def test_random_search():
    ds = load_iris()
    search = RandomSearch(
        KNNClassifier(),
        {"n_neighbors": [3, 5, 7]},
        n_iter=2,
        cv=3,
        random_state=0,
    )
    search.fit(ds.data, ds.target)
    assert search.best_params_["n_neighbors"] in [3, 5, 7]


def test_bayesian_search():
    ds = load_iris()
    search = BayesianSearch(
        KNNClassifier(),
        {"n_neighbors": [3, 5, 7]},
        n_iter=3,
        n_initial=2,
        cv=3,
        random_state=0,
    )
    search.fit(ds.data, ds.target)
    assert search.best_params_ is not None


def test_early_stopping_stops_search():
    ds = load_iris()
    es = EarlyStopping(patience=0, min_delta=0.0)
    search = GridSearch(
        KNNClassifier(),
        {"n_neighbors": [3, 5, 7, 9]},
        cv=3,
        early_stopping=es,
    )
    search.fit(ds.data, ds.target)
    assert len(search.cv_results_) <= 2
