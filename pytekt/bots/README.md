# pytekt.bots — High-Performance Native-Core Bot Framework

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![C++ Core](https://img.shields.io/badge/core-C%2B%2B14%20%2F%20pybind11-orange.svg)](pytekt/bots/_core/)
[![Tests](https://img.shields.io/badge/tests-26%20passed%20%2F%20100%25-green.svg)](tests/)

**`pytekt.bots`** is a high-throughput, platform-agnostic bot framework for Python backed by a compiled **C++14 core** with full **pure-Python fallback portability**.

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
                                    |    @bot.on_command / @bot.rate_limit    |
                                    +--------------------+--------------------+
                                                         |
                                    +--------------------+--------------------+
                                    |        pytekt.bots.ai (LLM Layer)       |
                                    |  Per-Chat Memory / RAG / @ai.tool / STT |
                                    +--------------------+--------------------+
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

## Module Layout

| Path | Description |
|------|-------------|
| [`__init__.py`](__init__.py) | Public package exports (`Bot`, `TelegramBot`, `DiscordBot`, `Context`, `AI`, `RateLimiter`, etc.). |
| [`base.py`](base.py) | Platform-agnostic `Bot` engine, decorators, middleware chain, `Context` async helpers. |
| [`telegram.py`](telegram.py) | `TelegramBot(Bot)` adapter with polling, webhooks, and automatic 429 retry backoff. |
| [`discord.py`](discord.py) | `DiscordBot(Bot)` adapter normalizing Discord gateway/webhook events. |
| [`ai.py`](ai.py) | High-level `AI` integration layer reusing `pytekt.providers`, `pytekt.rag`, and `pytekt.embed`. |
| [`_core/`](_core/) | C++14 source files (`dispatcher`, `ratelimiter`, `fsm`, `cache`, `antispam`, `metrics`, `webhook_server`, `bindings`). |
| [`_core_fallback.py`](_core_fallback.py) | 100% pure-Python reference implementation matching the C++ core interface. |
| [`pybind_module.pyi`](pybind_module.pyi) | Type stubs for compiled native module. |

---

## Step-by-Step Professional Tutorial

### Step 1: Getting Started with TelegramBot

Create a bot with command and message handlers:

```python
import os
from pytekt.bots import TelegramBot, Context

bot = TelegramBot(token=os.environ["TELEGRAM_BOT_TOKEN"])

@bot.on_command("start")
async def handle_start(ctx: Context):
    await ctx.reply(f"Hello, {ctx.metadata.get('first_name', 'there')}! Welcome to PyTekt Bots.")

@bot.on_command("help")
async def handle_help(ctx: Context):
    await ctx.reply("Commands:\n/start - Start bot\n/help - Show help menu")

@bot.on_message()
async def echo_all(ctx: Context):
    await ctx.reply(f"You said: {ctx.text}")

if __name__ == "__main__":
    bot.run()
```

---

### Step 2: High-Performance Rate Limiting & Auto 429 Flood Control

Configure token-bucket rate limits per user, chat, or globally. The C++ engine handles all bucket updates without GIL contention and automatically handles HTTP 429 backoff:

```python
from pytekt.bots import TelegramBot, Context

bot = TelegramBot(token="...")

# Limit user to 5 requests per 10 seconds; chat to 20 requests per minute
@bot.rate_limit(user="5/10s", chat="20/60s")
@bot.on_message()
async def chat_handler(ctx: Context):
    await ctx.reply("Message received and processed within rate limits!")
```

---

### Step 3: Conversational Finite State Machine (FSM) & In-Process Cache

Manage conversation steps and session data natively in C++ with automatic TTL expiration—no Redis required:

```python
from pytekt.bots import TelegramBot, Context

bot = TelegramBot(token="...")

@bot.on_command("survey")
async def start_survey(ctx: Context):
    # Transition to 'awaiting_name' with a 5-minute inactivity timeout
    await ctx.set_state("awaiting_name", ttl=300.0)
    await ctx.reply("What is your name?")

@bot.state("awaiting_name")
async def get_name(ctx: Context):
    # Store session data
    await ctx.set_data("name", ctx.text, ttl=300.0)
    await ctx.set_state("awaiting_age", ttl=300.0)
    await ctx.reply(f"Nice to meet you {ctx.text}! How old are you?")

@bot.state("awaiting_age")
async def get_age(ctx: Context):
    name = await ctx.get_data("name")
    age = ctx.text
    await ctx.clear_state()
    await ctx.reply(f"Survey completed! Name: {name}, Age: {age}.")
```

---

### Step 4: 1-Line AI/LLM Integration & Throttled Live Streaming

Connect your bot to OpenAI, Anthropic, Gemini, DeepSeek, or local Ollama instances. Per-chat rolling memory is automatically maintained in the C++ cache:

```python
from pytekt.bots import TelegramBot, Context
from pytekt.bots.ai import AI

bot = TelegramBot(token="...")

# Reuses PyTekt provider authentication (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
ai = AI(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    system="You are a friendly customer service assistant.",
    memory_limit=20,  # Retain last 20 turns per chat
    memory_ttl=3600,  # 1 hour expiration
)

# 1. Live token streaming with rate-limited Telegram edits
@bot.on_message()
async def handle_ai_chat(ctx: Context):
    await ctx.reply_ai(ai)

# 2. Manual ask with chat_id memory
@bot.on_command("ask")
async def handle_ask(ctx: Context):
    prompt = " ".join(ctx.args)
    response = await ai.ask(prompt, chat_id=ctx.chat_id)
    await ctx.reply(response)
```

---

### Step 5: Function Calling & Skills (`@ai.tool`)

Register plain Python functions with docstrings and type annotations. `pytekt.bots.ai` automatically extracts JSON Schemas and runs autonomous tool execution loops:

```python
from pytekt.bots.ai import AI

ai = AI(provider="openai", model="gpt-4o-mini")

@ai.tool
def get_crypto_price(symbol: str) -> str:
    """Fetch current market price for a cryptocurrency ticker symbol."""
    prices = {"BTC": "$95,000", "ETH": "$3,400", "SOL": "$210"}
    return f"{symbol.upper()} is currently trading at {prices.get(symbol.upper(), '$0.00')}."

@bot.on_command("crypto")
async def crypto_cmd(ctx: Context):
    # Model will autonomously call get_crypto_price if needed
    await ctx.reply_ai(ai, prompt=f"Answer user crypto inquiry: {ctx.text}")
```

---

### Step 6: Multimodal Processing (Voice & Photos)

Handle speech-to-text audio notes and computer vision image understanding without boilerplate:

```python
@bot.on_voice()
async def handle_voice(ctx: Context):
    # Automatically transcribes audio file/stream via Whisper/Gemini
    text = await ai.transcribe(ctx.audio)
    answer = await ai.ask(text, chat_id=ctx.chat_id)
    await ctx.reply(f"🎤 You said: \"{text}\"\n\n🤖 {answer}")

@bot.on_photo()
async def handle_photo(ctx: Context):
    # Multimodal image analysis
    description = await ai.vision(ctx.image, prompt="Describe what you see in this photo in detail.")
    await ctx.reply(description)
```

---

### Step 7: 1-Line RAG Knowledge Base

Index documentation or FAQ files directly into vector search using `pytekt.rag` and `pytekt.embed`:

```python
# Index local markdown or FAQ docs into vector storage
ai.knowledge_base("docs/faq.md")

@bot.on_command("faq")
async def faq_cmd(ctx: Context):
    # Retrieves relevant chunks and augments the system prompt
    answer = await ai.ask(ctx.text, chat_id=ctx.chat_id, use_kb=True)
    await ctx.reply(answer)
```

---

### Step 8: Declarative AI Command Menus

Turn natural language specifications into functioning command handlers:

```python
bot.ai_commands(ai, {
    "summarize": "Summarize the key points of the user prompt or replied-to message",
    "translate_es": "Translate the user message into Spanish",
    "code_review": "Perform a concise code review highlighting bugs and performance issues",
})
```

---

### Step 9: Webhook Server & Multi-Bot Multiplexing

Run bots in production using the embedded C++ `WebhookServer`:

```python
if __name__ == "__main__":
    # Starts internal high-throughput HTTP/1.1 listener on port 8443
    bot.run_webhook(host="0.0.0.0", port=8443, path="/telegram/webhook")
```

---

### Step 10: DiscordBot Adapter

Reuse the exact same handlers and AI logic with Discord:

```python
from pytekt.bots import DiscordBot, Context

bot = DiscordBot(token=os.environ["DISCORD_BOT_TOKEN"])

@bot.on_command("ping")
async def handle_ping(ctx: Context):
    await ctx.reply("Pong from Discord!")

if __name__ == "__main__":
    bot.run_webhook(port=8443, path="/discord")
```

---

## Full API Reference

### `UniversalEvent`
Normalized platform-independent data structure:
- `id`: Unique event/message ID string.
- `chat_id`: Normalized chat or channel identifier.
- `user_id`: Normalized sender user identifier.
- `text`: Message or command text.
- `platform`: `"telegram"`, `"discord"`, or `"generic"`.
- `event_type`: `"message"`, `"command"`, `"photo"`, `"voice"`, `"callback"`, `"interaction"`.
- `command`: Clean command name (without `/` or `!`).
- `args`: List of whitespace-delimited argument strings.
- `metadata`: Key-value map (usernames, file IDs, dimensions, reply IDs).
- `timestamp`: UTC epoch timestamp in seconds.

### `Bot` Base Class
- `@bot.on_command(cmd)`: Decorator for slash/exclamation commands.
- `@bot.on_message(pattern=None)`: Decorator for general messages or regex patterns.
- `@bot.on_voice()`: Decorator for audio and voice notes.
- `@bot.on_photo()`: Decorator for image attachments.
- `@bot.on_event(event_type)`: Decorator for raw event types.
- `@bot.state(state_name)`: Decorator for active FSM states.
- `@bot.rate_limit(user=None, chat=None, global_=None)`: Token-bucket rate limiter decorator.
- `@bot.middleware`: Register asynchronous middleware `fn(ctx, next_fn)`.
- `bot.ai_commands(ai, commands)`: Register natural language command menu.
- `bot.run()` / `bot.run_webhook(port, host, path)`: Start bot runtime.

### `Context`
- `ctx.reply(text, **kwargs)`: Send reply to chat.
- `ctx.reply_ai(ai, prompt=None, **kwargs)`: Stream/send LLM response with rate-limited edits.
- `ctx.send_photo(photo, caption=None)`: Send image.
- `ctx.send_voice(voice, caption=None)`: Send audio.
- `ctx.send_typing()`: Trigger typing indicator.
- `ctx.delete()`: Delete triggering message.
- `ctx.set_state(state, ttl=0.0)` / `ctx.get_state()` / `ctx.clear_state()`: FSM controls.
- `ctx.set_data(key, val, ttl=0.0)` / `ctx.get_data(key)`: Session data storage.

### `AI` Class (`pytekt.bots.ai`)
- `AI(provider, model=None, system=..., memory_ttl=3600, memory_limit=20)`: Construct AI interface.
- `await ai.ask(text, chat_id=None, use_kb=False, ...)`: Complete chat with memory & tools.
- `async for chunk in ai.ask_stream(...)`: Stream completion chunks.
- `@ai.tool`: Register Python skill/tool for autonomous invocation.
- `await ai.transcribe(audio)`: Speech-to-text.
- `await ai.vision(image, prompt=...)`: Image analysis.
- `ai.knowledge_base(source)`: Index RAG document collection.
- `await ai.remember(chat_id, fact)` / `await ai.forget(chat_id)`: Long-term fact store.
- `await ai.moderate(text)`: Safety check returning `True` if toxic/flagged.

---

## Compilation and Build

To compile the C++ extension in development:

```bash
# Build native extension inplace
pip install pybind11
python setup.py build_ext --inplace
```

To run test suites:

```bash
pytest tests/test_bots_core.py tests/test_bots_framework.py tests/test_bots_ai.py -v
```
