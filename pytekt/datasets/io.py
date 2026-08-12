"""Professional file I/O for :class:`Dataset` — pandas-style, stdlib-first.

Load tabular and text data from disk into :class:`Dataset`, or export back to
common formats.  Pandas-powered readers (Parquet, Excel, Feather) are used when
``pandas`` is installed (``pip install 'pytekt[ai]'``); otherwise CSV, JSON,
and JSONL work with the standard library only.

Examples
--------
>>> from pytekt.datasets import read_csv, read_file
>>> ds = read_csv("data.csv", target_column="label")
>>> ds = read_file("train.parquet", target_column="y")  # needs pandas
>>> ds.to_csv("export.csv")
>>> df = ds.to_dataframe()  # needs pandas
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

from ._base import Dataset

PathLike = Union[str, os.PathLike]

# Formats handled without pandas
_STDLIB_FORMATS = frozenset({".csv", ".tsv", ".json", ".jsonl", ".ndjson"})
# Formats that require pandas
_PANDAS_FORMATS = frozenset({
    ".parquet", ".pq",
    ".xlsx", ".xls", ".xlsm",
    ".feather",
    ".orc",
    ".pickle", ".pkl",
    ".h5", ".hdf5",
})


def _has_pandas() -> bool:
    try:
        import pandas  # noqa: F401
        return True
    except ImportError:
        return False


def _require_pandas(fmt: str) -> None:
    if not _has_pandas():
        raise ImportError(
            f"Reading {fmt!r} requires pandas. Install with: pip install 'pytekt[ai]'"
        )


def _extension(path: PathLike) -> str:
    return Path(path).suffix.lower()


def _rows_to_dataset(
    rows: Sequence[Dict[str, Any]],
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    name: str = "",
    description: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dataset:
    """Build a :class:`Dataset` from a list of row dicts."""
    if not rows:
        raise ValueError("Cannot build Dataset from empty data")

    keys = list(rows[0].keys())
    if target_column not in keys:
        raise ValueError(
            f"target_column {target_column!r} not in columns: {keys}"
        )

    if feature_columns is None:
        feature_columns = [k for k in keys if k != target_column]
    else:
        missing = set(feature_columns) - set(keys)
        if missing:
            raise ValueError(f"Unknown feature columns: {sorted(missing)}")

    targets: List[Any] = []
    feature_rows: List[List[Any]] = []

    for row in rows:
        targets.append(row[target_column])
        feature_rows.append([row[c] for c in feature_columns])

    # Numeric columns → float64 matrix; mixed/text → object column vector
    sample = feature_rows[0]
    all_numeric = all(
        isinstance(v, (int, float, bool, type(None))) or v is None
        for v in sample
    )

    if all_numeric and len(feature_columns) > 0:
        data = np.array(feature_rows, dtype=np.float64)
        for i, v in enumerate(sample):
            if v is None or (isinstance(v, float) and np.isnan(v)):
                col = data[:, i]
                col = np.where(np.isnan(col), np.nan, col)
                data[:, i] = col
    elif len(feature_columns) == 1:
        data = np.array([r[0] for r in feature_rows], dtype=object).reshape(-1, 1)
    else:
        data = np.array(feature_rows, dtype=object)

    target_arr = _coerce_target(targets)

    meta = dict(metadata or {})
    meta.setdefault("task", _infer_task(target_arr))
    meta["target_column"] = target_column
    meta["source_columns"] = list(keys)

    return Dataset(
        data=data,
        target=target_arr,
        feature_names=list(feature_columns),
        target_names=_target_names_from_array(target_arr),
        description=description or f"Loaded from tabular file ({len(rows)} rows).",
        name=name or "file_dataset",
        metadata=meta,
    )


def _coerce_target(values: Sequence[Any]) -> np.ndarray:
    """Convert target column to int64 (classification) or float64 (regression)."""
    if not values:
        return np.array([], dtype=np.float64)

    sample = values[0]
    if isinstance(sample, str):
        labels = sorted(set(str(v) for v in values))
        label_to_id = {lab: i for i, lab in enumerate(labels)}
        return np.array([label_to_id[str(v)] for v in values], dtype=np.int64)

    if all(isinstance(v, (bool, np.bool_)) for v in values):
        return np.array(values, dtype=np.int64)

    if all(isinstance(v, (int, np.integer)) and not isinstance(v, bool) for v in values):
        return np.array(values, dtype=np.int64)

    try:
        arr = np.array(values, dtype=np.float64)
        if np.all(arr == arr.astype(np.int64)):
            return arr.astype(np.int64)
        return arr
    except (ValueError, TypeError):
        labels = sorted(set(str(v) for v in values))
        label_to_id = {lab: i for i, lab in enumerate(labels)}
        return np.array([label_to_id[str(v)] for v in values], dtype=np.int64)


def _infer_task(target: np.ndarray) -> str:
    if target.dtype.kind in ("U", "O", "S"):
        return "classification"
    if target.dtype.kind in ("i", "u", "b"):
        unique = np.unique(target)
        if len(unique) <= 20:
            return "classification"
    if target.dtype.kind == "f":
        unique = np.unique(target)
        if len(unique) <= 20 and np.all(unique == unique.astype(int)):
            return "classification"
        return "regression"
    return "unknown"


def _target_names_from_array(target: np.ndarray) -> List[str]:
    if target.dtype.kind in ("i", "u", "b"):
        n = int(target.max()) + 1 if target.size else 0
        return [f"class_{i}" for i in range(max(n, len(np.unique(target))))]
    return ["target"]


# ---------------------------------------------------------------------------
# Stdlib readers
# ---------------------------------------------------------------------------

def read_csv(
    path: PathLike,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    delimiter: str = ",",
    encoding: str = "utf-8",
    has_header: bool = True,
    nrows: Optional[int] = None,
    name: str = "",
    **_: Any,
) -> Dataset:
    """Load a CSV file into a :class:`Dataset`.

    Parameters
    ----------
    target_column : str
        Column name used as the label / target vector.
    feature_columns : sequence of str, optional
        Columns to use as features.  Default: all columns except *target_column*.
    nrows : int, optional
        Maximum number of data rows to read (after header).
    """
    path = Path(path)
    rows: List[Dict[str, Any]] = []
    with open(path, newline="", encoding=encoding) as f:
        if has_header:
            reader = csv.DictReader(f, delimiter=delimiter)
            for i, row in enumerate(reader):
                if nrows is not None and i >= nrows:
                    break
                rows.append(dict(row))
        else:
            raw = csv.reader(f, delimiter=delimiter)
            header: Optional[List[str]] = None
            for i, line in enumerate(raw):
                if nrows is not None and i >= nrows:
                    break
                if header is None:
                    header = [f"col{j}" for j in range(len(line))]
                rows.append(dict(zip(header, line)))

    return _rows_to_dataset(
        rows,
        target_column=target_column,
        feature_columns=feature_columns,
        name=name or path.stem,
        description=f"CSV dataset from {path.name}",
        metadata={"path": str(path), "format": "csv"},
    )


def read_tsv(
    path: PathLike,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    encoding: str = "utf-8",
    nrows: Optional[int] = None,
    name: str = "",
) -> Dataset:
    """Load a TSV (tab-separated) file into a :class:`Dataset`."""
    return read_csv(
        path,
        target_column=target_column,
        feature_columns=feature_columns,
        delimiter="\t",
        encoding=encoding,
        nrows=nrows,
        name=name,
    )


def read_json(
    path: PathLike,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    encoding: str = "utf-8",
    records_key: Optional[str] = None,
    name: str = "",
) -> Dataset:
    """Load a JSON file (array of objects or wrapped list) into a :class:`Dataset`."""
    path = Path(path)
    with open(path, encoding=encoding) as f:
        payload = json.load(f)

    if records_key is not None:
        if not isinstance(payload, dict) or records_key not in payload:
            raise ValueError(f"JSON object has no key {records_key!r}")
        rows = payload[records_key]
    elif isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = [payload]
    else:
        raise ValueError("JSON must be a list of objects or a dict with a records key")

    if not all(isinstance(r, dict) for r in rows):
        raise ValueError("Each JSON record must be an object (dict)")

    return _rows_to_dataset(
        rows,
        target_column=target_column,
        feature_columns=feature_columns,
        name=name or path.stem,
        description=f"JSON dataset from {path.name}",
        metadata={"path": str(path), "format": "json"},
    )


def read_jsonl(
    path: PathLike,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    encoding: str = "utf-8",
    nrows: Optional[int] = None,
    name: str = "",
) -> Dataset:
    """Load JSON Lines (one JSON object per line) into a :class:`Dataset`."""
    path = Path(path)
    rows: List[Dict[str, Any]] = []
    with open(path, encoding=encoding) as f:
        for i, line in enumerate(f):
            if nrows is not None and i >= nrows:
                break
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    return _rows_to_dataset(
        rows,
        target_column=target_column,
        feature_columns=feature_columns,
        name=name or path.stem,
        description=f"JSONL dataset from {path.name}",
        metadata={"path": str(path), "format": "jsonl"},
    )


# ---------------------------------------------------------------------------
# Pandas-powered readers (optional)
# ---------------------------------------------------------------------------

def _read_with_pandas(
    path: PathLike,
    *,
    reader: str,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    nrows: Optional[int] = None,
    name: str = "",
    **pandas_kwargs: Any,
) -> Dataset:
    _require_pandas(reader)
    import pandas as pd

    path = Path(path)
    read_fn = getattr(pd, f"read_{reader}")
    if nrows is not None:
        pandas_kwargs.setdefault("nrows", nrows)
    df = read_fn(path, **pandas_kwargs)
    return from_dataframe(
        df,
        target_column=target_column,
        feature_columns=feature_columns,
        name=name or path.stem,
        metadata={"path": str(path), "format": reader},
    )


def read_parquet(
    path: PathLike,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    name: str = "",
    **pandas_kwargs: Any,
) -> Dataset:
    """Load a Parquet file (requires pandas + pyarrow or fastparquet)."""
    return _read_with_pandas(
        path,
        reader="parquet",
        target_column=target_column,
        feature_columns=feature_columns,
        name=name,
        **pandas_kwargs,
    )


def read_excel(
    path: PathLike,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    sheet_name: Union[str, int] = 0,
    name: str = "",
    **pandas_kwargs: Any,
) -> Dataset:
    """Load an Excel workbook (requires pandas + openpyxl or xlrd)."""
    pandas_kwargs.setdefault("sheet_name", sheet_name)
    return _read_with_pandas(
        path,
        reader="excel",
        target_column=target_column,
        feature_columns=feature_columns,
        name=name,
        **pandas_kwargs,
    )


def read_feather(
    path: PathLike,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    name: str = "",
    **pandas_kwargs: Any,
) -> Dataset:
    """Load a Feather file (requires pandas + pyarrow)."""
    return _read_with_pandas(
        path,
        reader="feather",
        target_column=target_column,
        feature_columns=feature_columns,
        name=name,
        **pandas_kwargs,
    )


def read_pickle(
    path: PathLike,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    name: str = "",
    **pandas_kwargs: Any,
) -> Dataset:
    """Load a pickled pandas DataFrame or table from disk."""
    return _read_with_pandas(
        path,
        reader="pickle",
        target_column=target_column,
        feature_columns=feature_columns,
        name=name,
        **pandas_kwargs,
    )


def from_dataframe(
    df: Any,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    name: str = "",
    description: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dataset:
    """Convert a pandas DataFrame into a :class:`Dataset`.

    Parameters
    ----------
    df : pandas.DataFrame
    target_column : str
        Name of the label column.
    feature_columns : sequence of str, optional
        Feature column names; default is all columns except *target_column*.
    """
    _require_pandas("DataFrame")
    import pandas as pd

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas.DataFrame, got {type(df).__name__}")

    if target_column not in df.columns:
        raise ValueError(
            f"target_column {target_column!r} not in columns: {list(df.columns)}"
        )

    if feature_columns is None:
        feature_columns = [c for c in df.columns if c != target_column]

    target_series = df[target_column]
    feature_df = df[list(feature_columns)]

    target_arr = _coerce_target(target_series.tolist())

    if feature_df.select_dtypes(include=[np.number]).shape[1] == len(feature_columns):
        data = feature_df.to_numpy(dtype=np.float64)
    else:
        data = feature_df.to_numpy(dtype=object)
        if data.ndim == 1:
            data = data.reshape(-1, 1)

    meta = dict(metadata or {})
    meta.setdefault("task", _infer_task(target_arr))
    meta["target_column"] = target_column

    return Dataset(
        data=data,
        target=target_arr,
        feature_names=list(feature_columns),
        target_names=_target_names_from_array(target_arr),
        description=description or f"Dataset from DataFrame ({len(df)} rows).",
        name=name or "dataframe",
        metadata=meta,
    )


# ---------------------------------------------------------------------------
# Auto-detect format
# ---------------------------------------------------------------------------

def read_file(
    path: PathLike,
    *,
    target_column: str,
    feature_columns: Optional[Sequence[str]] = None,
    format: Optional[str] = None,
    nrows: Optional[int] = None,
    name: str = "",
    **kwargs: Any,
) -> Dataset:
    """Load a dataset file; format inferred from the file extension.

    Supported without pandas: ``.csv``, ``.tsv``, ``.json``, ``.jsonl``, ``.ndjson``
    With ``pip install 'pytekt[ai]'``: ``.parquet``, ``.xlsx``, ``.xls``,
    ``.feather``, ``.pkl``, ``.pickle``, ``.h5``, ``.hdf5``, ``.orc``

    Parameters
    ----------
    format : str, optional
        Override extension detection (e.g. ``"csv"``, ``"parquet"``).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    fmt = (format or _extension(path)).lstrip(".").lower()
    if fmt == "tsv":
        return read_tsv(
            path,
            target_column=target_column,
            feature_columns=feature_columns,
            nrows=nrows,
            name=name,
        )
    if fmt in ("csv",):
        return read_csv(
            path,
            target_column=target_column,
            feature_columns=feature_columns,
            nrows=nrows,
            name=name,
            **{k: v for k, v in kwargs.items() if k in ("delimiter", "encoding")},
        )
    if fmt == "json":
        return read_json(
            path,
            target_column=target_column,
            feature_columns=feature_columns,
            name=name,
            **{k: v for k, v in kwargs.items() if k == "records_key"},
        )
    if fmt in ("jsonl", "ndjson"):
        return read_jsonl(
            path,
            target_column=target_column,
            feature_columns=feature_columns,
            nrows=nrows,
            name=name,
        )
    if fmt in ("parquet", "pq"):
        return read_parquet(
            path,
            target_column=target_column,
            feature_columns=feature_columns,
            name=name,
            **kwargs,
        )
    if fmt in ("xlsx", "xls", "xlsm", "excel"):
        return read_excel(
            path,
            target_column=target_column,
            feature_columns=feature_columns,
            name=name,
            **kwargs,
        )
    if fmt == "feather":
        return read_feather(
            path,
            target_column=target_column,
            feature_columns=feature_columns,
            name=name,
            **kwargs,
        )
    if fmt in ("pkl", "pickle"):
        return read_pickle(
            path,
            target_column=target_column,
            feature_columns=feature_columns,
            name=name,
            **kwargs,
        )

    ext = "." + fmt if not fmt.startswith(".") else fmt
    if ext in _PANDAS_FORMATS:
        _require_pandas(ext)

    raise ValueError(
        f"Unsupported file format {fmt!r} for {path.name}. "
        f"Use read_csv, read_json, read_parquet, etc. explicitly."
    )


