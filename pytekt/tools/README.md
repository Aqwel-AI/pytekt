# pytekt.tools — Package documentation

## 1. Title and overview

**`pytekt.tools`** supports **OpenAI-style tool calling**: JSON **schemas** from Python callables (**`function_tool`**), a **`ToolRegistry`**, HTTP **retry** (**`post_json_with_retry`**), **rate limiting** (**`TokenBucket`**), optional **token estimates** (OpenAI-style, **`tiktoken`** via **`[tools]`**), and **`run_tool_loop`** to drive multi-turn **`complete_turn`** sessions with **`OpenAIProvider`** / **`OpenAICompatibleProvider`**.

---

## 2. Module layout

| File | Role |
|------|------|
| `fake_provider.py` | `FakeToolProvider`, `make_tool_turn` — scripted `complete_turn` for offline demos/tests. |
| `schemas.py` | `function_tool` — build tool JSON from a Python function. |
| `registry.py` | `ToolRegistry` — register by name, dispatch tool calls. |
| `loop.py` | `run_tool_loop`, `tool_calls_to_message_payload`. |
| `retry.py` | `post_json_with_retry`. |
| `rate_limit.py` | `TokenBucket`. |
| `tokens.py` | `estimate_text_tokens_openai`, `estimate_messages_tokens_openai`. |

---

## 3. Public API (from `pytekt.tools`)

| Symbol | Description |
|--------|-------------|
| `function_tool` | Wrap callable → OpenAI tool schema dict. |
| `ToolRegistry` | Map tool name → implementation; JSON args in. |
| `run_tool_loop` | Multi-turn loop with provider `complete_turn`. |
| `tool_calls_to_message_payload` | Serialize assistant tool_calls for the next request. |
| `post_json_with_retry` | Resilient POST with backoff. |
| `TokenBucket` | Simple rate / concurrency guard. |
| `estimate_*_openai` | Token counts when `tiktoken` is installed. |
| `FakeToolProvider` | Returns fixed `AssistantTurn` sequence (no HTTP). |
| `make_tool_turn` | Build one assistant turn with tool calls for demos. |

```python
from pytekt.tools import ToolRegistry, function_tool, run_tool_loop
# Offline: FakeToolProvider, make_tool_turn
```

---

## 4. Examples

Runnable scripts: **[examples/](examples/)** — see [examples/README.md](examples/README.md).

```bash
python -m pytekt.tools.examples.demo_tool_loop
```

---

## 5. Conventions

- **Security:** Tool implementations receive **JSON-parsed** arguments; there is **no** `eval` of arbitrary code in the library path.
- **Provider:** Use **`complete_turn`** on providers that return **`AssistantTurn`** with **`tool_calls`**.

---

## 6. Dependencies

- **Standard library** for core loop/registry/retry.
- **Optional:** `tiktoken` — `pip install pytekt[tools]`.

---

## 7. See also

- Providers: [`../providers/README.md`](../providers/README.md)
- Structured turns: `pytekt.providers.structured`
- Root README: [../../README.md](../../README.md)
