"""CPU, memory, and disk metrics (requires ``psutil``; install ``aqwel-aion[monitor]``)."""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional


def _psutil():
    try:
        import psutil
    except ImportError as e:
        raise ImportError(
            "aion.monitor.hardware requires psutil. Install with: pip install 'aqwel-aion[monitor]'"
        ) from e
    return psutil


def _disk_root() -> str:
    if sys.platform == "win32":
        return os.environ.get("SystemDrive", "C:") + os.sep
    return "/"


def get_cpu(interval: float = 0.5) -> float:
    return float(_psutil().cpu_percent(interval=interval))


def get_cpu_detailed(interval: Optional[float] = None) -> Dict[str, Any]:
    """
    Overall and per-core CPU utilization (%).

    If ``interval`` is a positive number, block for that many seconds (first sample).
    If ``None``, non-blocking read (call once with an interval to prime, then use None in a loop).
    """
    ps = _psutil()
    overall = float(ps.cpu_percent(interval=interval))
    per = ps.cpu_percent(interval=None, percpu=True)
    per_core = [float(x) for x in per] if per else []
    return {"percent": overall, "per_core": per_core, "cores": len(per_core)}


def get_ram() -> Dict[str, Any]:
    mem = _psutil().virtual_memory()
    return {
        "total": int(mem.total),
        "used": int(mem.used),
        "percent": float(mem.percent),
    }


def get_disk(path: Optional[str] = None) -> Dict[str, Any]:
    disk = _psutil().disk_usage(path or _disk_root())
    return {
        "total": int(disk.total),
        "used": int(disk.used),
        "percent": float(disk.percent),
    }


def get_disk_io_counters():
    """Raw ``disk_io_counters`` (may be ``None`` on some hosts)."""
    return _psutil().disk_io_counters()
