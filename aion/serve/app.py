"""FastAPI server for serving LLM chat, RAG queries, and custom endpoints."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False


def _require_fastapi() -> None:
    if not _HAS_FASTAPI:
        raise ImportError(
            "aion.serve requires FastAPI. Install with: pip install aqwel-aion[monitor]"
        )


if _HAS_FASTAPI:
    class ChatRequest(BaseModel):
        messages: List[Dict[str, str]]
        model: str = ""
        temperature: float = 0.7
        max_tokens: int = 1024

    class ChatResponse(BaseModel):
        response: str
        model: str = ""
        usage: Dict[str, Any] = {}
        latency_ms: float = 0.0

    class RAGRequest(BaseModel):
        query: str
        top_k: int = 5

    class RAGResponse(BaseModel):
        answer: str
        sources: List[Dict[str, Any]] = []
        latency_ms: float = 0.0

    class HealthResponse(BaseModel):
        status: str = "ok"
        version: str = ""


class AionServer:
    """
    Configurable server that wraps providers, RAG indexes, and custom
    endpoints into a single FastAPI application.

    Parameters
    ----------
    provider : optional
        An ``aion.providers`` chat provider for the ``/chat`` endpoint.
    rag_index : optional
        An ``aion.rag.SimpleRAGIndex`` for the ``/rag`` endpoint.
    title : str
        API title shown in the OpenAPI docs.
    """

    def __init__(
        self,
        *,
        provider: Any = None,
        rag_index: Any = None,
        title: str = "Aion API",
        version: str = "",
    ) -> None:
        _require_fastapi()
        self.provider = provider
        self.rag_index = rag_index
        self.title = title
        self.version = version or self._get_version()
        self._custom_routes: List[Dict[str, Any]] = []

    @staticmethod
    def _get_version() -> str:
        try:
            from .. import __version__
            return __version__
        except Exception:
            return "0.0.0"

    def add_route(
        self,
        path: str,
        handler: Callable[..., Any],
        *,
        method: str = "POST",
        summary: str = "",
    ) -> None:
        """Register a custom endpoint."""
        self._custom_routes.append({
            "path": path,
            "handler": handler,
            "method": method.upper(),
            "summary": summary,
        })

    def build_app(self) -> Any:
        """Build and return the FastAPI application."""
        app = FastAPI(title=self.title, version=self.version)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        server = self

        @app.get("/health", response_model=HealthResponse)
        async def health():
            return HealthResponse(status="ok", version=server.version)

        if self.provider is not None:
            @app.post("/chat", response_model=ChatResponse)
            async def chat(req: ChatRequest):
                t0 = time.perf_counter()
                try:
                    from ..providers.base import ChatMessage
                    messages = [
                        ChatMessage(role=m["role"], content=m["content"])
                        for m in req.messages
                    ]
                    response = server.provider.complete(
                        messages,
                        temperature=req.temperature,
                        max_tokens=req.max_tokens,
                    )
                    elapsed = (time.perf_counter() - t0) * 1000
                    return ChatResponse(
                        response=response,
                        model=req.model,
                        latency_ms=round(elapsed, 2),
                    )
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

        if self.rag_index is not None:
            @app.post("/rag", response_model=RAGResponse)
            async def rag_query(req: RAGRequest):
                t0 = time.perf_counter()
                try:
                    result = server.rag_index.query(req.query, top_k=req.top_k)
                    elapsed = (time.perf_counter() - t0) * 1000
                    if isinstance(result, str):
                        return RAGResponse(answer=result, latency_ms=round(elapsed, 2))
                    return RAGResponse(
                        answer=result.get("answer", str(result)),
                        sources=result.get("sources", []),
                        latency_ms=round(elapsed, 2),
                    )
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

        for route in self._custom_routes:
            if route["method"] == "GET":
                app.get(route["path"], summary=route["summary"])(route["handler"])
            else:
                app.post(route["path"], summary=route["summary"])(route["handler"])

        return app


def create_app(
    *,
    provider: Any = None,
    rag_index: Any = None,
    title: str = "Aion API",
) -> Any:
    """
    Convenience function to build a ready-to-run FastAPI app.

    Usage::

        app = create_app(provider=OpenAIProvider())
        # uvicorn module:app --port 8000
    """
    server = AionServer(provider=provider, rag_index=rag_index, title=title)
    return server.build_app()
