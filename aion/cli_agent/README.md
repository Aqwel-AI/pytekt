<p align="center">
  <img src="../../aion-logo.png" alt="AION emblem — Aqwel AI brand mark" width="220"/>
</p>

# `aion.cli_agent` — terminal coding agent

Part of **Aqwel-Aion**, the open-source **Aqwel AI** product. Full documentation: [README — Terminal agent](../../README.md#pillar-2--terminal-coding-agent-aion-agent).

Interactive shell assistant: connect to **Ollama**, **OpenAI**, **Gemini**, **DeepSeek**, or **Anthropic**, then chat and edit code in your project.

## Run

```bash
aion agent
aion agent web    # Codex-style browser UI
```

Open the web UI: **http://127.0.0.1:3860/** — see [docs/AGENT_WEB.md](../../docs/AGENT_WEB.md).

## Commands (in the agent)

| Command | Description |
|---------|-------------|
| `/` | List slash commands |
| `/connect ollama` | Show all local models; pick one |
| `/connect <provider>` | Cloud provider |
| `/disconnect [name]` | Go offline |
| `/reconnect <name>` | New API key + connect |
| `/idle off` | Stay connected after restart (default) |
| `?` | Help |

## Private files (not in git)

| File | Contents |
|------|----------|
| `~/.aion.yaml` | API keys, saved provider/model, trust |
| `.env` (optional) | Environment API keys — use `.env.example` as template |

See [SECURITY.md](../../SECURITY.md) and [docs/PROJECT_STRUCTURE.md](../../docs/PROJECT_STRUCTURE.md).

## Code layout

| Module | Role |
|--------|------|
| `app.py` | Main chat loop, slash commands |
| `connect.py` | Provider connection (Ollama model menu, cloud APIs) |
| `connect_args.py` | Parse `/connect`, `/disconnect`, `/reconnect` |
| `session_prefs.py` | Persist provider, model, trust, idle policy |
| `config.py` | `~/.aion.yaml` load/save |
| `tools.py` | Workspace tool registry |
| `api.py` / `auth.py` | `aion api` and `aion auth` |
| `ui/` | Dashboard, intro, messages, help |

**Shims at package root:** `aion/agent_cli.py`, `aion/api_cli.py`, `aion/auth_cli.py`, `aion/agent_ui/` → re-export `cli_agent` for backward compatibility.

**Removed:** `aion/agent/` (legacy; do not recreate). The research library is `import aion`; coding tools also use `aion.tools.filesystem` and `aion.tools.workspace`.
