# Aion IDE integration

The Aion agent auto-attaches open editor files when the workspace contains a fresh sidecar:

`.aion/open_files.json`

## Sidecar protocol

```json
{
  "updated_at": 1710000000,
  "files": [
    {"path": "src/main.py", "cursor_line": 42},
    {"path": "README.md"}
  ]
}
```

The agent auto-attaches files when:

- The file exists under the workspace
- `updated_at` is within the last **30 seconds** (fresh IDE sync)

`cursor_line` is optional (forward-compatible; the CLI may ignore it).

## Extension (shipped)

Use **[extensions/aion-ide/](../extensions/aion-ide/)** — a VS Code / Cursor extension that:

- Writes the sidecar on editor changes
- Heartbeats every 20s so the agent never sees a stale file
- Optionally notifies the agent web UI at `POST http://127.0.0.1:3860/api/open-files`

See [extensions/aion-ide/README.md](../extensions/aion-ide/README.md) for install steps.

Workspace `.vscode/` settings are gitignored in this repo; keep extension config under `extensions/aion-ide/` only.

## @ mentions

- `@path/to/file` — attach file content
- `@folder/` — attach folder listing + sample files
- `@git`, `@diff`, `@staged`, `@changed` — git context
- `@symbol:file.py:ClassName.method` — symbol block
- `@web:https://...` — fetched page text
- `@docs:python:asyncio` — curated docs

## Multi-root workspace

Configure extra roots in `~/.aion.yaml`:

```yaml
agent:
  workspace_roots:
    - /path/to/other-pkg
```

Use `/root add ../other-pkg` or prefix paths as `other-pkg/src/foo.py` when aliased.
