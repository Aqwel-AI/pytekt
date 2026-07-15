"""Tests for provider restriction and command vocabulary."""

from aion.cli_agent.command_vocab import (
    complete_slash_line,
    connect_provider_names,
    suggest_connect_args,
    suggest_slash,
)
from aion.cli_agent.constants import CONNECTABLE_PROVIDERS, DISPLAY_PROVIDERS


def test_cloud_providers_connectable():
    assert CONNECTABLE_PROVIDERS == frozenset(
        {"ollama", "nvidia", "openai", "anthropic", "gemini", "deepseek"}
    )
    assert [pid for pid, _ in DISPLAY_PROVIDERS] == [
        "ollama",
        "nvidia",
        "openai",
        "anthropic",
        "gemini",
        "deepseek",
    ]


def test_suggest_slash_connect():
    assert "connect" in suggest_slash("con")
    assert suggest_slash("con")[0] == "connect"


def test_suggest_connect_providers():
    assert "nvidia" in suggest_connect_args("nv")
    assert set(connect_provider_names()) >= {"ollama", "nvidia"}


def test_complete_slash_line():
    assert "/connect" in complete_slash_line("/con")
    assert any(c.startswith("/connect nvidia") for c in complete_slash_line("/connect nv"))
