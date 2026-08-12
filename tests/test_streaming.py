"""Tests for streaming helper on OpenAI-compatible provider."""

from pytekt.providers.generic_openai import OpenAICompatibleProvider


def test_complete_stream_exists():
    p = OpenAICompatibleProvider(base_url="http://localhost:11434/v1", model="x")
    assert hasattr(p, "complete_stream")