def supported_formats() -> Dict[str, List[str]]:
    """Return file extensions grouped by dependency requirements."""
    pandas_ext = sorted(_PANDAS_FORMATS)
    stdlib_ext = sorted(_STDLIB_FORMATS)
    return {
        "stdlib": stdlib_ext,
        "pandas": pandas_ext,
        "all": sorted(set(stdlib_ext) | set(pandas_ext)),
    }


# ---------------------------------------------------------------------------
# Export / write
# ---------------------------------------------------------------------------

def write_csv(
    ds: Dataset,
    path: PathLike,
    *,
    include_target: bool = True,
    encoding: str = "utf-8",
    delimiter: str = ",",
) -> None:
    """Write a :class:`Dataset` to CSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = (["target"] if include_target else []) + (
        ds.feature_names or [f"x{i}" for i in range(ds.n_features)]
    )

    with open(path, "w", newline="", encoding=encoding) as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(headers)
        for i in range(ds.n_samples):
            row: List[Any] = []
            if include_target:
                row.append(ds.target[i])
            if ds.data.ndim == 1:
                row.append(ds.data[i])
            else:
                row.extend(ds.data[i].tolist())
            writer.writerow(row)


def write_json(
    ds: Dataset,
    path: PathLike,
    *,
    include_target: bool = True,
    indent: int = 2,
    encoding: str = "utf-8",
) -> None:
    """Write a :class:`Dataset` as a JSON array of row objects."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    names = ds.feature_names or [f"x{i}" for i in range(ds.n_features)]
    records = []
    for i in range(ds.n_samples):
        rec: Dict[str, Any] = {}
        if include_target:
            rec["target"] = _json_safe(ds.target[i])
        if ds.data.ndim == 1:
            rec[names[0]] = _json_safe(ds.data[i])
        else:
            for j, name in enumerate(names):
                rec[name] = _json_safe(ds.data[i, j])
        records.append(rec)

    with open(path, "w", encoding=encoding) as f:
        json.dump(records, f, indent=indent, default=str, ensure_ascii=False)


