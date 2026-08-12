"""Deprecated alias — use :mod:`pytekt.universe` instead."""

from __future__ import annotations

import warnings

warnings.warn(
    "pytekt.cosmos is renamed to pytekt.universe; update imports and CLI (pytekt universe).",
    DeprecationWarning,
    stacklevel=2,
)

from pytekt.universe import *  # noqa: F401,F403
from pytekt.universe import __all__  # noqa: F401
