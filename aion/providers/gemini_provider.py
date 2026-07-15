"""Google Gemini generateContent API (REST)."""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
import uuid
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from .base import ChatMessage
from .errors import ProviderError
from .http_utils import post_json
from .keys import resolve_api_key
from .structured import AssistantTurn, NormalizedToolCall

MessageInput = Union[ChatMessage, Mapping[str, Any]]

_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
_DEFAULT_MODEL = "gemini-2.0-flash"
# Fallbacks if the configured model is retired or unavailable.
_MODEL_FALLBACKS = (
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
)


def _openai_tools_to_gemini(tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
    if not tools:
        return None
    decls: List[Dict[str, Any]] = []
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        fn = tool.get("function") if tool.get("type") == "function" else tool
        if not isinstance(fn, dict) or not fn.get("name"):
            continue
        decl: Dict[str, Any] = {"name": str(fn["name"])}
        if fn.get("description"):
            decl["description"] = str(fn["description"])
        params = fn.get("parameters")
        if isinstance(params, dict):
            decl["parameters"] = params
        decls.append(decl)
    if not decls:
        return None
    return [{"functionDeclarations": decls}]


def _openai_messages_to_gemini(
    messages: Sequence[MessageInput],
) -> tuple[Optional[str], List[dict]]:
    system_parts: List[str] = []
    contents: List[dict] = []
    call_id_to_name: Dict[str, str] = {}

    for m in messages:
        msg = dict(m)
        role = msg.get("role", "")
        content = msg.get("content")

        if role == "system":
            if content:
                system_parts.append(str(content))
            continue

        if role == "tool":
            call_id = str(msg.get("tool_call_id") or "")
            name = str(
                msg.get("name")
                or msg.get("tool_name")
                or call_id_to_name.get(call_id)
                or "tool"
            )
            try:
                response_obj = json.loads(content) if isinstance(content, str) else {"result": content}
            except (json.JSONDecodeError, TypeError):
                response_obj = {"result": str(content or "")}
            if not isinstance(response_obj, dict):
                response_obj = {"result": str(response_obj)}
            contents.append(
                {
                    "role": "user",
                    "parts": [{"functionResponse": {"name": name, "response": response_obj}}],
                }
            )
            continue

        if role == "assistant":
            parts: List[dict] = []
            if content:
                parts.append({"text": str(content)})
            for tc in msg.get("tool_calls") or []:
                if not isinstance(tc, dict):
                    continue
                fn = tc.get("function") or {}
                tc_name = str((fn or {}).get("name") or "")
                tc_id = str(tc.get("id") or "")
                if tc_id and tc_name:
                    call_id_to_name[tc_id] = tc_name
                raw_args = fn.get("arguments") if isinstance(fn, dict) else "{}"
                try:
                    parsed = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                except (json.JSONDecodeError, TypeError):
                    parsed = {}
                if not isinstance(parsed, dict):
                    parsed = {}
                parts.append({"functionCall": {"name": tc_name, "args": parsed}})
            contents.append({"role": "model", "parts": parts or [{"text": ""}]})
            continue

        if role == "user":
            contents.append({"role": "user", "parts": [{"text": str(content or "")}]})
            continue

    system = "\n\n".join(system_parts) if system_parts else None
    return system, contents


def _parse_gemini_response(data: Dict[str, Any]) -> AssistantTurn:
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
    text_parts: List[str] = []
    tool_calls: List[NormalizedToolCall] = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        if "text" in part and part.get("text"):
            text_parts.append(str(part["text"]))
        fc = part.get("functionCall")
        if isinstance(fc, dict) and fc.get("name"):
            args = fc.get("args") if isinstance(fc.get("args"), dict) else {}
            tool_calls.append(
                NormalizedToolCall(
                    id=f"call_{uuid.uuid4().hex[:12]}",
                    name=str(fc["name"]),
                    arguments_json=json.dumps(args),
                )
            )

    text = "".join(text_parts) if text_parts else None
    if not text and not tool_calls:
        raise ProviderError(f"Gemini returned empty text (finishReason={finish!r}).")
    return AssistantTurn(content=text, tool_calls=tool_calls, raw=dict(data))


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

    supports_tools: bool = True

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
        messages: Sequence[MessageInput],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Any = None,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> AssistantTurn:
        system, contents = _openai_messages_to_gemini(messages)
        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hello"}]}]

        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        gemini_tools = _openai_tools_to_gemini(tools if isinstance(tools, list) else None)
        if gemini_tools:
            payload["tools"] = gemini_tools
            if tool_choice == "none":
                payload["toolConfig"] = {"functionCallingConfig": {"mode": "NONE"}}
            elif tool_choice == "auto" or tool_choice is None:
                payload["toolConfig"] = {"functionCallingConfig": {"mode": "AUTO"}}
        for k, v in kwargs.items():
            if k not in payload:
                payload[k] = v

        models_to_try = [self._model]
        for fallback in _MODEL_FALLBACKS:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error: Optional[ProviderError] = None
        for model in models_to_try:
            try:
                data = self._generate(payload, model)
                turn = _parse_gemini_response(data)
                if model != self._model:
                    self._model = model
                return turn
            except ProviderError as e:
                last_error = e
                if e.status == 404 or (e.body and "not found" in e.body.lower()):
                    continue
                raise
        if last_error:
            raise last_error
        raise ProviderError("Gemini request failed with no response.")

    def complete(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        turn = self.complete_turn(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=None,
            **kwargs,
        )
        return turn.content or ""

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
        turn = _parse_gemini_response(data)
        if turn.content:
            return turn.content
        raise ProviderError("Gemini returned empty text.")
