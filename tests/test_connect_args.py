"""Tests for slash-command argument parsing."""

from aion.cli_agent.connect_args import (
    normalize_company,
    parse_connect_args,
    parse_disconnect_args,
)


def test_parse_connect_new_key():
    prov, mod, new_key = parse_connect_args("gemini new")
    assert prov == "gemini"
    assert mod is None
    assert new_key is True


def test_parse_connect_model():
    prov, mod, new_key = parse_connect_args("openai gpt-4o")
    assert prov == "openai"
    assert mod == "gpt-4o"
    assert new_key is False


def test_normalize_company_names():
    assert normalize_company("OpenAI") == "openai"
    assert normalize_company("Google") == "gemini"


def test_disconnect_empty_active_session():
    req = parse_disconnect_args(
        "",
        connected=True,
        active_provider="gemini",
        active_model="gemini-2.0-flash",
    )
    assert req.provider == "gemini"
    assert req.clear_keys is True
    assert req.keys_only is False


def test_disconnect_free_text_matches_active():
    req = parse_disconnect_args(
        "google flash",
        connected=True,
        active_provider="gemini",
        active_model="gemini-2.0-flash",
    )
    assert req.keys_only is False
    assert req.provider == "gemini"


def test_disconnect_model_name():
    req = parse_disconnect_args(
        "gemini-2.0-flash",
        connected=True,
        active_provider="gemini",
        active_model="gemini-2.0-flash",
    )
    assert req.model == "gemini-2.0-flash"
    assert req.keys_only is False


def test_disconnect_other_provider_keys_only():
    req = parse_disconnect_args(
        "openai",
        connected=True,
        active_provider="gemini",
        active_model="gemini-2.0-flash",
    )
    assert req.provider == "openai"
    assert req.keys_only is True


def test_disconnect_unknown_still_leaves_active_session():
    req = parse_disconnect_args(
        "my backup ai",
        connected=True,
        active_provider="gemini",
        active_model="gemini-2.0-flash",
    )
    assert req.provider == "gemini"
    assert req.keys_only is False
