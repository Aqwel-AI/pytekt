"""
Comprehensive unit test suite for PyTekt bots ecosystem, persistence,
testing tools, scheduling, roles, i18n, extensions, and payments.
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path
import pytest

from pytekt.bots import (
    Bot,
    BotDB,
    BotTestClient,
    Context,
    DiscordBot,
    Extension,
    I18nManager,
    Invoice,
    LabeledPrice,
    NotSupportedError,
    RoleRegistry,
    Scheduler,
    TelegramBot,
    UniversalEvent,
    admin_only,
    requires_role,
)
from pytekt.bots.scaffold import generate_project
from pytekt.bots.scheduler import parse_interval_seconds, CronMatcher


# ==============================================================================
# 1. In-Memory Test Client & Event Testing
# ==============================================================================

def test_bot_test_client_commands_and_buttons():
    async def _run():
        bot = TelegramBot(token="123456:TEST_TOKEN")

        @bot.on_command("ping")
        async def handle_ping(ctx: Context):
            await ctx.reply("pong!")

        @bot.on_button("click_me")
        async def handle_btn(ctx: Context):
            await ctx.reply("button was clicked!")

        client = bot.test_client()

        # Send command
        cmd_res = await client.send_command("ping")
        assert len(cmd_res) == 1
        assert cmd_res[0].text == "pong!"
        assert client.last_reply.text == "pong!"

        # Click button
        btn_res = await client.click_button("click_me")
        assert len(btn_res) == 1
        assert btn_res[0].text == "button was clicked!"
        assert client.last_reply.text == "button was clicked!"

        # Assert has_text helper
        assert client.last_reply.has_text("clicked")

        client.clear()
        assert len(client.replies) == 0

    asyncio.run(_run())


# ==============================================================================
# 2. Durable Persistence (BotDB & Persistent FSM)
# ==============================================================================

def test_persistent_fsm_and_bot_db():
    async def _run():
        tmp_db = Path(tempfile.gettempdir()) / "test_bot_fsm.db"
        if tmp_db.exists():
            tmp_db.unlink()

        bot1 = TelegramBot(token="123456:TEST_TOKEN")
        bot1.init_db(f"sqlite:///{tmp_db}")

        @bot1.on_command("login")
        async def handle_login(ctx: Context):
            # Save state persistently
            await ctx.set_state("authenticated", persistent=True)
            await ctx.set_data("username", "neo", persistent=True)
            await ctx.reply("logged in!")

        client1 = bot1.test_client()
        await client1.send_command("login", chat_id="chat_42", user_id="user_7")

        # Simulate full bot restart with a brand new Bot instance pointing to same DB
        bot2 = TelegramBot(token="123456:TEST_TOKEN")
        bot2.init_db(f"sqlite:///{tmp_db}")

        ev = UniversalEvent(id="1", chat_id="chat_42", user_id="user_7", text="check", platform="telegram")
        ctx2 = Context(bot2, ev)

        # Verify state and data survived restart
        restored_state = await ctx2.get_state()
        restored_user = await ctx2.get_data("username")
        assert restored_state == "authenticated"
        assert restored_user == "neo"

        # Verify clearing state
        await ctx2.clear_state()
        assert await ctx2.get_state() == ""

        if tmp_db.exists():
            tmp_db.unlink()

    asyncio.run(_run())


# ==============================================================================
# 3. Scheduler (@bot.every, @bot.cron, and Interval Parsing)
# ==============================================================================

def test_scheduler_interval_and_cron():
    async def _run():
        assert parse_interval_seconds("30s") == 30.0
        assert parse_interval_seconds("15m") == 900.0
        assert parse_interval_seconds("2h") == 7200.0
        assert parse_interval_seconds("1d") == 86400.0
        assert parse_interval_seconds(45) == 45.0

        cron = CronMatcher("*/5 * * * *")
        import datetime
        dt_match = datetime.datetime(2026, 8, 27, 10, 15)
        dt_nomatch = datetime.datetime(2026, 8, 27, 10, 16)
        assert cron.matches(dt_match) is True
        assert cron.matches(dt_nomatch) is False

        bot = TelegramBot(token="123456:TEST_TOKEN")
        counter = {"ticks": 0}

        @bot.every("0.2s")
        def tick_job(b):
            counter["ticks"] += 1

        task = bot.scheduler.start()
        await asyncio.sleep(0.5)
        bot.scheduler.stop()
        assert counter["ticks"] >= 1

    asyncio.run(_run())


# ==============================================================================
# 4. Permissions & Roles (@bot.admin_only, @bot.requires_role)
# ==============================================================================

def test_rbac_roles_and_admin_only():
    async def _run():
        bot = TelegramBot(token="123456:TEST_TOKEN")

        @bot.on_command("ban")
        @bot.admin_only
        async def handle_ban(ctx: Context):
            await ctx.reply("User banned!")

        @bot.on_command("mod_queue")
        @bot.requires_role("moderator")
        async def handle_queue(ctx: Context):
            await ctx.reply("Queue cleared!")

        client = bot.test_client()

        # 1. Regular unauthorized user
        res1 = await client.send_command("ban", chat_id="chat_1", user_id="user_normie")
        assert "Access denied" in res1[0].text

        # 2. Grant admin
        bot.roles.grant("chat_1", "user_normie", "admin")
        assert bot.roles.is_admin("chat_1", "user_normie") is True

        res2 = await client.send_command("ban", chat_id="chat_1", user_id="user_normie")
        assert res2[0].text == "User banned!"

        # 3. Moderator check
        res3 = await client.send_command("mod_queue", chat_id="chat_1", user_id="user_mod")
        assert "Access denied" in res3[0].text

        bot.roles.grant("chat_1", "user_mod", "moderator")
        assert bot.roles.has_role("chat_1", "user_mod", "moderator") is True

        res4 = await client.send_command("mod_queue", chat_id="chat_1", user_id="user_mod")
        assert res4[0].text == "Queue cleared!"

        # 4. Revoke role
        bot.roles.revoke("chat_1", "user_mod", "moderator")
        assert bot.roles.has_role("chat_1", "user_mod", "moderator") is False

    asyncio.run(_run())


# ==============================================================================
# 5. Internationalization (i18n)
# ==============================================================================

def test_i18n_translation_and_fallbacks():
    i18n = I18nManager(default_lang="en")
    i18n.add_translations("en", {
        "welcome": "Welcome, {name}!",
        "menu.help": "Help Menu",
    })
    i18n.add_translations("es", {
        "welcome": "¡Bienvenido, {name}!",
        "menu.help": "Menú de Ayuda",
    })

    # Exact language
    assert i18n.translate("welcome", lang="es", name="Carlos") == "¡Bienvenido, Carlos!"
    # Dot notation
    assert i18n.translate("menu.help", lang="es") == "Menú de Ayuda"
    # Fallback to English
    assert i18n.translate("welcome", lang="fr", name="Jean") == "Welcome, Jean!"
    # Fallback from regional locale 'es-AR' -> 'es'
    assert i18n.translate("menu.help", lang="es-AR") == "Menú de Ayuda"
    # Missing key returns key itself
    assert i18n.translate("non_existent_key", lang="es") == "non_existent_key"


def test_i18n_context_integration():
    async def _run():
        bot = TelegramBot(token="123456:TEST_TOKEN")
        bot.add_translations("es", {"greeting": "Hola, {name}!"})
        bot.add_translations("en", {"greeting": "Hello, {name}!"})

        @bot.on_command("greet")
        async def handle_greet(ctx: Context):
            msg = ctx.t("greeting", name="Maria")
            await ctx.reply(msg)

        client = bot.test_client()

        # Send with Spanish user locale
        res = await client.send_command("greet", metadata={"language_code": "es"})
        assert res[0].text == "Hola, Maria!"

        # Send with English locale
        res_en = await client.send_command("greet", metadata={"language_code": "en"})
        assert res_en[0].text == "Hello, Maria!"

    asyncio.run(_run())


# ==============================================================================
# 6. Plugin & Extension System
# ==============================================================================

def test_bot_extension_system():
    async def _run():
        bot = TelegramBot(token="123456:TEST_TOKEN")

        class MathExtension(Extension):
            @Extension.command("square")
            async def cmd_square(self, ctx: Context):
                val = float(ctx.args[0]) if ctx.args else 2.0
                await ctx.reply(f"Result: {val ** 2}")

            @Extension.on_button("btn_calc")
            async def on_calc_btn(self, ctx: Context):
                await ctx.reply("Calculated!")

        ext = MathExtension(bot)
        bot.add_extension(ext)

        client = bot.test_client()

        # Test extension command
        res1 = await client.send_command("square", args=["5"])
        assert res1[0].text == "Result: 25.0"

        # Test extension button
        res2 = await client.click_button("btn_calc")
        assert res2[0].text == "Calculated!"

    asyncio.run(_run())


# ==============================================================================
# 7. Payments API & Cross-Platform Honesty
# ==============================================================================

def test_telegram_payments_mock_and_discord_error():
    async def _run():
        # Telegram Bot supports invoices
        tg_bot = TelegramBot(token="123456:TEST_TOKEN")

        async def _mock_api(method, payload=None, **kwargs):
            if method == "sendInvoice":
                return {"ok": True, "result": {"message_id": 999, "invoice": payload}}
            return {"ok": True}

        tg_bot._api_call = _mock_api

        client = tg_bot.test_client()
        invoice_resp = await tg_bot.send_invoice(
            chat_id="12345",
            title="Premium Subscription",
            description="1 month premium pass",
            payload="sub_premium_30d",
            provider_token="TEST:STRIPE:123",
            currency="USD",
            prices=[LabeledPrice(label="1 Month", amount=999)],
        )
        assert invoice_resp["ok"] is True
        assert invoice_resp["result"]["invoice"]["currency"] == "USD"

        # Discord Bot raises clear NotSupportedError
        dc_bot = DiscordBot(token="MOCK_DISCORD_TOKEN")
        with pytest.raises(NotSupportedError, match="Payments API is not supported on Discord"):
            await dc_bot.send_invoice(
                chat_id="12345",
                title="Premium",
                description="desc",
                payload="p",
                provider_token="tok",
                currency="USD",
                prices=[LabeledPrice("P", 100)],
            )

    asyncio.run(_run())


# ==============================================================================
# 8. Scaffolding Project Generation
# ==============================================================================

def test_generate_project_scaffolding():
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Default modular layout
        project_dir = generate_project("My Super Bot", platform="telegram", target_dir=temp_dir)
        assert project_dir.is_dir()
        assert (project_dir / "bot" / "main.py").is_file()
        assert (project_dir / "bot" / "config.py").is_file()
        assert (project_dir / "bot" / "handlers" / "commands.py").is_file()
        assert (project_dir / ".env.example").is_file()
        assert (project_dir / "requirements.txt").is_file()
        assert (project_dir / "pyproject.toml").is_file()
        assert (project_dir / "README.md").is_file()
        assert (project_dir / "tests" / "test_handlers.py").is_file()

        # Minimal layout
        min_dir = generate_project("My Min Bot", platform="telegram", target_dir=temp_dir, minimal=True)
        assert (min_dir / "main.py").is_file()
        assert (min_dir / "tests" / "test_bot.py").is_file()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
