# Aion Usage Dashboard (React)

**Not** the old HTML chat on port 3333 — that is usually another app (PHP). Aion uses **port 3847** by default.

## Run (recommended)

```bash
# From repo root — builds React + opens browser
./aion/usage/run_dashboard.sh

# Or if aion is installed:
aion usage
```

Open: **http://127.0.0.1:3847/** (not port 3333 — that may be another app)

Agent `/usage` slash command: **not available** (no `pytekt agent` in 0.2.0). Use `aion usage` today.

### What you see (React)

1. **Hardware** — CPU % per core (animated bars), overall CPU/RAM/disk, GPU util & VRAM, live charts, top processes  
2. **LLM usage** — today’s tokens, cost, provider charts, recent API calls

Requires for full hardware stats: `pip install 'pytekt[monitor]'` (psutil; optional NVIDIA GPU)

## React dev mode (hot reload)

```bash
# Terminal 1 — API server
python3 -m pytekt.cli usage --no-browser

# Terminal 2 — Vite dev server (proxies /api to 3847)
cd aion/usage/web && npm install && npm run dev
```

Then open **http://localhost:5173**

## Rebuild production UI

```bash
cd aion/usage/web && npm install && npm run build
```

Output: `aion/usage/static/` (served by Python).
