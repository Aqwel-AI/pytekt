"""
Unit and integration tests for pytekt.bots.ui.
Tests Button, Keyboard, Card, Modal, and Wizard compilation to Telegram and Discord payloads,
graceful degradation, and context integration.
"""

import asyncio
import json
import pytest

from pytekt.bots import Bot, Context, DiscordBot, TelegramBot
from pytekt.bots.ui import (
    Button,
    Card,
    Keyboard,
    Modal,
    ModalField,
    Wizard,
    WizardStep,
)


def test_button_and_keyboard_compilation():
    # 1. Telegram compilation
    kb = Keyboard([
        [("Primary", "btn_1"), Button("Link", url="https://aqwelai.xyz")],
        [Keyboard.web_app_button("Launch Mini-App", "https://app.aqwelai.xyz")],
    ])

    tg_payload = kb.to_telegram()
    assert "inline_keyboard" in tg_payload
    rows = tg_payload["inline_keyboard"]
    assert len(rows) == 2
    assert rows[0][0]["text"] == "Primary"
    assert rows[0][0]["callback_data"] == "btn_1"
    assert rows[0][1]["text"] == "Link"
    assert rows[0][1]["url"] == "https://aqwelai.xyz"
    assert rows[1][0]["text"] == "Launch Mini-App"
    assert rows[1][0]["web_app"]["url"] == "https://app.aqwelai.xyz"

    # 2. Discord compilation
    dc_payload = kb.to_discord()
    assert isinstance(dc_payload, list)
    assert len(dc_payload) == 2
    assert dc_payload[0]["type"] == 1  # ActionRow
    comps = dc_payload[0]["components"]
    assert comps[0]["type"] == 2  # Button
    assert comps[0]["label"] == "Primary"
    assert comps[0]["style"] == 1  # Primary blurple
    assert comps[0]["custom_id"] == "btn_1"

    assert comps[1]["type"] == 2
    assert comps[1]["label"] == "Link"
    assert comps[1]["style"] == 5  # Link style
    assert comps[1]["url"] == "https://aqwelai.xyz"

    assert dc_payload[1]["components"][0]["style"] == 5
    assert dc_payload[1]["components"][0]["url"] == "https://app.aqwelai.xyz"


def test_keyboard_discord_chunking():
    # Discord allows max 5 buttons per ActionRow
    kb = Keyboard()
    kb.add_row(*[Button(f"Btn {i}", f"b_{i}") for i in range(12)])

    dc_components = kb.to_discord()
    # 12 buttons should be chunked into 3 ActionRows (5, 5, 2)
    assert len(dc_components) == 3
    assert len(dc_components[0]["components"]) == 5
    assert len(dc_components[1]["components"]) == 5
    assert len(dc_components[2]["components"]) == 2


def test_card_compilation():
    kb = Keyboard([[("Accept", "acc"), ("Decline", "dec", "danger")]])
    card = Card(
        title="Server Status",
        description="All systems operational.",
        fields={"CPU Load": "12%", "Memory": "4.2 GB / 16 GB"},
        color="success",
        image="https://example.com/status.png",
        footer="Cluster: us-east-1",
        url="https://status.example.com",
        keyboard=kb,
    )

    # 1. Discord Embed compilation
    dc_payload = card.to_discord()
    assert "embed" in dc_payload
    embed = dc_payload["embed"]
    assert embed["title"] == "Server Status"
    assert embed["description"] == "All systems operational."
    assert embed["url"] == "https://status.example.com"
    assert embed["image"]["url"] == "https://example.com/status.png"
    assert embed["footer"]["text"] == "Cluster: us-east-1"
    assert embed["color"] == 0x57F287  # Green success
    assert len(embed["fields"]) == 2
    assert embed["fields"][0]["name"] == "CPU Load"
    assert embed["fields"][0]["value"] == "12%"
    assert "components" in dc_payload
    assert len(dc_payload["components"]) == 1

    # 2. Telegram Fallback compilation (Formatted HTML + photo)
    tg_payload = card.to_telegram()
    assert tg_payload["parse_mode"] == "HTML"
    assert tg_payload["photo"] == "https://example.com/status.png"
    assert "<b><a href=\"https://status.example.com\">Server Status</a></b>" in tg_payload["caption"]
    assert "• <b>CPU Load</b>: 12%" in tg_payload["caption"]
    assert "<i>Cluster: us-east-1</i>" in tg_payload["caption"]
    assert "reply_markup" in tg_payload
    assert len(tg_payload["reply_markup"]["inline_keyboard"]) == 1


def test_modal_compilation():
    modal = Modal(
        title="User Feedback",
        custom_id="modal_feedback",
        fields=[
            ModalField("name", "Your Name", placeholder="e.g. Alice", required=True),
            ModalField("comments", "Your Comments", style="paragraph", required=False),
        ],
    )

    # 1. Discord Native Modal
    dc_payload = modal.to_discord()
    assert dc_payload["type"] == 9  # MODAL response
    assert dc_payload["data"]["title"] == "User Feedback"
    assert dc_payload["data"]["custom_id"] == "modal_feedback"
    assert len(dc_payload["data"]["components"]) == 2
    assert dc_payload["data"]["components"][0]["components"][0]["custom_id"] == "name"
    assert dc_payload["data"]["components"][0]["components"][0]["style"] == 1  # Short
    assert dc_payload["data"]["components"][1]["components"][0]["custom_id"] == "comments"
    assert dc_payload["data"]["components"][1]["components"][0]["style"] == 2  # Paragraph

    # 2. Telegram Graceful Degradation (ForceReply prompt)
    tg_payload = modal.to_telegram()
    assert tg_payload["is_fallback"] is True
    assert tg_payload["reply_markup"]["force_reply"] is True
    assert "📋 <b>User Feedback</b>" in tg_payload["text"]
    assert "Your Name" in tg_payload["text"]


