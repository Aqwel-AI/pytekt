"""Validation helpers for agent outputs and artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Optional


def is_valid_json(text: str) -> bool:
    """Return ``True`` when the text parses as JSON."""
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return False
    return True


def file_exists(path: str) -> bool:
    """Return ``True`` when a path exists on disk."""
    return Path(path).exists()


def contains_citations(text: str) -> bool:
    """Check whether a response appears to contain citation-like markers."""
    return any(marker in text for marker in ("[", "]", "http://", "https://"))


def validate_output(
    text: str,
    *,
    require_json: bool = False,
    require_citations: bool = False,
) -> Dict[str, bool]:
    """Return a compact output validation report."""
    return {
        "non_empty": bool(text.strip()),
        "valid_json": is_valid_json(text) if require_json else True,
        "contains_citations": contains_citations(text) if require_citations else True,
    }


def validate_with(text: str, validator: Callable[[str], bool]) -> bool:
    """Run a custom validation callback."""
    return bool(validator(text))
