# Aion Agent Web UI

Codex-style browser interface for the Aion coding agent.

## Launch

```bash
# Build React UI and start server (recommended)
./aion/cli_agent/run_web.sh

# Or if aion is installed
aion agent web
```

Open: **http://127.0.0.1:3860/**

From the terminal agent, type **`/web`** to open the UI in your browser.

## Dev mode (hot reload)

```bash
# Terminal 1 — API server
python3 -m aion.cli agent web --no-browser

# Terminal 2 — Vite dev server (proxies /api to 3860)
cd aion/cli_agent/web/ui && npm install && npm run dev
```

Then open **http://localhost:5175**

## Features

- Connect providers (Ollama, NVIDIA NIM)
- **Mode dropdown** — plain, agent, debug, plan, review, test
- **Trust toggle** — enable workspace write/run tools
- **Undo** — restore last file snapshot
- Chat with **live tool progress** on the chat SSE stream (ThinkingBar + activity)
- **Plain mode** — real token streaming when the provider supports it
- **Copy buttons** on code blocks and messages
- **Slash commands** in composer — `/mode`, `/undo`, `/reset`, `/approve`, `/help`, …
- **Help panel** — `?` in header or `/help`
- File tree with @ attach and pin (right-click)
- Diff approval modal when `agent.approval_gate: true`
- Plan banner with approve button in plan mode

## Security

The server binds to **127.0.0.1** by default. Use `--host 0.0.0.0` only on trusted networks — the agent can edit files when trust is enabled.

## Config

Same as CLI agent (`~/.aion.yaml`): provider, model, pins, approval gate, workspace roots.