def write_jsonl(
    ds: Dataset,
    path: PathLike,
    *,
    include_target: bool = True,
    encoding: str = "utf-8",
) -> None:
    """Write a :class:`Dataset` as JSON Lines."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    names = ds.feature_names or [f"x{i}" for i in range(ds.n_features)]
    with open(path, "w", encoding=encoding) as f:
        for i in range(ds.n_samples):
            rec: Dict[str, Any] = {}
            if include_target:
                rec["target"] = _json_safe(ds.target[i])
            if ds.data.ndim == 1:
                rec[names[0]] = _json_safe(ds.data[i])
            else:
                for j, name in enumerate(names):
                    rec[name] = _json_safe(ds.data[i, j])
            f.write(json.dumps(rec, default=str, ensure_ascii=False) + "\n")


def write_parquet(
    ds: Dataset,
    path: PathLike,
    *,
    target_column: str = "target",
    **pandas_kwargs: Any,
) -> None:
    """Write a :class:`Dataset` to Parquet (requires pandas)."""
    _require_pandas("parquet")
    df = to_dataframe(ds, target_column=target_column)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, **pandas_kwargs)


def write_file(
    ds: Dataset,
    path: PathLike,
    *,
    format: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Save a :class:`Dataset`; format inferred from the file extension."""
    path = Path(path)
    fmt = (format or _extension(path)).lstrip(".").lower()

    if fmt in ("csv",):
        return write_csv(ds, path, **{k: v for k, v in kwargs.items() if k in ("include_target", "encoding", "delimiter")})
    if fmt == "json":
        return write_json(ds, path, **{k: v for k, v in kwargs.items() if k in ("include_target", "indent", "encoding")})
    if fmt in ("jsonl", "ndjson"):
        return write_jsonl(ds, path, **{k: v for k, v in kwargs.items() if k == "include_target"})
    if fmt in ("parquet", "pq"):
        return write_parquet(ds, path, **kwargs)

    raise ValueError(f"Unsupported export format: {fmt!r}")


def _json_safe(value: Any) -> Any:
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def to_dataframe(
    ds: Dataset,
    *,
    target_column: str = "target",
) -> Any:
    """Convert a :class:`Dataset` to a pandas DataFrame (requires pandas)."""
    _require_pandas("DataFrame")
    import pandas as pd

    names = ds.feature_names or [f"x{i}" for i in range(ds.n_features)]
    if ds.data.ndim == 1:
        data_dict = {names[0]: ds.data}
    else:
        data_dict = {names[i]: ds.data[:, i] for i in range(min(len(names), ds.data.shape[1]))}

    df = pd.DataFrame(data_dict)
    df.insert(0, target_column, ds.target)
    return df


def to_numpy(
    ds: Dataset,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return ``(X, y)`` feature matrix and target vector (convenience for sklearn-style APIs)."""
    return ds.data, ds.target
