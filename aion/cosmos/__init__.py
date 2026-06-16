"""Deprecated alias — use :mod:`aion.universe` instead."""

from __future__ import annotations

import warnings

warnings.warn(
    "aion.cosmos is renamed to aion.universe; update imports and CLI (aion universe).",
    DeprecationWarning,
    stacklevel=2,
)

from aion.universe import *  # noqa: F401,F403
from aion.universe import __all__  # noqa: F401
