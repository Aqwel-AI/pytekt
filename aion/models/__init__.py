"""
Classical machine learning models (NumPy implementations).

All estimators implement ``fit``, ``predict``, and ``score``.

Examples
--------
>>> from aion.models import LogisticRegression, KMeans
>>> from aion.datasets import load_iris
>>> ds = load_iris()
>>> clf = LogisticRegression(max_iter=500)
>>> # For binary subset or use GaussianNB for multiclass
"""

from ._base import BaseEstimator
from .linear import LinearRegression, LogisticRegression
from .neighbors import KNNClassifier, KNNRegressor
from .clustering import KMeans
from .decomposition import PCA
from .naive_bayes import GaussianNB
from .trees import DecisionTreeClassifier, DecisionTreeRegressor
from .pipeline import MLPipeline
from .io import save_model, load_model

__all__ = [
    "BaseEstimator",
    "LinearRegression",
    "LogisticRegression",
    "KNNClassifier",
    "KNNRegressor",
    "KMeans",
    "PCA",
    "GaussianNB",
    "DecisionTreeClassifier",
    "DecisionTreeRegressor",
    "MLPipeline",
    "save_model",
    "load_model",
]
