"""Load and save CSV, JSON, and JSONL files."""

from __future__ import annotations

import csv
import json
import os
from typing import Any, Dict, IO, List, Optional, Sequence, Union


def load_csv(
    path: str,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8",
    has_header: bool = True,
) -> List[Dict[str, Any]]:
    """
    Load a CSV file and return rows as a list of dicts.

    If *has_header* is ``False``, keys are ``"col0"``, ``"col1"``, etc.
    """
    rows: List[Dict[str, Any]] = []
    with open(path, newline="", encoding=encoding) as f:
        if has_header:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                rows.append(dict(row))
        else:
            reader_raw = csv.reader(f, delimiter=delimiter)
            for line in reader_raw:
                rows.append({f"col{i}": v for i, v in enumerate(line)})
    return rows


def save_csv(
    path: str,
    rows: Sequence[Dict[str, Any]],
    *,
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> None:
    """Write rows (list of dicts) to a CSV file."""
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: str, *, encoding: str = "utf-8") -> Any:
    """Load a JSON file (object or array)."""
    with open(path, encoding=encoding) as f:
        return json.load(f)


def save_json(
    path: str,
    data: Any,
    *,
    indent: int = 2,
    encoding: str = "utf-8",
) -> None:
    """Save data to a JSON file."""
    with open(path, "w", encoding=encoding) as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)


def load_jsonl(path: str, *, encoding: str = "utf-8") -> List[Dict[str, Any]]:
    """Load a JSONL (JSON Lines) file — one JSON object per line."""
    rows: List[Dict[str, Any]] = []
    with open(path, encoding=encoding) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def save_jsonl(
    path: str,
    rows: Sequence[Dict[str, Any]],
    *,
    encoding: str = "utf-8",
) -> None:
    """Write rows as JSONL (one JSON object per line)."""
    with open(path, "w", encoding=encoding) as f:
        for row in rows:
            f.write(json.dumps(row, default=str, ensure_ascii=False) + "\n")
