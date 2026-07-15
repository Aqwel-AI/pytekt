"""Tests for connect target resolution."""

from aion.cli_agent.connect import _resolve_connect_target
from aion.cli_agent.connect_args import infer_provider_from_model


def test_infer_nvidia_model_from_slash_id():
    assert infer_provider_from_model("meta/llama-3.3-70b-instruct") == "nvidia"


def test_infer_ollama_model_from_tag():
    assert infer_provider_from_model("llama3:latest") == "ollama"


def test_resolve_connect_nvidia():
    provider, model, rejected = _resolve_connect_target("nvidia", None)
    assert provider == "nvidia"
    assert model is None
    assert rejected is False


def test_resolve_connect_nim_alias():
    provider, model, rejected = _resolve_connect_target("nim", "meta/llama-3.1-8b-instruct")
    assert provider == "nvidia"
    assert model == "meta/llama-3.1-8b-instruct"
    assert rejected is False


def test_resolve_connect_openai_accepted():
    provider, model, rejected = _resolve_connect_target("openai", None)
    assert provider == "openai"
    assert rejected is False


def test_resolve_connect_gemini_accepted():
    provider, model, rejected = _resolve_connect_target("gemini", None)
    assert provider == "gemini"
    assert rejected is False


def test_resolve_connect_claude_alias():
    provider, model, rejected = _resolve_connect_target("claude", "claude-3-5-sonnet-latest")
    assert provider == "anthropic"
    assert model == "claude-3-5-sonnet-latest"
    assert rejected is False
