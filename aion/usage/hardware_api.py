"""Hardware metrics for the usage dashboard (CPU per-core, GPU, RAM, disk)."""

from __future__ import annotations

import platform
import sys
from typing import Any, Dict, List

_SAMPLER = None


def _get_sampler():
    global _SAMPLER
    if _SAMPLER is None:
        from aion.monitor.history import MetricSampler

        _SAMPLER = MetricSampler()
    return _SAMPLER


def start_hardware_sampling() -> None:
    """Start 1 Hz background sampler (idempotent)."""
    try:
        _get_sampler().start()
    except ImportError as e:
        print(f"Hardware sampling unavailable: {e}")
        print("Install: pip install 'aqwel-aion[monitor]'  (includes psutil)")


def stop_hardware_sampling() -> None:
    if _SAMPLER is not None:
        _SAMPLER.stop()


def get_system_info() -> Dict[str, Any]:
    """Static machine info: cores, OS, hostname."""
    info: Dict[str, Any] = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "python": sys.version.split()[0],
        "hostname": platform.node(),
        "logical_cores": 0,
        "physical_cores": 0,
        "psutil_available": False,
    }
    try:
        import psutil

        info["psutil_available"] = True
        info["logical_cores"] = psutil.cpu_count(logical=True) or 0
        info["physical_cores"] = psutil.cpu_count(logical=False) or 0
        # cpu_freq() often fails on Apple Silicon (sysctl HW_CPU_FREQ missing)
        try:
            freq = psutil.cpu_freq()
            if freq:
                info["cpu_freq_mhz"] = round(float(freq.current), 0)
                if freq.max:
                    info["cpu_freq_max_mhz"] = round(float(freq.max), 0)
        except (OSError, FileNotFoundError, RuntimeError, AttributeError):
            if platform.system() == "Darwin":
                info["cpu_freq_note"] = "CPU frequency unavailable on this Mac (Apple Silicon)"
    except ImportError:
        info["install_hint"] = "pip install 'aqwel-aion[monitor]'"
    except Exception as e:
        info["psutil_error"] = str(e)
    return info


def get_hardware_snapshot() -> Dict[str, Any]:
    """Live metrics + short history for charts."""
    system = get_system_info()
    try:
        start_hardware_sampling()
        snap = _get_sampler().snapshot()
        procs = []
        for p in snap.get("processes") or []:
            rss = int(p.get("rss") or 0)
            procs.append(
                {
                    "pid": p.get("pid"),
                    "name": p.get("name"),
                    "memory_mb": round(rss / (1024 * 1024), 1),
                    "cmdline": p.get("cmdline", ""),
                }
            )
        return {
            "ok": True,
            "system": system,
            **{k: v for k, v in snap.items() if k != "processes"},
            "processes": procs,
        }
    except ImportError as e:
        return {
            "ok": False,
            "error": str(e),
            "system": system,
            "history": [],
            "latest": None,
            "processes": [],
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "system": system,
            "history": [],
            "latest": None,
            "processes": [],
        }


def history_for_charts(history: List[Dict[str, Any]], max_points: int = 120) -> Dict[str, Any]:
    """Trim history for frontend line charts."""
    slice_h = history[-max_points:] if history else []
    labels: List[str] = []
    cpu: List[float] = []
    ram: List[float] = []
    cores_series: List[List[float]] = []

    for i, p in enumerate(slice_h):
        labels.append(str(i))
        cpu.append(float(p.get("cpu", 0)))
        ram.append(float(p.get("ram_pct", 0)))
        cores_series.append([float(x) for x in (p.get("cpu_cores") or [])])

    num_cores = max((len(c) for c in cores_series), default=0)
    per_core: Dict[str, List[float]] = {}
    for c in range(num_cores):
        per_core[f"core_{c}"] = [
            (cores_series[i][c] if c < len(cores_series[i]) else 0.0)
            for i in range(len(cores_series))
        ]

    return {
        "labels": labels,
        "cpu": cpu,
        "ram": ram,
        "per_core": per_core,
        "core_count": num_cores,
    }
