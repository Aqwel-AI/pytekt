"""Google Gemini generateContent API (REST)."""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from .base import ChatMessage
from .errors import ProviderError
from .http_utils import post_json
from .keys import resolve_api_key
from .structured import AssistantTurn

_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
_DEFAULT_MODEL = "gemini-2.0-flash"
# Fallbacks if the configured model is retired or unavailable.
_MODEL_FALLBACKS = (
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
)


class GeminiProvider:
    """
    Chat via Gemini ``generateContent``.

    Parameters
    ----------
    api_key : str, optional
        Defaults to ``GEMINI_API_KEY`` or ``GOOGLE_API_KEY``.
    model : str, optional
        Model id without the ``models/`` prefix, default ``gemini-2.0-flash``.
    """

    supports_tools: bool = False

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = _DEFAULT_MODEL,
    ):
        key = api_key or resolve_api_key("gemini")
        if not key:
            raise ValueError(
                "GeminiProvider requires api_key or GEMINI_API_KEY / GOOGLE_API_KEY "
                "(or gemini_api_key / google_api_key in ~/.aion.yaml)"
            )
        self._api_key = key
        self._model = model.lstrip("models/")

    @staticmethod
    def list_models(
        api_key: Optional[str] = None,
        *,
        timeout: float = 15.0,
    ) -> List[str]:
        """Return model ids that support ``generateContent``."""
        key = api_key or resolve_api_key("gemini")
        if not key:
            raise ValueError("API key required to list Gemini models.")
        url = f"{_GEMINI_BASE}/models?key={key}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
        ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            raise ProviderError(
                f"HTTP {e.code}: {e.reason}",
                status=e.code,
                body=body[:4000],
            ) from e
        except urllib.error.URLError as e:
            raise ProviderError(f"Cannot reach Gemini API: {e.reason}") from e

        out: List[str] = []
        for entry in data.get("models") or []:
            name = str(entry.get("name", "")).removeprefix("models/")
            methods = entry.get("supportedGenerationMethods") or []
            if name and "generateContent" in methods:
                out.append(name)
        return sorted(out, key=lambda n: (0 if "flash" in n else 1, n))

    def verify_connection(self) -> None:
        """Raise :class:`ProviderError` if the key or model is invalid."""
        self.complete(
            [{"role": "user", "content": "Reply with exactly: ok"}],
            temperature=0,
            max_tokens=16,
        )

    def complete_turn(
        self,
        messages: Sequence[Union[ChatMessage, Mapping[str, Any]]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Any = None,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> AssistantTurn:
        raise NotImplementedError(
            "GeminiProvider.complete_turn is not implemented: Gemini generateContent "
            "uses a different schema than OpenAI chat/completions. "
            "Use OpenAIProvider or OpenAICompatibleProvider with aion.tools for tool loops in v1."
        )

    def complete(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        payload = self._build_payload(messages, temperature=temperature, max_tokens=max_tokens)
        models_to_try = [self._model]
        for fallback in _MODEL_FALLBACKS:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error: Optional[ProviderError] = None
        for model in models_to_try:
            try:
                data = self._generate(payload, model)
                text = self._extract_text(data)
                if model != self._model:
                    self._model = model
                return text
            except ProviderError as e:
                last_error = e
                if e.status == 404 or (
                    e.body and "not found" in e.body.lower()
                ):
                    continue
                raise
        if last_error:
            raise last_error
        raise ProviderError("Gemini request failed with no response.")

    def _build_payload(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float,
        max_tokens: int,
    ) -> dict:
        system_parts: List[str] = []
        contents: List[dict] = []
        for m in messages:
            role = m["role"]
            text = m.get("content") or ""
            if role == "system":
                if text:
                    system_parts.append(text)
                continue
            if role == "user":
                contents.append({"role": "user", "parts": [{"text": text}]})
            elif role == "assistant":
                contents.append({"role": "model", "parts": [{"text": text}]})
            else:
                contents.append({"role": "user", "parts": [{"text": text}]})

        if not contents:
            contents.append({"role": "user", "parts": [{"text": "Hello"}]})

        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_parts:
            payload["systemInstruction"] = {
                "parts": [{"text": "\n\n".join(system_parts)}],
            }
        return payload

    def _generate(self, payload: dict, model: str) -> dict:
        url = f"{_GEMINI_BASE}/models/{model}:generateContent?key={self._api_key}"
        data = post_json(url, payload)
        self._last_raw_response = data  # type: ignore[attr-defined]
        if "error" in data:
            err = data["error"]
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            code = err.get("code") if isinstance(err, dict) else None
            raise ProviderError(
                f"Gemini API error: {msg}",
                status=int(code) if isinstance(code, int) else None,
                body=json.dumps(data)[:4000],
            )
        return data

    @staticmethod
    def _extract_text(data: dict) -> str:
        candidates = data.get("candidates") or []
        if not candidates:
            pf = data.get("promptFeedback") or {}
            block = pf.get("blockReason")
            if block:
                raise ProviderError(f"Gemini blocked the prompt: {block}")
            raise ProviderError(f"Gemini returned no candidates: {data!r}")

        candidate = candidates[0]
        finish = candidate.get("finishReason")
        if finish in ("SAFETY", "RECITATION", "BLOCKLIST"):
            raise ProviderError(f"Gemini stopped generation: {finish}")

        content = candidate.get("content") or {}
        parts = content.get("parts") or []
        text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        if text:
            return text
        raise ProviderError(
            f"Gemini returned empty text (finishReason={finish!r})."
        )
