"""NVIDIA GPU metrics via NVML (``nvidia-ml-py``) or ``nvidia-smi`` fallback."""

from __future__ import annotations

import csv
import io
import shutil
import subprocess
from typing import Any, Dict, List

_NVML_INITIALIZED = False


def _try_pynvml() -> List[Dict[str, Any]]:
    global _NVML_INITIALIZED
    try:
        import pynvml  # type: ignore
    except ImportError:
        return []

    try:
        if not _NVML_INITIALIZED:
            pynvml.nvmlInit()
            _NVML_INITIALIZED = True
        n = pynvml.nvmlDeviceGetCount()
        out: List[Dict[str, Any]] = []
        for i in range(n):
            h = pynvml.nvmlDeviceGetHandleByIndex(i)
            raw_name = pynvml.nvmlDeviceGetName(h)
            if isinstance(raw_name, bytes):
                name = raw_name.decode("utf-8", errors="replace")
            else:
                name = str(raw_name)
            util = pynvml.nvmlDeviceGetUtilizationRates(h)
            mem = pynvml.nvmlDeviceGetMemoryInfo(h)
            try:
                temp = int(pynvml.nvmlDeviceGetTemperature(h, pynvml.NVML_TEMPERATURE_GPU))
            except Exception:
                temp = None
            out.append(
                {
                    "index": i,
                    "name": name,
                    "utilization_gpu": int(util.gpu),
                    "memory_used": int(mem.used),
                    "memory_total": int(mem.total),
                    "temperature_c": temp,
                }
            )
        return out
    except Exception:
        return []


def _try_nvidia_smi() -> List[Dict[str, Any]]:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return []
    try:
        proc = subprocess.run(
            [
                exe,
                "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    out: List[Dict[str, Any]] = []
    reader = csv.reader(io.StringIO(proc.stdout.strip()))
    for row in reader:
        if len(row) < 6:
            continue
        try:
            idx = int(row[0].strip())
            name = row[1].strip()
            util = int(float(row[2].strip()))
            mem_used = int(float(row[3].strip())) * 1024 * 1024
            mem_total = int(float(row[4].strip())) * 1024 * 1024
            t_raw = row[5].strip()
            temp = int(float(t_raw)) if t_raw and t_raw != "[Not Supported]" else None
        except (ValueError, IndexError):
            continue
        out.append(
            {
                "index": idx,
                "name": name,
                "utilization_gpu": util,
                "memory_used": mem_used,
                "memory_total": mem_total,
                "temperature_c": temp,
            }
        )
    return out


def get_gpu_metrics() -> Dict[str, Any]:
    """
    Return all detected GPUs with utilization, VRAM, and temperature when available.

    Uses ``pynvml`` if installed, otherwise ``nvidia-smi`` on PATH.
    """
    gpus = _try_pynvml()
    if not gpus:
        gpus = _try_nvidia_smi()
    return {
        "gpus": gpus,
        "available": bool(gpus),
        "source": "nvml" if _NVML_INITIALIZED and gpus else ("nvidia-smi" if gpus else None),
    }
