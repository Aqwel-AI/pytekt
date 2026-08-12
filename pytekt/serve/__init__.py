"""
Lightweight serving: expose models, RAG indexes, and chat as REST APIs.

Built on FastAPI (reuses the same optional dependency as :mod:`pytekt.monitor`).
Start a server with ``aion.serve.create_app()`` or the CLI.

Examples
--------
>>> from pytekt.serve import create_app
>>> app = create_app(provider=my_provider)
>>> # Run with: uvicorn app:app
"""

from .app import create_app, AionServer

__all__ = [
    "AionServer",
    "create_app",
]
