"""Lightweight schema validation for tabular data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union


@dataclass
class Field:
    """
    Describes a single field in a record.

    Parameters
    ----------
    name : str
        Field name (dict key).
    dtype : type or tuple of types
        Expected Python type(s).
    required : bool
        Whether the field must be present.
    nullable : bool
        Whether ``None`` is accepted.
    choices : list, optional
        Whitelist of allowed values.
    validator : callable, optional
        Custom ``(value) -> bool`` predicate.
    """

    name: str
    dtype: Union[Type, tuple] = str
    required: bool = True
    nullable: bool = False
    choices: Optional[List[Any]] = None
    validator: Optional[Callable[[Any], bool]] = None


@dataclass
class Schema:
    """Collection of ``Field`` definitions for validating records."""

    fields: List[Field] = field(default_factory=list)

    def add(self, f: Field) -> "Schema":
        self.fields.append(f)
        return self

    def field_names(self) -> List[str]:
        return [f.name for f in self.fields]


def validate_record(
    record: Dict[str, Any],
    schema: Schema,
) -> List[str]:
    """
    Validate a single record against *schema*.

    Returns a list of error messages (empty list means valid).
    """
    errors: List[str] = []
    for f in schema.fields:
        if f.name not in record:
            if f.required:
                errors.append(f"missing required field '{f.name}'")
            continue
        val = record[f.name]
        if val is None:
            if not f.nullable:
                errors.append(f"field '{f.name}' is not nullable")
            continue
        if not isinstance(val, f.dtype):
            errors.append(
                f"field '{f.name}': expected {f.dtype}, got {type(val).__name__}"
            )
        if f.choices is not None and val not in f.choices:
            errors.append(f"field '{f.name}': value {val!r} not in {f.choices}")
        if f.validator is not None and not f.validator(val):
            errors.append(f"field '{f.name}': custom validator failed for {val!r}")
    return errors


def validate_dataset(
    data: Sequence[Dict[str, Any]],
    schema: Schema,
) -> Dict[str, Any]:
    """
    Validate every record in *data*.

    Returns ``{"valid": bool, "total": int, "errors": {row_index: [msgs]}}``.
    """
    all_errors: Dict[int, List[str]] = {}
    for i, record in enumerate(data):
        errs = validate_record(record, schema)
        if errs:
            all_errors[i] = errs
    return {
        "valid": len(all_errors) == 0,
        "total": len(data),
        "error_count": sum(len(v) for v in all_errors.values()),
        "errors": all_errors,
    }
