"""End-to-end Core ML stack integration tests."""

import pytekt
from pytekt.datasets import load_iris
from pytekt.preprocessing import StandardScaler, PreprocessingPipeline, SimpleImputer
from pytekt.models import GaussianNB
from pytekt.metrics import accuracy_score
from pytekt.hyperopt import GridSearch
from pytekt.models import KNNClassifier


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
