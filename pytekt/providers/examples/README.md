# pytekt.providers — Examples

## Offline demo (no API keys)

```bash
pip install -e .
python -m pytekt.providers.examples.demo_factory_parse
```

**demo_factory_parse.py** — prints `supported_providers()` and runs `parse_chat_completion_response` on a tiny in-memory JSON dict (no network).

## Live API calls

To call a real endpoint, set the usual env vars (`OPENAI_API_KEY`, etc.) and use `OpenAIProvider` / `create_provider` as in [`../README.md`](../README.md). Do not commit secrets.
