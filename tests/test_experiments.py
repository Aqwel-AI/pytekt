"""Tests for aion.experiments research utilities."""

import json
import os
import tempfile

from aion.experiments import (
    Experiment,
    BenchmarkSuite,
    export_results_table,
    build_manifest,
)
from aion.datasets import load_iris
from aion.models import GaussianNB
from aion.metrics import accuracy_score


def test_experiment_context():
    with tempfile.TemporaryDirectory() as tmp:
        exp = Experiment("test_run", seed=0, tracker_dir=tmp)
        with exp:
            ds = load_iris(seed=0)
            clf = GaussianNB().fit(ds.data, ds.target)
            acc = accuracy_score(ds.target, clf.predict(ds.data))
            exp.log_metrics(accuracy=acc)
        assert exp.run_id is not None
        manifest_path = os.path.join(exp.run_dir, "manifest.json")
        assert os.path.isfile(manifest_path)
        m = json.load(open(manifest_path))
        assert m["seed"] == 0


def test_export_latex():
    runs = [
        {"name": "a", "id": "1", "status": "completed", "metrics": {"accuracy": 0.9}},
        {"name": "b", "id": "2", "status": "completed", "metrics": {"accuracy": 0.85}},
    ]
    tex = export_results_table(runs, format="latex", metric_columns=["accuracy"])
    assert "\\begin{table}" in tex
    assert "0.9000" in tex or "0.9" in tex


def test_benchmark_suite_small():
    suite = BenchmarkSuite(seeds=[0, 1])
    results = suite.run(task_names=["iris"], estimator_names=["gaussian_nb"])
    assert len(results) == 2
    board = suite.leaderboard(results)
    assert board[0]["task"] == "iris"
    assert board[0]["mean"] > 0.5


def test_manifest():
    m = build_manifest(experiment_name="x", seed=1, extra={"dataset": "iris"})
    assert m["experiment_name"] == "x"
    assert m["seed"] == 1
