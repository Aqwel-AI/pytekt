"""Tests for slash-command argument parsing."""

from aion.cli_agent.connect_args import (
    looks_like_model_name,
    normalize_company,
    parse_connect_args,
    parse_disconnect_args,
)


def test_parse_connect_ollama_model():
    prov, mod, new_key = parse_connect_args("ollama llama3")
    assert prov == "ollama"
    assert mod == "llama3"
    assert new_key is False


def test_parse_connect_model_only():
    prov, mod, new_key = parse_connect_args("qwen2.5-coder")
    assert prov == "qwen2.5-coder"
    assert mod is None
    assert new_key is False
    assert looks_like_model_name(prov) is True


def test_normalize_company_names():
    assert normalize_company("Ollama") == "ollama"
    assert normalize_company("local") == "ollama"
    assert normalize_company("OpenAI") is None


def test_disconnect_empty_active_session():
    req = parse_disconnect_args(
        "",
        connected=True,
        active_provider="ollama",
        active_model="llama3",
    )
    assert req.provider == "ollama"
    assert req.clear_keys is True
    assert req.keys_only is False


def test_disconnect_model_name():
    req = parse_disconnect_args(
        "llama3",
        connected=True,
        active_provider="ollama",
        active_model="llama3",
    )
    assert req.model == "llama3"
    assert req.keys_only is False


def test_disconnect_other_provider_keys_only():
    req = parse_disconnect_args(
        "openai",
        connected=True,
        active_provider="ollama",
        active_model="llama3",
    )
    assert req.provider == "openai"
    assert req.keys_only is True
