"""Tests for NVIDIA NIM provider."""

import ssl

import pytest

from pytekt.providers import create_provider, supported_providers
from pytekt.providers.http_utils import get_json, ssl_context
from pytekt.providers.keys import resolve_api_key
from pytekt.providers.nvidia_provider import (
    DEFAULT_MODEL,
    NVIDIA_BASE_URL,
    POPULAR_MODELS,
    RECOMMENDED_CHAT_MODELS,
    NvidiaProvider,
    filter_chat_models,
    is_chat_model,
    prioritize_chat_models,
)


def test_supported_providers_includes_nvidia():
    names = supported_providers()
    assert "nvidia" in names
    assert "nim" in names


def test_resolve_nvidia_from_env(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "test-nvidia-key")
    assert resolve_api_key("nvidia") == "test-nvidia-key"
    assert resolve_api_key("nim") == "test-nvidia-key"


def test_resolve_nvidia_from_config():
    cfg = {"keys": {"nvidia_api_key": "from-config"}}
    assert resolve_api_key("nvidia", cfg) == "from-config"


def test_create_nvidia_provider(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")
    provider = create_provider("nvidia")
    assert isinstance(provider, NvidiaProvider)
    assert provider._model == DEFAULT_MODEL  # noqa: SLF001


def test_create_nvidia_via_nim_alias(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")
    provider = create_provider("nim", model="meta/llama-3.3-70b-instruct")
    assert isinstance(provider, NvidiaProvider)
    assert provider._model == "meta/llama-3.3-70b-instruct"  # noqa: SLF001


def test_nvidia_provider_requires_key(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    with pytest.raises(ValueError, match="NVIDIA_API_KEY"):
        NvidiaProvider()


def test_is_chat_model_filters_embeddings():
    assert not is_chat_model("nvidia/nv-embed-v1")
    assert not is_chat_model("nvidia/llama-3.1-nemotron-nano-8b-v1")
    assert is_chat_model("meta/llama-3.1-8b-instruct")


def test_prioritize_chat_models():
    models = ["z/model", "meta/llama-3.1-8b-instruct", "a/model"]
    ordered = prioritize_chat_models(models)
    assert ordered[0] == "meta/llama-3.1-8b-instruct"
    assert ordered[-1] == "z/model"


def test_filter_chat_models():
    all_models = [
        "meta/llama-3.1-8b-instruct",
        "nvidia/nv-embed-v1",
        "nvidia/llama-3.1-nemotron-nano-8b-v1",
    ]
    chat = filter_chat_models(all_models)
    assert "meta/llama-3.1-8b-instruct" in chat
    assert "nvidia/nv-embed-v1" not in chat
    assert "nvidia/llama-3.1-nemotron-nano-8b-v1" not in chat


def test_list_models_parses_openai_shape(monkeypatch):
    payload = {
        "data": [
            {"id": "meta/llama-3.1-8b-instruct", "object": "model"},
            {"id": "nvidia/nemotron-mini-4b-instruct", "object": "model"},
            {"id": "nvidia/nv-embed-v1", "object": "model"},
        ]
    }

    def fake_get_json(url, *, headers=None, timeout=15.0):
        assert url == f"{NVIDIA_BASE_URL}/models"
        assert headers and headers.get("Authorization") == "Bearer test-key"
        return payload

    monkeypatch.setattr("aion.providers.nvidia_provider.get_json", fake_get_json)
    models = NvidiaProvider.list_models(api_key="test-key")

    assert models[0] == "meta/llama-3.1-8b-instruct"
    assert "nvidia/nemotron-mini-4b-instruct" in models
    assert "nvidia/nv-embed-v1" not in models


def test_list_models_falls_back_when_empty(monkeypatch):
    monkeypatch.setattr(
        "aion.providers.nvidia_provider.get_json",
        lambda *args, **kwargs: {"data": []},
    )
    models = NvidiaProvider.list_models(api_key="test-key")
    assert models == list(POPULAR_MODELS)


def test_ssl_context_returns_context():
    ctx = ssl_context()
    assert isinstance(ctx, ssl.SSLContext)


def test_get_json_live_nvidia_models_endpoint():
    """Smoke test: public models catalog is reachable with proper SSL."""
    data = get_json(f"{NVIDIA_BASE_URL}/models", timeout=20.0)
    assert isinstance(data.get("data"), list)
    assert len(data["data"]) > 0


def test_recommended_models_are_chat_models():
    for model in RECOMMENDED_CHAT_MODELS:
        assert is_chat_model(model)
