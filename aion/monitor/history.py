"""Background sampling: up to 5 minutes of metrics at 1 Hz for dashboard graphs."""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from aion.monitor.gpu import get_gpu_metrics
from aion.monitor.hardware import get_cpu_detailed, get_disk, get_disk_io_counters, get_ram
from aion.monitor.processes import top_memory_processes

MAX_POINTS = 300  # 5 min @ 1 sample/sec
SAMPLE_INTERVAL = 1.0


class MetricSampler:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._points: Deque[Dict[str, Any]] = deque(maxlen=MAX_POINTS)
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._last_disk_io = None
        self._last_disk_ts: Optional[float] = None
        self._primed = False
        self._processes: List[Dict[str, Any]] = []
        self._tick = 0

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="aion-monitor-sampler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None

    def _disk_rates(self, now: float) -> Dict[str, float]:
        counters = get_disk_io_counters()
        if counters is None:
            return {"read_mbps": 0.0, "write_mbps": 0.0}
        if self._last_disk_io is None or self._last_disk_ts is None:
            self._last_disk_io = counters
            self._last_disk_ts = now
            return {"read_mbps": 0.0, "write_mbps": 0.0}
        dt = now - self._last_disk_ts
        if dt <= 0:
            return {"read_mbps": 0.0, "write_mbps": 0.0}
        read_b = counters.read_bytes - self._last_disk_io.read_bytes
        write_b = counters.write_bytes - self._last_disk_io.write_bytes
        self._last_disk_io = counters
        self._last_disk_ts = now
        return {
            "read_mbps": (read_b / dt) / (1024 * 1024),
            "write_mbps": (write_b / dt) / (1024 * 1024),
        }

    def _loop(self) -> None:
        # Prime CPU counters (blocking once)
        if not self._primed:
            get_cpu_detailed(interval=0.15)
            self._primed = True
        while not self._stop.is_set():
            t0 = time.time()
            now_ms = int(t0 * 1000)
            try:
                cpu = get_cpu_detailed(interval=None)
                ram = get_ram()
                disk_usage = get_disk()
                io_rates = self._disk_rates(t0)
                gpu_block = get_gpu_metrics()
                point: Dict[str, Any] = {
                    "t": now_ms,
                    "cpu": cpu["percent"],
                    "cpu_cores": cpu["per_core"],
                    "ram_pct": float(ram["percent"]),
                    "ram_used": int(ram["used"]),
                    "ram_total": int(ram["total"]),
                    "disk_pct": float(disk_usage["percent"]),
                    "disk_read_mbps": float(io_rates["read_mbps"]),
                    "disk_write_mbps": float(io_rates["write_mbps"]),
                    "gpus": [
                        {
                            "index": g["index"],
                            "name": g["name"],
                            "util": int(g["utilization_gpu"]),
                            "mem_used": int(g["memory_used"]),
                            "mem_total": int(g["memory_total"]),
                            "temp_c": g.get("temperature_c"),
                        }
                        for g in gpu_block.get("gpus", [])
                    ],
                }
                with self._lock:
                    self._points.append(point)
                    self._tick += 1
                    if self._tick % 2 == 0:
                        try:
                            self._processes = top_memory_processes(limit=40)
                        except Exception:
                            pass
            except Exception:
                pass
            elapsed = time.time() - t0
            wait = max(0.0, SAMPLE_INTERVAL - elapsed)
            self._stop.wait(wait)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            history = list(self._points)
            processes = list(self._processes)
        latest = history[-1] if history else None
        return {
            "sample_interval_sec": SAMPLE_INTERVAL,
            "history_max_points": MAX_POINTS,
            "history": history,
            "latest": latest,
            "processes": processes,
        }


sampler = MetricSampler()
