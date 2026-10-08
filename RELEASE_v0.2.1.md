# PyTekt v0.2.1 — Release Notes & Feature Specification

**Release Version:** `v0.2.1`  
**Author:** Aksel Aghajanyan  
**Developed by:** Aqwel AI Team  
**License:** Apache-2.0  
**Repository:** [https://github.com/Aqwel-AI/pytekt](https://github.com/Aqwel-AI/pytekt)  
**PyPI:** [https://pypi.org/project/pytekt/](https://pypi.org/project/pytekt/)  

---

## Executive Summary

PyTekt `v0.2.1` is a major milestone release introducing **PyTekt Agent** — an autonomous terminal-native coding agent inspired by modern CLI assistants (such as Claude Code and Google Antigravity CLI), combined with a local-first LLM philosophy and our C++ high-performance engine for bots and scientific computing.

This release also delivers a compiled C++ core for multi-platform bots (`pytekt.bots`), enhanced machine learning evaluation metrics compatible with NumPy 1.x and 2.x, and cross-platform build fixes across Python 3.8 through 3.13 on Linux, macOS, and Windows.

---

## 1. PyTekt Agent (`pytekt agent`)

`pytekt agent` is an interactive AI coding assistant running directly inside your terminal with real file system access, shell execution capabilities, automatic undo snapshots, and multi-provider connectivity.

### 1.1 Local Ollama Auto-Detection (Zero-Setup & Offline First)
- **Automatic Probe:** On launch, the agent automatically probes `http://localhost:11434/api/tags` to detect running local Ollama servers.
- **Model Discovery:** Discovers locally installed models (e.g. `Aks3L/linkai_x_v1_2:latest`, `llama3.2`, etc.) and automatically selects the first available local model as the active session model.
- **No Cloud Keys Required:** When local Ollama is active, the agent starts immediately without prompting for API keys or requiring cloud connectivity.
- **Privacy & Cost:** 100% private, offline-capable, and completely free of token costs.

### 1.2 Zero-Emoji Developer Aesthetic
- Designed for professional developer environments: removed all emojis from the TUI in favor of clean, readable text badges:
  - Modes: `[CODE]`, `[TALK]`, `[ML]`, `[BOT]`, `[FIX]`, `[REVIEW]`
  - Status: `[OK]`, `[ERR]`, `[!]`, `[--]`, `*`, `>`
- High-contrast ANSI colors, clean box borders, and real-time Braille spinners.

### 1.3 Multi-Provider Ecosystem
Unified provider abstraction layer supporting tool-calling across:
- **Ollama:** `http://localhost:11434` (OpenAI-compatible v1 endpoint and native API tags)
- **Anthropic:** Claude 3.5 Sonnet, Claude 3.5 Haiku
- **OpenAI:** GPT-4o, GPT-4o-mini
- **Google Gemini:** Gemini 2.0 Flash, Gemini 1.5 Pro
- **DeepSeek:** DeepSeek-Chat, DeepSeek-Reasoner
- **NVIDIA NIM:** Meta Llama 3.1 8B/70B Instruct

### 1.4 Interactive Working Modes
Switch modes dynamically using `/mode <name>` or dedicated CLI subcommands:
- **`[CODE]` (Default):** Full read/write/edit access to workspace files, bash command execution with safety prompts, and git integration.
- **`[TALK]`:** Conversational reasoning and Q&A without any tool execution or file modifications.
- **`[ML]`:** Automated tabular dataset profiling, feature analysis, and baseline classifier fitting via `pytekt.models`.
- **`[BOT]`:** Scaffolds full bot architectures (Telegram, Discord, Slack) with handlers, models, and validation tests.
- **`[FIX]`:** Self-healing loop: parses pytest failures, inspects tracebacks, modifies code, and re-runs tests until they pass.
- **`[REVIEW]`:** Git diff auditor detecting security vulnerabilities (leaked credentials, SQL injection risks) and generating conventional commit messages.

### 1.5 Autonomous Tool Registry
The agent executes operations via structured tool-calling:
- `read_file(path, offset, limit)`: Workspace file reading with line-number tracking.
- `write_file(path, content)`: Creates or rewrites files with snapshot recording.
- `edit_file(path, old_string, new_string)`: Verbatim string replacement with atomic safety checks.
- `run_command(command)`: Terminal shell execution with interactive approval (`[y]es / [n]o / [a]lways`).
- `list_files(path)`: Recursive directory browsing with `.gitignore` awareness.
- `glob_search(pattern)`: Workspace pattern matching.
- `grep_search(query)`: High-speed text and symbol searching across project files.

### 1.6 Safety Nets: Reversible Actions & Undo Stack
- **`UndoManager`:** Every file modification creates a pre-change snapshot in memory.
- **`/undo` Command:** Reverts the previous file change or creation instantly, restoring original file contents verbatim.

### 1.7 Smart Prompt Context Expansion
Special token resolution within user prompts:
- `@file.py`: Inlines the specified file's contents into the prompt.
- `@git`: Inlines `git status` and changed file lists.
- `@diff`: Inlines current unstaged `git diff`.
- `@tests`: Inlines recent pytest output.

---

## 2. High-Performance Native Bots Framework (`pytekt.bots`)

A modular bot engine featuring a compiled C++ core with pure-Python fallbacks.

### 2.1 C++ Native Core (`_pytekt_bots_core` / `_native_core`)
- **`StreamPacer`:** Adaptive message editor for streaming LLM responses to chat platforms. Handles semantic boundaries (newlines, sentence breaks) and handles platform HTTP 429 rate limits.
- **`Dispatcher`:** High-throughput compiled Trie router for command and pattern dispatching.
- **`RateLimiter`:** Token-bucket algorithm providing atomic multi-scope flood control (per-user, per-chat, global).
- **`FSM` & `Cache`:** Thread-safe state machines and TTL session caching for dialog trees.
- **`AntiSpam` & `Metrics`:** Bloom filter duplicate message detection and Prometheus-compatible metrics exporter.
- **`_core_fallback.py`:** 100% pure-Python fallback for environments without a C++ toolchain.

### 2.2 Platform Adapters
- **`SlackBot`:** Events API integration, Slash commands, interactive block kit actions, URL verification challenge, and HMAC-SHA256 signature verification.
- **`TelegramBot`:** Long-polling and webhook server support, inline keyboards, message editing, and state management.
- **`DiscordBot`:** Gateway socket adapter with slash commands and message reactions.

### 2.3 UI & Testing Toolkit
- **Declarative UI:** `Keyboard`, `Button`, `Card`, `Modal`, `Wizard`.
- **Database:** `BotDB` SQLite backend for chat histories and state persistence.
- **Testing:** `BotTestClient` for synchronous and asynchronous in-memory testing of bot handlers without live API credentials.

---

## 3. Core Machine Learning & Data Enhancements

### 3.1 Evaluation Metrics (`pytekt.metrics`)
- Added `roc_curve`, `precision_recall_curve`, and `average_precision_score`.
- Implemented `_trapz` for safe trapezoidal numerical integration compatible across both **NumPy 1.x** and **NumPy 2.x** (`np.trapezoid` vs `np.trapz`).

### 3.2 Dataset Splitting (`pytekt.data`)
- Enhanced `train_test_split` supporting multiple synchronized arrays (`X`, `y`, `weights`).
- Preserves native NumPy array types and supports `test_size`, `train_size`, `random_state`, and `shuffle` parameters.

---

## 4. Build Systems, Cross-Platform Compatibility & CI Hardening

### 4.1 GCC / Linux Header Fix
- Resolved missing `#include <vector>` in `pytekt/bots/_core/ratelimiter.hpp` and `pytekt/bots/_core/ratelimiter.cpp`, fixing GCC compilation failures on Ubuntu Linux runners.

### 4.2 Python 3.10 Compatibility (PEP 701)
- Resolved `SyntaxError: f-string expression part cannot include a backslash` in `pytekt/agent/tui.py`.
- Verified clean compilation across Python 3.8, 3.9, 3.10, 3.11, 3.12, and 3.13 using `py_compile`.

### 4.3 Python 3.12 Build Isolation in CI
- Configured GitHub Actions CI workflows (`ci.yml` and `security.yml`) to explicitly pre-install `setuptools` and `wheel` before invoking `setup.py build_ext --inplace`.
- Added `setuptools>=64.0` and `wheel` to `[project.optional-dependencies].dev` in `pyproject.toml`.

### 4.4 Automated Test Suite
- Comprehensive suite of **407 passing unit and integration tests** verifying core algorithms, physics engines, astronomy engines, bot frameworks, and agent workflows.

---

## 5. Quick Start Guide

### Installation
```bash
pip install -U pytekt
```

### Launching PyTekt Agent
```bash
# Launch interactive TUI (auto-detects local Ollama if running)
pytekt agent

# Run a one-shot task
pytekt agent "Profile data.csv and generate a baseline classifier"

# Explicitly choose a provider
pytekt agent --provider ollama --model Aks3L/linkai_x_v1_2:latest
pytekt agent --provider anthropic --model claude-3-5-sonnet-latest
pytekt agent --provider openai --model gpt-4o
```

### In-Agent Slash Commands
- `/mode <code|talk|ml|bot|fix|review>`: Switch agent operational mode
- `/undo`: Revert the last file modification
- `/connect`: Configure or switch API keys and models
- `/history`: View session action history
- `/clear`: Reset conversation context
- `/help`: Show command documentation
- `/exit`: Exit agent session

---

## 6. Repository Cleanliness & Security Safeguards

- `.gitignore` updated with exhaustive wildcards blocking all secret files, API tokens, local markdown notes (`*secret*.md`, `*token*.md`, `*key*.md`, `*private*.md`, `TODO*.md`, `AGENT_TASKS.md`, `*.secret`, `*.token`, `auth.json`).
- Core repository documentation explicitly preserved (`README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `RELEASE_*.md`).
