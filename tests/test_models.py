"""Tests for aion.models."""

import numpy as np
import pytest

from aion.datasets import load_iris, load_moons
from aion.models import (
    LinearRegression,
    LogisticRegression,
    KNNClassifier,
    KNNRegressor,
    KMeans,
    PCA,
    GaussianNB,
    DecisionTreeClassifier,
    DecisionTreeRegressor,
)


@pytest.fixture
def iris():
    return load_iris()


@pytest.fixture
def moons():
    return load_moons(seed=0)


def test_gaussian_nb_multiclass(iris):
    clf = GaussianNB()
    clf.fit(iris.data, iris.target)
    pred = clf.predict(iris.data)
    assert pred.shape == (150,)
    assert clf.score(iris.data, iris.target) > 0.85


def test_knn_classifier(iris):
    clf = KNNClassifier(n_neighbors=5)
    clf.fit(iris.data, iris.target)
    assert clf.predict(iris.data[:5]).shape == (5,)


def test_linear_regression():
    X = np.array([[1.0], [2.0], [3.0]])
    y = np.array([2.0, 4.0, 6.0])
    reg = LinearRegression().fit(X, y)
    pred = reg.predict([[4.0]])
    assert pred.shape == (1,)
    assert reg.score(X, y) > 0.99


def test_knn_regressor():
    X = np.array([[0.0], [1.0], [2.0]])
    y = np.array([0.0, 2.0, 4.0])
    reg = KNNRegressor(n_neighbors=2).fit(X, y)
    assert reg.predict([[1.5]]).shape == (1,)


def test_logistic_regression_binary(moons):
    clf = LogisticRegression(max_iter=500, learning_rate=0.1)
    clf.fit(moons.data, moons.target)
    assert clf.score(moons.data, moons.target) > 0.7


def test_kmeans(iris):
    km = KMeans(n_clusters=3, random_state=0)
    km.fit(iris.data)
    assert km.labels_.shape == (150,)
    assert km.cluster_centers_.shape == (3, 4)


def test_pca(iris):
    pca = PCA(n_components=2)
    out = pca.fit_transform(iris.data)
    assert out.shape == (150, 2)


def test_decision_tree_classifier(iris):
    clf = DecisionTreeClassifier(max_depth=4)
    clf.fit(iris.data, iris.target)
    assert clf.score(iris.data, iris.target) > 0.9


def test_decision_tree_regressor():
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0.0, 1.0, 2.0, 3.0])
    reg = DecisionTreeRegressor(max_depth=2).fit(X, y)
    assert reg.score(X, y) > 0.9
