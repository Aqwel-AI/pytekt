"""Reproducibility manifest for research runs."""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def build_manifest(
    *,
    experiment_name: str,
    seed: int,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Collect environment and experiment metadata for reproduction."""
    try:
        from aion import __version__
    except Exception:
        __version__ = "unknown"

    manifest: Dict[str, Any] = {
        "experiment_name": experiment_name,
        "seed": seed,
        "aion_version": __version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        import numpy as np

        manifest["numpy_version"] = np.__version__
    except Exception:
        pass
    if extra:
        manifest.update(extra)
    return manifest


def save_manifest(path: str | Path, manifest: Dict[str, Any]) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    return str(path)


def load_manifest(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
