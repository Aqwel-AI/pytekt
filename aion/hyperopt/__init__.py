"""
Hyperparameter optimization with cross-validation and experiment tracking.

Examples
--------
>>> from aion.hyperopt import GridSearch, EarlyStopping
>>> from aion.models import KNNClassifier
>>> from aion.datasets import load_iris
>>> ds = load_iris()
>>> search = GridSearch(KNNClassifier(), {"n_neighbors": [3, 5, 7]}, cv=3)
>>> search.fit(ds.data, ds.target)
>>> search.best_params_
"""

from ._cv import cross_val_score, kfold_indices
from .early_stopping import EarlyStopping
from .search import GridSearch, RandomSearch
from .bayesian import BayesianSearch

__all__ = [
    "cross_val_score",
    "kfold_indices",
    "EarlyStopping",
    "GridSearch",
    "RandomSearch",
    "BayesianSearch",
]
