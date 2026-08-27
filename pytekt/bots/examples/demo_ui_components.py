"""
PyTekt Bots Declarative UI Showcase.

Demonstrates all 5 UI components against a mocked Bot runtime:
1. Keyboard (Telegram Inline Keyboard & Discord Button rows + WebApp buttons)
2. Card (Native Discord Embed & Telegram formatted text/photo)
3. Modal (Discord Popup Form & Telegram ForceReply degradation)
4. Wizard (Multi-step interactive flow with in-place message navigation)
5. WebApp (Built-in C++ WebhookServer hosting custom HTML/JS Mini-Apps)
"""

import asyncio
import json
from pprint import pprint

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


def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_keyboard():
    print_section("1. KEYBOARD & WEB APP BUTTON COMPONENT")

    kb = Keyboard([
        [
            Button("🚀 Primary Action", callback_id="act_primary", style="primary"),
            Button("⚠️ Danger Action", callback_id="act_danger", style="danger"),
        ],
        [
            Button("🌐 Open Website", url="https://aqwelai.xyz"),
            Keyboard.web_app_button("📱 Launch Mini-App", "https://app.aqwelai.xyz"),
        ],
    ])

    print("\n[Telegram Inline Keyboard Compilation]:")
    print(json.dumps(kb.to_telegram(), indent=2))

    print("\n[Discord ActionRow Components Compilation]:")
    print(json.dumps(kb.to_discord(), indent=2))


def demo_card():
    print_section("2. CARD COMPONENT (EMBED / RICH MEDIA)")

    kb = Keyboard([[("Approve", "card_approve"), ("Reject", "card_reject", "danger")]])

    card = Card(
        title="Production Deployment #428",
        description="Deploying `pytekt.bots.ui` release to cluster **us-east-1**.",
        image="https://raw.githubusercontent.com/Aqwel-AI/pytekt/main/assets/banner.png",
        fields={
            "Environment": "Production",
            "Commit": "a1b2c3d",
            "Latency": "0.42ms (C++ Core)",
            "Status": "Passed (33/33 tests)",
        },
        color="success",
        footer="PyTekt Continuous Delivery",
        url="https://github.com/Aqwel-AI/pytekt",
        keyboard=kb,
    )

    print("\n[Discord Native Embed Payload]:")
    print(json.dumps(card.to_discord(), indent=2))

    print("\n[Telegram Graceful Degradation (HTML Formatted Photo/Caption)]:")
    print(json.dumps(card.to_telegram(), indent=2))


def demo_modal():
    print_section("3. MODAL COMPONENT (POPUP FORMS)")

    modal = Modal(
        title="Submit User Feedback",
        custom_id="modal_feedback_form",
        fields=[
            ModalField(
                id="user_name",
                label="Full Name",
                placeholder="e.g. Satoshi Nakamoto",
                required=True,
                style="short",
            ),
            ModalField(
                id="feedback_text",
                label="Your Comments / Suggestions",
                placeholder="Write your feedback here...",
                required=False,
                style="paragraph",
            ),
        ],
    )

    print("\n[Discord Native Interaction Modal Payload]:")
    print(json.dumps(modal.to_discord(), indent=2))

    print("\n[Telegram Graceful Degradation (ForceReply Conversational Prompt)]:")
    print(json.dumps(modal.to_telegram(), indent=2))


def demo_wizard():
    print_section("4. WIZARD COMPONENT (MULTI-STEP FLOW)")

    step1 = WizardStep(
        id="step_intro",
        title="Welcome to Bot Setup",
        description="This wizard configures your AI models and rate limits.",
        fields={"Current Platform": "Multi-Platform", "C++ Engine": "Active"},
    )
    step2 = WizardStep(
        id="step_ai",
        title="Select AI Model",
        description="Choose the primary LLM provider for conversational memory.",
        keyboard=Keyboard([[("Anthropic Claude", "sel_claude"), ("OpenAI GPT", "sel_gpt")]]),
    )
    step3 = WizardStep(
        id="step_confirm",
        title="Confirm & Deploy",
        description="Everything is configured! Click Apply to finalize.",
        color="success",
    )

    wizard = Wizard(
        id="setup_flow",
        steps=[step1, step2, step3],
        next_label="Next ➡️",
        back_label="⬅️ Back",
        finish_label="🚀 Apply & Finish",
    )

    print("\n[Rendering Step 0 on Telegram]:")
    print(json.dumps(wizard.render_step(0, "telegram"), indent=2))

    print("\n[Rendering Step 1 on Discord]:")
    print(json.dumps(wizard.render_step(1, "discord"), indent=2))

    print("\n[Rendering Step 2 (Final Step) on Telegram]:")
    print(json.dumps(wizard.render_step(2, "telegram"), indent=2))


async def demo_mocked_bot_interaction():
    print_section("5. MOCKED BOT RUNNER (CTX.REPLY / BUTTON HANDLERS / WEBHOOK)")

    bot = TelegramBot(token="123456:MOCK_TOKEN")
    sent_payloads = []

    async def mock_api_call(method, payload=None, **kwargs):
        sent_payloads.append((method, payload))
        print(f"  [Mock Telegram API Call] -> {method}")
        return {"message_id": len(sent_payloads), "chat": {"id": payload.get("chat_id")}}

    bot._api_call = mock_api_call

    # Register handlers
    @bot.on_command("dashboard")
    async def handle_dashboard(ctx: Context):
        kb = Keyboard([[("View Analytics", "btn_analytics"), ("Settings", "btn_settings")]])
        card = Card(
            title="Bot Operations Dashboard",
            description="All services running under sub-millisecond latency.",
            fields={"Uptime": "99.99%", "C++ Core": "Active"},
            color="primary",
            keyboard=kb,
        )
        await ctx.reply(ui=card)

    @bot.on_button("btn_analytics")
    async def handle_analytics_button(ctx: Context):
        await ctx.reply("📊 Analytics: 12,450 events processed, 0 rate limit drops.")

    # Serve custom HTML WebApp via built-in C++ WebhookServer
    app_path = bot.serve_web_app("/mini-app", "<html><body><h1>PyTekt WebApp UI</h1></body></html>")
    print(f"\n[WebApp Registered]: Mini-App served on internal C++ WebhookServer at '{app_path}'")

    print("\n[Simulating Incoming Event: /dashboard command]:")
    await bot.handle_event({
        "id": "101",
        "chat_id": "999",
        "user_id": "888",
        "text": "/dashboard",
        "event_type": "command",
    })

    print("\n[Simulating Incoming Event: Button Click 'btn_analytics']:")
    await bot.handle_event({
        "id": "102",
        "chat_id": "999",
        "user_id": "888",
        "text": "btn_analytics",
        "event_type": "callback",
    })

    print("\n[All Mock API Requests Executed Successfully]:", len(sent_payloads))


def main():
    print("=" * 70)
    print("  PyTekt Bots Declarative Cross-Platform UI Demonstration")
    print("=" * 70)

    demo_keyboard()
    demo_card()
    demo_modal()
    demo_wizard()
    asyncio.run(demo_mocked_bot_interaction())

    print("\n" + "=" * 70)
    print("  All UI component demos executed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
