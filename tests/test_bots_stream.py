"""
Unit and integration tests for C++ StreamPacer and ctx.stream() in pytekt.bots.
Tests token accumulation, adaptive rate pacing, semantic boundary flushing,
message length splitting, 429 backoff, and BotTestClient integration.
"""

import asyncio
import time
import pytest

from pytekt.bots import Bot, Context, DiscordBot, TelegramBot, StreamPacer, PacerDecision
from pytekt.bots._core_fallback import StreamPacer as FallbackStreamPacer
from pytekt.bots.testing import BotTestClient


def test_stream_pacer_semantic_boundaries():
    # Test boundary detection
    assert StreamPacer.is_semantic_boundary("Hello world.\n") is True
    assert StreamPacer.is_semantic_boundary("This is a sentence. ") is True
    assert StreamPacer.is_semantic_boundary("Warning! ") is True
    assert StreamPacer.is_semantic_boundary("What? ") is True
    assert StreamPacer.is_semantic_boundary("Paragraph\n\n") is True
    assert StreamPacer.is_semantic_boundary("code block```") is True
    assert StreamPacer.is_semantic_boundary("incomplete sent") is False


def test_stream_pacer_pacing_and_cursor():
    pacer = StreamPacer(min_interval=0.5, max_interval=1.0, min_delta_chars=5, cursor=" ▍")

    # Feed small fragment at t=1.0 -> should flush on first chunk
    d1 = pacer.feed("Hello ", current_time=1.0)
    assert d1.should_flush is True
    assert "Hello " in d1.text_with_cursor
    assert d1.text_with_cursor.endswith(" ▍")
    assert d1.text_final == "Hello "

    # Feed immediately at t=1.1 (only 0.1s elapsed, interval 0.5s not met)
    d2 = pacer.feed("world", current_time=1.1)
    assert d2.should_flush is False

    # Feed boundary at t=1.6 (0.6s elapsed >= 0.5s min_interval)
    d3 = pacer.feed("!\n", current_time=1.6)
    assert d3.should_flush is True
    assert d3.text_final == "Hello world!\n"
    assert d3.text_with_cursor == "Hello world!\n ▍"

    # Final flush removes cursor
    final_text = pacer.flush_final()
    assert final_text == "Hello world!\n"


def test_stream_pacer_max_length_splitting():
    # Set a tiny max_length=30 to test automatic multi-message pagination
    pacer = StreamPacer(min_interval=0.1, min_delta_chars=1, max_length=30)

    # First chunk: fits
    d1 = pacer.feed("Hello world! ", current_time=1.0)
    assert d1.should_flush is True
    assert d1.needs_new_message is False

    # Second chunk: causes total length to exceed 30
    d2 = pacer.feed("This is a very long response that exceeds the limit.", current_time=1.2)
    assert d2.should_flush is True
    assert d2.needs_new_message is True
    assert len(d2.text_final) <= 30
    assert len(d2.overflow_text) > 0


def test_stream_pacer_429_backoff():
    pacer = StreamPacer(min_interval=0.2, min_delta_chars=2)
    pacer.feed("First chunk. ", current_time=1.0)

    # Simulate platform 429 retry after 3 seconds
    pacer.record_429(3.0, current_time=1.1)
    assert pacer.get_retry_after(current_time=1.5) > 0.0

    # Feeding while backoff is active should NOT flush
    d = pacer.feed("Another chunk.\n", current_time=2.0)
    assert d.should_flush is False

    # Once backoff expires at t=4.2
    assert pacer.get_retry_after(current_time=4.2) == 0.0
    d_expired = pacer.feed("Now expired.\n", current_time=4.2)
    assert d_expired.should_flush is True


def test_stream_pacer_metrics_and_fallback_parity():
    # Verify fallback parity
    for PacerCls in (StreamPacer, FallbackStreamPacer):
        p = PacerCls(min_interval=0.5, min_delta_chars=5)
        for i in range(10):
            p.feed(f"chunk{i} ", current_time=1.0 + i * 0.1)
        metrics = p.get_metrics()
        assert metrics["total_chunks"] == 10.0
        assert metrics["flush_count"] >= 1.0
        assert metrics["edits_avoided"] >= 0.0


def test_ctx_stream_with_test_client():
    async def _run():
        bot = Bot(platform="telegram")
        client = BotTestClient(bot)

        # Define an async generator yielding tokens
        async def sample_tokens():
            tokens = ["Deep ", "learning ", "models ", "converge ", "rapidly.\n", "Next ", "sentence."]
            for t in tokens:
                yield t
                await asyncio.sleep(0.01)

        @bot.on_command("generate")
        async def handle_generate(ctx: Context):
            await ctx.stream(sample_tokens(), min_interval=0.01, min_delta_chars=1)

        # Run command
        responses = await client.send_command("generate", chat_id="chat_42", user_id="user_1")

        # Should have recorded initial sendMessage and subsequent editMessageText calls
        assert len(responses) >= 2
        assert responses[0].method == "sendMessage"
        assert any(r.method == "editMessageText" for r in responses)

        # Final response must have the full text without trailing cursor
        last_resp = client.last_reply
        assert "Deep learning models converge rapidly.\nNext sentence." in last_resp.text
        assert " ▍" not in last_resp.text

    asyncio.run(_run())


def test_ctx_stream_length_splitting_with_test_client():
    async def _run():
        bot = Bot(platform="discord")
        client = BotTestClient(bot)

        async def long_stream():
            yield "Paragraph 1: A quick brown fox jumps over the lazy dog.\n\n"
            yield "Paragraph 2: The second paragraph is also quite informative and long."

        @bot.on_command("story")
        async def handle_story(ctx: Context):
            await ctx.stream(long_stream(), min_interval=0.01, min_delta_chars=1, max_length=40)

        responses = await client.send_command("story", chat_id="channel_9", user_id="user_1")

        # Because max_length=40 is exceeded, it must have sent multiple messages (sendMessage called > 1)
        send_msgs = [r for r in responses if r.method == "sendMessage"]
        assert len(send_msgs) >= 2

    asyncio.run(_run())


def test_ctx_reply_ai_streaming():
    from pytekt.bots.ai import AI

    class DummyProvider:
        def complete(self, messages, **kwargs):
            return "This is a streamed reply from AI assistant."

    async def _run():
        bot = Bot(platform="telegram")
        client = BotTestClient(bot)

        ai = AI(provider="openai")
        ai._provider = DummyProvider()

        @bot.on_command("ask")
        async def handle_ask(ctx: Context):
            await ctx.reply_ai(ai, prompt="What is PyTekt?")

        responses = await client.send_command("ask", chat_id="chat_77", user_id="user_1")
        assert len(responses) >= 2
        last_resp = client.last_reply
        assert "streamed reply from AI assistant" in last_resp.text
        assert " ▍" not in last_resp.text

    asyncio.run(_run())

