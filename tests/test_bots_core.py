"""
Unit tests for pytekt.bots core components:
Dispatcher, RateLimiter, FSM, Cache, WebhookServer, AntiSpam, Metrics, UniversalEvent.
Tests both the compiled C++ native module and the pure-Python fallback for exact parity.
"""

import json
import time
import pytest

from pytekt.bots import _core as native_core
import pytekt.bots._core_fallback as fallback_core


@pytest.mark.parametrize("core_mod", [native_core, fallback_core])
def test_universal_event_basics(core_mod):
    EventCls = core_mod.UniversalEvent
    ev = EventCls(
        id="101",
        chat_id="chat_999",
        user_id="user_123",
        text="/start with args",
        platform="telegram",
        event_type="command",
        command="start",
        args=["with", "args"],
    )
    assert ev.id == "101"
    assert ev.chat_id == "chat_999"
    assert ev.user_id == "user_123"
    assert ev.text == "/start with args"
    assert ev.platform == "telegram"
    assert ev.event_type == "command"
    assert ev.command == "start"
    assert ev.args == ["with", "args"]
    assert "UniversalEvent" in repr(ev)


@pytest.mark.parametrize("core_mod", [native_core, fallback_core])
def test_dispatcher_routing(core_mod):
    DispatcherCls = core_mod.Dispatcher
    EventCls = core_mod.UniversalEvent
    d = DispatcherCls()

    d.add_command_handler("start", "h_start")
    d.add_command_handler("/help", "h_help")
    d.add_pattern_handler(r"^echo\s+(.*)", "h_echo")
    d.add_event_handler("voice", "h_voice")
    d.add_event_handler("photo", "h_photo")
    d.add_state_handler("awaiting_email", "h_state_email")

    # 1. Command match
    ev1 = EventCls(command="start", event_type="command", text="/start")
    assert "h_start" in d.match(ev1)

    # 2. Pattern match
    ev2 = EventCls(text="echo hello world", event_type="message")
    assert "h_echo" in d.match(ev2)

    # 3. Voice match
    ev3 = EventCls(event_type="voice")
    assert "h_voice" in d.match(ev3)

    # 4. State match
    ev4 = EventCls(text="test@example.com", event_type="message")
    assert "h_state_email" in d.match(ev4, current_state="awaiting_email")


@pytest.mark.parametrize("core_mod", [native_core, fallback_core])
def test_dispatcher_parsers(core_mod):
    d = core_mod.Dispatcher()

    # Telegram parser test
    tg_payload = json.dumps({
        "update_id": 5555,
        "message": {
            "message_id": 12345,
            "from": {"id": 9999, "username": "alice", "first_name": "Alice"},
            "chat": {"id": -100123, "type": "supergroup"},
            "text": "/ban @bob spamming",
        }
    })
    ev_tg = d.parse_telegram(tg_payload)
    assert ev_tg.platform == "telegram"
    assert ev_tg.chat_id == "-100123"
    assert ev_tg.user_id == "9999"
    assert ev_tg.command == "ban"
    assert "@bob" in ev_tg.args
    assert "spamming" in ev_tg.args
    assert ev_tg.metadata.get("username") == "alice"

    # Discord parser test
    discord_payload = json.dumps({
        "t": "MESSAGE_CREATE",
        "d": {
            "id": "8888",
            "channel_id": "7777",
            "author": {"id": "6666", "username": "charlie"},
            "content": "!roll 20",
        }
    })
    ev_dc = d.parse_discord(discord_payload)
    assert ev_dc.platform == "discord"
    assert ev_dc.chat_id == "7777"
    assert ev_dc.user_id == "6666"
    assert ev_dc.command == "roll"
    assert "20" in ev_dc.args


