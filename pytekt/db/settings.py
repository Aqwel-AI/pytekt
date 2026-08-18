"""Default database URL and config helpers."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from ..config.core import get_nested
from .base import Connection
from .factory import connect

DEFAULT_SQLITE_PATH = os.path.expanduser("~/.pytekt/agent.db")


def default_db_url() -> str:
    # sqlite:///absolute/path (three slashes after scheme)
    if DEFAULT_SQLITE_PATH.startswith("/"):
        return f"sqlite://{DEFAULT_SQLITE_PATH}"
    return f"sqlite:///{DEFAULT_SQLITE_PATH}"


def db_url_from_config(cfg: Dict[str, Any]) -> str:
    """Read ``db.url`` from config or return default SQLite path."""
    url = get_nested(cfg, "db.url")
    if url:
        return str(url).replace("~", os.path.expanduser("~"))
    return default_db_url()


def get_db_connection(cfg: Optional[Dict[str, Any]] = None, *, url: Optional[str] = None) -> Connection:
    """Open a configured :mod:`pytekt.db` connection."""
    if url:
        target = url.replace("~", os.path.expanduser("~"))
    elif cfg is not None:
        target = db_url_from_config(cfg)
    else:
        target = default_db_url()
    if target.startswith("sqlite:///"):
        parent = os.path.dirname(target.replace("sqlite:///", ""))
        if parent:
            os.makedirs(parent, exist_ok=True)
    return connect(target)
