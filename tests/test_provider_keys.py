"""Tests for provider API key resolution."""

import os

from pytekt.providers.keys import resolve_api_key


def test_resolve_gemini_from_google_env(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    assert resolve_api_key("gemini") == "test-google-key"


def test_resolve_gemini_from_config_aliases():
    cfg = {"keys": {"google_api_key": "from-config"}}
    assert resolve_api_key("gemini", cfg) == "from-config"