@pytest.mark.parametrize("core_mod", [native_core, fallback_core])
def test_rate_limiter(core_mod):
    RateLimiterCls = core_mod.RateLimiter
    rl = RateLimiterCls()

    # Test parse_rate
    ok, cap, win = rl.parse_rate("5/10s")
    assert ok is True
    assert cap == 5.0
    assert win == 10.0

    ok2, cap2, win2 = rl.parse_rate("20/1m")
    assert ok2 is True
    assert cap2 == 20.0
    assert win2 == 60.0

    rl.set_rule("user", "2/1s")

    # Acquire tokens
    assert rl.acquire("user:u1", 1.0) is True
    assert rl.acquire("user:u1", 1.0) is True
    # 3rd request exceeds capacity
    allowed, retry_after = rl.check("user:u1", 1.0)
    assert allowed is False
    assert retry_after > 0.0

    # Multi-scope check_and_acquire
    rl.set_rule("chat", "10/1s")
    allowed_multi, _ = rl.check_and_acquire(user_id="u2", chat_id="c1", tokens=1.0)
    assert allowed_multi is True

    # 429 backoff
    rl.record_429("api", 0.5)
    assert rl.get_retry_after("api") > 0.0


@pytest.mark.parametrize("core_mod", [native_core, fallback_core])
def test_fsm_and_ttl(core_mod):
    FSMCls = core_mod.FSM
    fsm = FSMCls()

    # Set and get state
    fsm.set_state("user:10", "awaiting_name", ttl_seconds=0.2)
    assert fsm.get_state("user:10") == "awaiting_name"

    # Set and get data
    fsm.set_data("user:10", "age", "25", ttl_seconds=0.2)
    assert fsm.get_data("user:10", "age") == "25"
    assert fsm.get_all_data("user:10") == {"age": "25"}

    # Clear state
    fsm.clear_state("user:10")
    assert fsm.get_state("user:10") == ""
    assert fsm.get_data("user:10", "age") == "25"

    # Expiry
    fsm.set_state("user:20", "step1", ttl_seconds=0.05)
    time.sleep(0.08)
    assert fsm.get_state("user:20") == ""


@pytest.mark.parametrize("core_mod", [native_core, fallback_core])
def test_cache_ttl(core_mod):
    CacheCls = core_mod.Cache
    cache = CacheCls()

    cache.set("session_1", "active_data", ttl_seconds=0.1)
    assert cache.has("session_1") is True
    assert cache.get("session_1") == "active_data"

    time.sleep(0.15)
    assert cache.has("session_1") is False
    assert cache.get("session_1") == ""

    cache.set("perm", "value", ttl_seconds=0.0)
    assert cache.get("perm") == "value"
    assert cache.delete("perm") is True
    assert cache.has("perm") is False


@pytest.mark.parametrize("core_mod", [native_core, fallback_core])
def test_antispam_and_scoring(core_mod):
    AntiSpamCls = core_mod.AntiSpam
    aspam = AntiSpamCls(bloom_size=1024, window_seconds=10.0)

    # Duplicate check
    assert aspam.is_duplicate("Hello everyone!", "user_1") is False
    aspam.add("Hello everyone!", "user_1")
    assert aspam.is_duplicate("Hello everyone!", "user_1") is True
    assert aspam.is_duplicate("Different message", "user_1") is False

    # Spam scoring
    clean_score = aspam.calculate_score("Hey, how is it going today?", message_rate=0.5, duplicate_count=0)
    assert clean_score < 0.3

    spam_text = "FREE CRYPTO AIRDROP!!! JOIN https://t.me/fake https://t.me/fake2 https://t.me/fake3 @everyone @admin"
    spam_score = aspam.calculate_score(spam_text, message_rate=6.0, duplicate_count=4)
    assert spam_score > 0.7
    assert aspam.is_spam(spam_text, threshold=0.6, message_rate=6.0) is True


@pytest.mark.parametrize("core_mod", [native_core, fallback_core])
def test_metrics_prometheus(core_mod):
    MetricsCls = core_mod.Metrics
    m = MetricsCls()

    m.increment_counter("bot_messages_total", 5.0, {"platform": "telegram"})
    m.record_latency("start", 0.02)
    m.record_latency("help", 0.15)

    prom_text = m.export_prometheus()
    assert "bot_messages_total" in prom_text
    assert "bot_command_latency_seconds" in prom_text
    assert "bot_command_calls_total" in prom_text
