"""MLPipeline, model I/O, statistical metrics."""

import tempfile
from pathlib import Path

import numpy as np

from pytekt.datasets import load_iris
from pytekt.models import MLPipeline, GaussianNB, save_model, load_model
from pytekt.preprocessing import StandardScaler
from pytekt.metrics import bootstrap_ci, compare_models


def test_mlpipeline():
    ds = load_iris()
    pipe = MLPipeline(StandardScaler(), GaussianNB())
    pipe.fit(ds.data, ds.target)
    assert pipe.score(ds.data, ds.target) > 0.85


def test_save_load_model():
    ds = load_iris()
    clf = GaussianNB().fit(ds.data, ds.target)
    with tempfile.TemporaryDirectory() as tmp:
        save_model(clf, Path(tmp) / "nb", metadata={"dataset": "iris"})
        loaded = load_model(Path(tmp) / "nb")
        pred = loaded.predict(ds.data)
        assert pred.shape == (150,)


def test_bootstrap_ci():
    mean, lo, hi = bootstrap_ci([0.8, 0.9, 0.85], n_bootstrap=200, seed=0)
    assert lo <= mean <= hi


def test_compare_models():
    y = [0, 1, 1, 0, 1]
    out = compare_models(y, [0, 1, 0, 0, 1], [0, 1, 1, 0, 1])
    assert "delta_accuracy" in out
