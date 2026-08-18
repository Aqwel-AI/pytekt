"""Tests for Gemini response parsing."""

import pytest

from pytekt.providers.gemini_provider import GeminiProvider
from pytekt.providers.errors import ProviderError


def test_extract_text_ok():
    data = {
        "candidates": [
            {
                "content": {"parts": [{"text": "Hello"}]},
                "finishReason": "STOP",
            }
        ]
    }
    assert GeminiProvider._extract_text(data) == "Hello"


def test_extract_text_blocked():
    data = {"candidates": [], "promptFeedback": {"blockReason": "SAFETY"}}
    with pytest.raises(ProviderError, match="blocked"):
        GeminiProvider._extract_text(data)
