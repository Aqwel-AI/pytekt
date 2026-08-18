# Security Policy

## Reporting vulnerabilities

If you find a security issue, please **do not** open a public GitHub issue with exploit details.

Contact the maintainers privately (e.g. GitHub Security Advisories or email listed on [aqwelai.xyz](https://aqwelai.xyz/)).

## What this repository contains

- **Open-source Python code** — safe to publish.
- **No user secrets** — API keys must never be committed.

## What must stay private (never in git)

| Item | Where it belongs |
|------|------------------|
| API keys (OpenAI, Gemini, Anthropic, …) | Environment variables or `~/.pytekt.yaml` (when configured) |
| `.env` with real values | Your machine only (see `.env.example`) |
| `~/.pytekt.yaml` | Your home directory (private config / future agent settings) |
| Private datasets, checkpoints, experiment logs | Local folders (see `.gitignore`) |
| Cursor/IDE project state | `.cursor/`, `.vscode/` (ignored) |

Cloning this repo **does not** give anyone access to your accounts or files.

## Terminal coding agent (not available)

In **0.2.0**, `pytekt agent` is **not available**. When the agent returns in a future release and **workspace trust** is enabled, it may:

- Read and write files in your project
- Run shell commands (if trusted mode allows)

Only enable trust in directories you control. Review tool output before running in sensitive environments.

Today, LLM calls from Python use **`pytekt.providers`** with keys from the environment — never commit those keys.

## Before you `git push`

1. Run `git status` — ensure no `.env`, `*.yaml` with keys, or `credentials/` files are staged.
2. Use `cp .env.example .env` locally; never add `.env` to commits.
3. If a key was committed by mistake: rotate the key immediately, then remove it from git history.

## Dependency security

Install from PyPI or this repo with pinned extras. Run your own `pip audit` or Dependabot in CI for production use.
