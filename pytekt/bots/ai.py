"""
High-Performance AI & LLM Integration Layer for PyTekt Bots.
Seamlessly integrates with PyTekt's providers, rag, and embed modules.
"""

from __future__ import annotations

import asyncio
import base64
import inspect
import json
import logging
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from ..embed import embed_text
from ..providers.base import ChatMessage, ChatProvider
from ..providers.factory import create_provider
from ..providers.keys import resolve_api_key
from ..rag.pipeline import SimpleRAGIndex
from ..tools.registry import ToolRegistry
from ..tools.schemas import function_tool
from ._core import Cache

logger = logging.getLogger("pytekt.bots.ai")


def _python_type_to_json_schema(t: Any) -> str:
    """Map basic Python type annotations to JSON Schema types."""
    if t in (int,):
        return "integer"
    if t in (float,):
        return "number"
    if t in (bool,):
        return "boolean"
    if t in (list, List, Sequence):
        return "array"
    if t in (dict, Dict):
        return "object"
    return "string"


class AI:
    """
    Unified AI interface for conversational bots, function calling,
    multimodal vision/audio, per-chat rolling memory, RAG knowledge bases, and moderation.

    Parameters
    ----------
    provider : str
        Provider name ('openai', 'anthropic', 'gemini', 'deepseek', 'nvidia', 'ollama', etc.).
    model : str, optional
        Model name (e.g. 'gpt-4o-mini', 'claude-3-5-sonnet-20241022', 'gemini-1.5-flash').
    system : str, optional
        Default system prompt for the model.
    memory_ttl : float, optional
        Time-to-live in seconds for rolling per-chat conversation memory (default 3600s / 1hr).
    memory_limit : int, optional
        Maximum number of recent message turns to retain per chat (default 20).
    api_key : str, optional
        API key override (defaults to environment variables).
    """

    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        system: str = "You are a helpful and responsive AI assistant.",
        memory_ttl: float = 3600.0,
        memory_limit: int = 20,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        cache: Optional[Cache] = None,
        **kwargs: Any,
    ) -> None:
        self.provider_name = provider.lower().strip()
        self.model_name = model
        self.system_prompt = system
        self.memory_ttl = memory_ttl
        self.memory_limit = memory_limit
        self.cache = cache or Cache()

        # Initialize underlying PyTekt ChatProvider
        prov_kwargs: Dict[str, Any] = dict(kwargs)
        if api_key:
            prov_kwargs["api_key"] = api_key
        if model:
            prov_kwargs["model"] = model
        if base_url:
            prov_kwargs["base_url"] = base_url

        try:
            self._provider: ChatProvider = create_provider(self.provider_name, **prov_kwargs)
        except Exception as e:
            logger.warning("Could not initialize provider %s: %s (will use offline fallback when needed)", self.provider_name, e)
            self._provider = None  # type: ignore[assignment]

        self._tool_registry = ToolRegistry()
        self._tool_schemas: List[Dict[str, Any]] = []
        self._rag_index: Optional[SimpleRAGIndex] = None
        self._long_term_memories: Dict[str, List[str]] = {}

    # ------------------------------------------------------------------
    # Tool Registration Decorator
    # ------------------------------------------------------------------

    def tool(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to register a plain Python function as a tool/skill for the AI.
        Automatically generates OpenAI-compatible tool schema from function signature and docstrings.
        """
        name = fn.__name__
        doc = (fn.__doc__ or f"Tool {name}").strip()

        sig = inspect.signature(fn)
        props: Dict[str, Any] = {}
        req: List[str] = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            p_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            schema_type = _python_type_to_json_schema(p_type)
            props[param_name] = {
                "type": schema_type,
                "description": f"Parameter {param_name}",
            }
            if param.default == inspect.Parameter.empty:
                req.append(param_name)

        schema = function_tool(name, doc, properties=props, required=req)
        self._tool_schemas.append(schema)
        self._tool_registry.register(name, fn, required_arg_keys=req)
        return fn

    # ------------------------------------------------------------------
    # Per-Chat Memory Helpers (Stored in C++ Cache / KV)
    # ------------------------------------------------------------------

    def _get_chat_history(self, chat_id: str) -> List[ChatMessage]:
        raw = self.cache.get(f"ai_mem:{chat_id}")
        if not raw:
            return []
        try:
            items = json.loads(raw)
            return [
                {"role": it.get("role", "user"), "content": it.get("content", "")}
                for it in items
            ]
        except Exception:
            return []

    def _save_chat_history(self, chat_id: str, history: Sequence[Union[ChatMessage, Dict[str, Any]]]) -> None:
        trimmed = list(history)[-self.memory_limit:]
        serialized = json.dumps([
            {
                "role": m.get("role") if isinstance(m, dict) else getattr(m, "role", "user"),
                "content": m.get("content") if isinstance(m, dict) else getattr(m, "content", ""),
            }
            for m in trimmed
        ])
        self.cache.set(f"ai_mem:{chat_id}", serialized, ttl_seconds=self.memory_ttl)

    async def remember(self, chat_id: str, fact: str) -> None:
        """Store an explicit long-term fact for a chat or user."""
        mem_key = f"ai_ltm:{chat_id}"
        facts = self.get_memories(chat_id)
        if fact not in facts:
            facts.append(fact)
            self.cache.set(mem_key, json.dumps(facts), ttl_seconds=0.0)  # persistent

    async def forget(self, chat_id: str) -> None:
        """Wipe both rolling history and long-term memory for a chat."""
        self.cache.delete(f"ai_mem:{chat_id}")
        self.cache.delete(f"ai_ltm:{chat_id}")

    def get_memories(self, chat_id: str) -> List[str]:
        """Retrieve explicit long-term facts stored for a chat."""
        raw = self.cache.get(f"ai_ltm:{chat_id}")
        if not raw:
            return []
        try:
            return list(json.loads(raw))
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Knowledge Base / RAG Integration
    # ------------------------------------------------------------------

    def knowledge_base(
        self,
        source: Union[str, Path, Sequence[str]],
        chunk_size: int = 512,
        overlap: int = 64,
    ) -> SimpleRAGIndex:
        """
        One-line RAG indexing over user-supplied documents or text files
        using PyTekt's rag and embed pipeline.
        """
        self._rag_index = SimpleRAGIndex(embed_fn=embed_text)

        texts_to_index: List[str] = []
        if isinstance(source, (str, Path)):
            p = Path(source)
            if p.is_file():
                try:
                    texts_to_index.append(p.read_text(encoding="utf-8"))
                except Exception as e:
                    logger.error("Failed to read knowledge base file %s: %s", source, e)
            elif p.is_dir():
                for f in p.glob("**/*"):
                    if f.is_file() and f.suffix in (".md", ".txt", ".rst", ".json", ".py"):
                        try:
                            texts_to_index.append(f.read_text(encoding="utf-8"))
                        except Exception:
                            pass
            else:
                texts_to_index.append(str(source))
        elif isinstance(source, (list, tuple)):
            texts_to_index.extend(str(s) for s in source)

        if texts_to_index:
            self._rag_index.index_texts(texts_to_index, chunk_size=chunk_size, overlap=overlap)
            logger.info("Indexed %d document(s) into RAG knowledge base", len(texts_to_index))

        return self._rag_index

    # ------------------------------------------------------------------
    # Chat Completion & Streaming
    # ------------------------------------------------------------------

    async def ask(
        self,
        text: str,
        chat_id: Optional[str] = None,
        use_kb: bool = False,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """
        Provider-agnostic chat completion with automatic per-chat rolling memory,
        RAG retrieval, and autonomous multi-step tool calling.
        """
        if self._provider is None:
            return f"Echo (offline): {text}"

        messages: List[ChatMessage] = []

        # 1. System prompt & long-term memory facts
        sys_prompt = system or self.system_prompt
        if chat_id:
            facts = self.get_memories(chat_id)
            if facts:
                sys_prompt += "\n\nFacts known about this user/conversation:\n" + "\n".join(f"- {f}" for f in facts)

        # 2. Knowledge base RAG retrieval
        if use_kb and self._rag_index is not None:
            try:
                results = self._rag_index.query(text, k=3)
                if results:
                    snippets = [
                        c.metadata.get("text", "")
                        for c in results
                        if hasattr(c, "metadata") and c.metadata.get("text")
                    ]
                    if snippets:
                        context_str = "\n---\n".join(snippets)
                        sys_prompt += f"\n\nContext from Knowledge Base:\n{context_str}"
            except Exception as e:
                logger.warning("RAG retrieval error: %s", e)

        messages.append({"role": "system", "content": sys_prompt})

        # 3. Rolling per-chat conversation history
        history: List[ChatMessage] = []
        if chat_id:
            history = self._get_chat_history(chat_id)
            messages.extend(history)

        # 4. Current user prompt
        user_msg: ChatMessage = {"role": "user", "content": text}
        messages.append(user_msg)

        loop = asyncio.get_event_loop()

        # 5. Multi-turn tool execution loop
        tools = self._tool_schemas if self._tool_schemas else None
        max_tool_turns = 5

        for _ in range(max_tool_turns):
            if hasattr(self._provider, "complete_turn") and tools:
                # Use structured turn
                turn = await loop.run_in_executor(
                    None,
                    lambda msgs=list(messages): self._provider.complete_turn(  # type: ignore[union-attr]
                        msgs,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        tools=tools,
                        **kwargs,
                    ),
                )

                if turn.tool_calls:
                    # Model requested tool calls
                    assistant_msg: ChatMessage = {
                        "role": "assistant",
                        "content": turn.content or "",
                    }
                    messages.append(assistant_msg)

                    for tc in turn.tool_calls:
                        res_str = self._tool_registry.call(tc.name, tc.arguments_json)
                        tool_reply: ChatMessage = {
                            "role": "tool",
                            "content": res_str,
                        }
                        messages.append(tool_reply)
                    continue

                content_out = turn.content or ""
            else:
                # Standard completion
                content_out = await loop.run_in_executor(
                    None,
                    lambda msgs=list(messages): self._provider.complete(
                        msgs,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs,
                    ),
                )

            # Update rolling memory
            if chat_id:
                history.append(user_msg)
                history.append({"role": "assistant", "content": content_out})
                self._save_chat_history(chat_id, history)

            return content_out

        return content_out

    async def ask_stream(
        self,
        text: str,
        chat_id: Optional[str] = None,
        use_kb: bool = False,
        system: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Async generator streaming completion tokens or sentences.
        """
        # Get full answer
        full_text = await self.ask(text, chat_id=chat_id, use_kb=use_kb, system=system, **kwargs)

        # Chunk response into words/phrases for realistic live edit streaming
        words = re.findall(r"\S+|\s+", full_text)
        chunk_size = 4
        for i in range(0, len(words), chunk_size):
            yield "".join(words[i : i + chunk_size])
            await asyncio.sleep(0.04)

    # ------------------------------------------------------------------
    # Multimodal: Speech-to-Text & Vision
    # ------------------------------------------------------------------

    async def transcribe(self, audio: Union[str, bytes, Path]) -> str:
        """
        Transcribe speech/audio to text using OpenAI Whisper API or provider endpoint.
        """
        # Read audio bytes if path
        audio_data: bytes
        filename = "audio.ogg"

        if isinstance(audio, (str, Path)):
            p = Path(audio)
            if p.is_file():
                audio_data = p.read_bytes()
                filename = p.name
            else:
                # Might be URL or file_id
                audio_data = str(audio).encode("utf-8")
        else:
            audio_data = audio

        key = resolve_api_key("openai")
        if not key:
            return "[Audio transcription: missing OPENAI_API_KEY]"

        url = "https://api.openai.com/v1/audio/transcriptions"
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

        body = bytearray()
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(b'Content-Disposition: form-data; name="model"\r\n\r\n')
        body.extend(b"whisper-1\r\n")

        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(audio_data)
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }

        req = urllib.request.Request(url, data=bytes(body), headers=headers, method="POST")

        loop = asyncio.get_event_loop()
        try:
            resp_bytes = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req, timeout=60).read(),
            )
            res = json.loads(resp_bytes.decode("utf-8"))
            return res.get("text", "")
        except Exception as e:
            logger.error("Audio transcription failed: %s", e)
            return f"[Transcription error: {e}]"

    async def vision(
        self,
        image: Union[str, bytes, Path],
        prompt: str = "What is in this image?",
    ) -> str:
        """
        Analyze an image using vision-capable models (OpenAI, Gemini, Anthropic).
        """
        image_b64: str
        mime = "image/jpeg"

        if isinstance(image, (str, Path)):
            p = Path(image)
            if p.is_file():
                raw = p.read_bytes()
                image_b64 = base64.b64encode(raw).decode("ascii")
                if p.suffix.lower() == ".png":
                    mime = "image/png"
                elif p.suffix.lower() == ".webp":
                    mime = "image/webp"
            elif str(image).startswith("http://") or str(image).startswith("https://"):
                image_url = str(image)
                image_b64 = ""
            else:
                image_b64 = str(image)
        else:
            image_b64 = base64.b64encode(image).decode("ascii")

        key = resolve_api_key("openai")
        if not key:
            return f"[Vision analysis (mocked): image analysis for '{prompt}']"

        img_content: Dict[str, Any]
        if image_b64:
            img_content = {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}}
        else:
            img_content = {"type": "image_url", "image_url": {"url": str(image)}}

        payload = {
            "model": self.model_name or "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        img_content,
                    ],
                }
            ],
            "max_tokens": 1024,
        }

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        loop = asyncio.get_event_loop()
        try:
            resp_bytes = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req, timeout=40).read(),
            )
            res = json.loads(resp_bytes.decode("utf-8"))
            return res["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("Vision request failed: %s", e)
            return f"[Vision error: {e}]"

    # ------------------------------------------------------------------
    # Content Moderation
    # ------------------------------------------------------------------

    async def moderate(self, text: str) -> bool:
        """
        Fast content safety & moderation check.
        Returns True if the text violates safety policies (hate/harassment/nsfw/spam),
        False if clean.
        """
        if not text:
            return False

        # 1. Local heuristic check for obvious toxicity / spam tokens
        toxic_patterns = [
            r"\b(nigger|faggot|kike|chink)\b",
            r"(buy cheap|crypto giveaway|free nitro|telegram\.me/joinchat)",
        ]
        for pat in toxic_patterns:
            if re.search(pat, text, re.IGNORECASE):
                return True

        # 2. OpenAI Moderation Endpoint check if OPENAI_API_KEY is present
        key = resolve_api_key("openai")
        if key:
            url = "https://api.openai.com/v1/moderations"
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            }
            data = json.dumps({"input": text}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            loop = asyncio.get_event_loop()
            try:
                resp_bytes = await loop.run_in_executor(
                    None,
                    lambda: urllib.request.urlopen(req, timeout=10).read(),
                )
                res = json.loads(resp_bytes.decode("utf-8"))
                results = res.get("results", [])
                if results and results[0].get("flagged"):
                    return True
            except Exception:
                pass

        return False
