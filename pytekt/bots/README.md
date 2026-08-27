# pytekt.bots — High-Performance Native-Core Bot Framework

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![C++ Core](https://img.shields.io/badge/core-C%2B%2B14%20%2F%20pybind11-orange.svg)](pytekt/bots/_core/)
[![Security](https://img.shields.io/badge/security-hardened%20%26%20fuzzed-brightgreen.svg)](SECURITY.md)
[![Tests](https://img.shields.io/badge/tests-52%20passed%20%2F%20100%25-green.svg)](tests/)

**`pytekt.bots`** is a high-throughput, platform-agnostic bot framework for Python backed by a compiled **C++14 core** with full **pure-Python fallback portability**, a declarative **cross-platform UI layer**, **durable database persistence**, **RBAC permissions**, **i18n**, **event-loop task scheduling**, **extensible plugins**, **Telegram payments**, and **enterprise security hardening**.

Most popular Python bot frameworks (*python-telegram-bot*, *aiogram*, *discord.py*) hit concurrency and latency bottlenecks in three areas:
1. **Linear event dispatching** and redundant JSON deserialization under high message volume.
2. **Rate-limiting and flood-control bookkeeping** with Python GIL contention.
3. **In-memory state and session caching** that typically requires bolting on external Redis servers.

`pytekt.bots` compiles these hot paths directly into C++ via `pybind11`—achieving **5–20x throughput improvements** while keeping the developer-facing API 100% Python, declarative, and ergonomic.

---

## Architecture

```
                                    +-----------------------------------------+
                                    |         User Application (Python)       |
                                    |    @bot.on_command / @bot.on_button     |
                                    +--------------------+--------------------+
                                                         |
                     +-----------------------------------+-----------------------------------+
                     |                                   |                                   |
      +--------------+--------------+     +--------------+--------------+     +--------------+--------------+
      |   pytekt.bots.ui Layer      |     |  pytekt.bots.ai (LLM Layer) |     |  Ecosystem & Persistence    |
      |   - Keyboard / Buttons      |     |  - Per-Chat Memory          |     |  - bot.db (Durable Storage) |
      |   - Card (Embeds/Photos)    |     |  - One-Line RAG Pipeline    |     |  - Scheduler (@bot.every)   |
      |   - Modal (Popups/Prompts)  |     |  - @ai.tool Skills          |     |  - RBAC (@bot.admin_only)   |
      |   - Wizard (Multi-Step)     |     |  - Voice STT & Vision       |     |  - i18n (bot.t) & Plugins   |
      +--------------+--------------+     +--------------+--------------+     +--------------+--------------+
                     |                                   |                                   |
                     +-----------------------------------+-----------------------------------+
                                                         |
                              +--------------------------+--------------------------+
                              |                                                     |
               +--------------+--------------+                       +--------------+--------------+
               |  TelegramBot (Adapter)      |                       |   DiscordBot (Adapter)      |
               |  Long Polling & Webhooks    |                       |   Gateway & Webhooks        |
               +--------------+--------------+                       +--------------+--------------+
                              |                                                     |
                              +--------------------------+--------------------------+
                                                         |
                                    +--------------------+--------------------+
                                    |        UniversalEvent Normalizer        |
                                    |    Platform-Agnostic Event Struct       |
                                    +--------------------+--------------------+
                                                         |
                         +-------------------------------+-------------------------------+
                         |                                                               |
    +--------------------+--------------------+                     +--------------------+--------------------+
    |   Native C++ Core (pybind11)            |                     |   Pure-Python Fallback              |
    |   - Dispatcher (Trie & Regex Match)     |                     |   - Dispatcher                      |
    |   - RateLimiter (Token Buckets + 429)   |   <--- Auto --->    |   - RateLimiter                     |
    |   - FSM (TTL States & Sessions)         |      Fallback       |   - FSM                             |
    |   - Cache (In-Process TTL Key-Value)    |                     |   - Cache                           |
    |   - AntiSpam (Bloom Filter & Heuristics)|                     |   - AntiSpam                        |
    |   - Metrics (Prometheus Text Exporter)  |                     |   - Metrics                         |
    |   - WebhookServer (HTTP/1.1 Socket)     |                     |   - WebhookServer                   |
    +-----------------------------------------+                     +-----------------------------------------+
```

---

## 1. CLI Scaffolding & Local Hot-Reload

### 1-Line Project Scaffolding
Scaffold immediately runnable projects with sensible defaults, testing setup, and `.env.example`:

```bash
# Scaffold Telegram bot
pytekt bots new my_telegram_bot --platform telegram

# Scaffold Discord bot
pytekt bots new my_discord_bot --platform discord
```

Generated project layout:
```
my_telegram_bot/
  ├── main.py              # Working entrypoint with sample command & message handlers
  ├── .env.example         # Documented token placeholders
  ├── requirements.txt     # Locked dependencies
  ├── pyproject.toml       # Modern Python packaging configuration
  ├── README.md            # Quickstart instructions
  └── tests/
      └── test_bot.py      # Ready-to-run pytest test suite using bot.test_client()
```

### Hot-Reload Development Server
Run your bot with automatic file-watching and hot-reload:

```bash
# Runs main.py and automatically restarts on code/env changes
pytekt bots dev main.py
```

---

## 2. In-Memory Testing Client (`bot.test_client()`)

Test bot commands, button clicks, modals, and conversational flows in pytest **without touching Telegram or Discord network APIs**:

```python
import pytest
from pytekt.bots import TelegramBot, Context

bot = TelegramBot(token="123456:TEST_TOKEN")

@bot.on_command("hello")
async def handle_hello(ctx: Context):
    await ctx.reply("Hello there!")

def test_hello_command():
    # In-memory test client records all bot replies
    client = bot.test_client()
    responses = client.send_command("hello", chat_id="123", user_id="456")
    
    assert len(responses) == 1
    assert responses[0].text == "Hello there!"
    assert client.last_reply.has_text("Hello")
```

---

## 3. Durable Database Persistence (`bot.db` & `persistent=True`)

Connect to SQLite, PostgreSQL, MySQL, or MongoDB via `pytekt.db` to persist user sessions, FSM states, and AI long-term memories across bot restarts:

```python
from pytekt.bots import TelegramBot, Context

bot = TelegramBot()

# Initialize durable persistence backed by pytekt.db
bot.init_db("sqlite:///./bot_data.db")

@bot.on_command("login")
async def login_handler(ctx: Context):
    # persistent=True writes to bot.db so state survives restarts and works across replicas
    await ctx.set_state("authenticated", persistent=True)
    await ctx.set_data("username", "neo", persistent=True)
    await ctx.reply("Session saved to durable storage!")

@bot.on_message()
async def check_auth(ctx: Context):
    state = await ctx.get_state()
    username = await ctx.get_data("username")
    if state == "authenticated":
        await ctx.reply(f"Welcome back, {username}!")
```

---

## 4. Event-Loop Task Scheduling (`@bot.every` & `@bot.cron`)

Run periodic and cron-scheduled background tasks directly on the bot event loop without third-party dependencies:

```python
from pytekt.bots import TelegramBot

bot = TelegramBot()

# Periodic interval job: runs every 30 seconds
@bot.every("30s")
async def health_check(bot):
    print("Heartbeat tick...")

# Cron job: runs every morning at 9:00 AM (min hour dom month dow)
@bot.cron("0 9 * * *")
async def morning_digest(bot):
    await bot.send_message(chat_id="CHANNEL_ID", text="🌅 Good morning! Here is today's digest.")
```

---

## 5. Role-Based Access Control (`@bot.admin_only` & `@bot.requires_role`)

Manage per-chat roles and protect privileged commands:

```python
from pytekt.bots import TelegramBot, Context

bot = TelegramBot()

# Grant roles per-chat or globally ('*' for all chats)
bot.roles.grant(chat_id="chat_1", user_id="user_42", role="moderator")
bot.roles.set_admin(user_id="user_admin")

@bot.on_command("ban")
@bot.admin_only
async def ban_cmd(ctx: Context):
    await ctx.reply("User banned!")

@bot.on_command("review")
@bot.requires_role("moderator")
async def review_cmd(ctx: Context):
    await ctx.reply("Opening moderation queue...")
```

---

## 6. Internationalization (i18n)

Automatic language detection from user platform locale (`ctx.lang`) and translation dictionary lookup:

```python
from pytekt.bots import TelegramBot, Context

bot = TelegramBot()

# Add translation tables directly or load from JSON/YAML directory
bot.add_translations("en", {"welcome": "Welcome, {name}!", "menu.help": "Help Menu"})
bot.add_translations("es", {"welcome": "¡Bienvenido, {name}!", "menu.help": "Menú de Ayuda"})

# Load translation files from locales/ directory (en.json, es.json, fr.yaml, etc.)
bot.load_translations("locales/")

@bot.on_command("start")
async def handle_start(ctx: Context):
    # Automatically resolves user language code from Telegram/Discord user metadata
    greeting = ctx.t("welcome", name=ctx.metadata.get("first_name", "there"))
    await ctx.reply(greeting)
```

---

## 7. Modular Plugin & Extension Architecture

Package and distribute bot features as independent, reusable extensions:

```python
from pytekt.bots import Extension, Context

class WeatherPlugin(Extension):
    @Extension.command("weather")
    async def weather_cmd(self, ctx: Context):
        city = ctx.args[0] if ctx.args else "London"
        await ctx.reply(f"Weather for {city}: 21°C, Sunny ☀️")

    @Extension.every("1h")
    async def hourly_update(self, bot):
        print("Updating weather cache...")

# Register extension with bot
bot.add_extension(WeatherPlugin(bot))

# Or dynamically load by module path (like discord.py cogs)
bot.load_extension("my_bot.plugins.analytics")
```

---

## 8. Native Payments (`pytekt.bots.payments`)

Send Telegram in-chat payment invoices and handle pre-checkout queries with honest cross-platform boundaries:

```python
from pytekt.bots import TelegramBot, Context, LabeledPrice

bot = TelegramBot()

@bot.on_command("buy")
async def handle_buy(ctx: Context):
    # Send native payment invoice
    await ctx.send_invoice(
        title="1-Month Pro Subscription",
        description="Unlock full AI capabilities",
        payload="order_sub_pro_1m",
        provider_token=os.environ["PAYMENT_PROVIDER_TOKEN"],
        currency="USD",
        prices=[LabeledPrice(label="Pro Membership", amount=999)], # $9.99
    )

@bot.on_pre_checkout
async def handle_pre_checkout(ctx: Context):
    # Confirm order validity before processing transaction
    await bot.answer_pre_checkout_query(ctx.event.id, ok=True)

@bot.on_payment
async def handle_payment_success(ctx: Context):
    await ctx.reply("🎉 Payment received! Your Pro features are now active.")
```

> [!NOTE]
> On platforms without native in-chat payment APIs (such as Discord), calling `bot.send_invoice(...)` raises `NotSupportedError` immediately rather than silently failing.

---

## 9. Declarative Cross-Platform UI (`pytekt.bots.ui`)

Write UI components once; they automatically compile down to native platform representations or graceful silent fallbacks:

```python
from pytekt.bots import TelegramBot, Context
from pytekt.bots.ui import Keyboard, Button, Card, Modal, Wizard, WizardStep

# 1. Interactive Keyboards & WebApp Launcher Buttons
kb = Keyboard([
    [
        Button("🚀 Primary Action", callback_id="act_primary", style="primary"),
        Button("⚠️ Danger Action", callback_id="act_danger", style="danger"),
    ],
    [
        Button("🌐 Visit Website", url="https://aqwelai.xyz"),
        Keyboard.web_app_button("📱 Launch Mini-App", "https://app.aqwelai.xyz"),
    ],
])

# 2. Rich Media Cards (Discord Embeds / Telegram Formatted HTML & Photos)
card = Card(
    title="Server Node #42",
    description="Cluster operational.",
    fields={"CPU": "14%", "RAM": "3.8 GB"},
    color="success",
    image="https://example.com/server.png",
    keyboard=kb,
)

@bot.on_command("status")
async def handle_status(ctx: Context):
    await ctx.reply(ui=card)
```

---

## 10. Multi-Step Interactive Wizards (`Wizard`)

Create multi-step guided workflows that track the current step index and edit messages in place:

```python
from pytekt.bots.ui import Wizard, WizardStep

wizard = Wizard(
    id="account_setup",
    steps=[
        WizardStep("step1", "Step 1: Choose Username", description="Enter your desired username."),
        WizardStep("step2", "Step 2: Preferences", description="Select notification settings."),
        WizardStep("step3", "Step 3: Confirmation", description="Review and finish setup.", color="success"),
    ],
    next_label="Next ➡️",
    back_label="⬅️ Back",
    finish_label="✅ Finish Setup",
    on_finish=lambda ctx: ctx.reply("🎉 Account setup completed!"),
)

@bot.on_command("setup")
async def start_setup_wizard(ctx: Context):
    await ctx.start_wizard(wizard)
```

---

## Full API Reference

### `Bot` Class
- `bot.init_db(source)`: Initialize durable database persistence layer (`bot.db`).
- `bot.test_client()`: Create in-memory `BotTestClient` for unit testing.
- `@bot.every(interval)`: Register recurring interval job (`"30s"`, `"10m"`, `"1h"`).
- `@bot.cron(cron_expr)`: Register cron job (`"0 9 * * *"`).
- `@bot.admin_only`: Restrict command access to administrators.
- `@bot.requires_role(role)`: Restrict command access to specific user role.
- `bot.t(key, lang=None, **kwargs)`: Translate string with language fallback.
- `bot.load_translations(path)` / `bot.add_translations(lang, dict)`: Register translation tables.
- `bot.add_extension(ext)` / `bot.load_extension(module_path)`: Register modular plugin.
- `bot.send_invoice(...)`: Send native payment invoice.
- `@bot.on_pre_checkout`: Register pre-checkout confirmation handler.
- `@bot.on_payment`: Register payment success handler.
- `@bot.on_command(cmd)`: Register command handler (`/start`, `!info`).
- `@bot.on_message(pattern=None)`: Register message handler.
- `@bot.on_button(callback_id=None)`: Register button click handler.
- `@bot.on_modal_submit(custom_id=None)`: Register modal form submission handler.
- `@bot.rate_limit(user=None, chat=None, global_=None)`: Token-bucket rate limiter.
- `@bot.middleware`: Register asynchronous middleware.
- `bot.run()` / `bot.run_webhook(port, host, path)`: Start bot.

### `Context`
- `ctx.lang`: User's language code from platform metadata.
- `ctx.t(key, **kwargs)`: Translate string for the current user's language.
- `ctx.reply(text, ui=None, **kwargs)`: Send reply with optional `Keyboard` or `Card`.
- `ctx.show_modal(modal)`: Display native popup modal or ForceReply prompt.
- `ctx.start_wizard(wizard)`: Initiate multi-step interactive guided flow.
- `ctx.reply_ai(ai, prompt=None, **kwargs)`: Stream/send LLM response with rate-limited edits.
- `ctx.send_invoice(...)`: Send payment invoice to current chat.
- `ctx.set_state(state, ttl=0.0, persistent=False)`: Set FSM state.
- `ctx.get_state()` / `ctx.clear_state()`: Retrieve / clear FSM state.
- `ctx.set_data(key, val, ttl=0.0, persistent=False)`: Store session data.
- `ctx.get_data(key)` / `ctx.clear_data()`: Retrieve / clear session data.

---

## Compilation & Verification

To compile the C++ extension in development:

```bash
# Standard compilation
pip install pybind11
python setup.py build_ext --inplace

# Compile with AddressSanitizer and UndefinedBehaviorSanitizer
PYTEKT_ENABLE_ASAN=1 python setup.py build_ext --inplace
```

To run all unit, UI, security, and ecosystem test suites:

```bash
# Scan repository for hardcoded secrets
python scripts/scan_secrets.py

# Run all 52 tests across the full suite
pytest tests/test_bots_*.py -v
```
