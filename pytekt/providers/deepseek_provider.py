"""DeepSeek API (OpenAI-compatible chat/completions)."""

from __future__ import annotations

import os
from typing import Optional

from .generic_openai import OpenAICompatibleProvider

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"


class DeepSeekProvider(OpenAICompatibleProvider):
    """
    Chat via DeepSeek's OpenAI-compatible API.

    Parameters
    ----------
    api_key : str, optional
        Defaults to ``DEEPSEEK_API_KEY``.
    model : str, optional
        Default ``deepseek-chat``. Also: ``deepseek-reasoner``, ``deepseek-coder``.
    base_url : str, optional
        Default ``https://api.deepseek.com/v1``.
    """

    supports_tools: bool = True

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEEPSEEK_BASE_URL,
    ):
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError(
                "DeepSeekProvider requires api_key or DEEPSEEK_API_KEY environment variable"
            )
        super().__init__(base_url=base_url.rstrip("/"), model=model, api_key=key)
