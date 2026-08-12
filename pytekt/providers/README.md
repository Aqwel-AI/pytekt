# pytekt.providers — Package documentation

## 1. Title and overview

**`pytekt.providers`** implements **HTTP chat clients** for **OpenAI**, **Google Gemini**, **Anthropic**, and **OpenAI-compatible** servers. It exposes a small **`ChatProvider`** abstraction, **`ChatMessage`**, **`complete`** for text replies, and on OpenAI-shaped APIs **`complete_turn`** returning **`AssistantTurn`** (with optional **tool calls**). A **factory** selects providers by name.

---

## 2. Module layout

| File | Role |
|------|------|
| `base.py` | `ChatProvider`, `ChatMessage` protocol / datatypes. |
| `openai_provider.py` | `OpenAIProvider` — `complete`, `complete_turn`. |
| `gemini_provider.py` | `GeminiProvider`. |
| `anthropic_provider.py` | `AnthropicProvider`. |
| `generic_openai.py` | `OpenAICompatibleProvider` — custom base URL. |
| `structured.py` | `AssistantTurn`, `NormalizedToolCall`, response parsing. |
| `factory.py` | `create_provider`, `supported_providers`. |
| `errors.py` | `ProviderError`. |
| `http_utils.py` | Shared HTTP helpers. |

---

## 3. Public API (from `pytekt.providers`)

| Symbol | Description |
|--------|-------------|
| `OpenAIProvider`, `GeminiProvider`, `AnthropicProvider`, `OpenAICompatibleProvider` | Vendor clients. |
| `ChatMessage`, `ChatProvider` | Message model and interface. |
| `create_provider`, `supported_providers` | Factory by string name. |
| `AssistantTurn`, `NormalizedToolCall`, `parse_chat_completion_response` | Structured / tool flows. |
| `ProviderError` | Typed failure. |

**Environment variables (typical):** `OPENAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`.

```python
from pytekt.providers import OpenAIProvider
from pytekt.providers.base import ChatMessage

p = OpenAIProvider()
reply = p.complete([ChatMessage(role="user", content="Hello.")])
```

---

## 4. Examples

Runnable scripts: **[examples/](examples/)** — see [examples/README.md](examples/README.md).

```bash
python -m pytekt.providers.examples.demo_factory_parse
```

---

## 5. Conventions

- **Keys:** Never commit secrets; use env vars or your own secret store.
- **`complete_turn`:** Use with **`pytekt.tools.run_tool_loop`** for agent-style tool execution on OpenAI-compatible endpoints.

---

## 6. Dependencies

**Standard library** (`urllib`, `json`, …) for HTTP; **no** hard dependency on vendor SDKs. Network access required at runtime.

---

## 7. See also

- Tool loop: **`pytekt.tools`** — [`../tools/README.md`](../tools/README.md)
- Offline demos: **`pytekt.tools.FakeToolProvider`**
- Root README: [../../README.md](../../README.md)
