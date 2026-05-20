"""Persistent usage log at ``~/.aion/usage/events.jsonl``."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional


def default_store_path() -> str:
    return os.path.expanduser("~/.aion/usage/events.jsonl")


class UsageStore:
    """Append-only JSONL event log with in-process locking."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or default_store_path()
        self._lock = threading.Lock()
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Dict[str, Any]) -> None:
        event = dict(event)
        event.setdefault("ts", datetime.now(timezone.utc).isoformat())
        line = json.dumps(event, default=str) + "\n"
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line)

    def iter_events(self) -> Iterator[Dict[str, Any]]:
        if not os.path.isfile(self.path):
            return
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def read_all(self) -> List[Dict[str, Any]]:
        return list(self.iter_events())

    def clear(self) -> None:
        with self._lock:
            if os.path.isfile(self.path):
                os.remove(self.path)
