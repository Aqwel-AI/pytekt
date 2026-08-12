"""Build static HTML dashboards for experiments and datasets."""

from __future__ import annotations

import webbrowser
from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

from .html import PageBuilder, escape_html, table_html

PathLike = Union[str, Path]


def build_experiment_dashboard(
    tracker_dir: str = ".aion_experiments",
    *,
    output: PathLike = "experiments.html",
    title: str = "Experiment runs",
    metric_sort: Optional[str] = None,
    open_browser: bool = False,
) -> str:
    """Generate an HTML dashboard from :class:`aion.tracker.Tracker` data.

  Returns the path to the saved HTML file.
    """
    from ..tracker import Tracker

    tracker = Tracker(tracker_dir)
    runs = tracker.compare_runs(metric_sort) if metric_sort else tracker.list_runs()

    page = PageBuilder(title, subtitle=f"Tracker: {tracker_dir}")
    page.add_metrics({"total_runs": len(runs)})

    if not runs:
        page.add_paragraph("No experiment runs found in this directory.")
    else:
        headers = ["name", "id", "status", "duration_s"]
        metric_keys: List[str] = []
        for run in runs:
            metric_keys.extend(run.get("metrics", {}).keys())
        metric_keys = sorted(set(metric_keys))[:6]
        headers.extend(metric_keys)

        rows: List[List[Any]] = []
        for run in runs:
            row = [
                run.get("name", ""),
                run.get("id", ""),
                run.get("status", ""),
                f"{run.get('duration_s', 0):.1f}" if run.get("duration_s") else "—",
            ]
            metrics = run.get("metrics", {})
            for mk in metric_keys:
                val = metrics.get(mk)
                row.append(f"{val:.4g}" if isinstance(val, float) else (val or "—"))
            rows.append(row)

        page.add_heading("Runs")
        page.add_table(headers, rows)

        if metric_sort:
            page.add_paragraph(f"Sorted by metric: {metric_sort}")

    path = page.save(output)
    if open_browser:
        open_html_file(path)
    return path


def build_dataset_report(
    dataset: Any,
    *,
    output: PathLike = "dataset_report.html",
    title: Optional[str] = None,
    sample_rows: int = 10,
    open_browser: bool = False,
) -> str:
    """Generate an HTML preview for a :class:`aion.datasets.Dataset`.

    Parameters
    ----------
    dataset : Dataset
        Object with ``data``, ``target``, ``feature_names``, ``n_samples``, etc.
    """
    name = getattr(dataset, "name", "dataset") or "dataset"
    page = PageBuilder(title or f"Dataset: {name}", subtitle=getattr(dataset, "description", ""))

    page.add_metrics({
        "samples": getattr(dataset, "n_samples", "?"),
        "features": getattr(dataset, "n_features", "?"),
        "task": (getattr(dataset, "metadata", {}) or {}).get("task", "unknown"),
    })

    target_names = getattr(dataset, "target_names", []) or []
    if target_names:
        page.add_paragraph("Targets: " + ", ".join(str(t) for t in target_names))

    feature_names = getattr(dataset, "feature_names", None) or []
    data = getattr(dataset, "data", None)
    target = getattr(dataset, "target", None)

    if data is not None and hasattr(data, "shape"):
        n = min(sample_rows, int(data.shape[0]))
        headers = ["#", "target"] + list(feature_names[: min(len(feature_names), data.shape[1] if data.ndim > 1 else 1)])
        rows = []
        for i in range(n):
            row: List[Any] = [i, target[i] if target is not None else ""]
            if data.ndim == 1:
                row.append(data[i])
            else:
                for j in range(min(data.shape[1], len(feature_names) or data.shape[1])):
                    v = data[i, j]
                    row.append(f"{v:.4g}" if isinstance(v, float) else str(v))
            rows.append(row)
        page.add_heading("Sample rows")
        page.add_table(headers, rows)

    path = page.save(output)
    if open_browser:
        open_html_file(path)
    return path


def open_html_file(path: PathLike) -> None:
    """Open a local HTML file in the default browser."""
    path = Path(path).resolve()
    webbrowser.open(path.as_uri())
