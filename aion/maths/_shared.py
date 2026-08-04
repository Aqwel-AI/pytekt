"""Shared dependencies for the categorized maths functions."""

import math
import random
import warnings
from typing import Any, Callable, List, Optional, Sequence, Tuple, Union

import numpy as np

try:
    import scipy.linalg as sla  # pyright: ignore [reportMissingImports]
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False
    sla = None
    warnings.warn(
        "scipy not available — using numpy-based fallbacks for matrix operations."
    )
