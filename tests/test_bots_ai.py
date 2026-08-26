"""
Unit and integration tests for pytekt.bots.ai.
Tests AI class, per-chat rolling memory in C++ cache, tool decorators,
RAG knowledge bases, multimodal methods, moderation, and declarative ai_commands.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pytekt.bots import Bot, Context, TelegramBot
from pytekt.bots.ai import AI
from pytekt.providers import AssistantTurn, ChatMessage, ChatProvider, NormalizedToolCall


class MockChatProvider:
    """Mock Provider for unit testing."""

    def __init__(self, responses=None):
        self.responses = responses or ["Mock assistant reply"]
        self.calls = []

    def complete(self, messages, **kwargs):
        self.calls.append(messages)
        if self.responses:
            return self.responses.pop(0)
        return "Default reply"

    def complete_turn(self, messages, tools=None, **kwargs):
        self.calls.append(messages)
        if self.responses:
            resp = self.responses.pop(0)
            if isinstance(resp, AssistantTurn):
                return resp
            return AssistantTurn(content=str(resp), tool_calls=[])
        return AssistantTurn(content="Default turn reply", tool_calls=[])


def test_ai_ask_and_rolling_memory():
    async def _run():
        mock_p = MockChatProvider(responses=["Hello user!", "I remember you said python."])
        ai = AI(provider="openai", system="You are helpful.")
        ai._provider = mock_p

        # Turn 1
        ans1 = await ai.ask("Hi, I like python", chat_id="chat_123")
        assert ans1 == "Hello user!"

        # Verify history was saved to cache
        history = ai._get_chat_history("chat_123")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hi, I like python"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hello user!"

        # Turn 2
        ans2 = await ai.ask("What do I like?", chat_id="chat_123")
        assert ans2 == "I remember you said python."

        # Verify messages passed to provider in Turn 2 included history
        turn2_messages = mock_p.calls[1]
        assert any(
            (m["content"] if isinstance(m, dict) else getattr(m, "content", "")) == "Hi, I like python"
            for m in turn2_messages
        )

    asyncio.run(_run())


def test_ai_remember_and_forget():
    async def _run():
        ai = AI(provider="openai")
        ai._provider = MockChatProvider()

        await ai.remember("chat_456", "User prefers dark mode")
        await ai.remember("chat_456", "User location is Paris")

        memories = ai.get_memories("chat_456")
        assert "User prefers dark mode" in memories
        assert "User location is Paris" in memories

        await ai.forget("chat_456")
        assert ai.get_memories("chat_456") == []

    asyncio.run(_run())


def test_ai_tool_decorator_and_execution():
    async def _run():
        ai = AI(provider="openai")

        @ai.tool
        def calculate_tax(amount: float, rate: float = 0.2) -> str:
            """Calculate tax on an amount."""
            return f"Tax is {amount * rate:.2f}"

        # Verify schema was generated
        assert len(ai._tool_schemas) == 1
        schema = ai._tool_schemas[0]
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "calculate_tax"
        assert "amount" in schema["function"]["parameters"]["properties"]

        # Test tool invocation via ToolRegistry
        call_res = ai._tool_registry.call("calculate_tax", json.dumps({"amount": 100.0, "rate": 0.15}))
        assert call_res == "Tax is 15.00"

        # Test multi-turn loop with mock provider
        tool_call = NormalizedToolCall(
            id="call_1",
            name="calculate_tax",
            arguments_json=json.dumps({"amount": 200.0, "rate": 0.1}),
        )
        turn1 = AssistantTurn(content=None, tool_calls=[tool_call])
        turn2 = AssistantTurn(content="The calculated tax is 20.00.", tool_calls=[])

        mock_p = MockChatProvider(responses=[turn1, turn2])
        ai._provider = mock_p

        ans = await ai.ask("How much is tax on 200 at 10%?", chat_id="chat_tools")
        assert "20.00" in ans

    asyncio.run(_run())


def test_ai_knowledge_base_rag():
    async def _run():
        ai = AI(provider="openai")
        mock_p = MockChatProvider(responses=["Based on documentation, refunds take 3-5 days."])
        ai._provider = mock_p

        # Index text snippets
        faq_docs = [
            "Refund Policy: All refunds are processed within 3-5 business days.",
            "Shipping Policy: Standard shipping takes 2-4 business days worldwide.",
        ]
        ai.knowledge_base(faq_docs)

        ans = await ai.ask("How long do refunds take?", use_kb=True)
        assert "3-5 days" in ans

        # Verify knowledge base context was injected into system prompt
        last_call = mock_p.calls[-1]
        system_msg = next(
            (m["content"] if isinstance(m, dict) else getattr(m, "content", ""))
            for m in last_call
            if (m.get("role") if isinstance(m, dict) else getattr(m, "role", "")) == "system"
        )
        assert "Refund Policy" in system_msg

    asyncio.run(_run())


def test_ai_moderation():
    async def _run():
        ai = AI(provider="openai")

        # Clean text
        assert await ai.moderate("Hello world, nice to meet you!") is False

        # Toxic / spam keywords
        assert await ai.moderate("buy cheap crypto giveaway telegram.me/joinchat now") is True

    asyncio.run(_run())


def test_ctx_reply_ai_and_ai_commands():
    async def _run():
        bot = Bot(platform="generic")
        mock_p = MockChatProvider(responses=["Summary: User discussed PyTekt bots architecture."])
        ai = AI(provider="openai")
        ai._provider = mock_p

        replies = []

        async def mock_send_message(chat_id, text, **kwargs):
            replies.append((chat_id, text))
            return {"id": "1", "text": text}

        bot.send_message = mock_send_message

        # Declarative ai_commands
        bot.ai_commands(ai, {
            "summarize": "Summarize the discussed topic",
        })

        # Trigger command
        await bot.handle_event({
            "id": "1",
            "chat_id": "c10",
            "user_id": "u10",
            "text": "/summarize PyTekt bots C++ core",
            "event_type": "command",
        })

        assert len(replies) >= 1
        assert "Summary:" in replies[-1][1]

    asyncio.run(_run())
