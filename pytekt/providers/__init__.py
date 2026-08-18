"""
Remote LLM providers (OpenAI, Gemini, Anthropic, OpenAI-compatible servers).

Use these classes to call vendor chat APIs from your own scripts or services.
API keys are read from arguments or standard environment variables.
See ``pytekt/providers/README.md`` for a full layout and API summary.

Examples
--------
>>> from pytekt.providers import OpenAIProvider
>>> from pytekt.providers.base import ChatMessage
>>> p = OpenAIProvider()  # OPENAI_API_KEY
>>> p.complete([ChatMessage(role="user", content="Say hi in one word.")])

Environment variables
---------------------
- ``OPENAI_API_KEY`` — OpenAI
- ``GEMINI_API_KEY`` or ``GOOGLE_API_KEY`` — Gemini
- ``ANTHROPIC_API_KEY`` — Anthropic
- ``DEEPSEEK_API_KEY`` — DeepSeek
- ``NVIDIA_API_KEY`` — NVIDIA NIM
"""

from .anthropic_provider import AnthropicProvider
from .deepseek_provider import DeepSeekProvider
from .base import ChatMessage, ChatProvider
from .errors import ProviderError
from .factory import create_provider, supported_providers
from .gemini_provider import GeminiProvider
from .generic_openai import OpenAICompatibleProvider
from .nvidia_provider import NvidiaProvider
from .openai_provider import OpenAIProvider
from .structured import AssistantTurn, NormalizedToolCall, parse_chat_completion_response

__all__ = [
    "AnthropicProvider",
    "AssistantTurn",
    "ChatMessage",
    "ChatProvider",
    "DeepSeekProvider",
    "GeminiProvider",
    "NvidiaProvider",
    "OpenAIProvider",
    "NormalizedToolCall",
    "OpenAICompatibleProvider",
    "parse_chat_completion_response",
    "ProviderError",
    "create_provider",
    "supported_providers",
]
