# Aion IDE integration (design hook)

Future Cursor/VS Code extensions can write open editor state for the CLI agent.

## Sidecar protocol

Create `.aion/open_files.json` in the workspace root:

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

- The file exists
- `updated_at` is within the last 30 seconds (fresh IDE sync)

No extension ships in this phase; the CLI reads the sidecar when present.

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
