"""Create database connections from URLs or config dicts."""

from __future__ import annotations

from typing import Any, Dict, Union
from urllib.parse import urlparse

from .base import Connection
from .errors import ConnectionError

SUPPORTED_ENGINES = ("sqlite", "mysql", "postgresql", "mongodb", "redis")


def supported_engines() -> list[str]:
    return list(SUPPORTED_ENGINES)


def _parse_url(url: str) -> Dict[str, Any]:
    parsed = urlparse(url)
    scheme = (parsed.scheme or "sqlite").lower()
    if scheme in ("postgres", "postgresql"):
        scheme = "postgresql"
    if scheme == "mongo":
        scheme = "mongodb"
    cfg: Dict[str, Any] = {
        "engine": scheme,
        "host": parsed.hostname or "localhost",
        "port": parsed.port,
        "database": (parsed.path or "").lstrip("/") or None,
        "username": parsed.username,
        "password": parsed.password,
    }
    if scheme == "sqlite":
        cfg["path"] = url
    return cfg


def _normalize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    cfg = dict(config)
    engine = (cfg.get("engine") or cfg.get("driver") or "sqlite").lower()
    if engine in ("postgres", "postgresql"):
        engine = "postgresql"
    if engine == "mongo":
        engine = "mongodb"
    cfg["engine"] = engine
    return cfg


def connect(source: Union[str, Dict[str, Any]]) -> Connection:
    """
    Connect to a database.

    Examples
    --------
    >>> import pytekt.db as db
    >>> conn = db.connect("sqlite://./app.db")
    >>> conn = db.connect({"engine": "mysql", "host": "localhost", "database": "app"})
    """
    if isinstance(source, str):
        cfg = _parse_url(source)
    else:
        cfg = _normalize_config(source)

    engine = cfg["engine"]

    if engine == "sqlite":
        from .backends.sqlite import connect_sqlite

        path = cfg.get("path") or cfg.get("database") or cfg.get("db_path") or "sqlite://./.pytekt.db"
        if not str(path).startswith("sqlite:"):
            path = f"sqlite:///{path}"
        return connect_sqlite(str(path))

    if engine == "mysql":
        from .backends.mysql import connect_mysql

        return connect_mysql(cfg)

    if engine == "postgresql":
        from .backends.postgres import connect_postgres

        return connect_postgres(cfg)

    if engine == "mongodb":
        from .backends.mongo import connect_mongo

        return connect_mongo(cfg)

    if engine == "redis":
        from .backends.redis import connect_redis

        return connect_redis(cfg)

    raise ConnectionError(
        f"Unknown engine {engine!r}. Try: {', '.join(SUPPORTED_ENGINES)}"
    )


create_db = connect
