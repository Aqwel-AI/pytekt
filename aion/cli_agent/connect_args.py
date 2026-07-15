"""Parse /connect and /disconnect slash-command arguments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

_NEW_KEY_FLAGS = frozenset({"new", "--new-key", "fresh"})
_FORGET_FLAGS = frozenset({"forget", "--forget", "-f"})
_KEYS_FLAGS = frozenset({"keys", "--keys", "key", "remove-keys", "clear-keys"})

# User-facing names → internal provider id (extend as needed).
_COMPANY_ALIASES: Dict[str, str] = {
    "ollama": "ollama",
    "local": "ollama",
    "nvidia": "nvidia",
    "nim": "nvidia",
    "openai": "openai",
    "anthropic": "anthropic",
    "claude": "anthropic",
    "gemini": "gemini",
    "google": "gemini",
    "deepseek": "deepseek",
}


@dataclass
class DisconnectRequest:
    """Result of parsing ``/disconnect <what you name>``."""

    label: str = ""  # what the user typed (for messages)
    provider: Optional[str] = None
    model: Optional[str] = None
    forget_saved: bool = False
    clear_keys: bool = False
    keys_only: bool = False
    disconnect_session: bool = True


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
    if "/" in m and ":" not in m:
        return "nvidia"
    if looks_like_model_name(m):
        return "ollama"
    return None


def looks_like_model_name(text: str) -> bool:
    t = text.lower().strip()
    if not t or t in _COMPANY_ALIASES or t == "ollama":
        return False
    if "-" in t or ":" in t or "." in t or any(c.isdigit() for c in t):
        return True
    return t in {
        "llama",
        "mistral",
        "qwen",
        "phi",
        "gemma",
        "mixtral",
        "codellama",
    }


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


def _split_disconnect_tokens(raw: str) -> Tuple[List[str], bool, bool]:
    """Return (content_tokens, wants_forget, wants_keys)."""
    tokens = raw.split()
    wants_forget = any(t.lower() in _FORGET_FLAGS for t in tokens)
    wants_keys = any(t.lower() in _KEYS_FLAGS for t in tokens)
    content = [t for t in tokens if t.lower() not in _FORGET_FLAGS | _KEYS_FLAGS]
    return content, wants_forget, wants_keys


def parse_disconnect_args(
    args: str,
    *,
    connected: bool = False,
    active_provider: Optional[str] = None,
    active_model: Optional[str] = None,
) -> DisconnectRequest:
    """
    Parse ``/disconnect`` or ``/disconnect <anything>``.

    Default ``/disconnect``: go offline but keep saved provider/model for next startup.
    ``/disconnect forget``: clear saved connection (API keys kept unless ``keys``).
    ``/disconnect nvidia keys``: remove saved API key only.
    """
    raw = args.strip()
    label = raw or (active_provider or "session")

    if not raw:
        return DisconnectRequest(
            label=label,
            provider=active_provider,
            model=active_model,
            forget_saved=False,
            clear_keys=False,
            disconnect_session=True,
        )

    content_tokens, wants_forget, wants_keys = _split_disconnect_tokens(raw)
    content = " ".join(content_tokens).strip()
    label = content or raw

    # keys-only: /disconnect keys nvidia  or  /disconnect nvidia keys
    if wants_keys and not content:
        if connected and active_provider:
            return DisconnectRequest(
                label=active_provider,
                provider=active_provider,
                model=active_model,
                forget_saved=False,
                clear_keys=True,
                keys_only=True,
                disconnect_session=False,
            )
        return DisconnectRequest(
            label=raw,
            forget_saved=False,
            clear_keys=False,
            keys_only=False,
            disconnect_session=False,
        )

    if wants_keys and content:
        prov = _provider_from_free_text(content)
        if not prov and content_tokens:
            prov = _provider_from_free_text(content_tokens[0])
        if prov:
            keys_only = bool(
                connected
                and active_provider
                and active_provider != prov
            )
            return DisconnectRequest(
                label=content,
                provider=prov,
                forget_saved=wants_forget,
                clear_keys=True,
                keys_only=keys_only,
                disconnect_session=not keys_only,
            )

    if wants_forget and not content:
        return DisconnectRequest(
            label=label,
            provider=active_provider,
            model=active_model,
            forget_saved=True,
            clear_keys=False,
            disconnect_session=True,
        )

    if not content:
        return DisconnectRequest(
            label=label,
            provider=active_provider,
            model=active_model,
            forget_saved=wants_forget,
            clear_keys=False,
            disconnect_session=True,
        )

    # Match active session by name
    if connected and _text_matches_active(content, active_provider, active_model):
        return DisconnectRequest(
            label=content,
            provider=active_provider,
            model=active_model,
            forget_saved=wants_forget,
            clear_keys=False,
            disconnect_session=True,
        )

    # Model id
    if looks_like_model_name(content) or ("-" in content and any(c.isdigit() for c in content)):
        prov = _provider_from_free_text(content) or infer_provider_from_model(content)
        keys_only = bool(
            connected
            and active_model
            and not _text_matches_active(content, None, active_model)
        )
        return DisconnectRequest(
            label=content,
            model=content,
            provider=prov,
            forget_saved=wants_forget,
            clear_keys=False,
            keys_only=keys_only,
            disconnect_session=not keys_only,
        )

    # Provider name
    prov = _provider_from_free_text(content)
    if prov:
        keys_only = bool(connected and active_provider and active_provider != prov)
        return DisconnectRequest(
            label=content,
            provider=prov,
            forget_saved=wants_forget,
            clear_keys=False,
            keys_only=keys_only,
            disconnect_session=not keys_only,
        )

    # Unknown name while connected — disconnect current session
    if connected:
        return DisconnectRequest(
            label=content,
            provider=active_provider,
            model=active_model,
            forget_saved=wants_forget,
            clear_keys=False,
            disconnect_session=True,
        )

    # Offline — best effort key clear if we guessed a provider
    prov = _provider_from_free_text(content_tokens[0]) if content_tokens else None
    return DisconnectRequest(
        label=content,
        provider=prov,
        forget_saved=False,
        clear_keys=bool(prov),
        keys_only=bool(prov),
        disconnect_session=False,
    )
