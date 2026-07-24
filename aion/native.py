"""Library-wide introspection for optional native C++ backends.

This module centralizes information about Aion's optional compiled
extensions so the rest of the library can reason about C++ acceleration
without duplicating import logic in multiple places.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import shutil
from typing import Dict


@dataclass(frozen=True)
class NativeBackendStatus:
    """Describe one optional compiled backend shipped by the library."""

    key: str
    name: str
    module_name: str
    source: str
    available: bool
    fallback: str
    purpose: str

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-friendly representation."""
        return asdict(self)


def _core_available() -> bool:
    try:
        from ._core import using_native_extension

        return bool(using_native_extension())
    except Exception:
        return False


def _universe_available() -> bool:
    try:
        from .universe._native import using_native_extension

        return bool(using_native_extension())
    except Exception:
        return False


def _bigdata_available() -> bool:
    try:
        from .bigdata import using_native_extension

        return bool(using_native_extension())
    except Exception:
        return False


def native_backends() -> Dict[str, NativeBackendStatus]:
    """Return every optional native backend known to the library."""
    return {
        "core": NativeBackendStatus(
            key="core",
            name="aion core numerics",
            module_name="aion._aion_core",
            source="src/aion_core.cpp",
            available=_core_available(),
            fallback="NumPy",
            purpose="Fast vector numerics and reductions exposed as aion.fast_*.",
        ),
        "universe": NativeBackendStatus(
            key="universe",
            name="aion universe astronomy",
            module_name="aion._aion_universe",
            source="src/aion_universe.cpp",
            available=_universe_available(),
            fallback="Pure Python",
            purpose="Astronomy, coordinate, and cosmology hot paths in aion.universe.",
        ),
        "bigdata": NativeBackendStatus(
            key="bigdata",
            name="aion big-data kernels",
            module_name="aion._aion_bigdata",
            source="src/aion_bigdata.cpp",
            available=_bigdata_available(),
            fallback="NumPy / Python",
            purpose="Prefix sums, rolling windows, histograms, and chunk stats.",
        ),
    }


def native_status() -> Dict[str, Dict[str, object]]:
    """Return native backend status as plain dictionaries."""
    return {key: status.to_dict() for key, status in native_backends().items()}


def using_any_native_extension() -> bool:
    """Return True when any optional compiled backend is active."""
    return any(status.available for status in native_backends().values())


def native_build_info() -> Dict[str, object]:
    """Return build/toolchain hints for enabling compiled acceleration."""
    root = Path(__file__).resolve().parent.parent
    compiler = shutil.which("c++") or shutil.which("clang++") or shutil.which("g++")
    cmake = shutil.which("cmake")
    return {
        "root": str(root),
        "compiler": compiler,
        "cmake": cmake,
        "pybind11_required": True,
        "editable_build_command": 'pip install -e ".[dev]"',
        "recommended_native_build_command": 'pip install pybind11 && pip install -e .',
        "sources": [status.source for status in native_backends().values()],
    }


def native_status_report() -> str:
    """Format a concise multi-line summary for CLIs and diagnostics."""
    lines = []
    for status in native_backends().values():
        state = "native" if status.available else f"fallback: {status.fallback}"
        lines.append(f"{status.name}: {state} ({status.source})")
    return "\n".join(lines)


__all__ = [
    "NativeBackendStatus",
    "native_backends",
    "native_status",
    "native_build_info",
    "native_status_report",
    "using_any_native_extension",
]
