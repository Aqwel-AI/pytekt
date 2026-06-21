# Headless agent for CI

Run the Aion agent non-interactively in GitHub Actions or other CI:

```bash
aion agent run --task "Fix failing tests in tests/test_foo.py" --provider nvidia --yes
```

## Options

| Flag | Description |
|------|-------------|
| `--task` | User message (required) |
| `--provider` | Provider id (ollama, nvidia, openai, …) |
| `--model` | Model name |
| `--yes` | Auto-approve mutating tool calls (approval gate) |
| `--workspace` | Working directory (default: cwd) |

## Exit codes

- `0` — success; JSON summary on stdout
- `1` — connect failure, tool error, or exception

## Example GitHub Action

```yaml
- name: Aion agent fix
  run: |
    aion agent run \
      --task "Summarize test failures and propose a minimal fix" \
      --provider nvidia \
      --yes
  env:
    NVIDIA_API_KEY: ${{ secrets.NVIDIA_API_KEY }}
```

Stdout is a single JSON object: `{"ok": true, "response": "..."}` or `{"ok": false, "error": "..."}`.
