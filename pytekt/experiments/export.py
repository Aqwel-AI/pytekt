"""Export experiment results for papers and reports."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

PathLike = Union[str, Path]


def _latest_metric(run: Dict[str, Any], name: str) -> Optional[float]:
    metrics = run.get("metrics") or {}
    val = metrics.get(name)
    if val is None:
        return None
    return float(val)


def export_results_table(
    runs: Sequence[Dict[str, Any]],
    *,
    metric_columns: Optional[Sequence[str]] = None,
    format: str = "markdown",
    caption: str = "Experiment results",
    label: str = "tab:results",
) -> str:
    """
    Build a comparison table from tracker run summaries.

    Parameters
    ----------
    runs : list of dict
        Output of :meth:`pytekt.tracker.Tracker.list_runs` or compare_runs.
    metric_columns : sequence, optional
        Metric names to include; default = union of all metrics in runs.
    format : str
        ``markdown``, ``csv``, ``latex``, or ``html``.
    """
    if not runs:
        return ""

    if metric_columns is None:
        keys: set = set()
        for r in runs:
            keys.update((r.get("metrics") or {}).keys())
        metric_columns = sorted(keys)

    headers = ["name", "id", "status"] + list(metric_columns)
    rows: List[List[str]] = []
    for r in runs:
        row = [
            str(r.get("name", "")),
            str(r.get("id", "")),
            str(r.get("status", "")),
        ]
        for m in metric_columns:
            v = _latest_metric(r, m)
            row.append(f"{v:.4f}" if v is not None else "—")
        rows.append(row)

    if format == "csv":
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(headers)
        w.writerows(rows)
        return buf.getvalue()

    if format == "latex":
        col_spec = "l" * len(headers)
        lines = [
            "\\begin{table}[ht]",
            "\\centering",
            f"\\caption{{{caption}}}",
            f"\\label{{{label}}}",
            f"\\begin{{tabular}}{{{col_spec}}}",
            " \\hline",
            " & ".join(_latex_escape(h) for h in headers) + " \\\\",
            " \\hline",
        ]
        for row in rows:
            lines.append(" & ".join(_latex_escape(c) for c in row) + " \\\\")
        lines.extend([" \\hline", "\\end{tabular}", "\\end{table}"])
        return "\n".join(lines)

    if format == "html":
        head = "".join(f"<th>{h}</th>" for h in headers)
        body = []
        for row in rows:
            body.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
        return (
            f"<table><caption>{caption}</caption><thead><tr>{head}</tr></thead>"
            f"<tbody>{''.join(body)}</tbody></table>"
        )

    # markdown
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep] + body)


def _latex_escape(text: str) -> str:
    for a, b in [("\\", "\\textbackslash{}"), ("_", "\\_"), ("%", "\\%"), ("&", "\\&")]:
        text = text.replace(a, b)
    return text


def export_results_file(
    runs: Sequence[Dict[str, Any]],
    path: PathLike,
    **kwargs: Any,
) -> str:
    """Write :func:`export_results_table` output to *path*."""
    fmt = kwargs.pop("format", None) or Path(path).suffix.lstrip(".")
    if fmt == "tex":
        fmt = "latex"
    text = export_results_table(runs, format=fmt, **kwargs)
    Path(path).write_text(text, encoding="utf-8")
    return str(path)
