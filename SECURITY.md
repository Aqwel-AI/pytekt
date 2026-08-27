# Security Policy & Hardening Guidelines

PyTekt takes security, memory safety, and token protection seriously across all layers—from the high-performance C++ native core to the declarative Python bot framework.

---

## 1. Supported Versions

| Version | Supported | Security Updates |
|---|---|---|
| **0.1.x / 0.2.x** | :white_check_mark: | Active |
| **< 0.1.0** | :x: | End of Life |

---

## 2. Reporting a Vulnerability

If you discover a security vulnerability within PyTekt (such as a memory safety issue, secret leak, or authentication bypass), **please do not open a public GitHub issue**.

### Responsible Disclosure Contact
- **Email:** `security@aqwelai.xyz` (or `aksel@aqwelai.xyz`)
- **PGP Key:** Available upon request for encrypted disclosure.

### What to Include
1. Description of the vulnerability and its potential impact.
2. Minimal proof-of-concept (PoC) code or test case reproducing the issue.
3. Target platform details (OS, Python version, architecture).
4. Proposed patch or mitigation if available.

### Response Timeline
- **Initial Response:** Within 24–48 hours.
- **Triage & Status Update:** Within 72 hours.
- **Coordinated Release & Advisory:** Target within 14 days of confirmation.

---

## 3. Security Architecture & Guarantees

### A. Secrets Protection
- **Masked Representations:** `TelegramBot`, `DiscordBot`, and `AI` instances mask credentials in `__repr__` and string outputs (e.g. `123456:***`).
- **Sanitized Logs & Exceptions:** Network exception loggers automatically redact bot tokens from API URLs.
- **Cache Isolation:** API keys and credentials are never stored or serialized into the C++ `Cache` or `FSM` state stores.
- **Environment Loading:** Default loading pattern reads tokens from environment variables (`TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`, `OPENAI_API_KEY`, etc.).
- **Automated CI Scanning:** The repository runs `scripts/scan_secrets.py` on every commit to prevent accidental leakage of credentials.

### B. C++ Memory Safety & Parsing Robustness
- **Bounded Deserialization:** The C++ `JsonParser` enforces a maximum parsing recursion depth (64 levels) and a 10MB input size ceiling to prevent stack overflows and memory exhaustion attacks.
- **ASan & UBSan:** C++ extensions can be built with `-fsanitize=address,undefined` via `PYTEKT_ENABLE_ASAN=1`.
- **Fuzz Testing:** Continuous fuzz testing targets `UniversalEvent` update parsers (`parse_telegram`, `parse_discord`, `parse_generic`) with malformed, deeply nested, and corrupted JSON payloads.

### C. Webhook Server & Header Authentication
- **Secret Token Validation:** Telegram webhooks can be secured with `X-Telegram-Bot-Api-Secret-Token` via `bot.run_webhook(secret_token=...)`, rejecting unauthenticated requests before event dispatch.
- **Endpoint Segregation:** Mini-App and Activity routes hosted via `bot.serve_web_app(path, ...)` are strictly isolated from internal bot event dispatching endpoints.

### D. AI Tool-Calling & Prompt Injection Defenses
- **Untrusted Model Output:** All arguments supplied by language models for `@ai.tool` invocations are treated as untrusted user input, validated against expected JSON structures and type signatures before execution.
- **RAG Prompt Injection Containment:** Retrieved knowledge base documents are enclosed within explicitly delimited `<retrieved_reference_documents>` tags with strict system instructions that untrusted documents cannot override system behavior or invoke unauthorized tools.

### E. Rate Limiting as DoS Protection
- **Multi-Scope Token Buckets:** Thread-safe C++ rate limiting applies separate buckets for `user`, `chat`, and `global` scopes.
- **Attacker Isolation:** Malicious floods from a single user or chat are dropped immediately without consuming rate limit quotas of other users or chats.

---

## 4. Developer Responsibilities

While PyTekt enforces framework-level guardrails, developers building bots must maintain the following security practices:

1. **Keep Secrets in Environment Variables:** Never commit `.env` files, API tokens, or webhook secrets to public version control.
2. **Sanitize Tool Logic:** Ensure custom `@ai.tool` functions validate domain-specific constraints (e.g. database access permissions, input path sanitization).
3. **Use HTTPS for Webhooks:** In production, always terminate TLS/HTTPS in front of `WebhookServer` using a reverse proxy (e.g. Nginx, Cloudflare, Caddy).
4. **Regular Dependency Audits:** Run `pip-audit` regularly to monitor third-party package vulnerabilities.
