"""Top processes by resident memory (RSS)."""

from __future__ import annotations

from typing import Any, Dict, List

from aion.monitor.hardware import _psutil


def _cmdline_preview(p, max_len: int = 140) -> str:
    ps = _psutil()
    try:
        parts = p.cmdline()
    except (ps.AccessDenied, ps.Error):
        return ""
    if not parts:
        try:
            return p.name() or ""
        except (ps.AccessDenied, ps.Error):
            return ""
    line = " ".join(parts)
    if len(line) > max_len:
        return line[: max_len - 1] + "…"
    return line


def top_memory_processes(limit: int = 40) -> List[Dict[str, Any]]:
    ps = _psutil()
    rows: List[Dict[str, Any]] = []
    for p in ps.process_iter(["pid", "name", "memory_info"]):
        try:
            info = p.info
            if not info or info.get("memory_info") is None:
                continue
            rss = int(info["memory_info"].rss)
            pid = int(info["pid"])
            name = str(info.get("name") or "")
        except (ps.Error, TypeError, ValueError, KeyError):
            continue
        try:
            cmd = _cmdline_preview(p)
        except (ps.Error, TypeError):
            cmd = name
        rows.append(
            {
                "pid": pid,
                "name": name,
                "rss": rss,
                "cmdline": cmd,
            }
        )
    rows.sort(key=lambda r: r["rss"], reverse=True)
    return rows[:limit]
