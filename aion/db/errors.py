"""Database errors for :mod:`aion.db`."""

from __future__ import annotations


class DbError(Exception):
    """Base error for aion.db."""


class ConnectionError(DbError):
    """Failed to connect or connection lost."""


class QueryError(DbError):
    """Invalid query or execution failure."""


class DuplicateKeyError(DbError):
    """Unique constraint violation."""


class NotFoundError(DbError):
    """Requested row/document not found."""
