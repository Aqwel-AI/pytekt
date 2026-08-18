"""Minimal .env parsing and required environment variable checks."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Union

PathLike = Union[str, os.PathLike[str]]


def load_dotenv_file(
    path: PathLike,
    *,
    override: bool = False,
) -> Dict[str, str]:
    """
    Parse KEY=VALUE lines from a ``.env`` file (no shell expansion).

    Lines starting with ``#`` and blank lines are ignored. Values may be
    quoted with ``"`` or ``'``. Does not modify ``os.environ`` unless
    ``override`` is True (then sets missing keys only by default).
    """
    p = Path(path)
    if not p.is_file():
        return {}
    out: Dict[str, str] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        key, _, rest = s.partition("=")
        key = key.strip()
        val = rest.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        out[key] = val
        if override or key not in os.environ:
            os.environ[key] = val
    return out


def require_env(*names: str) -> Dict[str, str]:
    """
    Return a dict of ``name -> value`` for each name in ``os.environ``.
    Raises ``ValueError`` if any are missing or empty.
    """
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise ValueError(f"Missing or empty environment variables: {missing}")
    return {n: os.environ[n] for n in names}
