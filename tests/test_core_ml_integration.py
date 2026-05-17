"""End-to-end Core ML stack integration tests."""

import aion
from aion.datasets import load_iris
from aion.preprocessing import StandardScaler, PreprocessingPipeline, SimpleImputer
from aion.models import GaussianNB
from aion.metrics import accuracy_score
from aion.hyperopt import GridSearch
from aion.models import KNNClassifier


def test_package_exports():
    assert hasattr(aion, "preprocessing")
    assert hasattr(aion, "models")
    assert hasattr(aion, "metrics")
    assert hasattr(aion, "hyperopt")


def test_full_pipeline():
    ds = load_iris()
    pipe = PreprocessingPipeline([
        ("scale", StandardScaler()),
    ])
    X = pipe.fit_transform(ds.data)
    clf = GaussianNB().fit(X, ds.target)
    acc = accuracy_score(ds.target, clf.predict(X))
    assert acc > 0.85

    search = GridSearch(
        KNNClassifier(),
        {"n_neighbors": [3, 7]},
        cv=3,
    )
    search.fit(ds.data, ds.target)
    assert search.best_score_ > 0.5
