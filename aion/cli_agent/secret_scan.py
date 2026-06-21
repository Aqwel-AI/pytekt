"""Scan content for likely secrets before writes or commands."""

from __future__ import annotations

import re
from typing import List, Tuple

_PATTERNS = [
    re.compile(r"nvapi-[A-Za-z0-9_-]{20,}", re.I),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
]


def scan_text(text: str) -> List[str]:
    """Return human-readable warnings for detected secret patterns."""
    warnings: List[str] = []
    for pat in _PATTERNS:
        if pat.search(text):
            warnings.append(f"Matched pattern: {pat.pattern[:40]}…")
    return warnings


def scan_command(command: str) -> List[str]:
    return scan_text(command)


def should_block(text: str, *, block: bool = True) -> Tuple[bool, List[str]]:
    hits = scan_text(text)
    if not hits:
        return False, []
    return block, hits
