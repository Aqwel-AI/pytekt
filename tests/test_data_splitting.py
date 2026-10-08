"""Tests for dataset splitting utilities in pytekt.data."""

import numpy as np
import pytest

from pytekt.data import kfold_split, train_test_split, train_val_test_split


def test_train_test_split_single_list():
    data = list(range(100))
    train, test = train_test_split(data, test_ratio=0.2, seed=42)
    assert len(train) == 80
    assert len(test) == 20
    assert set(train) | set(test) == set(data)


def test_train_test_split_multi_array_numpy():
    X = np.arange(100).reshape(50, 2)
    y = np.arange(50)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    assert len(X_train) == 40 and len(X_test) == 10
    assert len(y_train) == 40 and len(y_test) == 10
    assert isinstance(X_train, np.ndarray)
    assert isinstance(y_train, np.ndarray)


def test_train_test_split_length_mismatch():
    with pytest.raises(ValueError, match="same length"):
        train_test_split([1, 2, 3], [1, 2])


def test_train_val_test_split():
    data = list(range(100))
    train, val, test = train_val_test_split(
        data, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42
    )
    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15


def test_kfold_split():
    data = list(range(20))
    folds = kfold_split(data, k=4, seed=42)
    assert len(folds) == 4
    for train_fold, test_fold in folds:
        assert len(test_fold) == 5
        assert len(train_fold) == 15
