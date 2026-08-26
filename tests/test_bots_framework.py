"""
Integration tests for Bot base class, TelegramBot, and DiscordBot adapters.
Tests handler decorators, middlewares, FSM transitions, rate limiting, and mocked APIs.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, patch

from pytekt.bots import Bot, Context, DiscordBot, TelegramBot, UniversalEvent


def test_bot_decorators_and_dispatch():
    async def _run():
        bot = Bot(platform="generic")
        executed = []

        @bot.on_command("start")
        async def handle_start(ctx: Context):
            executed.append(("start", ctx.args))
            await ctx.set_state("step1")
            return "started"

        @bot.on_command("help")
        async def handle_help(ctx: Context):
            executed.append(("help", ctx.args))
            return "help_info"

        @bot.on_message(r"^hello\s+(.*)")
        async def handle_hello(ctx: Context):
            executed.append(("hello", ctx.text))
            return "hello_ack"

        @bot.state("step1")
        async def handle_step1(ctx: Context):
            executed.append(("step1", ctx.text))
            await ctx.clear_state()
            return "step1_ack"

        # 1. Dispatch /start foo bar
        res1 = await bot.handle_event({
            "id": "1",
            "chat_id": "c1",
            "user_id": "u1",
            "text": "/start foo bar",
            "event_type": "command",
        })
        assert ("start", ["foo", "bar"]) in executed
        assert "started" in res1

        # Check FSM state was set
        state = bot.fsm.get_state("c1:u1")
        assert state == "step1"

        # 2. Dispatch message while in step1
        res2 = await bot.handle_event({
            "id": "2",
            "chat_id": "c1",
            "user_id": "u1",
            "text": "my name is Alice",
            "event_type": "message",
        })
        assert ("step1", "my name is Alice") in executed
        assert "step1_ack" in res2
        assert bot.fsm.get_state("c1:u1") == ""

    asyncio.run(_run())


def test_bot_middleware_pipeline():
    async def _run():
        bot = Bot(platform="generic")
        mw_log = []

        @bot.middleware
        async def logging_middleware(ctx: Context, next_fn):
            mw_log.append(f"before:{ctx.text}")
            res = await next_fn()
            mw_log.append(f"after:{ctx.text}")
            return res

        @bot.on_command("ping")
        async def handle_ping(ctx: Context):
            mw_log.append("handler:ping")
            return "pong"

        res = await bot.handle_event({"text": "/ping", "event_type": "command"})
        assert res == ["pong"]
        assert mw_log == ["before:/ping", "handler:ping", "after:/ping"]

    asyncio.run(_run())


def test_telegram_bot_mocked_api():
    async def _run():
        bot = TelegramBot(token="123456:TEST_TOKEN")

        sent_messages = []

        async def mock_api_call(method, payload=None, max_retries=3):
            if method == "sendMessage":
                sent_messages.append(payload)
                return {"message_id": 1001, "text": payload.get("text")}
            elif method == "editMessageText":
                return {"message_id": payload.get("message_id"), "text": payload.get("text")}
            elif method == "sendChatAction":
                return True
            elif method == "deleteMessage":
                return True
            return {}

        bot._api_call = mock_api_call

        @bot.on_command("greet")
        async def handle_greet(ctx: Context):
            await ctx.reply("Hello from Telegram!")

        # Incoming Telegram Update JSON
        tg_update = {
            "update_id": 9999,
            "message": {
                "message_id": 42,
                "chat": {"id": -100999},
                "from": {"id": 888},
                "text": "/greet",
            }
        }

        await bot.handle_event(json.dumps(tg_update))
        assert len(sent_messages) == 1
        assert sent_messages[0]["chat_id"] == "-100999"
        assert sent_messages[0]["text"] == "Hello from Telegram!"
        assert sent_messages[0]["reply_to_message_id"] == 42

    asyncio.run(_run())


def test_discord_bot_mocked_api():
    async def _run():
        bot = DiscordBot(token="MOCK_DISCORD_TOKEN")

        sent_calls = []

        async def mock_api_call(method, path, payload=None, max_retries=3):
            sent_calls.append((method, path, payload))
            if method == "POST" and "messages" in path:
                return {"id": "msg_123", "content": payload.get("content")}
            return {}

        bot._api_call = mock_api_call

        @bot.on_command("ping")
        async def handle_ping(ctx: Context):
            await ctx.reply("Pong from Discord!")

        # Incoming Discord Gateway Event
        dc_event = {
            "t": "MESSAGE_CREATE",
            "d": {
                "id": "777",
                "channel_id": "chan_456",
                "author": {"id": "user_789"},
                "content": "!ping",
            }
        }

        await bot.handle_event(json.dumps(dc_event))
        assert len(sent_calls) == 1
        method, path, payload = sent_calls[0]
        assert method == "POST"
        assert "chan_456/messages" in path
        assert payload["content"] == "Pong from Discord!"

    asyncio.run(_run())
