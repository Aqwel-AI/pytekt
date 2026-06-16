"""Log observing sessions to :mod:`aion.db`."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DEFAULT_DB = os.path.expanduser("~/.aion/universe.db")

_OBSERVATION_SCHEMA = {
    "ts": "",
    "latitude": 0.0,
    "longitude": 0.0,
    "object_count": 0,
    "objects": [],
    "notes": "",
}


def _hydrate_observations(conn) -> None:
    """Register schema on a fresh connection so ``find`` works on existing DB files."""
    if hasattr(conn, "_ensure_table"):
        conn._ensure_table("observations", _OBSERVATION_SCHEMA)


def log_observation(
    *,
    latitude: float,
    longitude: float,
    objects: List[Dict[str, Any]],
    notes: str = "",
    db_url: Optional[str] = None,
) -> Any:
    """Insert one observing session row."""
    from ..db import connect

    url = db_url or f"sqlite:///{DEFAULT_DB}"
    parent = os.path.dirname(DEFAULT_DB)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = connect(url)
    _hydrate_observations(conn)
    doc = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "latitude": latitude,
        "longitude": longitude,
        "object_count": len(objects),
        "objects": [o.get("name", "?") for o in objects[:20]],
        "notes": notes,
    }
    row_id = conn.observations.insert(doc)
    conn.close()
    return row_id


def list_observations(*, db_url: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    from ..db import connect

    url = db_url or f"sqlite:///{DEFAULT_DB}"
    if db_url is None and not os.path.isfile(DEFAULT_DB):
        return []
    conn = connect(url)
    _hydrate_observations(conn)
    rows = conn.observations.find(_limit=limit)
    conn.close()
    return rows
