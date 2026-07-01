<p align="center">
  <img
    src="logo.png"
    alt="AION emblem — Aqwel AI transparent brand mark"
    width="250"
  />
</p>

# Aion

**Official open-source product from [Aqwel AI](https://aqwelai.xyz/) · v0.2.0**

[![PyPI](https://img.shields.io/pypi/v/aqwel-aion?label=PyPI)](https://pypi.org/project/aqwel-aion/)
[![Python](https://img.shields.io/pypi/pyversions/aqwel-aion?label=Python)](https://pypi.org/project/aqwel-aion/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Aqwel AI](https://img.shields.io/badge/Product-Aqwel%20AI-0066cc)](https://aqwelai.xyz/)

**Aion** is the flagship Python platform from **Aqwel AI**: one install for **research-grade ML** in notebooks and a **terminal coding agent** for day-to-day development. Apache-2.0, published on [PyPI](https://pypi.org/project/aqwel-aion/) as `aqwel-aion`.

| Pillar | Audience | Entry point |
|--------|----------|-------------|
| **Research library** (~50%) | AI researchers, data scientists, ML engineers | `import aion` |
| **Terminal agent** (~50%) | Developers who want a local coding assistant in the shell | `aion agent` |

Shared stack: **`aion.providers`** (OpenAI, Gemini, Anthropic, Ollama, DeepSeek, …), **`aion.agents`** (ReAct, planning), **`aion.tools`** (files, grep, shell). Install only what you need: `[ai]`, `[viz]`, `[rag]`, `[config]`, `[full]`.

**Official links:** [Aqwel AI website](https://aqwelai.xyz/) · [Product docs](https://aqwelai.xyz/#/docs) · [PyPI](https://pypi.org/project/aqwel-aion/) · [This repo — structure](docs/PROJECT_STRUCTURE.md) · [Security](SECURITY.md) · [`.env.example`](.env.example)

---

## About Aqwel AI

**Aqwel AI** builds practical AI tools for researchers and developers. **Aion** is our primary open-source product: a single Python package that replaces scattered scripts for numerics, classical ML, LLM workflows, experiment tracking, and—new in v0.2.0—a **terminal agent** that helps you read, edit, and run code in your project.

- **Company:** [aqwelai.xyz](https://aqwelai.xyz/)
- **Product:** Aqwel-Aion (`pip install aqwel-aion`)
- **Created by:** [Aqwel AI](https://aqwelai.xyz/) · **Main developer:** Aksel Aghajanyan
- **License:** Apache-2.0 · **Support:** [CONTRIBUTING.md](CONTRIBUTING.md) · security: [SECURITY.md](SECURITY.md)

---

## Aion product documentation

This README is the **main documentation** for the GitHub repository. Deeper maps and agent-specific notes live in linked files below.

### Documentation map

| Document | What it covers |
|----------|----------------|
| **This README** | Full product overview, install, features, examples, architecture diagrams |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Two-pillar layout (library vs `cli_agent`) |
| [aion/cli_agent/README.md](aion/cli_agent/README.md) | Terminal agent commands and module layout |
| [docs/AGENT_WEB.md](docs/AGENT_WEB.md) | Browser agent UI (`/web`, dev mode, security) |
| [aion/algorithms/CATALOG.md](aion/algorithms/CATALOG.md) | Full algorithms catalog (572+ functions) |
| [aion/db/README.md](aion/db/README.md) | Unified database layer |
| [aion/universe/README.md](aion/universe/README.md) | Astronomy module |
| [SECURITY.md](SECURITY.md) | API keys, `~/.aion.yaml`, trust mode, safe publishing |
| [.env.example](.env.example) | Environment variables (copy to `.env` locally only) |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development and PR process |
| [aion/algorithms/README.md](aion/algorithms/README.md) | Algorithms module |
| [aion/visualization/README.md](aion/visualization/README.md) | Plotting and reports |
| [aqwelai.xyz/#/docs](https://aqwelai.xyz/#/docs) | Official web documentation (Aqwel AI) |

### Pillar 1 — Research library (`import aion`)

For **notebooks, papers, and pipelines**: NumPy-first classical ML, built-in datasets (no downloads), algorithms, RAG, tokenizers, `former` transformer training, trackers, LLM eval, Hub UI (`aion start`).

```bash
pip install "aqwel-aion[ai,viz]"    # or pip install -e ".[ai,viz]" from this repo
```

```python
import aion
from aion.datasets import load_iris
from aion.preprocessing import StandardScaler
from aion.models import GaussianNB
from aion.metrics import accuracy_score

ds = load_iris()
X = StandardScaler().fit_transform(ds.data)
clf = GaussianNB().fit(X, ds.target)
print(accuracy_score(ds.target, clf.predict(X)))
```

| Module area | Capabilities |
|-------------|--------------|
| `aion.maths`, `aion.algorithms` | Linear algebra; **572+** algorithms across 21 categories |
| `aion.preprocessing`, `aion.models`, `aion.metrics`, `aion.hyperopt` | Core ML stack (sklearn-style, NumPy-first) |
| `aion.datasets`, `aion.data` | 24+ built-in benchmarks, loaders, splits |
| `aion.providers`, `aion.tools`, `aion.rag`, `aion.agents` | LLM clients, tool loops, RAG, ReAct agents |
| `aion.tracker`, `aion.llm_eval`, `aion.cache`, `aion.store` | Experiments, eval metrics, caching, SQLite stores |
| `aion.former`, `aion.visualization`, `aion.ui` | Transformer training, plots/3D, Aion Hub |

CLI helpers: `aion start`, `aion usage` (token & cost dashboard), `aion embed`, `aion eval`, `aion benchmark`, `aion doctor` — see [Getting Started](#getting-started) and [Features](#features).

### Pillar 2 — Terminal coding agent (`aion agent`)

For **developers**: interactive shell assistant in your repo—connect to **Ollama** (all local models) or **NVIDIA NIM**, chat naturally, and use tools to read/edit files when needed.

```bash
pip install -e ".[ai,config]"
cp .env.example .env              # optional; never commit .env
aion agent
```

**First-time setup (API keys — private, not in git):**

| Method | Where keys are stored |
|--------|------------------------|
| `aion api add nvidia YOUR_KEY` | `~/.aion.yaml` (home directory) |
| Environment variables | `.env` on your machine (see [.env.example](.env.example)) |
| `/connect nvidia new` | Prompts for key, saves to `~/.aion.yaml` |

**Agent connect providers:** **Ollama** (local) and **NVIDIA NIM** (`/connect nvidia`, `NVIDIA_API_KEY`). The research library **`aion.providers`** still supports OpenAI, Gemini, Anthropic, DeepSeek, and OpenAI-compatible servers for notebooks and scripts—the terminal agent connect UI is intentionally limited to Ollama + NVIDIA.

**Slash commands inside the agent:**

| Command | Description |
|---------|-------------|
| `/` or `/help` | List commands (prefix autocomplete: `/con` → `/connect`) |
| `/connect ollama` | List all installed Ollama models; pick one |
| `/connect nvidia [model]` | Connect to NVIDIA NIM (API key required) |
| `/connect <provider> new` | Enter a new API key and connect |
| `/reconnect <provider>` | Replace API key and reconnect |
| `/disconnect [name]` | Go offline, or disconnect a named provider/model |
| `/disconnect forget` | Clear saved keys for disconnected providers |
| `/web` | Open browser chat UI at http://127.0.0.1:3860/ |
| `/idle [minutes or off]` | Auto-disconnect after idle (`off` = stay connected) |
| `/models` | Refresh session dashboard |
| `/init` | Create `AION.md` project notes in the workspace |
| `/quit` | Exit agent |
| `/usage` | Open usage dashboard in browser |

**Behavior:** Casual messages (e.g. “Hey”) use **chat-only** mode; coding tasks use **tool-assisted** ReAct (read file, edit, grep, run command when workspace trust is enabled). Session auto-restores last Ollama/NVIDIA provider and model from `~/.aion.yaml` on restart.

**Workspace trust:** When enabled, the agent can modify files and run shell commands in your project—only use in directories you control. See [SECURITY.md](SECURITY.md).

```mermaid
flowchart LR
  Dev[Developer] --> CLI[aion agent]
  CLI --> Conn[connect.py providers]
  Conn --> Ollama[Ollama local]
  Conn --> NVIDIA[NVIDIA NIM]
  CLI --> Agent[aion.agents ReAct]
  Agent --> Tools[aion.tools filesystem workspace]
  Tools --> Repo[Your project files]
  Conn --> Config["~/.aion.yaml private"]
```

More detail: [aion/cli_agent/README.md](aion/cli_agent/README.md).

### Agent Web UI (`/web`)

Browser chat for the same agent session—Grok/Gemini-style layout with Aion green (`#12B981`).

| Launch | URL |
|--------|-----|
| `/web` inside `aion agent` | http://127.0.0.1:3860/ |
| `aion agent web` | Same |
| `./aion/cli_agent/run_web.sh` | Builds React UI + starts server |

**Features:** live tool-step progress (ThinkingBar), SSE streaming (plain mode tokens; agent mode chunked reply), file drawer with `@` attach (debounced autocomplete), diff approval modal, plan banner. Web chat memory clears when the terminal session ends. Server uses a threaded HTTP handler so SSE and API requests run concurrently.

Full details: [docs/AGENT_WEB.md](docs/AGENT_WEB.md) · dev mode (Vite hot reload on port 5175).

### Quick start — choose your path

| I am a… | Do this |
|---------|---------|
| **Data scientist / researcher** | `pip install "aqwel-aion[ai]"` → `import aion` → see [Getting Started](#getting-started) |
| **Developer using terminal AI** | `pip install -e ".[ai,config]"` → `aion agent` → `/connect ollama` or `/connect nvidia` |
| **Both** | `pip install -e ".[full]"` from this repo |

---

## Author

**Aqwel-Aion** is an open-source product from **[Aqwel AI](https://aqwelai.xyz/)**.

| Name | Role | GitHub | LinkedIn |
|------|------|--------|----------|
| Aksel Aghajanyan | Main developer · CEO · Data Scientist | [@Aksel588](https://github.com/Aksel588) | [Aksel Aghajanyan](https://www.linkedin.com/in/aksel-aghajanyan/) |

**Created by:** Aqwel AI · **Main developer:** Aksel Aghajanyan

---

## Table of Contents

- [About Aqwel AI](#about-aqwel-ai)
- [Aion product documentation](#aion-product-documentation)
  - [Documentation map](#documentation-map)
  - [Pillar 1 — Research library](#pillar-1--research-library-import-aion)
  - [Pillar 2 — Terminal coding agent](#pillar-2--terminal-coding-agent-aion-agent)
  - [Agent Web UI](#agent-web-ui-web)
  - [Quick start — choose your path](#quick-start--choose-your-path)
- [Author](#author)
- [Overview](#overview)
- [What's new in 0.2.0](#whats-new-in-020)
  - [Everything new since v0.1.9](#everything-new-since-v019)
  - [Recent updates (since v0.2.0)](#recent-updates-since-v020)
- [Architecture and structure](#architecture-and-structure)
- [Package architecture and diagrams](#package-architecture-and-diagrams)
- [Optional dependency matrix](#optional-dependency-matrix)
- [Requirements](#requirements)
- [Installation](#installation)
- [Aion install animation](#aion-install-animation)
- [Getting Started](#getting-started)
- [Features](#features)
- [Usage Examples](#usage-examples)
- [Module Reference](#module-reference)
- [Supported Languages](#supported-languages)
- [Documentation and Resources](#documentation-and-resources)
- [What shows on GitHub](#what-shows-on-github)
- [Contributing](#contributing)
- [Author and License](#author-and-license)
- [Library Statistics](#library-statistics)

---

## Overview

**Aqwel-Aion** is a **dual-purpose Aqwel AI product**: the same package powers **library workflows** (`import aion`) and the **terminal agent** (`aion agent`). Both share providers, agents, and tools.

The research library gives you one coherent **import surface** for work that usually spans half a dozen ad-hoc utilities: **linear algebra and stats**, **classical algorithms** (search, arrays, **graphs** with shortest paths and components), a **Core ML stack** (`preprocessing`, `models`, `metrics`, `hyperopt`), **plotting** (1D/2D/training/**3D**, PDF/HTML figure bundles), **embeddings and evaluation**, **PDF/docs generation**, and **systems-style helpers** (files, watcher, Git).

**LLM-era additions** include **`aion.providers`** (REST chat for OpenAI, Gemini, Anthropic, and OpenAI-compatible servers), **`aion.tools`** (schemas, registry, multi-turn **tool loops** with `complete_turn`), **`aion.rag`** (chunking, **vector stores**, optional FAISS, `SimpleRAGIndex`), plus **`aion.io`** for streaming reads, atomic writes, and checksums.

**New in 0.2.0:** **Fifteen** new modules covering classical ML and the full AI application stack — **`aion.preprocessing`**, **`aion.models`**, **`aion.metrics`**, **`aion.hyperopt`** (NumPy-first Core ML), **`aion.agents`** (ReAct, planning, multi-agent orchestration with conversation memory), **`aion.cache`** (memory/disk/LLM caching with TTL), **`aion.data`** (CSV/JSON/JSONL loaders, dataset splitting, text augmentation, schema validation), **`aion.datasets`** (24 built-in benchmarks + synthetic generators + file I/O), **`aion.tokenizer`** (trainable BPE and WordPiece), **`aion.pipeline`** (step-based processing chains), **`aion.store`** (SQLite key-value, persistent vector store, chat history), **`aion.tracker`** (experiment logging and comparison), **`aion.llm_eval`** (similarity, faithfulness, toxicity, cost tracking), **`aion.structures`** (Trie, Bloom filter, LRU cache, heaps, Union-Find), **`aion.serve`** (FastAPI endpoints for chat, RAG, and models), **`aion.ui`** (Hub launchers, HTML reports, optional Gradio/Streamlit), plus **`aion start`** (Aion Hub browser dashboard with module explorer and Python playground).

The design goal is simple: **progressive disclosure**—core installs stay small; heavy stacks are behind **named extras** (`[viz]`, `[ai]`, `[full]`, `[tools]`, `[rag]`, `[serve]`, and others).

The **terminal agent** (`aion/cli_agent/`) adds an interactive layer on top: persisted connections in `~/.aion.yaml`, Ollama model menus, slash commands, and workspace-aware coding tools—documented in [Aion product documentation](#pillar-2--terminal-coding-agent-aion-agent).

---

## What's new in 0.2.0

Version 0.2.0 adds **15+ new modules** spanning the full AI application lifecycle — from the **Core ML stack** and built-in datasets through tokenization, agent orchestration, API serving, and the **Aion Hub** developer UI.

### Everything new since v0.1.9

v0.1.9 already included `aion.tools`, `aion.rag`, `aion.config`, `aion.env`, `aion.benchmarks`, provider `complete_turn`, partial graph algorithms, basic 3D/PDF viz, and extras `[tools]`, `[rag]`, `[config]`. It **removed** top-level `aion.datasets` and `aion.dataframe`.

**v0.2.0 adds everything below** (not in v0.1.9):

| # | Area | Package / entry | Key capabilities |
|---|------|-----------------|------------------|
| 1 | **Terminal agent** | `aion.cli_agent` · `aion agent` | Slash commands, trust, tools, `~/.aion.yaml`, `aion api` |
| 2 | **Agent framework** | `aion.agents` | ReAct, Planning, MultiAgent; SlidingWindow/Summary/TokenBudget memory |
| 3 | **Caching** | `aion.cache` | MemoryCache, DiskCache, LLMCache, `@cached` |
| 4 | **Data (restored)** | `aion.data` | CSV/JSON/JSONL, splits, augmentation, schema validation |
| 5 | **Datasets (restored)** | `aion.datasets` | 24 benchmarks, generators, `fetch`/`list_datasets`, file I/O |
| 6 | **Tokenizer** | `aion.tokenizer` | BPE, WordPiece, Vocabulary |
| 7 | **Pipelines** | `aion.pipeline` | Pipeline, FunctionStep, MapStep, FilterStep, BatchStep |
| 8 | **Store** | `aion.store` | KeyValueStore, PersistentVectorStore, ChatHistoryStore |
| 9 | **Tracker** | `aion.tracker` | Tracker/Run, compare_runs, best_run |
| 10 | **LLM eval** | `aion.llm_eval` | Similarity, faithfulness, toxicity, PII, cost tracking |
| 11 | **Structures** | `aion.structures` | Trie, BloomFilter, LRU, heaps, UnionFind |
| 12 | **Serve** | `aion.serve` | FastAPI `/chat`, `/rag`, `/health` |
| 13 | **Core ML** | `preprocessing`, `models`, `metrics`, `hyperopt` | NumPy-first sklearn-style stack |
| 14 | **UI / Hub** | `aion.ui` · `aion start` | React-style Python UI, Hub, HTML reports, optional Gradio/Streamlit |
| 15 | **Database** | `aion.db` | SQLite + MySQL/Postgres/Mongo/Redis; dict API, query builder |
| 16 | **Universe** | `aion.universe` | Coordinates, observing, orbits, cosmology, C++ fast path, web dashboard |
| 17 | **Experiments** | `aion.experiments` | `Experiment`, `BenchmarkSuite`, LaTeX export, `aion benchmark`, `aion doctor` |
| 18 | **Usage** | `aion.usage` | Token & cost dashboard (`aion usage`) |
| 19 | **NVIDIA provider** | `aion.providers` | `NvidiaProvider` / NIM integration (used by agent) |
| 20 | **New extras** | `pyproject.toml` | `[serve]`, `[db]`, `[universe]`, `[ui]` |
| 21 | **Bug fixes** | `aion.algorithms` | `matrix_*`, scaling helpers; `a_star`/`pagerank` import fixes |

> **Note:** `aion.data` and `aion.datasets` were removed in v0.1.9 and **brought back in v0.2.0**.

### Terminal coding agent (`aion agent`) — Aqwel AI CLI product

- **`aion agent`** — Full-screen terminal assistant with Aion branding, intro animation, and slash commands.
- **Connect** — `/connect ollama` (all local models) or `/connect nvidia` (NIM); auto-restore from `~/.aion.yaml`.
- **Browser UI** — `/web` or `aion agent web` → http://127.0.0.1:3860/ ([docs/AGENT_WEB.md](docs/AGENT_WEB.md)).
- **Session persistence** — Saved provider, model, trust level, idle disconnect policy.
- **Coding tools** — Read/edit files, grep, run commands (with workspace trust).
- **Chat vs tools** — Greetings and Q&A without tool spam; coding tasks use ReAct + JSON tools.
- **API management** — `aion api add/list/disconnect`; keys never committed to git ([SECURITY.md](SECURITY.md)).

### Agent framework (`aion.agents`)
- **`ReActAgent`** — Observe/think/act loop with tool calling, configurable memory, and step logging.
- **`PlanningAgent`** — Task decomposition into numbered sub-steps, then tool-assisted execution of each.
- **`MultiAgent`** — Role-based orchestrator that delegates sub-tasks to specialized agents and synthesizes results.
- **Conversation memory** — `SlidingWindowMemory` (last N messages), `SummaryMemory` (LLM-compressed history), `TokenBudgetMemory` (fit within a token limit).

### Caching (`aion.cache`)
- **`MemoryCache`** — Thread-safe in-memory cache with optional per-key TTL and max-size eviction.
- **`DiskCache`** — SQLite-backed persistent cache with TTL.
- **`LLMCache`** — Cache LLM completions keyed by (messages, model, temperature); tracks hit/miss statistics.
- **`@cached` decorator** — Transparently cache any function's return value (memory or custom backend).

### Data processing (`aion.data`)
- **Loaders** — `load_csv`, `load_json`, `load_jsonl` with encoding and schema options; matching `save_*` functions.
- **Splitting** — `train_test_split`, `train_val_test_split`, `kfold_split` with optional stratification.
- **Text augmentation** — `random_delete`, `random_swap`, `random_insert`, `synonym_replace`, `augment_text`.
- **Schema validation** — `Schema`, `Field`, `validate_record`, `validate_dataset` for tabular data.

### Benchmark datasets (`aion.datasets`)
- **`Dataset` container** — NumPy `data` / `target`, feature and target names, metadata, `head()`, train/test split helpers.
- **Classic toy sets (in-memory, no download)** — `load_iris`, `load_digits`, `load_housing`, `load_moons`, `load_circles`, `load_blobs`, `load_wine`, `load_breast_cancer`, `load_diabetes`, `load_linnerud`.
- **NLP samples** — `load_sentiment`, `load_topics`, `load_ner` (BIO tags), `load_spam`, `load_qa` (RAG-style Q&A with contexts).
- **Synthetic generators** — `make_classification`, `make_regression`, `make_clusters`, `make_moons`, `make_circles`, `make_blobs`, `make_sparse_classification`, `make_time_series`, `make_multilabel`.
- **Registry** — `fetch("iris", return_split=True)`, `list_datasets()`, `summary("wine")`.
- **File I/O (`aion.datasets.io`)** — pandas-style loaders: `read_csv`, `read_json`, `read_jsonl`, `read_file` (auto-detect); with `[ai]`: `read_parquet`, `read_excel`, `from_dataframe`; export via `to_csv`, `to_json`, `to_parquet`, `to_dataframe`, `to_numpy`. Distinct from **`aion.data`** (row dicts for pipelines) and **`aion.former.datasets`** (LM text windows).

### User interfaces (`aion.ui`) — React-style frontend in Python
- **Component model** — `Component` base class + `@function_component` (like React class/function components).
- **`html` tags** — `html.div`, `html.button`, `html.h1`, … (like JSX; props use `className`, `onClick`).
- **`h()` / `Fragment`** — low-level `createElement` and fragment grouping (`<>...</>`).
- **Layout components** — `AppShell`, `Card`, `Stack`, `Row`, `MetricGrid`, `DataTable`, `Button`.
- **`render_app()` / `serve_app()`** — export a full HTML page or run a local dev server (stdlib).
- **Legacy reports** — `PageBuilder`, `build_experiment_dashboard()`, `build_dataset_report()`.
- **Hub & monitor** — `launch_hub()` / `aion start`, `launch_monitor()` (`[monitor]`).
- **Optional apps (`[ui]` extra)** — Gradio/Streamlit launchers.
- **CLI:** `aion ui --list`, `aion ui --report`, `aion ui --gradio`, `aion ui --streamlit`.
- **Install animation:** `aion welcome` — replay the animated module install screen ([see README](#aion-install-animation)).

### Tokenization (`aion.tokenizer`)
- **`BPETokenizer`** — Trainable byte-pair encoding: train on a corpus, encode/decode, save/load.
- **`WordPieceTokenizer`** — BERT-style sub-word tokenizer with `##` continuation tokens.
- **`Vocabulary`** — Bidirectional token↔id mapping with special tokens (`<pad>`, `<unk>`, `<bos>`, `<eos>`), save/load to JSON.

### Pipelines (`aion.pipeline`)
- **`Pipeline`** — Sequential chain of `Step` objects with per-step timing, retry, fallback, dry-run, and JSON serialization.
- **Built-in steps** — `FunctionStep`, `MapStep`, `FilterStep`, `BatchStep`.

### Persistent storage (`aion.store`)
- **`KeyValueStore`** — SQLite key-value store with namespace support.
- **`PersistentVectorStore`** — SQLite-backed vector store with brute-force cosine similarity search.
- **`ChatHistoryStore`** — Persistent conversation threads with message history, listing, and full-text search.

### Unified database (`aion.db`)
- **`connect(url)`** — One API for SQLite (core), MySQL, PostgreSQL, MongoDB, Redis (`pip install aqwel-aion[db]`).
- **Dict API** — `conn.users.insert({...})`, `conn.users.find(name="Alice")`, `find(score__gte=5)`.
- **Query builder** — `conn.table("users").where(conn.col.age > 25).select("name").all()`.
- **Aion-only** — `hybrid_search`, `agent_memory`, `bulk_upsert`, `sync_usage`, pipeline `DbReadStep` / `DbWriteStep`.
- See [`aion/db/README.md`](aion/db/README.md).

### Astronomy (`aion.universe`)
- **Coordinates** — RA/Dec ↔ Alt/Az, galactic transform, angular separation.
- **Time** — Julian date, GMST/LST for observing.
- **Observing** — Moon phase, air mass, `whats_up()` with builtin bright-star catalog.
- **Orbits & cosmology** — Kepler elements, Hohmann transfer, flat ΛCDM distances.
- **CLI & agent** — `aion universe moon|sky|coords|web`, agent `/sky` slash command (`aion cosmos` deprecated).
- **Web dashboard** — `aion universe web` (React sky map, moon, cosmology, observation log).
- **C++ fast path** — hot calculations in `aion._aion_universe` with Python fallbacks.
- See [`aion/universe/README.md`](aion/universe/README.md).

### Experiment tracking (`aion.tracker`)
- **`Tracker` / `Run`** — Log parameters, metrics (with step tracking), tags, and artifacts to a local directory.
- **`compare_runs` / `best_run`** — Sort and compare runs by any metric.

### Core ML stack

Four NumPy-first modules for classical ML workflows (sklearn-style `fit` / `transform` / `predict`, no scikit-learn required):

#### Preprocessing (`aion.preprocessing`)
- **Scalers** — `StandardScaler`, `MinMaxScaler`, `RobustScaler`, `Normalizer`.
- **Encoders** — `LabelEncoder`, `OneHotEncoder`, `OrdinalEncoder`.
- **Imputers** — `SimpleImputer` (mean, median, most_frequent, constant).
- **Transforms** — `PolynomialFeatures`, `Binarizer`, `KBinsDiscretizer`.
- **Composition** — `ColumnTransformer`, `PreprocessingPipeline` (named steps, `fit_transform`).

#### Models (`aion.models`)
- **Regression** — `LinearRegression`.
- **Classification** — `LogisticRegression` (binary), `KNNClassifier`, `GaussianNB`, `DecisionTreeClassifier`.
- **Regression (nonlinear)** — `KNNRegressor`, `DecisionTreeRegressor`.
- **Clustering** — `KMeans`.
- **Decomposition** — `PCA`.
- All estimators expose `fit`, `predict`, and `score` (accuracy for classifiers, R² for regressors).

#### Metrics (`aion.metrics`)
- **Classification** — `accuracy_score`, `precision_score`, `recall_score`, `f1_score`, `confusion_matrix`, `roc_auc_score`, `matthews_corrcoef`, `classification_report`.
- **Regression** — `mean_squared_error`, `root_mean_squared_error`, `mean_absolute_error`, `mean_absolute_percentage_error`, `r2_score`, `adjusted_r2_score`, `explained_variance_score`.
- **Clustering** — `silhouette_score`, `adjusted_rand_score`.
- **NLP** — `bleu_score`, `rouge_l_score`, `perplexity`.
- **Ranking** — `ndcg_score`, `mrr_score`.
- Distinct from **`aion.evaluate`** (legacy helpers and file-based prediction evaluation).

#### Hyperparameter optimization (`aion.hyperopt`)
- **`GridSearch`** — Exhaustive search over a discrete parameter grid with k-fold CV.
- **`RandomSearch`** — Random sampling from the grid.
- **`BayesianSearch`** — Lightweight acquisition over past trials (good for small grids).
- **`EarlyStopping`** — Stop search when CV score plateaus.
- **`cross_val_score` / `kfold_indices`** — Standalone CV utilities.
- Optional **`tracker`** integration — each trial logs params and `cv_score` to `aion.tracker`.
- **`MLPipeline`** — chain preprocessing + estimator; **`save_model` / `load_model`** for checkpoints.

### Research experiments (`aion.experiments`)
- **`Experiment`** — context manager: fixed `seed`, `tracker` logging, `manifest.json` for reproduction.
- **`export_results_table`** — paper-ready **LaTeX**, CSV, Markdown, HTML from tracker runs.
- **`BenchmarkSuite`** — multi-seed baselines on iris, wine, breast cancer, digits (`aion benchmark` CLI).
- **`aion doctor`** — environment check (Python, numpy, optional extras, tracker dir, C++ extension).
- **Stats** — `bootstrap_ci`, `compare_models`, `mcnemar_test` in `aion.metrics`.

### LLM evaluation (`aion.llm_eval`)
- **Semantic similarity** — `semantic_similarity`, `batch_similarity`, `relevance_score` using embeddings.
- **Faithfulness** — `faithfulness_score`, `check_groundedness` to verify RAG outputs against source documents.
- **Safety** — `toxicity_check` (keyword-based), `contains_pii` (emails, phones, SSNs, credit cards, IPs).
- **Cost tracking** — `estimate_cost` per provider, `CostTracker` for cumulative usage and spend.

### Data structures (`aion.structures`)
- **`Trie`** — Prefix tree for autocomplete and prefix search.
- **`BloomFilter`** — Probabilistic membership testing with tunable false-positive rate.
- **`LRUCache`** — Bounded least-recently-used cache with O(1) get/set and hit-rate tracking.
- **`MinHeap` / `MaxHeap` / `PriorityQueue`** — Heap-based priority queues.
- **`UnionFind`** — Disjoint-set with path compression and union by rank.

### API serving (`aion.serve`)
- **`AionServer` / `create_app`** — FastAPI application exposing `/chat`, `/rag`, `/health` endpoints.
- Custom route registration, CORS enabled. Reuses the same `[serve]` / `[monitor]` FastAPI dependency.

### Bug fixes
- Fixed missing `matrix_transpose`, `matrix_multiply`, `z_score_normalization`, `min_max_scaling` functions in `aion.algorithms.arrays`.
- Fixed `a_star` and `pagerank` import name mismatches in `aion.algorithms.graphs`.

### Recent updates (since v0.2.0)

Development in this repository after the v0.2.0 tag:

| Area | Highlights |
|------|------------|
| **Agent Web UI** | React UI at `:3860`, Grok/Gemini green theme, ThinkingBar, SSE streaming, `ThreadingHTTPServer`, graceful SSE disconnect |
| **Agent connect** | Ollama + NVIDIA only in connect UI; prefix command autocomplete; persistent NVIDIA restore |
| **Algorithms catalog** | **572** registered functions across **21** categories; `count_algorithms()`, `list_algorithms()`, [CATALOG.md](aion/algorithms/CATALOG.md) |
| **Visualization** | Seaborn in `[viz]`; Plotly 3D in `[viz3d]` extra |

---

## Architecture and structure

This part of the README is the **structural map** of the Aqwel AI **Aion** product: conceptual layers (diagrams), design rules, and a **file-level tree** of the `aion/` package. The **terminal agent** lives in `aion/cli_agent/` (see [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)).

### Package architecture and diagrams

The diagrams below are [Mermaid](https://mermaid.js.org/)—they render on GitHub and in many Markdown viewers.

#### Layered stack (how capabilities build on each other)

```mermaid
flowchart TB
  Foundation[Foundation NumPy plus stdlib]
  Core[Core maths algorithms parser code files text utils watcher evaluate]
  DataIO[io streaming and atomic writes]
  DataProc[data loaders splitting augmentation and tokenizer]
  Datasets[datasets benchmarks generators file IO]
  LLM[providers tools and embed]
  RAGModule[rag]
  Agents[agents ReAct planning multi-agent]
  Cache[cache memory disk LLM]
  Structures[structures Trie BloomFilter LRU heaps UnionFind]
  VizDoc[visualization and pdf]
  Former[former transformer stack]
  Pipeline[pipeline step chains]
  Store[store kv vectors chat history]
  Tracker[tracker experiment runs]
  LLMEval[llm_eval similarity faithfulness cost]
  Serve[serve FastAPI endpoints]
  CoreML[preprocessing models metrics hyperopt]
  UI[ui Hub HTML reports]
  CLIAgent[cli_agent terminal coding agent]
  Ops[config env benchmarks]
  Foundation --> Core
  Foundation --> Structures
  Core --> CoreML
  Core --> DataIO
  Core --> DataProc
  Core --> Datasets
  CoreML --> Tracker
  Core --> LLM
  DataIO --> RAGModule
  LLM --> RAGModule
  LLM --> Agents
  LLM --> CLIAgent
  Agents --> CLIAgent
  LLM --> LLMEval
  LLM --> Serve
  RAGModule --> Agents
  RAGModule --> Serve
  Core --> VizDoc
  Core --> Former
  Core --> Pipeline
  Foundation --> Cache
  Foundation --> Store
  Foundation --> Tracker
  Foundation --> Ops
```

#### Conceptual module map (import-oriented)

```mermaid
flowchart LR
  subgraph importSurface [Typical import paths]
    A["import aion"]
    B["aion.algorithms"]
    C["aion.visualization"]
    D["aion.providers"]
    E["aion.tools"]
    F["aion.rag"]
    G["aion.agents"]
    H["aion.cache"]
    I["aion.data"]
    I2["aion.datasets"]
    J["aion.tokenizer"]
    K["aion.pipeline"]
    L["aion.store"]
    M["aion.tracker"]
    N["aion.llm_eval"]
    O["aion.serve"]
    P["aion.structures"]
    Q["aion.preprocessing"]
    R["aion.models"]
    S["aion.metrics"]
    T["aion.hyperopt"]
    U["aion.ui"]
  end
  A --> B
  A --> C
  A --> D
  D --> E
  A --> F
  D --> G
  A --> H
  A --> I
  A --> I2
  A --> J
  A --> K
  A --> L
  A --> M
  A --> N
  A --> O
  A --> P
  A --> Q
  A --> R
  A --> S
  A --> T
  A --> U
  Q --> R
  R --> S
  R --> T
  T --> M
```

#### Tool-calling loop (OpenAI-shaped providers)

```mermaid
sequenceDiagram
  participant App as Your script
  participant RTL as run_tool_loop
  participant API as OpenAIProvider.complete_turn
  participant Reg as ToolRegistry
  App->>RTL: messages plus tool defs
  RTL->>API: complete_turn
  API-->>RTL: AssistantTurn tool_calls
  loop Each tool call
    RTL->>Reg: call name plus JSON args
    Reg-->>RTL: tool message content
  end
  RTL->>API: follow-up with tool results
  API-->>RTL: final text
  RTL-->>App: text plus full history
```

#### RAG pipeline (reference implementation)

```mermaid
flowchart LR
  T[Raw text] --> CH[chunk_text]
  CH --> E[embed_text]
  E --> VS[VectorStore]
  Q[User query] --> EQ[embed_text]
  EQ --> SR[search top-k]
  VS --> SR
  SR --> H[ScoredChunk hits]
```

### High-level design

- **Single package:** Public APIs live under `aion`. Prefer `import aion` and attribute access, or explicit `from aion.X import …` for subpackages.
- **Core single-file modules:** `maths`, `code`, `embed`, `evaluate`, `files`, `git`, `parser`, `pdf`, `prompt`, `snippets`, `text`, `utils`, `watcher`, `cli`, plus **`_core`** (`fast_*` bridge to optional native code).
- **Data and control plane:** `io` (streaming, atomic writes, checksums), `config` (implementation in `config/core.py`), `env`.
- **Data processing:** `data` (CSV/JSON/JSONL loaders as row dicts, splitting, augmentation, schema validation), `datasets` (built-in benchmarks, synthetic generators, `Dataset` + pandas-style file I/O), `tokenizer` (BPE, WordPiece, vocabulary management).
- **Developer UI:** `aion start` launches **Aion Hub** (`aion/hub/`) — module explorer, dependency checker, and in-browser Python playground (stdlib server).
- **LLM surface:** `providers` (chat REST, `complete` and `complete_turn` where supported), `tools` (OpenAI-style tool JSON, registry, retries, token bucket, optional tiktoken).
- **Retrieval:** `rag` (chunking, `MemoryVectorStore`, optional `FaissVectorStore`, `SimpleRAGIndex`).
- **Agents:** `agents` (ReAct, planning, multi-agent orchestration with sliding-window, summary, and token-budget memory).
- **Evaluation:** `llm_eval` (semantic similarity, faithfulness, toxicity, PII detection, cost tracking).
- **Caching:** `cache` (in-memory, SQLite disk, LLM-specific; TTL; `@cached` decorator).
- **Storage:** `store` (SQLite key-value, persistent vector store, chat history).
- **Pipelines:** `pipeline` (step-based chains with retry, fallback, timing, serialization).
- **Tracking:** `tracker` (experiment run logger with metrics, params, artifacts, comparison).
- **Core ML:** `preprocessing` (scalers, encoders, imputers, pipelines), `models` (linear, KNN, trees, KMeans, PCA, Naive Bayes), `metrics` (classification, regression, clustering, NLP, ranking), `hyperopt` (grid/random/Bayesian search with CV and tracker hooks).
- **Data structures:** `structures` (Trie, Bloom filter, LRU cache, heaps, Union-Find).
- **Serving:** `serve` (FastAPI-based `/chat`, `/rag`, `/health` endpoints).
- **Algorithms and visualization:** `algorithms` (search, arrays, **graphs**: BFS, DFS, toposort, Dijkstra, A*, components, MST, max flow, PageRank), `visualization` (1D/2D/training/**3D**, `save_figures_pdf`, HTML figure bundles).
- **Former:** NumPy autograd transformer training (`aion.former.*`), including **`aion.former.datasets`** for tokenizer and text windows.
- **Quality:** `benchmarks`.
- **Optional dependencies:** Heavy stacks behind extras (`[viz]`, `[ai]`, `[docs]`, `[full]`, `[tools]`, `[rag]`, `[config]`, …). LLM calls need network + API keys. **No `eval`** in tool execution—arguments are JSON-parsed and passed to registered callables only.
- **Native extension:** `src/aion_core.cpp` + pybind11 produces `aion._aion_core`; otherwise NumPy fallbacks.
- **Terminal agent:** `aion/cli_agent/` — `aion agent`, `aion api`, `aion config`; config in `~/.aion.yaml` (private).
- **Entry points:** `aion.cli` (`aion` console script), package metadata on `aion`, shims `agent_cli.py` / `api_cli.py` / `auth_cli.py`, repo `main.py`.

### Directory structure

Layout below matches the repository as shipped (file names only; omit your local `.venv`, build artifacts, and caches).

#### Repository root

```
.                              # Project root (clone / sdist)
├── README.md
├── aion-logo.png              # README hero / install animation branding
├── 0.1.9.png                  # Legacy release banner (optional)
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── .env.example                 # Template only — copy to .env locally (gitignored)
├── docs/
│   └── PROJECT_STRUCTURE.md     # Library vs terminal agent map
├── MANIFEST.in
├── pyproject.toml
├── setup.py
├── requirements.txt
├── example.py                 # Runnable demo (algorithms / visualization)
├── main.py                    # CLI entry script
├── src/
│   └── aion_core.cpp          # C++ sources for optional aion._aion_core (pybind11)
├── tests/                     # Pytest suite (64 tests: Core ML, algorithms, io, …)
│   ├── test_preprocessing.py
│   ├── test_models.py
│   ├── test_metrics.py
│   ├── test_hyperopt.py
│   ├── test_core_ml_integration.py
│   └── …
└── aion/                      # Python package (see next tree)
```

**Repo check:** The layout above is the **documented** shipping shape. The repository includes a **`tests/`** directory (run `pytest tests/` after `pip install -e ".[dev,ai]"`). If `import aion` fails after a partial checkout, restore package stubs with  
`git checkout HEAD -- aion/benchmarks/__init__.py`.  
The library surface is **`aion.code`** (`code.py` module only—not a `aion/code/` package). Do not keep empty `aion/agent/` or `aion/code/` folders (legacy cache-only dirs).

#### Package `aion/` (complete source tree)

Top-level names follow **lexicographic** order (`ls | sort`). This tree reflects the **current** repository layout, including LLM tools, RAG, infra, and 3D/report visualization.

```
aion/
├── __init__.py                # Version, metadata, public submodule exports
├── _core.py                   # fast_* → optional aion._aion_core or NumPy
├── agents/
│   ├── __init__.py
│   ├── action_detect.py       # Route chat-only vs tool-assisted turns
│   ├── json_tools.py          # Parse model JSON tool calls (CLI agent)
│   ├── memory.py              # SlidingWindowMemory, SummaryMemory, TokenBudgetMemory
│   ├── react.py               # ReActAgent (observe/think/act loop)
│   ├── planner.py             # PlanningAgent (decompose → execute)
│   └── multi.py               # MultiAgent (role-based delegation)
├── agent_cli.py               # Shim → cli_agent (``aion agent``)
├── agent_ui/                  # Shim → cli_agent.ui (``aion help``)
│   └── __init__.py
├── api_cli.py                 # Shim → cli_agent.api
├── auth_cli.py                # Shim → cli_agent.auth
├── algorithms/
│   ├── README.md
│   ├── __init__.py
│   ├── arrays.py
│   ├── examples/
│   │   ├── README.md
│   │   ├── 01_search_algorithms.ipynb
│   │   └── 02_array_utilities.ipynb
│   ├── graphs.py              # bfs, dfs, toposort, dijkstra, connected_components, …
│   └── search.py
├── benchmarks/
│   └── __init__.py            # timed_run, compare_sum_numpy_vs_fast
├── cache/
│   ├── __init__.py
│   ├── core.py                # Cache protocol, MemoryCache, DiskCache
│   ├── decorator.py           # @cached decorator
│   └── llm_cache.py           # LLMCache (prompt-keyed response cache)
├── cli.py                     # Main CLI router (``aion`` entry point)
├── cli_agent/                 # Terminal coding agent (``aion agent``)
│   ├── README.md
│   ├── __init__.py
│   ├── app.py                 # Chat loop, slash commands
│   ├── api.py                 # ``aion api`` connect/list/remove
│   ├── auth.py                # ``aion auth`` (login status)
│   ├── commands.py
│   ├── config.py              # ~/.aion.yaml load/save
│   ├── connect.py             # Provider wiring (Ollama menu, cloud APIs)
│   ├── connect_args.py        # Parse /connect, /disconnect, /reconnect
│   ├── constants.py
│   ├── session_prefs.py       # Persist provider, model, trust, idle
│   ├── tools.py               # Workspace tool registry for agent
│   ├── trust.py
│   └── ui/
│       ├── __init__.py
│       ├── aion_shell.py      # Dashboard, input prompt
│       ├── console.py         # Boot / intro
│       ├── glitch.py          # Logo intro animation
│       ├── help.py            # CLI command catalog
│       ├── menus.py
│       ├── messages.py
│       ├── slash_help.py
│       ├── status.py
│       └── style.py
├── code.py
├── config/
│   ├── README.md
│   ├── __init__.py            # Re-exports from core ([config] extra)
│   ├── core.py                # TOML/YAML, deep merge, env merge, dotted keys
│   └── examples/
│       ├── README.md
│       ├── __init__.py
│       ├── 01_config_loading_merge.ipynb
│       ├── sample.toml
│       └── sample_override.yaml
├── data/
│   ├── __init__.py
│   ├── loaders.py             # load_csv, load_json, load_jsonl + save_*
│   ├── splitting.py           # train_test_split, train_val_test_split, kfold_split
│   ├── augmentation.py        # random_delete, random_swap, synonym_replace, augment_text
│   └── schema.py              # Schema, Field, validate_record, validate_dataset
├── datasets/
│   ├── __init__.py
│   ├── _base.py               # Dataset dataclass, train_test_split_dataset
│   ├── toy.py                 # load_iris, load_digits, load_moons, load_wine, …
│   ├── text.py                # load_sentiment, load_topics, load_ner, load_spam, load_qa
│   ├── generators.py          # make_classification, make_regression, make_clusters, …
│   ├── loaders.py             # fetch, list_datasets, summary
│   └── io.py                  # read_csv, read_file, read_parquet, to_dataframe, …
├── embed.py
├── env/
│   └── __init__.py            # load_dotenv_file, require_env
├── evaluate.py
├── files.py
├── former/
│   ├── README.md
│   ├── __init__.py
│   ├── core/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── autograd.py
│   │   ├── operations.py
│   │   ├── tensor.py
│   │   └── examples/
│   │       ├── README.md
│   │       ├── __init__.py
│   │       └── demo_tensor.py
│   ├── datasets/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── tokenizer.py
│   │   └── examples/
│   │       ├── README.md
│   │       ├── __init__.py
│   │       └── demo_tokenizer.py
│   ├── docs/
│   │   └── architecture.md
│   ├── example.py
│   ├── example_attention.png      # Sample attention figure (docs / previews)
│   ├── example_training_metrics.png
│   ├── examples/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── attention_demo.py
│   │   ├── attention_demo_all_heads.png
│   │   ├── attention_demo_head0.png
│   │   └── text_generation.py
│   ├── examples_results/
│   │   ├── README.md
│   │   ├── example_attention.png
│   │   └── example_training_metrics.png
│   ├── experiments/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   ├── train_small_model.py
│   │   └── examples/
│   │       ├── README.md
│   │       ├── __init__.py
│   │       └── demo_config.py
│   ├── models/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── attention.py
│   │   ├── embedding.py
│   │   ├── feedforward.py
│   │   ├── transformer.py
│   │   └── examples/
│   │       ├── README.md
│   │       ├── __init__.py
│   │       └── demo_forward.py
│   ├── training/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── checkpoint.py    # weights npz + save_checkpoint_sidecar_meta
│   │   ├── loss.py
│   │   ├── optimizer.py
│   │   ├── trainer.py
│   │   └── examples/
│   │       ├── README.md
│   │       ├── __init__.py
│   │       └── demo_loss.py
│   └── visualization/
│       ├── README.md
│       ├── __init__.py
│       ├── attention_map.py
│       ├── training_metrics.py
│       ├── weight_spectrum.py
│       └── examples/
│           ├── README.md
│           ├── __init__.py
│           └── demo_attention_plot.py
├── git.py
├── hyperopt/
│   ├── __init__.py
│   ├── _cv.py                 # kfold_indices, cross_val_score
│   ├── search.py              # GridSearch, RandomSearch
│   ├── bayesian.py            # BayesianSearch
│   └── early_stopping.py      # EarlyStopping
├── hub/
│   ├── __init__.py
│   ├── launch.py              # aion start → open browser
│   ├── server.py              # stdlib HTTP API + static dashboard
│   └── static/
│       └── index.html         # Aion Hub UI (overview, playground, quick ref)
├── ui/
│   ├── __init__.py
│   ├── component.py           # Component, @function_component
│   ├── vdom.py                # VNode, h(), Fragment, render_vnode
│   ├── html_tags.py           # html.div, html.button, … (JSX-like)
│   ├── builtins.py            # AppShell, Card, MetricGrid, Stack, …
│   ├── render.py              # render_app, serve_app
│   ├── theme.py               # REACT_THEME_CSS
│   ├── html.py                # PageBuilder (legacy reports)
│   ├── dashboard.py           # build_experiment_dashboard, build_dataset_report
│   ├── launchers.py           # launch_hub, launch_monitor
│   └── apps.py                # Gradio / Streamlit (optional [ui] extra)
├── llm_eval/
│   ├── __init__.py
│   ├── similarity.py          # semantic_similarity, batch_similarity, relevance_score
│   ├── faithfulness.py        # faithfulness_score, check_groundedness
│   ├── toxicity.py            # toxicity_check, contains_pii
│   └── cost.py                # estimate_cost, CostTracker
├── io/
│   ├── README.md
│   ├── __init__.py
│   ├── atomic.py
│   ├── checksum.py
│   ├── streaming.py
│   └── examples/
│       ├── README.md
│       ├── __init__.py
│       └── demo_atomic_checksum.py
├── maths.py
├── metrics/
│   ├── __init__.py
│   ├── classification.py    # accuracy, precision, recall, F1, ROC-AUC, MCC
│   ├── regression.py        # MSE, RMSE, MAE, MAPE, R²
│   ├── clustering.py        # silhouette, adjusted Rand
│   ├── nlp.py               # BLEU, ROUGE-L, perplexity
│   └── ranking.py           # NDCG, MRR
├── models/
│   ├── __init__.py
│   ├── _base.py               # BaseEstimator (fit / predict / score)
│   ├── linear.py              # LinearRegression, LogisticRegression
│   ├── neighbors.py           # KNNClassifier, KNNRegressor
│   ├── clustering.py          # KMeans
│   ├── decomposition.py       # PCA
│   ├── naive_bayes.py         # GaussianNB
│   └── trees.py               # DecisionTreeClassifier, DecisionTreeRegressor
├── parser.py
├── pdf.py
├── pipeline/
│   ├── __init__.py
│   ├── core.py                # Pipeline, Step, PipelineResult
│   └── steps.py               # FunctionStep, MapStep, FilterStep, BatchStep
├── preprocessing/
│   ├── __init__.py
│   ├── _base.py               # TransformerMixin
│   ├── scalers.py             # StandardScaler, MinMaxScaler, RobustScaler, Normalizer
│   ├── encoders.py            # LabelEncoder, OneHotEncoder, OrdinalEncoder
│   ├── imputers.py            # SimpleImputer
│   ├── transforms.py          # PolynomialFeatures, Binarizer, KBinsDiscretizer
│   └── pipeline.py            # ColumnTransformer, PreprocessingPipeline
├── prompt.py
├── providers/
│   ├── README.md
│   ├── __init__.py
│   ├── anthropic_provider.py
│   ├── base.py
│   ├── deepseek_provider.py
│   ├── errors.py              # friendly_message() for API errors
│   ├── factory.py
│   ├── gemini_provider.py
│   ├── generic_openai.py
│   ├── http_utils.py
│   ├── keys.py                # resolve_api_key, ~/.aion.yaml + env
│   ├── ollama.py              # Local Ollama chat
│   ├── openai_provider.py
│   ├── structured.py          # AssistantTurn, NormalizedToolCall, parse_chat_completion_response
│   └── examples/
│       ├── README.md
│       ├── __init__.py
│       └── demo_factory_parse.py
├── rag/
│   ├── README.md
│   ├── __init__.py
│   ├── chunking.py
│   ├── pipeline.py            # SimpleRAGIndex
│   ├── types.py               # VectorStore, ScoredChunk
│   ├── stores/
│   │   ├── __init__.py
│   │   ├── faiss_store.py
│   │   └── memory.py
│   └── examples/
│       ├── README.md
│       ├── __init__.py
│       └── demo_simple_index.py
├── serve/
│   ├── __init__.py
│   └── app.py                 # AionServer, create_app (FastAPI chat/RAG/health)
├── snippets.py
├── store/
│   ├── __init__.py
│   ├── kv.py                  # KeyValueStore (SQLite)
│   ├── vector.py              # PersistentVectorStore (SQLite + cosine search)
│   └── chat_history.py        # ChatHistoryStore (threads + messages)
├── structures/
│   ├── __init__.py
│   ├── trie.py                # Trie (prefix tree)
│   ├── bloom_filter.py        # BloomFilter
│   ├── lru.py                 # LRUCache
│   ├── priority_queue.py      # MinHeap, MaxHeap, PriorityQueue
│   └── union_find.py          # UnionFind (disjoint-set)
├── text.py
├── tokenizer/
│   ├── __init__.py
│   ├── bpe.py                 # BPETokenizer (byte-pair encoding)
│   ├── wordpiece.py           # WordPieceTokenizer (BERT-style)
│   └── vocab.py               # Vocabulary (token↔id mapping)
├── tools/
│   ├── README.md
│   ├── __init__.py
│   ├── code_agent.py          # Coding-agent tool helpers
│   ├── fake_provider.py       # FakeToolProvider, make_tool_turn (offline demos)
│   ├── filesystem.py          # read_file, write_file, list_dir
│   ├── workspace.py           # Project-root scoped file ops
│   ├── loop.py                # run_tool_loop
│   ├── rate_limit.py
│   ├── registry.py
│   ├── retry.py
│   ├── schemas.py
│   ├── tokens.py
│   └── examples/
│       ├── README.md
│       ├── __init__.py
│       └── demo_tool_loop.py
├── tracker/
│   ├── __init__.py
│   ├── core.py                # Tracker, Run (experiment logging)
│   └── compare.py             # compare_runs, best_run
├── utils.py
├── visualization/
│   ├── README.md
│   ├── __init__.py
│   ├── arrays.py
│   ├── classification.py
│   ├── examples/
│   │   ├── README.md
│   │   ├── 01_array_visualization.ipynb
│   │   ├── 02_matrix_visualization.ipynb
│   │   └── 03_training_visualization.ipynb
│   ├── examples_visualization/  # committed plot previews (*.png)
│   │   ├── example_array.png
│   │   ├── example_array_mean.png
│   │   ├── example_confusion_matrix.png
│   │   ├── example_histogram.png
│   │   ├── example_matrix_heatmap.png
│   │   ├── example_multiple_arrays.png
│   │   ├── example_scatter.png
│   │   └── example_training_history.png
│   ├── matrices.py
│   ├── report.py              # save_figures_pdf, figures_to_html_img_tags
│   ├── three_d.py             # plot_3d_scatter, plot_3d_surface
│   ├── training.py
│   └── utils.py
└── watcher.py
```

After a local build, you may also see **`aion/_aion_core*.so`** (macOS/Linux) or **`aion/_aion_core*.pyd`** (Windows) next to these sources; those binaries are compiled outputs, not part of the documented source tree. **`__pycache__/`** is created at import time.

**Current `aion` surface (trimmed layout):** Subpackages include **`agents`**, **`algorithms`**, **`bench`**, **`benchmarks`**, **`cache`**, **`cli_agent`**, **`config`**, **`data`**, **`datasets`**, **`env`**, **`experiments`**, **`former`**, **`hub`**, **`hyperopt`**, **`io`**, **`llm_eval`**, **`metrics`**, **`models`**, **`monitor`**, **`pipeline`**, **`preprocessing`**, **`providers`**, **`rag`**, **`serve`**, **`store`**, **`structures`**, **`tokenizer`**, **`tools`**, **`tracker`**, **`ui`**, **`vision`**, and **`visualization`**, plus top-level modules (`cli.py`, `code.py`, `agent_cli.py`, …) and shims **`agent_ui/`**. **`aion.cli_agent`** powers **`aion agent`**; **`aion.data`** / **`aion.datasets`** / Core ML / **`aion.former`** / **`aion start`** (Hub) as above.

### Design principles

- **Explicit imports:** Subpackages re-export stable symbols from `__init__.py` (e.g. `from aion.algorithms import binary_search` or `from aion.algorithms.search import binary_search`).
- **Backend-safe visualization:** Plotting APIs return matplotlib `Figure` objects and support `show=False` for servers and CI; 3D uses `mpl_toolkits.mplot3d` (still `[viz]` / matplotlib).
- **Layered dependencies:** Core + algorithms target NumPy and the standard library where possible. `io` avoids heavy deps. `providers`, `tools`, and `rag` may require network keys or optional FAISS / sentence-transformers. Never install `[full]` unless you need the whole research stack.
- **Safety:** Tool execution uses **JSON object** arguments mapped to registered callables—no arbitrary code execution from model output.

---

## Optional dependency matrix

| Extra | Purpose | Notable dependencies |
|-------|---------|----------------------|
| *(base)* | Core library (incl. Core ML stack, data, datasets, cache, structures, pipeline, store, tracker, tokenizer, llm_eval, agents, hub) | `numpy`, `watchdog`, `gitpython` |
| `[viz]` | Plots (1D/2D/3D, reports) | `matplotlib`, `seaborn` |
| `[former]` | Aion Former training | `matplotlib`, `pyyaml` |
| `[ai]` | ML / transformers / pandas | `torch`, `transformers`, `pandas`, `scikit-learn`, … |
| `[docs]` | PDF generation | `reportlab`, `pillow` |
| `[dev]` | Tests and formatters | `pytest`, `black`, `flake8` |
| `[tools]` | Token counting for prompts | `tiktoken` |
| `[rag]` | Embeddings + FAISS index | `sentence-transformers`, `faiss-cpu` |
| `[config]` | TOML on older Python + YAML | `tomli` (3.8–3.10), `pyyaml` |
| `[serve]` | REST API serving | `fastapi`, `uvicorn` |
| `[db]` | MySQL, Postgres, Mongo, Redis backends for `aion.db` | `pymysql`, `psycopg`, `pymongo`, `redis` |
| `[universe]` | Astronomy plots for `aion.universe` | `matplotlib` |
| `[viz3d]` | Plotly 3D + enhanced viz (post-0.2.0) | `plotly`, `matplotlib`, `seaborn` |
| `[monitor]` | Hardware dashboard | `psutil`, `fastapi`, `uvicorn`, `nvidia-ml-py` |
| `[ui]` | Gradio / Streamlit app launchers | `gradio`, `streamlit` |
| `[full]` | Convenience “everything” set | Combines most stacks above (+ OpenAI client, tiktoken, etc.) |

Combine extras as needed, e.g. `pip install "aqwel-aion[viz,tools,serve]"` or editable `pip install -e ".[dev,full]"` from a clone.

---

## Requirements

- **Python:** 3.8 or higher (3.9 through 3.13 supported per package classifiers).
- **pip:** For installing the package and optional extras.
- **Core runtime:** `numpy>=1.21.0`, `watchdog>=2.1.0`, `gitpython>=3.1.0` (optional for Git features).
- **Optional:** SciPy, scikit-learn, pandas, matplotlib, ReportLab, sentence-transformers, PyTorch, vendor LLM credentials for `aion.providers`, etc. See [Installation](#installation) for extras.
- **Native extension (optional):** C++14 compiler and `pybind11` to build `aion._aion_core` from `src/aion_core.cpp`; otherwise fast helpers in `aion` use NumPy.

A virtual environment (e.g. `venv` or `conda`) is recommended to isolate dependencies.

---

## Installation

### Base install (required dependencies only)

```bash
pip install aqwel-aion
```

This installs the core package with numpy, watchdog, and gitpython. Enough for maths, algorithms, parser, files, utils, text, and most of the code and evaluate modules.

### Optional dependency groups

```bash
pip install aqwel-aion[viz]   # Visualization (matplotlib, seaborn)
pip install aqwel-aion[former] # Transformer training (Aion Former: matplotlib, pyyaml)
pip install aqwel-aion[ai]     # ML stack: scipy, scikit-learn, pandas, matplotlib, transformers, torch, sentence-transformers, openai
pip install aqwel-aion[docs]   # PDF/docs: reportlab, pillow
pip install aqwel-aion[full]   # All optional dependencies including seaborn, faiss-cpu
pip install aqwel-aion[dev]    # Development: pytest, black, flake8
pip install aqwel-aion[tools]  # tiktoken for token estimates
pip install aqwel-aion[rag]    # sentence-transformers + faiss-cpu
pip install aqwel-aion[config] # tomli on Python 3.8–3.10 + PyYAML
pip install aqwel-aion[serve]  # FastAPI + uvicorn for aion.serve
pip install aqwel-aion[db]     # MySQL, Postgres, Mongo, Redis for aion.db
pip install aqwel-aion[universe]  # Astronomy matplotlib plots
pip install aqwel-aion[viz3d]  # Plotly 3D visualization
pip install aqwel-aion[ui]     # Gradio + Streamlit for aion.ui apps
```

### Editable install (for development)

```bash
git clone https://github.com/aqwelai/aion.git
cd aion
pip install -e .[dev,full]
```

### Step-by-step (first-time setup)

1. Create and activate a virtual environment (recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

2. Upgrade pip and install the package:

   ```bash
   pip install --upgrade pip
   pip install aqwel-aion
   ```

3. For visualization and full ML/docs, use extras:

   ```bash
   pip install aqwel-aion[full]
   ```

4. Verify the install (you should see an **animated install screen** with large module names and ✓ INSTALLED lines):

   ```bash
   python -c "import aion; print(aion.__version__)"
   aion welcome    # replay the install animation anytime
   ```

   Disable the animation: `AION_NO_SPLASH=1 pip install aqwel-aion` or `aion welcome --no-animation`.

   See [Aion install animation](#aion-install-animation) for the logo and a full preview of the welcome screen.

5. (Optional) Run smoke tests from a clone:

   ```bash
   pip install -e ".[dev]"
   pytest tests/
   ```

---

## Aion install animation

<p align="center">
  <img src="aion-logo.png" alt="AION emblem — Aqwel AI brand mark" width="320"/>
</p>

<p align="center">
  <strong>Replay the install celebration in your terminal</strong>
</p>

After `pip install aqwel-aion` (or `pip install -e .` from a clone), Aion prints an animated screen: the **AION** banner, a large **INSTALLED** label, a progress bar, and each module name in **big spaced letters** with **✓ INSTALLED** (Core ML, datasets, agents, UI, and more).

### Command

```bash
# After pip install -e .  (or pip install aqwel-aion)
aion welcome
```

If `aion` is not on your `PATH` (common with conda / python.org installs):

```bash
python -m aion welcome
```

Static list (no animation delays, useful in CI or logs):

```bash
aion welcome --no-animation
# or
python -m aion welcome --no-animation
```

The animation also runs automatically at the end of **`pip install aqwel-aion`** and **`pip install -e .`**. To skip it:

```bash
AION_NO_SPLASH=1 pip install aqwel-aion
```

---

## Getting Started

### Verify installation

```python
import aion
print(aion.__version__)     # 0.2.0
print(aion.__author__)      # Aksel Aghajanyan
print(aion.__developer__)   # Aqwel AI Team (package metadata; main developer: Aksel Aghajanyan)
```

### Minimal example (no optional deps)

```python
import aion

# Mathematics (uses numpy; no optional deps)
r = aion.maths.addition(2, 3)           # 5
r = aion.maths.mean([1.0, 2.0, 3.0])    # 2.0
r = aion.maths.determinant([[1, 2], [3, 4]])  # -2.0

# Algorithms (stdlib only from aion.algorithms)
idx = aion.algorithms.binary_search([1, 3, 5, 7, 9], 7)  # 4
flat = aion.algorithms.flatten_array([[1, 2], [3, 4]])   # [1, 2, 3, 4]
```

### Minimal Core ML example (no scikit-learn)

```python
from aion.datasets import load_iris
from aion.preprocessing import StandardScaler
from aion.models import GaussianNB
from aion.metrics import accuracy_score

ds = load_iris()
X = StandardScaler().fit_transform(ds.data)
clf = GaussianNB().fit(X, ds.target)
print(accuracy_score(ds.target, clf.predict(X)))
```

### Run the CLI (if installed)

```bash
python -m aion.cli
# or, if entry point is installed:
aion --help
```

**High-value commands:**

| Command | Description |
|---------|-------------|
| `aion agent` | **Terminal coding agent** — connect LLMs, chat, edit project files ([docs](#pillar-2--terminal-coding-agent-aion-agent)) |
| `aion agent web` | **Browser agent UI** — http://127.0.0.1:3860/ ([docs/AGENT_WEB.md](docs/AGENT_WEB.md)) |
| `aion benchmark` | Run standard ML benchmark suite on built-in datasets |
| `aion doctor` | Environment check (Python, numpy, optional extras, tracker dir, C++ extension) |
| `aion usage` / `aion stats` | **Usage dashboard** (React) — tokens, cost, animated charts · [http://127.0.0.1:3847](http://127.0.0.1:3847) |
| `aion universe web` | Astronomy web dashboard (sky map, moon, cosmology) |
| `aion api connect` / `aion api add` | Manage provider API keys (stored in `~/.aion.yaml`) |
| `aion config` | CLI and agent settings |
| `aion start` / `aion ui` | Open **Aion Hub** (module explorer, playground, quick reference) |
| `aion ui --report DIR` | Build experiment HTML dashboard from tracker directory |
| `aion ui --list` | List all available UIs (hub, monitor, reports, Gradio, Streamlit) |
| `aion info` | Environment and optional dependency status |
| `aion monitor` / `aion dashboard` | Hardware metrics dashboard (`[monitor]` extra) |
| `aion embed <file>` | Embed a file or `--text` |
| `aion eval <preds> <answers>` | Evaluate predictions |
| `aion chat` | Interactive prompt REPL |
| `aion git status` | Git repository tools (needs GitPython) |

```bash
aion start                    # http://127.0.0.1:3000
aion start --port 8080        # custom port
aion start --no-browser      # server only
```

The repository includes root **`example.py`**: algorithms and visualization (sections 1–3), plus v0.1.9 areas ( **`aion.io`**, providers, tools, RAG, config, env, benchmarks, graphs, 3D/PDF, **`aion.pdf`** ). Run **`python example.py`** after installing dependencies for the sections you need (e.g. matplotlib for plots; **`[config]`** for the TOML sample in section 4).

---

## Features

### Mathematics and Statistics

- **71+ mathematical functions** for linear algebra, statistics, and numerical computation.
- **Linear algebra:** vectors, matrices, eigenvalues, SVD, determinant, inverse; optional SciPy for matrix exponential and logarithm with NumPy fallbacks.
- **Statistics:** correlation, regression, probability distributions, hypothesis testing, descriptive statistics.
- **Machine learning helpers:** activation functions (sigmoid, ReLU, tanh, etc.), loss functions, distance metrics.
- **Signal processing:** FFT, convolution, filtering, frequency analysis.
- **Trigonometry, logarithms, and basic arithmetic** with support for scalars, lists, and string numerals.

### Algorithms

- **572+ registered functions** across **21** categories — search, arrays, graphs, sorting, dynamic programming, trees, strings, math, queues/stacks, and more ([CATALOG.md](aion/algorithms/CATALOG.md)).
- **Discovery API:** `count_algorithms()`, `list_algorithms(category)`, `get_algorithm(name)`, `categories()`.
- **Core modules:** `search`, `arrays`, `graphs` — binary search, matrix ops, BFS/DFS, Dijkstra, PageRank, MST, max flow, and related helpers.
- Jupyter example notebooks in `aion/algorithms/examples/` with full API coverage and explanations.

### Visualization

- **1D arrays:** plot_array, plot_histogram, plot_scatter, plot_multiple_arrays, plot_array_with_mean, plot_running_mean; plot_boxplot, plot_density, plot_cdf; plot_error_bars, plot_rolling_std, plot_min_max_band; plot_autocorrelation, plot_quantiles, plot_scatter_with_fit, plot_dual_axis.
- **2D matrices:** plot_matrix_heatmap, plot_confusion_matrix (raw and normalized), plot_matrix_surface, plot_matrix_contour, plot_matrix_with_values; plot_correlation_matrix, plot_similarity_matrix; plot_matrix_histogram, plot_masked_heatmap; plot_attention_map, plot_matrix_sparsity.
- **Training:** plot_training_history, plot_metric, plot_train_vs_val, plot_learning_rate, plot_metric_with_best, plot_metrics_grid, plot_confidence_band, plot_early_stopping, plot_epoch_time.
- **3D & reports:** `plot_3d_scatter`, `plot_3d_surface`, `save_figures_pdf`, `figures_to_html_img_tags`; **seaborn** statistical plots (`[viz]`); **Plotly 3D** (`[viz3d]` extra).
- All matplotlib plotting functions return a `Figure`; use `aion.visualization.utils.save_plot(fig, path)` to save. Example notebooks in `aion/visualization/examples/`.

### AI Research and ML

- **Text embeddings:** Sentence-transformers integration and vector operations (e.g. cosine similarity).
- **Prompt engineering:** Specialized AI prompt templates and utilities for research workflows.
- **Code analysis:** Structural explanation, function/class/import extraction, comment stripping, cyclomatic complexity, docstring extraction, operator counts, code smell detection.
- **Model evaluation:** Classification metrics (accuracy, precision, recall, F1, confusion matrix, ROC-AUC), regression metrics (MSE, RMSE, MAE, R²); file-based evaluation (JSON/CSV) with automatic task detection.

### Documentation Generation

- **PDF and text:** Full API reference, user guides, changelogs, module dependency reports; configurable branding (colors, fonts, logo). ReportLab is optional—PDF entry points fall back to plain text when it is not installed.
- **Markdown and HTML:** `create_api_documentation_md` (TOC + per-module sections), `create_api_documentation_html` (self-contained static page, no extra deps).
- **Single module:** `create_module_reference_doc` writes Markdown, text, or PDF for one `aion.*` submodule; optional class and method listings.
- **Discovery:** `search_public_api(query)` finds public functions (and optionally classes) by name substring across documentable modules.
- **Exports:** `export_api_index` as JSON, CSV, or **Markdown table**; optional `include_classes=True`. `export_function_list`, dependency Mermaid snippets in text reports.
- **Introspection:** `generate_module_documentation(module, include_classes=False)` lists public functions; set `include_classes=True` for classes defined in that module and their public methods.

### Development and Infrastructure

- **File management:** Create, move, copy, delete; directory listing and organization helpers.
- **Safe I/O (`aion.io`):** `iter_lines`, `read_chunks`, atomic writes, SHA-256 `file_sha256` / `verify_sha256`. Runnable demo: `python -m aion.io.examples.demo_atomic_checksum`.
- **LLM providers (`aion.providers`):** `OpenAIProvider`, `GeminiProvider`, `AnthropicProvider`, `OpenAICompatibleProvider`, `create_provider`, `supported_providers`. OpenAI-shaped APIs also expose **`complete_turn`** → `AssistantTurn` with optional **`tool_calls`**; see `aion.providers.structured`. Offline demo: `python -m aion.providers.examples.demo_factory_parse`.
- **Tool calling (`aion.tools`, extra `[tools]` for tiktoken):** `function_tool`, `ToolRegistry`, `run_tool_loop`, `FakeToolProvider`, `make_tool_turn`, `post_json_with_retry`, `TokenBucket`, token estimation helpers. Offline demo: `python -m aion.tools.examples.demo_tool_loop`.
- **RAG (`aion.rag`, extra `[rag]`):** `chunk_text`, `MemoryVectorStore`, `FaissVectorStore`, `SimpleRAGIndex` over `aion.embed`. Local demo: `python -m aion.rag.examples.demo_simple_index`.
- **Config & runtime:** `aion.config` (TOML/YAML + env merge), `aion.env` (`.env` parsing). Use **`logging.basicConfig`** (stdlib) for log levels.
- **Benchmarks:** `aion.benchmarks` (timings, NumPy vs `fast_*` comparison).
- **Analytics:** Use **`aion.metrics`** for classification, regression, clustering, NLP, and ranking metrics; **`aion.evaluate`** remains for legacy/file-based workflows. Tabular ML prototyping uses **`aion.datasets`** (built-in sets + file I/O) with **`aion.models`** and **`aion.hyperopt`**; row-based ETL uses **`aion.data`**; full pandas/scikit-learn workflows are available via **`[ai]`** extras.
- **Former checkpoints:** `save_checkpoint_sidecar_meta` writes `.meta.json` via stdlib JSON.
- **Fast numerics (`aion` / `_core`):** Same `fast_*` API with or without the C++ extension—native build accelerates the hot paths; `using_native_extension` reports which path is active.
- **Visualization extras:** `plot_3d_scatter`, `plot_3d_surface`, `save_figures_pdf`, `figures_to_html_img_tags` in `aion.visualization` (matplotlib; `[viz]`).
- **Code parser:** Language detection and detailed analysis for 30+ programming languages (see [Supported Languages](#supported-languages)).
- **Real-time monitoring:** File change detection and callbacks via the watcher module.
- **Git integration:** Status, commit history, branches, diffs, file history (optional dependency: GitPython).
- **Utilities and CLI:** General helpers and command-line interface for common operations.

### Caching and Storage (new in 0.2.0)

- **Caching (`aion.cache`):** Thread-safe `MemoryCache` and SQLite `DiskCache` with per-key TTL; `LLMCache` for prompt-keyed response caching; `@cached` decorator for any function.
- **Persistent storage (`aion.store`):** `KeyValueStore` (SQLite with namespaces), `PersistentVectorStore` (cosine-similarity vector search), `ChatHistoryStore` (conversation threads with full-text search).

### Data Processing and Tokenization (new in 0.2.0)

- **Data (`aion.data`):** `load_csv`, `load_json`, `load_jsonl` loaders with matching savers; `train_test_split`, `train_val_test_split`, `kfold_split` with stratification; text augmentation (`random_delete`, `random_swap`, `random_insert`, `synonym_replace`, `augment_text`); schema validation (`Schema`, `Field`, `validate_record`, `validate_dataset`).
- **Datasets (`aion.datasets`):** 24 built-in benchmarks and generators; `Dataset` dataclass; `fetch`, `list_datasets`, `summary`; file I/O via `read_csv`, `read_file`, `read_parquet` (with `[ai]`), `to_dataframe`, `to_numpy` — see [What's new — Benchmark datasets](#benchmark-datasets-aiondatasets).
- **Tokenization (`aion.tokenizer`):** Trainable `BPETokenizer` (byte-pair encoding) and `WordPieceTokenizer` (BERT-style `##` continuations); `Vocabulary` with special tokens, save/load to JSON.

### User interfaces (new in 0.2.0)

- **`aion.ui` (React-style):** Build frontends in Python with `Component`, `html.*` tags, `AppShell`, `MetricGrid`, and `render_app()` — no React/Node install required; renders to static HTML.
- **Aion Hub:** `aion start` or `aion ui` — browse modules, check deps, run playground code (stdlib server).
- **HTML reports:** `PageBuilder`, `build_experiment_dashboard()`, `build_dataset_report()`.
- **Dev server:** `serve_app(MyApp(), port=8765)` for quick local preview.
- **Optional:** `pip install 'aqwel-aion[ui]'` for Gradio and Streamlit app launchers.

### Data Structures (new in 0.2.0)

- **`aion.structures`:** `Trie` (prefix tree for autocomplete), `BloomFilter` (probabilistic membership), `LRUCache` (bounded O(1) cache), `MinHeap`/`MaxHeap`/`PriorityQueue`, `UnionFind` (disjoint-set with path compression).

### Pipelines and Tracking (new in 0.2.0)

- **Pipelines (`aion.pipeline`):** `Pipeline` with composable `Step` objects; built-in `FunctionStep`, `MapStep`, `FilterStep`, `BatchStep`; per-step timing, retry, fallback, dry-run, JSON serialization.
- **Experiment tracking (`aion.tracker`):** `Tracker`/`Run` for logging parameters, metrics (with step tracking), tags, and artifacts to local JSON files; `compare_runs`/`best_run` for experiment comparison.

### Core ML stack (`aion.preprocessing`, `aion.models`, `aion.metrics`, `aion.hyperopt`)

- **Preprocessing:** Scalers, encoders, imputers, polynomial/binning transforms; `PreprocessingPipeline` and `ColumnTransformer` for composed feature engineering.
- **Models:** NumPy implementations of linear/logistic regression, KNN, decision trees, KMeans, PCA, and Gaussian Naive Bayes — sklearn-like API without sklearn.
- **Metrics:** Full metric suite for supervised learning, clustering, NLP generation quality, and ranking; use alongside or instead of `aion.evaluate`.
- **Hyperopt:** `GridSearch`, `RandomSearch`, `BayesianSearch` with k-fold cross-validation, `EarlyStopping`, and optional `Tracker` logging per trial.

### LLM Evaluation (new in 0.2.0)

- **`aion.llm_eval`:** `semantic_similarity`/`batch_similarity` (embedding-based); `faithfulness_score`/`check_groundedness` for RAG output verification; `toxicity_check` and `contains_pii` for safety; `estimate_cost`/`CostTracker` for LLM spend tracking across providers.

### Agent Framework (new in 0.2.0)

- **`aion.agents`:** `ReActAgent` (observe/think/act loop with tool calling), `PlanningAgent` (task decomposition then execution), `MultiAgent` (role-based delegation to specialized sub-agents); conversation memory strategies: `SlidingWindowMemory`, `SummaryMemory`, `TokenBudgetMemory`.

### API Serving (new in 0.2.0)

- **`aion.serve`:** `AionServer`/`create_app` builds a FastAPI application with `/chat`, `/rag`, `/health` endpoints; custom route registration; CORS enabled. Install with `[serve]`.

### Terminal coding agent (new in 0.2.0)

- **`aion agent`:** Full-screen terminal assistant with slash commands, workspace trust, and ReAct tool loop.
- **Connect:** Ollama (local models) and NVIDIA NIM; keys in `~/.aion.yaml`; prefix autocomplete on commands.
- **Browser UI:** `/web` or `aion agent web` — SSE chat at http://127.0.0.1:3860/ ([docs/AGENT_WEB.md](docs/AGENT_WEB.md)).
- **API CLI:** `aion api add/list/disconnect` for provider keys. See [Pillar 2](#pillar-2--terminal-coding-agent-aion-agent).

### Unified database (new in 0.2.0)

- **`aion.db`:** One API for SQLite (core), MySQL, PostgreSQL, MongoDB, Redis (`[db]` extra).
- **Dict API** — `conn.users.insert({...})`, `find(name="Alice")`, `find(score__gte=5)`.
- **Query builder**, hybrid search, agent memory, pipeline `DbReadStep`/`DbWriteStep`. See [`aion/db/README.md`](aion/db/README.md).

### Astronomy / universe (new in 0.2.0)

- **`aion.universe`:** RA/Dec ↔ Alt/Az, moon phase, air mass, orbits, flat ΛCDM cosmology.
- **CLI:** `aion universe moon|sky|coords|web`; agent `/sky` slash command.
- **Web dashboard:** `aion universe web` (React sky map, observation log).
- **C++ fast path** in `aion._aion_universe` with Python fallbacks. See [`aion/universe/README.md`](aion/universe/README.md).

### Research experiments (new in 0.2.0)

- **`aion.experiments`:** `Experiment` context manager (fixed seed, tracker logging, `manifest.json`).
- **`BenchmarkSuite`** — multi-seed baselines on iris, wine, breast cancer, digits (`aion benchmark` CLI).
- **`export_results_table`** — LaTeX, CSV, Markdown, HTML from tracker runs.
- **`aion doctor`** — environment and optional-dependency health check.

### Usage dashboard

- **`aion.usage`:** Token and cost tracking with browser dashboard (`aion usage` → http://127.0.0.1:3847).

### Aion Former — Transformer training

- **Decoder-only (GPT-style) transformers** with NumPy-backed autograd: no PyTorch/TF required for small-scale experiments.
- **Core:** `Tensor` with gradient tracking; `matmul`, `softmax`, `layer_norm`, `relu`, scaled dot-product attention.
- **Model:** Embedding, sinusoidal positional encoding, multi-head attention, feed-forward blocks, pre-norm stack, LM head.
- **Training:** Cross-entropy loss, Adam optimizer, `Trainer` with `train_step` / `train_epoch`.
- **Data:** Character- or word-level tokenizer, sliding-window text dataset, batch loader.
- **Visualization:** Attention heatmaps (per head/layer), training loss over epochs, weight eigenvalue/singular-value spectrum.
- **Install:** `pip install aqwel-aion[former]`. Run: `python -m aion.former.experiments.train_small_model`, `python -m aion.former.examples.attention_demo`, `python -m aion.former.examples.text_generation`. Per-subpackage demos: `python -m aion.former.core.examples.demo_tensor`, `aion.former.datasets.examples.demo_tokenizer`, `aion.former.experiments.examples.demo_config`, `aion.former.models.examples.demo_forward`, `aion.former.training.examples.demo_loss`, `aion.former.visualization.examples.demo_attention_plot`.

---

## Usage Examples

The following examples are drawn from the library and the project’s `example.py` and notebooks. They show how to use the main modules after installation.

### Mathematics and statistics

```python
import aion

# Basic arithmetic and statistics
aion.maths.addition(10, 5)
aion.maths.mean([1, 2, 3, 4, 5])
aion.maths.variance([1, 2, 3, 4, 5])
aion.maths.std_dev([1, 2, 3, 4, 5])
aion.maths.correlation([1, 2, 3, 4], [2, 4, 6, 8])
aion.maths.min_max_scale([1, 2, 3, 4, 5])
aion.maths.z_score([1.0, 2.0, 3.0, 4.0, 5.0])

# Linear algebra
aion.maths.determinant([[1, 2], [3, 4]])
aion.maths.dot_product([1, 2, 3], [4, 5, 6])
aion.maths.transpose([[1, 2], [3, 4], [5, 6]])
aion.maths.matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
aion.maths.normalize_vector([3, 4], norm="l2")

# Activations and ML helpers
aion.maths.sigmoid([0, 1, -1])
aion.maths.relu([-1, 0, 1, 2])
aion.maths.softmax([1.0, 2.0, 3.0])
```

### Algorithms: search and arrays

```python
import aion
from aion.algorithms import binary_search, lower_bound, upper_bound, flatten_array, chunk_array
from aion.algorithms.search import is_sorted, jump_search, find_peak_element, exponential_search
from aion.algorithms.arrays import sliding_window, rolling_sum, remove_duplicates

# Search (sorted list required for binary_search, lower_bound, upper_bound)
arr = [10, 20, 30, 40, 50, 60, 70]
binary_search(arr, 50)    # 4
lower_bound(arr, 35)     # 2
upper_bound(arr, 50)     # 5
is_sorted([1, 2, 3, 4])  # True
jump_search([1, 3, 5, 7, 9], step=2, target=7)
exponential_search([1, 3, 5, 7, 9], 9)
find_peak_element([1, 3, 2, 4, 1])  # [3, 4]

# Array utilities
flatten_array([[1, 2], [3, 4], [5]])
chunk_array([1, 2, 3, 4, 5, 6, 7], size=3)
list(sliding_window([1, 2, 3, 4, 5, 6], 3))
rolling_sum([1, 2, 3, 4, 5, 6], 3)
remove_duplicates([3, 1, 2, 1, 4, 2, 3])
```

### Safe I/O and checksums

```python
from pathlib import Path

from aion.io import atomic_write, file_sha256, iter_lines, verify_sha256

# Line iteration without loading the whole file
for line in iter_lines(Path("large.log")):
    if "ERROR" in line:
        alert(line)

# Atomic replace (crash-safe config writes)
atomic_write(Path("state.json"), '{"epoch": 3}')

digest = file_sha256(Path("dataset.bin"))
assert verify_sha256(Path("dataset.bin"), digest)
```

### LLM providers (remote APIs)

```python
from aion.providers import OpenAIProvider, create_provider, supported_providers
from aion.providers.base import ChatMessage

# Explicit provider (set OPENAI_API_KEY in your environment)
p = OpenAIProvider()
reply = p.complete([ChatMessage(role="user", content="Summarize Aion in one sentence.")])
print(reply)

# Factory by name (see supported_providers() for strings)
# p2 = create_provider("openai")
```

### Fast numerics (NumPy fallback or native extension)

```python
import aion

print("Native extension active:", aion.using_native_extension())
x = [1.0, 2.0, 3.0]
print(aion.fast_sum(x), aion.fast_mean(x), aion.fast_softmax(x))
print(aion.fast_norm1([-1.0, 2.0]), aion.fast_clip(x, 0.0, 2.5))
sorted_keys = [0.0, 0.5, 1.0, 1.5]
print(aion.fast_lower_bound(sorted_keys, 1.0), aion.fast_upper_bound(sorted_keys, 1.0))
```

### Visualization (requires matplotlib)

```python
import aion
from aion.visualization import (
    plot_array,
    plot_histogram,
    plot_scatter,
    plot_multiple_arrays,
    plot_array_with_mean,
    plot_running_mean,
    plot_matrix_heatmap,
    plot_confusion_matrix,
    plot_training_history,
)
from aion.visualization.utils import save_plot

# 1D plots (use show=False in scripts to avoid blocking)
fig = plot_array([1, 3, 2, 5, 4], title="Basic Array Plot", show=False)
save_plot(fig, "example_array.png")

fig = plot_histogram([1, 2, 2, 3, 3, 3, 4, 4, 4, 4], bins=4, title="Value Distribution", show=False)
save_plot(fig, "example_histogram.png")

fig = plot_scatter(x=[1, 2, 3, 4, 5], y=[5, 4, 3, 2, 1], title="Scatter", show=False)
save_plot(fig, "example_scatter.png")

fig = plot_multiple_arrays(
    arrays=[[1, 2, 3, 4], [4, 3, 2, 1]],
    labels=["Increasing", "Decreasing"],
    title="Multiple Arrays",
    show=False,
)
save_plot(fig, "example_multiple_arrays.png")

fig = plot_array_with_mean([10, 12, 9, 11, 10, 13], title="Array with Mean", show=False)
save_plot(fig, "example_array_mean.png")

fig = plot_running_mean(
    [15, 16, 14, 17, 18, 20, 19, 21, 22, 20, 18, 17],
    window_size=6,
    show=False,
)
save_plot(fig, "example_running_mean.png")

# Matrix and training
fig = plot_matrix_heatmap([[1, 2, 3], [4, 5, 6], [7, 8, 9]], title="Matrix Heatmap", show=False)
save_plot(fig, "example_matrix_heatmap.png")

fig = plot_confusion_matrix(
    [[50, 5], [8, 37]],
    labels=["Negative", "Positive"],
    title="Confusion Matrix",
    show=False,
)
save_plot(fig, "example_confusion_matrix.png")

history = {"loss": [1.0, 0.7, 0.4, 0.25], "val_loss": [1.1, 0.8, 0.5, 0.3], "accuracy": [0.5, 0.65, 0.78, 0.85]}
fig = plot_training_history(history, show=False)
save_plot(fig, "example_training_history.png")
```

### 3D plots and figure reports (requires matplotlib, `[viz]`)

```python
import numpy as np
from aion.visualization import plot_3d_scatter, plot_3d_surface, save_figures_pdf

fig1 = plot_3d_scatter([0, 1, 2], [0, 1, 0], [0, 0, 1], title="Embedding preview", show=False)
x = np.linspace(-2, 2, 30)
y = np.linspace(-2, 2, 40)
X, Y = np.meshgrid(x, y)
Z = np.sin(X) + 0.1 * Y
fig2 = plot_3d_surface(x, y, Z, title="Loss landscape (example)", show=False)
save_figures_pdf([fig1, fig2], "report_figures.pdf")
```

### Core ML — preprocessing, models, metrics, hyperopt

```python
from aion.datasets import load_iris
from aion.preprocessing import StandardScaler, PreprocessingPipeline
from aion.models import GaussianNB
from aion.metrics import accuracy_score, classification_report
from aion.hyperopt import GridSearch
from aion.tracker import Tracker

ds = load_iris()
X = StandardScaler().fit_transform(ds.data)
clf = GaussianNB()
clf.fit(X, ds.target)
print("accuracy:", accuracy_score(ds.target, clf.predict(X)))
print(classification_report(ds.target, clf.predict(X)))

# Hyperparameter search with experiment tracking
tracker = Tracker(".aion_experiments")
from aion.models import KNNClassifier
search = GridSearch(
    KNNClassifier(),
    {"n_neighbors": [3, 5, 7, 11]},
    cv=3,
    tracker=tracker,
    tracker_run_name="iris_knn",
)
search.fit(ds.data, ds.target)
print(search.best_params_, search.best_score_)
```

### Research workflow — experiments, benchmarks, papers

```python
from aion.experiments import Experiment, BenchmarkSuite, export_results_table
from aion.experiments import export_results_file
from aion.tracker import Tracker
from aion.datasets import load_iris
from aion.models import GaussianNB, MLPipeline, save_model
from aion.preprocessing import StandardScaler
from aion.metrics import accuracy_score

# Reproducible run with manifest + tracker
with Experiment("iris_nb_v1", seed=42) as exp:
    ds = load_iris(seed=42)
    pipe = MLPipeline(StandardScaler(), GaussianNB())
    pipe.fit(ds.data, ds.target)
    exp.log_metrics(accuracy=accuracy_score(ds.target, pipe.predict(ds.data)))
    save_model(pipe.estimator, f"{exp.run_dir}/model", metadata={"dataset": "iris"})

# LaTeX table for a paper
runs = Tracker(".aion_experiments").list_runs()
print(export_results_table(runs, format="latex", metric_columns=["accuracy"]))

# Standard benchmark leaderboard
suite = BenchmarkSuite(seeds=[0, 1, 2, 3, 4])
print(suite.leaderboard_markdown(suite.run()))
```

```bash
python -m aion doctor
python -m aion benchmark --seeds 5 -o leaderboard.md
```

### Model evaluation (legacy `aion.evaluate`)

```python
import aion

# In-memory metrics (legacy API)
y_true = [0, 1, 1, 0, 1]
y_pred = [0, 1, 0, 0, 1]
metrics = aion.evaluate.calculate_classification_metrics(y_pred, y_true)

# Prefer aion.metrics for new code:
from aion.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
print(accuracy_score(y_true, y_pred), f1_score(y_true, y_pred))

pred_vals = [1.2, 2.1, 3.0]
true_vals = [1.0, 2.0, 3.2]
print(r2_score(true_vals, pred_vals), mean_squared_error(true_vals, pred_vals))

# File-based evaluation (JSON or CSV)
file_metrics = aion.evaluate.evaluate_predictions("preds.json", "answers.json")
```

### Code analysis

```python
import aion

source = """
def train_model(x, y):
    return x + y

class Trainer:
    pass
"""
aion.code.explain_code(source)
aion.code.extract_functions(source)
aion.code.extract_classes(source)
aion.code.extract_imports(source)
aion.code.strip_comments(source)
aion.code.analyze_complexity(source)
aion.code.extract_docstrings(source)
aion.code.count_operators(source)
aion.code.find_code_smells(source)
```

### File management and watcher

```python
import aion

aion.files.create_empty_file("research.txt")
# Other helpers: move, copy, delete, list files, etc.

def on_change(path):
    print("Changed:", path)
aion.watcher.watch_file_for_changes("data.csv", on_change_callback=on_change)
```

### Documentation generation (optional: reportlab for PDF)

```python
import aion

aion.pdf.generate_complete_documentation("my_docs")
aion.pdf.create_api_documentation("api_ref.pdf")
aion.pdf.create_api_documentation_html("api_ref.html")
aion.pdf.create_user_guide_pdf("user_guide.pdf")
aion.pdf.create_changelog_pdf("changelog.pdf")
aion.pdf.create_module_reference_doc("text", format="md")  # e.g. aion_text_reference.md
aion.pdf.export_api_index("api_index.md", format="md")
hits = aion.pdf.search_public_api("embed")  # [{"module", "kind", "name"}, ...]
# Also: create_api_documentation_md, create_text_documentation, create_module_dependency_doc,
# export_api_index(..., include_classes=True), validate_documentation, create_documentation_index, …
```

### Embeddings (optional: sentence-transformers)

```python
import aion

vec = aion.embed.embed_text("Machine learning research")
sim = aion.embed.cosine_similarity(vec1, vec2)
```

### Git (optional: gitpython)

```python
import aion

manager = aion.git.GitManager(".")
status = manager.status()
commits = manager.get_commit_history(limit=10)
```

### LLM tool loop (OpenAI or OpenAI-compatible, API keys required)

```python
from aion.providers import OpenAIProvider
from aion.tools import ToolRegistry, function_tool, run_tool_loop

registry = ToolRegistry()
registry.register("double", lambda n: n * 2, required_arg_keys=["n"])
tools = [
    function_tool(
        "double",
        "Return twice n",
        properties={"n": {"type": "number", "description": "input"}},
        required=["n"],
    )
]
provider = OpenAIProvider()
messages = [{"role": "user", "content": "Call double with n=21 once, then reply with the number only."}]
text, history = run_tool_loop(provider, messages, tools, registry, max_rounds=6)
```

### RAG-style index (in-memory store; use `[rag]` for FAISS + sentence-transformers)

```python
import numpy as np
from aion.rag import MemoryVectorStore, SimpleRAGIndex

store = MemoryVectorStore()
index = SimpleRAGIndex(
    store=store,
    embed_fn=lambda s: np.array([float(len(s)), float(s.count("a"))]),  # toy 2-D embedding
)
index.index_texts(["alpha research", "beta notes"], chunk_size=32, overlap=8)
hits = index.query("alpha", k=2)
```

### Caching

```python
from aion.cache import MemoryCache, DiskCache, LLMCache, cached

# In-memory cache with 5-minute TTL
cache = MemoryCache(default_ttl=300)
cache.set("result", {"accuracy": 0.95})
cache.get("result")  # {"accuracy": 0.95}

# Disk-backed persistent cache (SQLite)
disk = DiskCache(".my_cache.db", default_ttl=3600)
disk.set("config", {"lr": 0.001})

# LLM response cache (avoid repeated API calls)
llm_cache = LLMCache("disk", db_path=".llm_cache.db", default_ttl=86400)
# llm_cache.get(messages, model="gpt-4") → cached response or None

# Decorator: cache any function
@cached(ttl=60)
def expensive_computation(x):
    return x ** 2
```

### Data processing

```python
from aion.data import load_csv, load_jsonl, train_val_test_split, augment_text
from aion.data import Schema, Field, validate_dataset

# Load data
rows = load_csv("dataset.csv")
records = load_jsonl("data.jsonl")

# Split with stratification
train, val, test = train_val_test_split(
    rows, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42,
    stratify_key=lambda r: r["label"],
)

# Text augmentation
variants = augment_text("The quick brown fox jumps", num_variants=4, seed=42)

# Schema validation
schema = Schema(fields=[
    Field("name", str, required=True),
    Field("age", int, required=True, validator=lambda x: 0 < x < 150),
    Field("email", str, required=False),
])
result = validate_dataset(rows, schema)
# {"valid": True/False, "total": N, "errors": {...}}
```

### Benchmark datasets

```python
from aion.datasets import (
    load_iris, load_sentiment, make_classification,
    fetch, list_datasets, summary,
    read_csv, read_file, train_test_split_dataset,
)

# Built-in benchmarks (no download)
iris = load_iris()
print(iris.shape)          # (150, 4)
print(iris.feature_names)  # sepal_length, sepal_width, …
print(iris.head())

# Train/test split on Dataset objects
train, test = fetch("iris", return_split=True)
# or: train, test = train_test_split_dataset(iris, test_ratio=0.2, seed=42)

# Synthetic data at any scale
ds = make_classification(n_samples=10_000, n_features=50, n_classes=5, n_informative=20)

# NLP samples
sent = load_sentiment()    # 50 binary reviews
ner = load_ner()           # 20 BIO-tagged sentences

# Load from disk (pandas-style → Dataset)
ds = read_csv("train.csv", target_column="label")
ds = read_file("data.parquet", target_column="y")  # needs [ai] for Parquet

# Export
ds.to_csv("export.csv")
X, y = ds.to_numpy()       # sklearn-style
df = ds.to_dataframe()     # needs pandas

print(summary("wine"))
print(f"Available: {len(list_datasets())} datasets")
```

**`aion.data` vs `aion.datasets`:** use **`aion.data`** when you need a list of row dicts for pipelines and schema validation; use **`aion.datasets`** when you need a **`Dataset`** with NumPy arrays for ML prototyping, built-in benchmarks, or file round-trips.

### User interfaces — React-style frontend

```python
from aion.ui import (
    Component,
    html,
    AppShell,
    MetricGrid,
    Card,
    Stack,
    render_app,
    function_component,
)
from aion.datasets import load_iris
from aion.models import GaussianNB
from aion.metrics import accuracy_score
from aion.preprocessing import StandardScaler

# --- React-like component tree ---
@function_component
def MetricsPanel(props):
    return MetricGrid(metrics=props["metrics"])

class ExperimentDashboard(Component):
    def render(self):
        ds = load_iris()
        X = StandardScaler().fit_transform(ds.data)
        clf = GaussianNB().fit(X, ds.target)
        acc = accuracy_score(ds.target, clf.predict(X))
        return AppShell(
            title="ML Experiment",
            subtitle="Iris · Gaussian Naive Bayes",
            children=Stack(
                children=[
                    MetricsPanel(metrics={"accuracy": acc, "samples": ds.n_samples}),
                    Card(title="Next steps", children=[
                        html.p({}, "Tune with aion.hyperopt or log runs to aion.tracker."),
                    ]),
                ]
            ),
        )

render_app(ExperimentDashboard(), output="dashboard.html", open_browser=True)
# serve_app(ExperimentDashboard(), port=8765)  # local dev server

# --- Imperative HTML reports (legacy) ---
from aion.ui import PageBuilder, build_experiment_dashboard, launch_hub

page = PageBuilder("Training summary", subtitle="Run 42")
page.add_metrics({"accuracy": 0.94, "loss": 0.08})
page.save("summary.html")
build_experiment_dashboard(".aion_experiments", output="runs.html")
# launch_hub()  # Aion Hub at http://127.0.0.1:3000
```

```bash
aion ui --list
aion ui --report .aion_experiments -o experiments.html
aion ui --gradio          # needs pip install 'aqwel-aion[ui]'
aion ui --streamlit
```

### Tokenization

```python
from aion.tokenizer import BPETokenizer, WordPieceTokenizer

# Train a BPE tokenizer on your corpus
bpe = BPETokenizer(vocab_size=8000)
bpe.train(["Your training text here..."] * 100)
ids = bpe.encode("hello world")
text = bpe.decode(ids)  # "hello world"
bpe.save("my_tokenizer.json")

# WordPiece (BERT-style)
wp = WordPieceTokenizer(vocab_size=8000)
wp.train(["Your training text here..."] * 100)
tokens = wp.tokenize("unbelievable")  # ["un", "##believ", "##able"]
```

### Data structures

```python
from aion.structures import Trie, BloomFilter, LRUCache, UnionFind, PriorityQueue

# Trie for autocomplete
trie = Trie()
trie.insert("python"); trie.insert("pytorch"); trie.insert("pandas")
trie.starts_with("py")  # ["python", "pytorch"]

# Bloom filter for fast membership checks
bf = BloomFilter(expected_items=100_000, fp_rate=0.01)
bf.add("seen_user_123")
bf.might_contain("seen_user_123")  # True

# LRU cache
lru = LRUCache(capacity=1000)
lru.set("key", "value")

# Union-Find for connected components
uf = UnionFind()
uf.union("A", "B"); uf.union("B", "C")
uf.connected("A", "C")  # True

# Priority queue
pq = PriorityQueue()
pq.push("low-priority", priority=10)
pq.push("urgent", priority=1)
pq.pop()  # (1, "urgent")
```

### Pipelines

```python
from aion.pipeline import Pipeline, MapStep, FilterStep, FunctionStep

pipe = Pipeline([
    MapStep("tokenize", lambda text: text.lower().split()),
    FilterStep("remove_short", lambda tokens: len(tokens) > 2),
    FunctionStep("count", lambda data, ctx: {"count": len(data), "data": data}),
])
result = pipe.execute(["Hello World", "Hi", "Good morning everyone"])
detailed = pipe.execute_detailed(["Hello World", "Hi", "Good morning everyone"])
print(detailed.total_ms)  # execution time
```

### Persistent storage

```python
from aion.store import KeyValueStore, PersistentVectorStore, ChatHistoryStore
import numpy as np

# Key-value store
kv = KeyValueStore("app.db")
kv.set("user:1", {"name": "Alice", "role": "admin"}, namespace="users")
kv.get("user:1")  # {"name": "Alice", "role": "admin"}

# Persistent vector store
vs = PersistentVectorStore("vectors.db", dimension=384)
vs.add("doc1", np.random.randn(384).astype(np.float32), text="First document")
results = vs.query(np.random.randn(384).astype(np.float32), top_k=5)

# Chat history
chat = ChatHistoryStore("chat.db")
thread_id = chat.create_thread(title="Support conversation")
chat.add_message(thread_id, "user", "How do I reset my password?")
chat.add_message(thread_id, "assistant", "Go to Settings > Security...")
thread = chat.get_thread(thread_id)
```

### Unified database (`aion.db`)

```python
import aion.db as db

conn = db.connect("sqlite://./app.db")  # zero extra deps
conn.users.insert({"name": "Alice", "score": 10})
print(conn.users.find(name="Alice"))

# Query builder
rows = conn.table("users").where(conn.col.score > 5).select("name", "score").all()

# Remote DBs: pip install aqwel-aion[db]
# conn = db.connect("mysql://user:pass@localhost/mydb")
# conn = db.connect("mongodb://localhost:27017/mydb")

# CLI: aion db status | sync-usage | sync-tracker
# Agent: /db status | /db sync all
```

### Experiment tracking

```python
from aion.tracker import Tracker

tracker = Tracker(".experiments")
run = tracker.start_run("baseline_v1")
run.log_params({"lr": 0.001, "batch_size": 32, "epochs": 10})

for epoch in range(10):
    loss = 1.0 / (epoch + 1)  # simulated
    run.log_metric("loss", loss)
    run.log_metric("accuracy", 1 - loss * 0.5)

run.end()
# Compare all runs
best = tracker.compare_runs(metric_name="loss")
```

### LLM evaluation

```python
from aion.llm_eval import toxicity_check, contains_pii, estimate_cost, CostTracker

# Safety checks
tox = toxicity_check("Your LLM output here")
pii = contains_pii("Contact john@example.com or 555-123-4567")
print(pii)  # {"has_pii": True, "findings": {"email": [...], "phone": [...]}, ...}

# Cost tracking across multiple calls
tracker = CostTracker()
tracker.record("openai", prompt_tokens=1500, completion_tokens=800)
tracker.record("anthropic", prompt_tokens=2000, completion_tokens=1000)
print(tracker.summary())
# {"total_cost_usd": 0.031, "total_tokens": 5300, "call_count": 2, ...}
```

### Agents (requires LLM provider + API key)

```python
from aion.agents import ReActAgent, PlanningAgent, SlidingWindowMemory
from aion.providers import OpenAIProvider
from aion.tools import ToolRegistry, function_tool

# Set up tools
registry = ToolRegistry()
registry.register("calculate", lambda expression: str(eval(expression)))
tools = [function_tool("calculate", "Evaluate a math expression",
         properties={"expression": {"type": "string"}}, required=["expression"])]

# ReAct agent (reason + act loop)
agent = ReActAgent(
    provider=OpenAIProvider(),
    registry=registry,
    tools=tools,
    memory=SlidingWindowMemory(window_size=20, system_prompt="You are a helpful assistant."),
)
answer = agent.run("What is 234 * 567?")

# Planning agent (decompose → execute)
planner = PlanningAgent(provider=OpenAIProvider(), registry=registry, tools=tools)
result = planner.run("Calculate the average of 100, 200, and 300")
```

### API serving (requires pip install aqwel-aion[serve])

```python
from aion.serve import create_app
from aion.providers import OpenAIProvider

# Create a FastAPI app with /chat and /health endpoints
app = create_app(provider=OpenAIProvider())
# Run with: uvicorn module:app --port 8000
# POST /chat  {"messages": [{"role": "user", "content": "Hello"}]}
# GET  /health → {"status": "ok", "version": "0.2.0"}
```

### Aion Former — transformer training (optional: pip install aqwel-aion[former])

```python
import aion
from aion.former import Transformer, Trainer
from aion.former.datasets import create_dataloader
from aion.former.visualization import plot_attention_map, plot_training_metrics

text = "Your training corpus here. " * 100
dataset, get_batch = create_dataloader(text, seq_length=64, batch_size=32, level="char")
model = Transformer(
    vocab_size=dataset.vocab_size,
    embed_dim=128,
    num_heads=4,
    num_layers=2,
    max_seq_len=64,
)
trainer = Trainer(model, lr=0.001)
for epoch in range(10):
    loss = trainer.train_epoch(get_batch, 50)
    print(f"Epoch {epoch + 1}  loss = {loss:.4f}")
plot_training_metrics(trainer.history)
```

Run from command line: `python -m aion.former.experiments.train_small_model`, `python -m aion.former.examples.attention_demo`, `python -m aion.former.examples.text_generation`.

---

## Module Reference

| Module | Description |
|--------|-------------|
| `aion.maths` | Mathematics, statistics, linear algebra, ML helpers, signal processing. |
| `aion.io` | Streaming reads, atomic writes, SHA-256 checksum helpers. [`aion/io/README.md`](aion/io/README.md), [`aion/io/examples/`](aion/io/examples/). |
| `aion.providers` | Chat clients + `create_provider`; `complete` / **`complete_turn`**. [`aion/providers/README.md`](aion/providers/README.md), [`aion/providers/examples/`](aion/providers/examples/). |
| `aion` (`fast_*`, `using_native_extension`) | 1D/2D numerics: sums, dot/norms, mean/variance, argmin/max, min/max, ReLU/softmax/sigmoid/tanh/clip, cumsum, matvec, sorted `lower_bound` / `upper_bound`; C++ when `_aion_core` is built else NumPy. |
| `aion.algorithms` | **572+** functions across 21 categories; catalog API; search, arrays, graphs, sorting, DP, trees, strings, … [`CATALOG.md`](aion/algorithms/CATALOG.md). |
| `aion.visualization` | 1D/2D/training plots; heatmaps, confusion matrices, attention maps; **3D** plots; seaborn (`[viz]`); Plotly 3D (`[viz3d]`); multi-page **PDF** / HTML figure reports. |
| `aion.former` | Transformer training: Transformer, Trainer, TextDataset, tokenizer, attention/training/weight-spectrum plots. Install with `[former]`. See [`aion/former/README.md`](aion/former/README.md) and per-subpackage `examples/` (e.g. `aion/former/core/examples/`). |
| `aion.embed` | Text embeddings and vector similarity (optional: sentence-transformers). |
| `aion.evaluate` | Legacy classification/regression metrics; file-based evaluation. Prefer `aion.metrics` for new code. |
| `aion.preprocessing` | Scalers, encoders, imputers, transforms; `PreprocessingPipeline`, `ColumnTransformer`. |
| `aion.models` | `LinearRegression`, `LogisticRegression`, `KNNClassifier`/`KNNRegressor`, `KMeans`, `PCA`, `GaussianNB`, decision trees. |
| `aion.metrics` | `accuracy_score`, `f1_score`, `confusion_matrix`, `r2_score`, `silhouette_score`, `bleu_score`, `ndcg_score`, … |
| `aion.hyperopt` | `GridSearch`, `RandomSearch`, `BayesianSearch`, `EarlyStopping`, `cross_val_score`; integrates with `aion.tracker`. |
| `aion.experiments` | `Experiment`, `BenchmarkSuite`, `export_results_table` (LaTeX/CSV/MD); research reproducibility. |
| `aion.code` | Code explanation, extraction, complexity, docstrings, code smells. |
| `aion.prompt` | Prompt templates and utilities. |
| `aion.snippets` | Code snippet utilities. |
| `aion.pdf` | API/user-guide/changelog (PDF, text, Markdown, **HTML**), module dependency reports, `search_public_api`, `create_module_reference_doc`, `export_api_index` (JSON/CSV/**MD**), class-aware introspection. Optional ReportLab for PDF. |
| `aion.parser` | Language detection and code parsing (30+ languages). |
| `aion.files` | File and directory operations. |
| `aion.watcher` | Real-time file change monitoring. |
| `aion.git` | Git repository operations (optional: GitPython). |
| `aion.utils` | General utilities. |
| `aion.text` | Text processing. |
| `aion.cli` | Command-line interface: `aion start` (Hub), `info`, `embed`, `eval`, `chat`, `monitor`, `git`, … |
| `aion.ui` | **React-style:** `Component`, `html`, `render_app`, `AppShell`, `MetricGrid`, …; **legacy:** `PageBuilder`, `launch_hub`, dashboards; optional Gradio/Streamlit (`[ui]`). |
| `aion.hub` | Aion Hub static server (used by `aion.ui.launch_hub` / `aion start`). |
| `aion.tools` | Tool schemas, registry, `run_tool_loop`, `FakeToolProvider` / `make_tool_turn`, retry/rate-limit, token estimates (`[tools]`). [`aion/tools/README.md`](aion/tools/README.md), [`aion/tools/examples/`](aion/tools/examples/). |
| `aion.rag` | Chunking, vector stores, `SimpleRAGIndex` (`[rag]`). [`aion/rag/README.md`](aion/rag/README.md), [`aion/rag/examples/`](aion/rag/examples/). |
| `aion.config` | TOML/YAML load, layered files, dotted keys, env merge, typed coercion (`[config]`). See [`aion/config/README.md`](aion/config/README.md) and [`aion/config/examples/`](aion/config/examples/). |
| `aion.env` | `.env` file parsing, `require_env`. |
| `aion.benchmarks` | `timed_run`, NumPy vs `fast_sum` comparison. |
| `aion.cache` | `MemoryCache`, `DiskCache` (SQLite), `LLMCache`, `@cached` decorator — all with TTL. |
| `aion.structures` | `Trie`, `BloomFilter`, `LRUCache`, `MinHeap`, `MaxHeap`, `PriorityQueue`, `UnionFind`. |
| `aion.data` | CSV/JSON/JSONL loaders (row dicts), `train_val_test_split`, `kfold_split`, text augmentation, `Schema` validation. |
| `aion.datasets` | Built-in benchmarks (Iris, Digits, Moons, Wine, …), NLP sets (sentiment, NER, spam, Q&A), `make_*` generators, `Dataset`, `fetch`/`list_datasets`/`summary`, file I/O (`read_csv`, `read_file`, `read_parquet`, `to_dataframe`). |
| `aion.tokenizer` | `BPETokenizer`, `WordPieceTokenizer`, `Vocabulary` (save/load, special tokens). |
| `aion.pipeline` | `Pipeline`, `Step`, `FunctionStep`, `MapStep`, `FilterStep`, `BatchStep` — retry, fallback, timing. |
| `aion.store` | `KeyValueStore` (SQLite), `PersistentVectorStore`, `ChatHistoryStore` (threads + search). |
| `aion.db` | Unified DB: SQLite, MySQL, Postgres, Mongo, Redis — dict API + query builder. [`aion/db/README.md`](aion/db/README.md). |
| `aion.universe` | Astronomy: coordinates, observing, orbits, cosmology, catalogs (C++ accelerated). [`aion/universe/README.md`](aion/universe/README.md). |
| `aion.tracker` | `Tracker`, `Run` — log params, metrics, artifacts; `compare_runs`, `best_run`. |
| `aion.llm_eval` | `semantic_similarity`, `faithfulness_score`, `check_groundedness`, `toxicity_check`, `contains_pii`, `estimate_cost`, `CostTracker`. |
| `aion.agents` | `ReActAgent`, `PlanningAgent`, `MultiAgent`, `AgentRole`, `SlidingWindowMemory`, `SummaryMemory`, `TokenBudgetMemory`. |
| `aion.serve` | `AionServer`, `create_app` — FastAPI `/chat`, `/rag`, `/health` endpoints (`[serve]`). |
| `aion.cli_agent` | Terminal agent (`aion agent`) and browser UI (`aion agent web`, `/web`). [`aion/cli_agent/README.md`](aion/cli_agent/README.md). |
| `aion.usage` | Token/cost dashboard (`aion usage`). |

Package entry point and version:

```python
import aion
print(aion.__version__)  # 0.2.0
```

---

## Supported Languages

The parser and code analysis modules support the following (among others):

**Programming languages:** Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, Swift, Kotlin, Scala, Haskell, PHP, Ruby, Perl, Lua, Julia, R, MATLAB, Clojure, PowerShell, Bash.

**Markup and data:** HTML, CSS, SQL, JSON, XML, YAML, Markdown, Dockerfile, Terraform, Ansible.

See `aion.parser` and `aion.code` for language-specific behavior and APIs.

---

## Documentation and Resources

### Aqwel AI — official

| Resource | URL |
|----------|-----|
| **Aqwel AI (company & products)** | [https://aqwelai.xyz/](https://aqwelai.xyz/) |
| **Aion product documentation (web)** | [https://aqwelai.xyz/#/docs](https://aqwelai.xyz/#/docs) |
| **PyPI package** | [https://pypi.org/project/aqwel-aion/](https://pypi.org/project/aqwel-aion/) |

### Repository documentation (this project)

| Resource | Description |
|----------|-------------|
| [README.md](README.md) | **Primary doc** — product overview, both pillars, install, features, Mermaid architecture, module tree, examples |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Library vs terminal agent layout |
| [aion/cli_agent/README.md](aion/cli_agent/README.md) | `aion agent` slash commands and code map |
| [docs/AGENT_WEB.md](docs/AGENT_WEB.md) | Browser agent UI (`/web`, dev mode) |
| [aion/algorithms/CATALOG.md](aion/algorithms/CATALOG.md) | Full algorithms catalog (572+ functions) |
| [aion/db/README.md](aion/db/README.md) | Unified database layer |
| [aion/universe/README.md](aion/universe/README.md) | Astronomy module |
| [SECURITY.md](SECURITY.md) | Secrets, `~/.aion.yaml`, publishing checklist |
| [.env.example](.env.example) | Env var template (private `.env` is gitignored) |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute to Aqwel-Aion |
| [pyproject.toml](pyproject.toml) | Version, extras (`[ai]`, `[full]`, …), PyPI metadata |

### In-package and generated docs

- **`aion.pdf`:** `generate_complete_documentation(output_dir)` — API + user-guide bundles; or `create_api_documentation_html` / `create_api_documentation_md` for a single reference.
- **Module READMEs:** [aion/algorithms/README.md](aion/algorithms/README.md), [aion/visualization/README.md](aion/visualization/README.md).

### Example notebooks and runnable demos

| Area | Path |
|------|------|
| Algorithms | `aion/algorithms/examples/` — search, arrays |
| Visualization | `aion/visualization/examples/` — arrays, matrices, training |
| Config | `aion/config/examples/` — TOML/YAML merge |
| I/O & LLM | `aion/io/examples/`, `aion/providers/examples/`, `aion/rag/examples/`, `aion/tools/examples/` |
| Former (transformers) | `aion/former/examples/` and `aion/former/*/examples/` |
| Root scripts | `example.py`, `main.py` |

### CLI reference (summary)

| Command | Product area |
|---------|----------------|
| `aion agent` | Terminal coding agent |
| `aion api` / `aion auth` | Provider keys and auth |
| `aion start` / `aion ui` | Aion Hub browser UI |
| `aion embed`, `aion eval`, `aion rag`, `aion prompt` | Research / LLM utilities |
| `aion benchmark`, `aion doctor` | ML benchmarks and environment check |
| `aion welcome` | Install animation overview |
| `aion --help` / `aion help` | Full command catalog |

### Testing

```bash
pip install -e ".[dev,ai]"
pytest tests/
```

Includes Core ML, providers, connect args, JSON tools, and code-agent tools.

---

## What shows on GitHub

This repository is open source. The following **should show** (and are committed):

| Category | What shows |
|----------|------------|
| **Docs** | `README.md`, `docs/PROJECT_STRUCTURE.md`, `SECURITY.md`, `.env.example`, `aion/cli_agent/README.md`, `aion-logo.png`, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md` |
| **Config** | `pyproject.toml`, `setup.py`, `MANIFEST.in`, `requirements.txt` |
| **Source** | `aion/**/*.py`, `src/aion_core.cpp` |
| **Tests** | `tests/` — 64 pytest cases (algorithms, io, maths, text, snippets, pdf, Core ML stack); `pip install -e ".[dev]"` then `pytest tests/` |
| **Examples** | `example.py`, `main.py`; notebooks in `aion/algorithms/examples/`, `aion/visualization/examples/`, `aion/config/examples/`; `python -m` demos under `aion/io/examples/`, `aion/providers/examples/`, `aion/rag/examples/`, `aion/tools/examples/`, `aion/former/*/examples/` |
| **Example assets** | `aion/visualization/examples_visualization/*.png` (plot previews); `aion/former/examples/*.png` (attention demos); `aion/former/examples_results/*.png` when committed (see folder README) |
| **Repo meta** | `.gitignore` |

The following **do not show** (ignored via `.gitignore`):

- Build artifacts: `build/`, `dist/`, `*.egg`, `*.egg-info/`, compiled extension modules under `aion/_aion_core*.so` / `aion/_aion_core*.pyd`
- Python cache: `__pycache__/`, `*.pyc`, `*.pyo`
- Virtual environments: `.venv/`, `venv/`, `env/`
- Secrets: `.env`, `.env.*` (never commit; copy from [`.env.example`](.env.example))
- User config: `~/.aion.yaml`, `.aion.yaml`, `*.local.yaml` (API keys and agent settings — **private**)
- Credentials: `secrets/`, `credentials/`, `*.pem`, `*.key`
- ML artifacts: `wandb/`, `checkpoints/`, `*.pt`, `*.pth`, `*.ckpt`, `mlruns/`, local `data/private/`
- IDE/editor: `.idea/`, `.vscode/`, `.cursor/`
- OS files: `.DS_Store`
- Test/coverage: `.coverage`, `htmlcov/`, `.pytest_cache/`, `.mypy_cache/`, `.ipynb_checkpoints/`
- Generated output: `example_output/`, optional `aion/former/examples_results/*.png`
- Native builds: `aion/_aion_core*.so`, `aion/_aion_core*.pyd`

Full list: [`.gitignore`](.gitignore). Security notes: [`SECURITY.md`](SECURITY.md).

If something that should be hidden still appears, it was committed before being added to `.gitignore`. Remove it from tracking with `git rm -r --cached <path>` and commit.

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:

- How to report bugs and suggest features
- Development setup (`pip install -e .[dev,full]`)
- Code style (PEP 8, type hints, docstrings)
- Testing and documentation expectations
- Pull request and review process

---

## Author and License

**Aqwel-Aion** is an **Aqwel AI** open-source product.

- **Product:** Aqwel-Aion (Aion)  
- **Created by:** [Aqwel AI](https://aqwelai.xyz/)  
- **Main developer:** Aksel Aghajanyan  
- **Company:** [Aqwel AI](https://aqwelai.xyz/) · **Contact:** aqwelai.company@gmail.com  
- **Copyright:** 2025–2026 Aqwel AI  
- **License:** Apache-2.0 (see [LICENSE](LICENSE))

---

## Library Statistics

- **`aion/`** contains **35+ subpackages** including **`cli_agent`** (terminal + web UI), **`db`**, **`universe`**, **`experiments`**, **`usage`**, **`agents`**, **`providers`**, Core ML, **`former`**, **`hub`**, **`ui`**, and the rest listed in [Directory structure](#directory-structure).
- **63 public exports** in `aion.__all__` (up from 51 in v0.1.9), including **`preprocessing`**, **`models`**, **`metrics`**, **`hyperopt`**, and **`ui`**.
- **268 pytest cases** in `tests/` (Core ML, agent web, algorithms catalog, universe, io, maths, text, snippets, pdf).
- **572 algorithms** across **21** categories via `aion.algorithms` catalog API.
- **24 built-in datasets** via `aion.datasets` (10 toy/tabular, 5 NLP, 9 generators) plus pandas-style file loaders.
- **Core ML stack:** 4 subpackages — preprocessing (12 transformers), models (10 estimators), metrics (22 functions), hyperopt (grid/random/Bayesian search + CV).
- **19 `fast_*` entry points** (plus `using_native_extension`) for 1D/2D vector numerics, re-exported from `aion`.
- **71+ mathematical functions** in the maths module.
- **Aion Former:** Decoder-only transformer training with NumPy autograd, multi-head attention, and visualization (optional `[former]` extra).
- **Agent framework:** ReAct, planning, and multi-agent orchestration with pluggable conversation memory.
- **Terminal + browser agent:** `aion agent` and web UI at http://127.0.0.1:3860/.
- **Full AI pipeline** from data loading, tokenization, and augmentation through training, evaluation, caching, experiment tracking, and API serving.
- **Optional dependencies** for embeddings, PDF generation, serving, DB backends, astronomy, Plotly 3D, Parquet/Excel file I/O, and full PyTorch/sklearn stack; core modules work with minimal dependencies (numpy + stdlib).

---

**Aqwel-Aion** is built so you can move from **numeric and algorithmic baselines** through **classical ML** (preprocess → train → evaluate → tune) to **LLM-assisted workflows**, **autonomous agents**, **retrieval**, **experiment tracking**, and **production serving**—and, when you need it, **`aion agent`** in the terminal or browser for everyday coding—all in one **Aqwel AI** product with clear optional extras.

*Aqwel AI product · Main developer: Aksel Aghajanyan · [Documentation](https://aqwelai.xyz/#/docs) · [PyPI](https://pypi.org/project/aqwel-aion/)*
