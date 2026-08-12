"""
Built-in benchmark datasets for ML research and prototyping.

Provides toy/classic datasets (Iris, Digits, Housing, Moons, Circles, Blobs,
Wine, Breast Cancer, Diabetes), NLP datasets (sentiment, topic classification,
NER, spam, Q&A), and parametric generators for classification, regression,
clustering, time-series, multi-label, and sparse data.

All loaders return a :class:`Dataset` dataclass with ``data``, ``target``,
``feature_names``, ``target_names``, and ``metadata`` fields.

File I/O (CSV, JSON, Parquet, Excel) lives in :mod:`aion.datasets.io` — stdlib
for CSV/JSON/JSONL; install ``[ai]`` for pandas formats.

Quick start
-----------
>>> from pytekt.datasets import load_iris, fetch, read_csv, read_file
>>> ds = load_iris()
>>> ds.shape
(150, 4)
>>> train, test = fetch("iris", return_split=True)
>>> ds = read_csv("data.csv", target_column="label")
>>> ds.to_csv("export.csv")
"""

from ._base import Dataset, train_test_split_dataset

# Classic toy datasets
from .toy import (
    load_iris,
    load_digits,
    load_housing,
    load_moons,
    load_circles,
    load_blobs,
    load_wine,
    load_breast_cancer,
    load_diabetes,
    load_linnerud,
)

# Text / NLP datasets
from .text import (
    load_sentiment,
    load_topics,
    load_ner,
    load_spam,
    load_qa,
)

# Synthetic generators
from .generators import (
    make_classification,
    make_regression,
    make_clusters,
    make_moons as make_moons_gen,
    make_circles as make_circles_gen,
    make_blobs as make_blobs_gen,
    make_sparse_classification,
    make_time_series,
    make_multilabel,
)

# Registry helpers
from .loaders import fetch, list_datasets, summary

# File I/O (pandas-style; optional pandas for Parquet/Excel)
from .io import (
    read_csv,
    read_tsv,
    read_json,
    read_jsonl,
    read_file,
    read_parquet,
    read_excel,
    read_feather,
    read_pickle,
    from_dataframe,
    write_csv,
    write_json,
    write_jsonl,
    write_parquet,
    write_file,
    to_dataframe,
    to_numpy,
    supported_formats,
)

__all__ = [
    # Base
    "Dataset",
    "train_test_split_dataset",
    # Toy datasets
    "load_iris",
    "load_digits",
    "load_housing",
    "load_moons",
    "load_circles",
    "load_blobs",
    "load_wine",
    "load_breast_cancer",
    "load_diabetes",
    "load_linnerud",
    # Text datasets
    "load_sentiment",
    "load_topics",
    "load_ner",
    "load_spam",
    "load_qa",
    # Generators
    "make_classification",
    "make_regression",
    "make_clusters",
    "make_moons_gen",
    "make_circles_gen",
    "make_blobs_gen",
    "make_sparse_classification",
    "make_time_series",
    "make_multilabel",
    # Helpers
    "fetch",
    "list_datasets",
    "summary",
    # File I/O
    "read_csv",
    "read_tsv",
    "read_json",
    "read_jsonl",
    "read_file",
    "read_parquet",
    "read_excel",
    "read_feather",
    "read_pickle",
    "from_dataframe",
    "write_csv",
    "write_json",
    "write_jsonl",
    "write_parquet",
    "write_file",
    "to_dataframe",
    "to_numpy",
    "supported_formats",
]