def test_wizard_multi_step_flow():
    step1 = WizardStep(
        id="step_intro",
        title="Welcome",
        description="Let's configure your bot settings.",
        fields={"Current Version": "v0.2.1"},
    )
    step2 = WizardStep(
        id="step_pref",
        title="Preferences",
        description="Choose your preferred notifications.",
        keyboard=Keyboard([[("Enable Alerts", "act_alerts")]]),
    )
    step3 = WizardStep(
        id="step_confirm",
        title="Confirmation",
        description="Ready to apply settings.",
        color="success",
    )

    wizard = Wizard(
        id="setup_wiz",
        steps=[step1, step2, step3],
        next_label="Continue ➡️",
        finish_label="🚀 Apply",
    )

    # Test Step 0 render
    r0 = wizard.render_step(0, "telegram")
    assert "Step 1 of 3: Welcome" in r0["text"]
    assert "Current Version" in r0["text"]
    # Step 0 should have Continue and Cancel buttons, but no Back button
    nav_buttons = r0["reply_markup"]["inline_keyboard"][-1]
    assert any("Continue" in b["text"] for b in nav_buttons)
    assert not any("Back" in b["text"] for b in nav_buttons)

    # Test Step 1 render
    r1 = wizard.render_step(1, "discord")
    assert "Step 2 of 3: Preferences" in r1["embed"]["title"]
    # Step 1 should have custom keyboard + Back + Continue + Cancel
    assert len(r1["components"]) == 2
    action_btns = r1["components"][1]["components"]
    assert any("Back" in b["label"] for b in action_btns)
    assert any("Continue" in b["label"] for b in action_btns)

    # Test Step 2 (Final step) render
    r2 = wizard.render_step(2, "telegram")
    assert "Step 3 of 3: Confirmation" in r2["text"]
    last_btns = r2["reply_markup"]["inline_keyboard"][-1]
    assert any("🚀 Apply" in b["text"] for b in last_btns)


def test_context_reply_ui_and_buttons():
    async def _run():
        bot = TelegramBot(token="123456:MOCK")
        sent = []

        async def mock_api(method, payload=None, **kwargs):
            sent.append((method, payload))
            if method == "sendMessage":
                return {"message_id": 999, "chat": {"id": payload.get("chat_id")}}
            elif method == "sendPhoto":
                return {"message_id": 1000, "chat": {"id": payload.get("chat_id")}}
            return {}

        bot._api_call = mock_api

        # 1. Reply with Card + Keyboard
        card = Card(
            title="Profile",
            description="User details",
            image="https://example.com/avatar.jpg",
            keyboard=Keyboard([[("Edit", "btn_edit"), ("Logout", "btn_logout")]]),
        )

        @bot.on_command("profile")
        async def handle_profile(ctx: Context):
            await ctx.reply(ui=card)

        # 2. Button handler registration
        button_clicks = []

        @bot.on_button("btn_edit")
        async def handle_edit_click(ctx: Context):
            button_clicks.append(ctx.text)
            await ctx.reply("Editing mode activated!")

        # Dispatch command
        await bot.handle_event({
            "id": "1",
            "chat_id": "123",
            "user_id": "456",
            "text": "/profile",
            "event_type": "command",
        })

        assert len(sent) == 1
        method, payload = sent[0]
        assert method == "sendPhoto"
        assert payload["photo"] == "https://example.com/avatar.jpg"
        assert "Profile" in payload["caption"]
        assert len(payload["reply_markup"]["inline_keyboard"]) == 1

        # Dispatch button click (callback_query)
        await bot.handle_event({
            "id": "cb_1",
            "chat_id": "123",
            "user_id": "456",
            "text": "btn_edit",
            "event_type": "callback",
        })

        assert button_clicks == ["btn_edit"]
        assert sent[-1][0] == "sendMessage"
        assert sent[-1][1]["text"] == "Editing mode activated!"

    asyncio.run(_run())


def test_context_modal_and_wizard():
    async def _run():
        bot = DiscordBot(token="MOCK_DISCORD")
        sent = []

        async def mock_api(method, path, payload=None, **kwargs):
            sent.append((method, path, payload))
            if method == "POST" and "messages" in path:
                return {"id": "msg_555", "content": payload.get("content")}
            return {}

        bot._api_call = mock_api

        modal = Modal(
            title="Bug Report",
            custom_id="modal_bug",
            fields=[ModalField("desc", "Describe issue", style="paragraph")],
        )

        wiz = Wizard(
            id="onboarding",
            steps=[
                WizardStep("s1", "Step 1: Account"),
                WizardStep("s2", "Step 2: Finish"),
            ],
        )

        @bot.on_command("report")
        async def handle_report(ctx: Context):
            await ctx.show_modal(modal)

        @bot.on_command("wizard")
        async def handle_wiz(ctx: Context):
            await ctx.start_wizard(wiz)

        # Dispatch /report
        await bot.handle_event({
            "id": "1",
            "chat_id": "c99",
            "user_id": "u99",
            "text": "/report",
            "event_type": "command",
        })
        assert len(sent) >= 1

        # Dispatch /wizard
        await bot.handle_event({
            "id": "2",
            "chat_id": "c99",
            "user_id": "u99",
            "text": "/wizard",
            "event_type": "command",
        })
        assert any("Step 1 of 2: Step 1: Account" in str(s) for s in sent)

    asyncio.run(_run())
