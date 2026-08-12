"""Tests for pytekt.preprocessing."""

import numpy as np
import pytest

from pytekt.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    LabelEncoder,
    OneHotEncoder,
    SimpleImputer,
    PolynomialFeatures,
    PreprocessingPipeline,
)


@pytest.fixture
def X():
    return np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])


def test_standard_scaler_fit_transform_inverse(X):
    scaler = StandardScaler()
    out = scaler.fit_transform(X)
    assert out.shape == X.shape
    assert np.allclose(out.mean(axis=0), 0, atol=1e-7)
    assert np.allclose(scaler.inverse_transform(out), X)


def test_minmax_scaler_range(X):
    scaler = MinMaxScaler(feature_range=(0, 1))
    out = scaler.fit_transform(X)
    assert out.min() >= -1e-9
    assert out.max() <= 1.0 + 1e-9


def test_label_encoder():
    le = LabelEncoder()
    y = ["a", "b", "a", "c"]
    enc = le.fit_transform(y)
    assert list(enc) == [0, 1, 0, 2]
    assert le.inverse_transform(enc).tolist() == y


def test_one_hot_encoder():
    enc = OneHotEncoder()
    X = np.array([["a"], ["b"], ["a"]])
    out = enc.fit_transform(X)
    assert out.shape[0] == 3
    assert out.sum() == 3


def test_simple_imputer_mean():
    X = np.array([[1.0, np.nan], [3.0, 4.0]])
    imp = SimpleImputer(strategy="mean")
    out = imp.fit_transform(X)
    assert not np.isnan(out).any()
    assert out[0, 1] == 4.0


def test_polynomial_features():
    pf = PolynomialFeatures(degree=2, include_bias=False)
    X = np.array([[1.0, 2.0]])
    out = pf.fit_transform(X)
    assert out.shape[1] >= 2


def test_preprocessing_pipeline(X):
    pipe = PreprocessingPipeline([
        ("impute", SimpleImputer(strategy="mean")),
        ("scale", StandardScaler()),
    ])
    out = pipe.fit_transform(X)
    assert out.shape == X.shape
