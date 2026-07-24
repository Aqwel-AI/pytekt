# Aion IDE Bridge

VS Code / Cursor extension that keeps `.aion/open_files.json` fresh so `aion agent` can auto-attach open editors (see [docs/AGENT_IDE_INTEGRATION.md](../../docs/AGENT_IDE_INTEGRATION.md)).

## Install (development)

```bash
cd extensions/aion-ide
npm install
npm run compile
```

Then in VS Code or Cursor:

1. **Extensions: Install from Location…** → select this `extensions/aion-ide` folder, **or**
2. Open this folder and press F5 to launch an Extension Development Host.

## Behavior

- On editor focus / visible-tab changes, and every **20 seconds**, writes:

```json
{
  "updated_at": 1710000000.0,
  "files": [
    {"path": "src/main.py", "cursor_line": 42}
  ]
}
```

- Paths are workspace-relative.
- If the Aion web UI is running, also `POST`s paths to `http://127.0.0.1:3860/api/open-files`.

## Command

**Aion: Sync Open Files Now** — force an immediate sidecar write.
