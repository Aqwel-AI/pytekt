"""Tests for user-friendly provider error messages."""

from aion.providers.errors import ProviderError


def test_friendly_429_quota():
    body = """{
      "error": {
        "message": "You exceeded your current quota.\\n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash\\nPlease retry in 25.6s."
      }
    }"""
    err = ProviderError("HTTP 429: Too Many Requests", status=429, body=body)
    msg = err.friendly_message()
    assert "usage limit" in msg.lower()
    assert "gemini-2.0-flash" in msg
    assert "25 seconds" in msg
    assert "/connect ollama" in msg
    assert "HTTP 429" not in msg


def test_friendly_401():
    err = ProviderError("HTTP 401", status=401, body='{"error":{"message":"Invalid API key"}}')
    assert "API key" in err.friendly_message()
    assert "HTTP 401" not in err.friendly_message()
