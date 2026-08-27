"""
PyTekt Bots — Ecosystem, Persistence, Testing & Scheduling Demo.
Demonstrates:
  1. In-memory testing harness (bot.test_client())
  2. Durable DB persistence (bot.db & persistent=True)
  3. Background task scheduling (@bot.every and @bot.cron)
  4. Role-based access control (@bot.admin_only, @bot.requires_role)
  5. Multi-language internationalization (ctx.t)
  6. Reusable plugins (Extension base class)
  7. Native payments (bot.send_invoice)
"""

import asyncio
import os
from pytekt.bots import (
    TelegramBot,
    Context,
    Extension,
    LabeledPrice,
)
from pytekt.bots.ui import Keyboard, Button, Card

# 1. Initialize Bot
bot = TelegramBot(token=os.environ.get("TELEGRAM_BOT_TOKEN", "123456:DEMO_TOKEN"))

# 2. Wire Durable Database Persistence
bot.init_db("sqlite:///./demo_bot.db")

# 3. Setup Internationalization (i18n)
bot.add_translations("en", {
    "welcome": "Welcome, {name}!",
    "status_online": "Status: Systems operational",
})
bot.add_translations("es", {
    "welcome": "¡Bienvenido, {name}!",
    "status_online": "Estado: Sistemas operativos",
})

# 4. Define Reusable Extension Plugin
class ModerationExtension(Extension):
    @Extension.command("purge")
    @bot.admin_only
    async def handle_purge(self, ctx: Context):
        await ctx.reply("🧹 Channel message backlog purged by admin.")

    @Extension.every("1h")
    async def cleanup_task(self, b):
        print("🕒 [Hourly Task] Pruning expired cache items...")

bot.add_extension(ModerationExtension(bot))

# 5. Core Handlers
@bot.on_command("start")
async def handle_start(ctx: Context):
    # Store durable persistent state surviving restarts
    await ctx.set_state("started", persistent=True)
    
    greeting = ctx.t("welcome", name=ctx.metadata.get("first_name", "Explorer"))
    status = ctx.t("status_online")
    
    card = Card(
        title=greeting,
        description=status,
        fields={"Storage": "Durable SQLite (pytekt.db)", "Dispatch": "Native C++"},
        color="success",
        keyboard=Keyboard([[Button("💳 Buy Pro Pass", callback_id="btn_buy")]]),
    )
    await ctx.reply(ui=card)

@bot.on_button("btn_buy")
async def handle_buy_button(ctx: Context):
    # Telegram In-Chat Payments
    await ctx.send_invoice(
        title="1-Month Pro Membership",
        description="Full access to AI and high-frequency dispatch",
        payload="invoice_pro_monthly",
        provider_token=os.environ.get("PAYMENT_PROVIDER_TOKEN", "TEST:PROVIDER:123"),
        currency="USD",
        prices=[LabeledPrice(label="Pro Membership", amount=999)],
    )

# 6. Event-Loop Scheduling
@bot.every("10s")
async def periodic_heartbeat(b):
    print("💓 Heartbeat tick from native scheduler event loop")


# 7. Self-Verification via In-Memory Test Client
async def run_simulation():
    print("🧪 Running in-memory simulation via bot.test_client()...\n")
    client = bot.test_client()

    # Test /start command with Spanish locale
    res1 = await client.send_command("start", user_id="user_carlos", metadata={"first_name": "Carlos", "language_code": "es"})
    print(f"User Carlos (/start):\n{res1[0].text}\n")
    assert client.last_reply.has_text("Carlos")

    # Test Admin Command Authorization
    res2 = await client.send_command("purge", user_id="user_normie")
    print(f"Unauthorized user (/purge):\n{res2[0].text}\n")
    assert "Access denied" in res2[0].text

    # Grant admin and re-test
    bot.roles.grant(chat_id="test_chat", user_id="user_normie", role="admin")
    res3 = await client.send_command("purge", user_id="user_normie")
    print(f"Authorized admin user (/purge):\n{res3[0].text}\n")
    assert "purged" in res3[0].text

    print("✅ All simulation scenarios executed successfully without live network requests!")


if __name__ == "__main__":
    asyncio.run(run_simulation())
