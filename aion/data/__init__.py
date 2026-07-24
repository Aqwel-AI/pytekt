"""
Data processing: loaders, splitting, augmentation, schema validation.

Load tabular and text data from CSV, JSON, and JSONL files; split datasets
into train/val/test partitions with optional stratification; augment text
with simple transforms; validate records against a schema.

Examples
--------
>>> from aion.data import load_csv, train_val_test_split
>>> rows = load_csv("data.csv")
>>> train, val, test = train_val_test_split(rows)
"""

from .loaders import load_csv, load_json, load_jsonl, save_csv, save_json, save_jsonl
from .splitting import train_test_split, train_val_test_split, kfold_split
from .augmentation import (
    random_delete,
    random_insert,
    random_swap,
    synonym_replace,
    augment_text,
)
from .schema import Schema, Field, validate_record, validate_dataset

__all__ = [
    "Field",
    "Schema",
    "augment_text",
    "kfold_split",
    "load_csv",
    "load_json",
    "load_jsonl",
    "random_delete",
    "random_insert",
    "random_swap",
    "save_csv",
    "save_json",
    "save_jsonl",
    "synonym_replace",
    "train_test_split",
    "train_val_test_split",
    "validate_dataset",
    "validate_record",
]
