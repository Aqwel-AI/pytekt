"""Unit tests for pytekt.bots.slack.SlackBot adapter."""

import asyncio
import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock, patch

import pytest

from pytekt.bots.slack import SlackBot


@pytest.fixture
def slack_bot():
    return SlackBot(token="xoxb-test-mock-token-12345", signing_secret="secret_abc123")


def test_slack_bot_init_and_repr(slack_bot):
    assert slack_bot.platform == "slack"
    assert "xoxb-t***" in repr(slack_bot)


def test_slack_bot_requires_token(monkeypatch):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    with pytest.raises(ValueError, match="requires a bot token"):
        SlackBot(token="")


def test_verify_signature(slack_bot):
    ts = str(int(time.time()))
    body = b'{"type":"url_verification"}'
    sig_basestring = f"v0:{ts}:".encode("utf-8") + body
    valid_sig = "v0=" + hmac.new(
        b"secret_abc123", sig_basestring, hashlib.sha256
    ).hexdigest()

    assert slack_bot.verify_signature(ts, body, valid_sig) is True
    assert slack_bot.verify_signature(ts, body, "v0=invalid_sig") is False
    # Timestamp drift > 300s
    old_ts = str(int(time.time()) - 400)
    assert slack_bot.verify_signature(old_ts, body, valid_sig) is False


def test_parse_url_verification(slack_bot):
    payload = {"type": "url_verification", "challenge": "test_challenge_token_456"}
    event = slack_bot.parse_webhook_payload(payload)
    assert event is not None
    assert event.id == "url_verification"
    assert event.text == "test_challenge_token_456"


def test_parse_events_api_message(slack_bot):
    payload = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "user": "U12345",
            "channel": "C67890",
            "text": "Hello bot!",
            "ts": "1700000000.000100",
        },
    }
    event = slack_bot.parse_webhook_payload(payload)
    assert event is not None
    assert event.event_type == "message"
    assert event.user_id == "U12345"
    assert event.chat_id == "C67890"
    assert event.text == "Hello bot!"


def test_parse_events_api_command(slack_bot):
    payload = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "user": "U12345",
            "channel": "C67890",
            "text": "/stats daily",
            "ts": "1700000000.000200",
        },
    }
    event = slack_bot.parse_webhook_payload(payload)
    assert event is not None
    assert event.event_type == "command"
    assert event.command == "stats"


def test_parse_slash_command_form(slack_bot):
    raw_body = b"command=%2Fhelp&text=topics&user_id=U999&channel_id=C888"
    event = slack_bot.parse_webhook_payload(raw_body)
    assert event is not None
    assert event.event_type == "command"
    assert event.command == "help"
    assert event.user_id == "U999"
    assert event.chat_id == "C888"
    assert "/help topics" in event.text


def test_parse_block_action(slack_bot):
    payload = {
        "type": "block_actions",
        "user": {"id": "U777"},
        "channel": {"id": "C777"},
        "actions": [{"action_id": "btn_confirm", "value": "confirmed"}],
        "message": {"ts": "1700000000.000300"},
    }
    event = slack_bot.parse_webhook_payload(payload)
    assert event is not None
    assert event.event_type == "callback"
    assert event.user_id == "U777"
    assert event.chat_id == "C777"
    assert event.text == "confirmed"
    assert event.metadata.get("action_id") == "btn_confirm"


@pytest.mark.anyio
async def test_handle_webhook_url_verification(slack_bot):
    payload = json.dumps({"type": "url_verification", "challenge": "secret_token"})
    res = await slack_bot.handle_webhook_payload(payload)
    assert res == {"challenge": "secret_token"}


@pytest.mark.anyio
async def test_handle_webhook_dispatch(slack_bot):
    received = []

    @slack_bot.on_command("ping")
    async def on_ping(ctx):
        received.append(ctx.text)
        await ctx.reply("pong")

    with patch.object(slack_bot, "_api_call", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = {"ok": True, "ts": "1700000000.000999"}
        payload = {
            "type": "event_callback",
            "event": {
                "type": "message",
                "user": "U111",
                "channel": "C222",
                "text": "/ping",
                "ts": "1700000000.000400",
            },
        }
        res = await slack_bot.handle_webhook_payload(json.dumps(payload))
        assert res == {"ok": True}
        assert len(received) == 1
        mock_api.assert_called_once()
        call_args = mock_api.call_args[0]
        assert call_args[0] == "chat.postMessage"
        assert call_args[1]["text"] == "pong"
        assert call_args[1]["channel"] == "C222"


@pytest.mark.anyio
async def test_send_edit_delete_message(slack_bot):
    with patch.object(slack_bot, "_api_call", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = {"ok": True, "ts": "123.456"}

        # Send
        await slack_bot.send_message("C123", "hi")
        mock_api.assert_called_with("chat.postMessage", {"channel": "C123", "text": "hi"})

        # Edit
        await slack_bot.edit_message_text("C123", "123.456", "edited")
        mock_api.assert_called_with("chat.update", {"channel": "C123", "ts": "123.456", "text": "edited"})

        # Delete
        await slack_bot.delete_message("C123", "123.456")
        mock_api.assert_called_with("chat.delete", {"channel": "C123", "ts": "123.456"})
