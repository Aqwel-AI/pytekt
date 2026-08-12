# pytekt.tools — Examples

## Offline tool loop

Uses **`pytekt.tools.FakeToolProvider`** so no API keys or HTTP.

```bash
pip install -e .
python -m pytekt.tools.examples.demo_tool_loop
```

**demo_tool_loop.py** — registers a small `add` tool, scripts two assistant turns (one tool call, one text reply), runs `run_tool_loop`.

Optional token estimates need **`pip install pytekt[tools]`** (`tiktoken`). See [`../README.md`](../README.md).
