"""Parse /connect and /disconnect slash-command arguments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

_NEW_KEY_FLAGS = frozenset({"new", "--new-key", "fresh", "key"})
_FORGET_FLAGS = frozenset({"forget", "--forget", "-f", "stay"})

# User-facing names → internal provider id (extend as needed).
_COMPANY_ALIASES: Dict[str, str] = {
    "aqwel": "aqwel",
    "aqwelai": "aqwel",
    "aqwel_ai": "aqwel",
    "openai": "openai",
    "chatgpt": "openai",
    "gpt": "openai",
    "gemini": "gemini",
    "google": "gemini",
    "deepseek": "deepseek",
    "anthropic": "anthropic",
    "claude": "anthropic",
    "ollama": "ollama",
    "groq": "groq",
    "mistral": "mistral",
    "openai_compatible": "openai_compatible",
    "compatible": "openai_compatible",
}


@dataclass
class DisconnectRequest:
    """Result of parsing ``/disconnect <what you name>``."""

    label: str = ""  # what the user typed (for messages)
    provider: Optional[str] = None
    model: Optional[str] = None
    forget_saved: bool = True
    clear_keys: bool = False
    keys_only: bool = False


def parse_connect_args(args: str) -> Tuple[str, Optional[str], bool]:
    """Returns (provider, model, new_key)."""
    tokens = args.split()
    if not tokens:
        return "", None, False
    provider = tokens[0].lower()
    new_key = False
    model_parts: list[str] = []
    for token in tokens[1:]:
        if token.lower() in _NEW_KEY_FLAGS:
            new_key = True
        else:
            model_parts.append(token)
    model = " ".join(model_parts) if model_parts else None
    return provider, model, new_key


def _compact(s: str) -> str:
    return s.lower().replace(" ", "").replace("_", "").replace("-", "")


def _text_matches_active(query: str, provider: Optional[str], model: Optional[str]) -> bool:
    if not query:
        return False
    q = query.lower().strip()
    qc = _compact(q)
    if provider:
        p = provider.lower()
        if q in p or p in q or qc in _compact(p):
            return True
    if model:
        m = model.lower()
        if q in m or m in q or qc in _compact(m):
            return True
    return False


def normalize_company(name: str) -> Optional[str]:
    """Map a label to an internal provider id."""
    key = name.lower().strip().replace(" ", "_")
    if key in _COMPANY_ALIASES:
        return _COMPANY_ALIASES[key]
    for alias, provider_id in _COMPANY_ALIASES.items():
        if key == alias:
            return provider_id
        if len(alias) >= 3 and alias in key:
            return provider_id
    return None


def infer_provider_from_model(model: str) -> Optional[str]:
    m = model.lower().strip().removeprefix("models/")
    if m.startswith("gemini"):
        return "gemini"
    if m.startswith("gpt") or m.startswith("o1") or m.startswith("o3") or m.startswith("o4"):
        return "openai"
    if "deepseek" in m:
        return "deepseek"
    if m.startswith("claude"):
        return "anthropic"
    if m.startswith("llama") or m.startswith("qwen") or m.startswith("mistral"):
        return "ollama"
    return None


def looks_like_model_name(text: str) -> bool:
    t = text.lower().strip()
    if "-" in t or any(c.isdigit() for c in t):
        return (
            t.startswith("gemini")
            or t.startswith("gpt")
            or t.startswith("claude")
            or t.startswith("llama")
            or t.startswith("o1")
            or t.startswith("o3")
            or t.startswith("o4")
            or t.startswith("deepseek")
            or t.startswith("qwen")
            or t.startswith("mistral")
        )
    return False


def _provider_from_free_text(text: str) -> Optional[str]:
    """Best-effort provider id from anything the user typed."""
    raw = text.strip()
    if not raw:
        return None
    low = raw.lower()
    prov = normalize_company(raw) or normalize_company(low.replace(" ", "_"))
    if prov:
        return prov
    for alias, provider_id in _COMPANY_ALIASES.items():
        if len(alias) >= 3 and alias in low:
            return provider_id
    return infer_provider_from_model(raw)


def parse_disconnect_args(
    args: str,
    *,
    connected: bool = False,
    active_provider: Optional[str] = None,
    active_model: Optional[str] = None,
) -> DisconnectRequest:
    """
    Parse ``/disconnect`` or ``/disconnect <anything>``.

    The argument is free text: company name, model id, or words that match
    the current session. Empty means disconnect whatever is active now.
    """
    raw = args.strip()
    label = raw or (active_provider or "session")

    if not raw:
        return DisconnectRequest(
            label=label,
            provider=active_provider,
            model=active_model,
            forget_saved=True,
            clear_keys=bool(active_provider),
        )

    if any(t.lower() in _FORGET_FLAGS for t in raw.split()):
        pass  # still resolve target below; forget is default

    # 1) Matches what you are using right now → leave that session
    if connected and _text_matches_active(raw, active_provider, active_model):
        return DisconnectRequest(
            label=raw,
            provider=active_provider,
            model=active_model,
            forget_saved=True,
            clear_keys=True,
        )

    # 2) Whole line is a model id
    if looks_like_model_name(raw) or ("-" in raw and any(c.isdigit() for c in raw)):
        prov = _provider_from_free_text(raw) or infer_provider_from_model(raw)
        req = DisconnectRequest(
            label=raw,
            model=raw,
            provider=prov,
            forget_saved=True,
            clear_keys=bool(prov),
        )
        if connected and active_model and not _text_matches_active(raw, None, active_model):
            req.keys_only = bool(prov)
        return req

    # 3) Resolved provider from free text
    prov = _provider_from_free_text(raw)
    if prov:
        req = DisconnectRequest(
            label=raw,
            provider=prov,
            forget_saved=True,
            clear_keys=True,
        )
        if connected and active_provider and active_provider != prov:
            req.keys_only = True
        return req

    # 4) Connected but name did not match — still disconnect current session
    if connected:
        return DisconnectRequest(
            label=raw,
            provider=active_provider,
            model=active_model,
            forget_saved=True,
            clear_keys=bool(active_provider),
        )

    # 5) Offline and unknown name — best effort clear keys if we guessed a provider
    prov = _provider_from_free_text(raw.split()[0]) if raw.split() else None
    return DisconnectRequest(
        label=raw,
        provider=prov,
        forget_saved=True,
        clear_keys=bool(prov),
    )
