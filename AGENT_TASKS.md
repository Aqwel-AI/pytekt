# PyTekt Agent — Implementation Tasks & Roadmap

**Feature:** `pytekt agent` (Claude Code / Antigravity CLI-style autonomous terminal assistant)  
**Author:** Aksel Aghajanyan  
**Developed by:** Aqwel AI Team  
**Status:** Completed  

---

## Phase 1: API Connection & Provider Setup
- [x] **1.1 CLI `pytekt agent connect`**: Dedicated non-interactive and interactive CLI subcommands for API configuration.
- [x] **1.2 Connection Validation**: Real ping/test-completion verification for providers (OpenAI, Anthropic, Gemini, DeepSeek, Ollama, OpenRouter, NVIDIA NIM).
- [x] **1.3 Secure Key Persistence**: Safe storage in `~/.pytekt.yaml` and `.env` with file permissions.
- [x] **1.4 TUI `/connect` Integration**: Dynamic hot-reloading of sessions when switching providers or keys inside the TUI.

---

## Phase 2: Core Coding Assistant & Undo Engine
- [x] **2.1 File Edit Undo Stack (`UndoStack`)**: Pre-edit snapshots of files modified by `write_file` or `edit_file`.
- [x] **2.2 Slash Command `/undo`**: Instantly revert the last file modification made by the agent.
- [x] **2.3 Smart Context Mentions**: Resolve `@file`, `@git`, `@diff`, and `@tests` in user prompts before dispatching to the LLM.
- [x] **2.4 Command Confirmation Safety**: Interactive prompt `[y]es / [n]o / [a]lways` before executing shell commands.

---

## Phase 3: Self-Healing Test & Debugger (`pytekt agent fix` / `/fix`)
- [x] **3.1 Pytest Failure Diagnostics**: Automatically capture pytest tracebacks, identify failed assertion lines, and locate relevant files.
- [x] **3.2 Autonomous Repair Loop**: Formulate targeted edits, apply fixes, and re-run pytest in a self-healing loop.
- [x] **3.3 `/fix` Slash Command**: Run auto-healing directly inside an active agent session.

---

## Phase 4: Autonomous ML & Research Agent (`pytekt agent ml` / `/ml`)
- [x] **4.1 Dataset Profiling Tool**: Compute shapes, missing values, column types, and statistics for tabular datasets.
- [x] **4.2 Model Training & Benchmarking**: Train baseline estimators using `pytekt.models` and `pytekt.preprocessing`.
- [x] **4.3 Evaluation & Visualization**: Compute classification curves (`roc_curve`, `precision_recall_curve`) via `pytekt.metrics` and export summaries.

---

## Phase 5: Bot Architect Agent (`pytekt agent bot` / `/bot`)
- [x] **5.1 Natural Language Bot Generation**: Translate plain-text requirements into `pytekt.bots` architectures (Telegram, Discord, Slack).
- [x] **5.2 Automated In-Memory Validation**: Run generated handlers against `BotTestClient` to verify zero errors before finishing.

---

## Phase 6: Git & Code Review Agent (`pytekt agent review` / `/review`)
- [x] **6.1 Uncommitted Diff Review**: Analyze `git diff` for security risks (API keys, secrets, unescaped queries), bugs, and missing type hints.
- [x] **6.2 Conventional Commit Generator**: Auto-generate clean, standardized commit messages (`feat: ...`, `fix: ...`).

---

## Phase 7: Testing & Verification
- [x] **7.1 Unit Tests**: Comprehensive test suite covering session creation, tools, undo stack, provider connectors, and CLI flags.
- [x] **7.2 End-to-End Test Suite Pass**: 100% pass across all tests with `pytest`.
