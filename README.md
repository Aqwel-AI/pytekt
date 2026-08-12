<p align="center">
  <img src="0.2.0v.png" alt="Aqwel AI — PyTekt v0.2.0 major new release, now available" width="100%" />
</p>

# PyTekt

**Official open-source product from [Aqwel AI](https://aqwelai.xyz/) · v0.2.0**

[![PyPI](https://img.shields.io/pypi/v/pytekt?label=PyPI)](https://pypi.org/project/pytekt/)
[![Python](https://img.shields.io/pypi/pyversions/pytekt?label=Python)](https://pypi.org/project/pytekt/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Aqwel AI](https://img.shields.io/badge/Product-Aqwel%20AI-0066cc)](https://aqwelai.xyz/)

**PyTekt** is the flagship Python research library from **Aqwel AI**: one install for **research-grade ML** in notebooks, optional **C++ acceleration** for hot paths, plus **physics**, **astronomy**, and **computer vision** modules. Apache-2.0, published on [PyPI](https://pypi.org/project/pytekt/) as `pytekt`.

| Focus | Audience | Entry point |
|-------|----------|-------------|
| **Research library** (ships in 0.2.0) | AI researchers, data scientists, ML engineers | `import pytekt` |

Shared stack: **`pytekt.providers`**, **`pytekt.tools`**, **`pytekt.rag`**, Core ML, physics, universe, vision. Install only what you need: `[ai]`, `[viz]`, `[vision]`, `[physics]`, `[universe]`, `[full]`.

**Official links:** [Aqwel AI website](https://aqwelai.xyz/) · [Product docs](https://aqwelai.xyz/#/docs) · [PyPI](https://pypi.org/project/pytekt/) · [This repo — structure](docs/PROJECT_STRUCTURE.md) · [Security](SECURITY.md) · [`.env.example`](.env.example)

---

## 5 minutes to PyTekt

Install, import, and run a first example.

**1. Install**

```bash
pip install pytekt
# optional stacks:
pip install "pytekt[ai,viz]"           # ML + plots
pip install "pytekt[vision,physics]"   # CV + physics
```

**2. Check it works**

```bash
python -c "import pytekt; print(pytekt.__version__)"
pytekt doctor
```

**3. Use the library**

```python
import pytekt
from pytekt.datasets import load_iris
from pytekt.preprocessing import StandardScaler
from pytekt.models import GaussianNB
from pytekt.metrics import accuracy_score

ds = load_iris()
X = StandardScaler().fit_transform(ds.data)
clf = GaussianNB().fit(X, ds.target)
print("PyTekt", pytekt.__version__, "→ accuracy", accuracy_score(ds.target, clf.predict(X)))
```

**4. Try a CLI tool**

```bash
pytekt welcome          # install animation
pytekt physics tasks    # physics toolkit (needs [physics] / matplotlib)
pytekt vision --help    # computer vision CLI (needs [vision])
```

More paths: [Quick start](#quick-start-choose-your-path) · [Installation](#installation) · [Getting Started](#getting-started)

---

## About Aqwel AI

**Aqwel AI** builds practical AI tools for researchers and developers. **PyTekt** is our primary open-source product: a single Python package for numerics, classical ML, LLM workflows, experiment tracking, physics, astronomy, and vision.

- **Company:** [aqwelai.xyz](https://aqwelai.xyz/)
- **Product:** PyTekt (`pip install pytekt`)
- **Created by:** [Aqwel AI](https://aqwelai.xyz/) · **Main developer:** Aksel Aghajanyan
- **License:** Apache-2.0 · **Support:** [CONTRIBUTING.md](CONTRIBUTING.md) · security: [SECURITY.md](SECURITY.md)

---

## PyTekt product documentation

This README is the **main documentation** for the GitHub repository. Deeper maps live in linked files below.

### Documentation map

| Document | What it covers |
|----------|----------------|
| **This README** | Full product overview, install, features, examples, architecture diagrams |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Package layout for the research library |
| [pytekt/algorithms/CATALOG.md](pytekt/algorithms/CATALOG.md) | Full algorithms catalog (572+ functions) |
| [pytekt/physics/README.md](pytekt/physics/README.md) | Classical physics toolkit |
| [pytekt/universe/README.md](pytekt/universe/README.md) | Astronomy module |
| [pytekt/vision/README.md](pytekt/vision/README.md) | Computer vision (image arrays) |
| [pytekt/db/README.md](pytekt/db/README.md) | Unified database layer |
| [SECURITY.md](SECURITY.md) | API keys, `~/.pytekt.yaml`, safe publishing |
| [.env.example](.env.example) | Environment variables (copy to `.env` locally only) |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development and PR process |
| [pytekt/algorithms/README.md](pytekt/algorithms/README.md) | Algorithms module |
| [pytekt/visualization/README.md](pytekt/visualization/README.md) | Plotting and reports |
| [aqwelai.xyz/#/docs](https://aqwelai.xyz/#/docs) | Official web documentation (Aqwel AI) |

### Research library (`import pytekt`)

For **notebooks, papers, and pipelines**: NumPy-first classical ML, built-in datasets (no downloads), algorithms, RAG, tokenizers, `former` transformer training, trackers, LLM eval, Hub UI (`pytekt start`), physics, universe, vision.

```bash
pip install "pytekt[ai,viz]"    # or pip install -e ".[ai,viz]" from this repo
```

```python
import pytekt
from pytekt.datasets import load_iris
from pytekt.preprocessing import StandardScaler
from pytekt.models import GaussianNB
from pytekt.metrics import accuracy_score

ds = load_iris()
X = StandardScaler().fit_transform(ds.data)
clf = GaussianNB().fit(X, ds.target)
print(accuracy_score(ds.target, clf.predict(X)))
```

| Module area | Capabilities |
|-------------|--------------|
| `pytekt.maths`, `pytekt.algorithms` | Linear algebra; **572+** algorithms across 21 categories |
| `pytekt.preprocessing`, `pytekt.models`, `pytekt.metrics`, `pytekt.hyperopt` | Core ML stack (sklearn-style, NumPy-first) |
| `pytekt.datasets`, `pytekt.data` | 24+ built-in benchmarks, loaders, splits |
| `pytekt.providers`, `pytekt.tools`, `pytekt.rag` | LLM clients, tool loops, RAG |
| `pytekt.physics`, `pytekt.universe`, `pytekt.vision` | Physics toolkit, astronomy, classic CV (`[vision]`) |
| `pytekt.tracker`, `pytekt.llm_eval`, `pytekt.cache`, `pytekt.store` | Experiments, eval metrics, caching, SQLite stores |
| `pytekt.former`, `pytekt.visualization`, `pytekt.ui` | Transformer training, plots/3D, PyTekt Hub |

CLI helpers: `pytekt start`, `pytekt usage`, `pytekt physics`, `pytekt universe`, `pytekt vision`, `pytekt embed`, `pytekt eval`, `pytekt benchmark`, `pytekt doctor` — see [Getting Started](#getting-started) and [Features](#features).

### Not in 0.2.0

The terminal coding agent (`pytekt agent`) and in-package ReAct framework (`pytekt.agents`) are **not shipped**. CLI stubs for `pytekt agent` / `api` / `auth` print a notice. For LLM workflows, use **`pytekt.providers`** and **`pytekt.tools`** from Python.

### Quick start — choose your path

| I am a… | Do this |
|---------|---------|
| **Data scientist / researcher** | `pip install "pytekt[ai]"` → `import pytekt` → see [Getting Started](#getting-started) |
| **Physics / astronomy** | `pip install "pytekt[physics,universe]"` → `pytekt physics` / `pytekt universe` |
| **Computer vision** | `pip install "pytekt[vision]"` → see [`pytekt/vision/README.md`](pytekt/vision/README.md) |
| **Full local install** | `pip install -e ".[full]"` from this repo |

---

## Author

**PyTekt** is an open-source product from **[Aqwel AI](https://aqwelai.xyz/)**.

| Name | Role | GitHub | LinkedIn |
|------|------|--------|----------|
| Aksel Aghajanyan | Main developer · CEO · Data Scientist | [@Aksel588](https://github.com/Aksel588) | [Aksel Aghajanyan](https://www.linkedin.com/in/aksel-aghajanyan/) |

**Created by:** Aqwel AI · **Main developer:** Aksel Aghajanyan

---

## Table of Contents

- [5 minutes to PyTekt](#5-minutes-to-pytekt)
- [About Aqwel AI](#about-aqwel-ai)
- [PyTekt product documentation](#pytekt-product-documentation)
  - [Documentation map](#documentation-map)
  - [Research library](#research-library-import-pytekt)
  - [Not in 0.2.0](#not-in-020)
  - [Quick start — choose your path](#quick-start-choose-your-path)
- [Author](#author)
- [Overview](#overview)
  - [What's new in 0.2.0](#whats-new-in-020)
  - [Everything new since v0.1.9](#everything-new-since-v019)
- [Architecture and structure](#architecture-and-structure)
- [Package architecture and diagrams](#package-architecture-and-diagrams)
- [Optional dependency matrix](#optional-dependency-matrix)
- [Requirements](#requirements)
- [Installation](#installation)
- [PyTekt install animation](#pytekt-install-animation)
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

**PyTekt** is an **Aqwel AI research library**: one coherent **import surface** for work that usually spans half a dozen ad-hoc utilities — **linear algebra and stats**, **classical algorithms**, a **Core ML stack**, **plotting**, **embeddings and evaluation**, **physics / astronomy / vision**, plus **LLM-era** helpers (`providers`, `tools`, `rag`).

**New in 0.2.0 (ships now):** Core ML modules, datasets/data restore, tokenizer, pipeline, store, tracker, llm_eval, structures, serve, ui/hub, db, **universe**, **physics**, **vision** (`[vision]`), usage dashboard, install splash (`pytekt welcome`), experiments/doctor/benchmark.

See [Not in 0.2.0](#not-in-020) for features that are not shipped in this release.

The design goal is simple: **progressive disclosure**—core installs stay small; heavy stacks are behind **named extras** (`[viz]`, `[ai]`, `[vision]`, `[physics]`, `[universe]`, `[full]`, and others).

---

## What's new in 0.2.0

Version 0.2.0 expands the **research library** — Core ML, datasets, serving, Hub UI, **physics**, **universe**, **vision**, and install splash.

### Everything new since v0.1.9

v0.1.9 already included `pytekt.tools`, `pytekt.rag`, `pytekt.config`, `pytekt.env`, `pytekt.benchmarks`, provider `complete_turn`, partial graph algorithms, basic 3D/PDF viz, and extras `[tools]`, `[rag]`, `[config]`. It **removed** top-level `pytekt.datasets` and `pytekt.dataframe`.

**v0.2.0 adds everything below** (not in v0.1.9):

| # | Area | Package / entry | Key capabilities |
|---|------|-----------------|------------------|
| 1 | **Physics** | `pytekt.physics` · `pytekt physics` | Classical mechanics, NL query, C++ path, web dashboard |
| 2 | **Universe** | `pytekt.universe` · `pytekt universe` | Coordinates, observing, orbits, cosmology, web dashboard |
| 3 | **Vision** | `pytekt.vision` · `[vision]` | Image I/O, transforms, filters, draw, metrics, OpenCV ops |
| 4 | **Caching** | `pytekt.cache` | MemoryCache, DiskCache, LLMCache, `@cached` |
| 5 | **Data (restored)** | `pytekt.data` | CSV/JSON/JSONL, splits, augmentation, schema validation |
| 6 | **Datasets (restored)** | `pytekt.datasets` | 24 benchmarks, generators, `fetch`/`list_datasets`, file I/O |
| 7 | **Tokenizer** | `pytekt.tokenizer` | BPE, WordPiece, Vocabulary |
| 8 | **Pipelines** | `pytekt.pipeline` | Pipeline, FunctionStep, MapStep, FilterStep, BatchStep |
| 9 | **Store** | `pytekt.store` | KeyValueStore, PersistentVectorStore, ChatHistoryStore |
| 10 | **Tracker** | `pytekt.tracker` | Tracker/Run, compare_runs, best_run |
| 11 | **LLM eval** | `pytekt.llm_eval` | Similarity, faithfulness, toxicity, PII, cost tracking |
| 12 | **Structures** | `pytekt.structures` | Trie, BloomFilter, LRU, heaps, UnionFind |
| 13 | **Serve** | `pytekt.serve` | FastAPI `/chat`, `/rag`, `/health` |
| 14 | **Core ML** | `preprocessing`, `models`, `metrics`, `hyperopt` | NumPy-first sklearn-style stack |
| 15 | **UI / Hub** | `pytekt.ui` · `pytekt start` | Hub, HTML reports, optional Gradio/Streamlit |
| 16 | **Database** | `pytekt.db` | SQLite + MySQL/Postgres/Mongo/Redis |
| 17 | **Experiments** | `pytekt.experiments` | `Experiment`, `BenchmarkSuite`, `pytekt benchmark`, `pytekt doctor` |
| 18 | **Usage** | `pytekt.usage` | Token & cost dashboard (`pytekt usage`) |
| 19 | **Install splash** | `pytekt welcome` | PYTEKT logo animation on install/upgrade |
| 20 | **New extras** | `pyproject.toml` | `[serve]`, `[db]`, `[universe]`, `[physics]`, `[vision]`, `[ui]`, … |
| 21 | **Bug fixes** | `pytekt.algorithms` | `matrix_*`, scaling helpers; `a_star`/`pagerank` import fixes |

### Not available in 0.2.0

See [Not in 0.2.0](#not-in-020) near the top of this README.

> **Note:** `pytekt.data` and `pytekt.datasets` were removed in v0.1.9 and **brought back in v0.2.0**.

### Physics (`pytekt.physics`)
- Classical mechanics, kinematics, thermo, EM, optics, relativity, integrators, NL query router.
- CLI: `pytekt physics …` / `pytekt physics-dashboard`. See [`pytekt/physics/README.md`](pytekt/physics/README.md).

### Vision (`pytekt.vision`)
- Classic image-array helpers (Pillow + OpenCV): I/O, transforms, color, filters, draw, metrics.
- Not detection/segmentation models (use `[ai]` for deep learning). See [`pytekt/vision/README.md`](pytekt/vision/README.md).

### Caching (`pytekt.cache`)
- **`MemoryCache`** — Thread-safe in-memory cache with optional per-key TTL and max-size eviction.
- **`DiskCache`** — SQLite-backed persistent cache with TTL.
- **`LLMCache`** — Cache LLM completions keyed by (messages, model, temperature); tracks hit/miss statistics.
- **`@cached` decorator** — Transparently cache any function's return value (memory or custom backend).

### Data processing (`pytekt.data`)
- **Loaders** — `load_csv`, `load_json`, `load_jsonl` with encoding and schema options; matching `save_*` functions.
- **Splitting** — `train_test_split`, `train_val_test_split`, `kfold_split` with optional stratification.
- **Text augmentation** — `random_delete`, `random_swap`, `random_insert`, `synonym_replace`, `augment_text`.
- **Schema validation** — `Schema`, `Field`, `validate_record`, `validate_dataset` for tabular data.

### Benchmark datasets (`pytekt.datasets`)
- **`Dataset` container** — NumPy `data` / `target`, feature and target names, metadata, `head()`, train/test split helpers.
- **Classic toy sets (in-memory, no download)** — `load_iris`, `load_digits`, `load_housing`, `load_moons`, `load_circles`, `load_blobs`, `load_wine`, `load_breast_cancer`, `load_diabetes`, `load_linnerud`.
- **NLP samples** — `load_sentiment`, `load_topics`, `load_ner` (BIO tags), `load_spam`, `load_qa` (RAG-style Q&A with contexts).
- **Synthetic generators** — `make_classification`, `make_regression`, `make_clusters`, `make_moons`, `make_circles`, `make_blobs`, `make_sparse_classification`, `make_time_series`, `make_multilabel`.
- **Registry** — `fetch("iris", return_split=True)`, `list_datasets()`, `summary("wine")`.
- **File I/O (`pytekt.datasets.io`)** — pandas-style loaders: `read_csv`, `read_json`, `read_jsonl`, `read_file` (auto-detect); with `[ai]`: `read_parquet`, `read_excel`, `from_dataframe`; export via `to_csv`, `to_json`, `to_parquet`, `to_dataframe`, `to_numpy`. Distinct from **`pytekt.data`** (row dicts for pipelines) and **`pytekt.former.datasets`** (LM text windows).

### User interfaces (`pytekt.ui`) — React-style frontend in Python
- **Component model** — `Component` base class + `@function_component` (like React class/function components).
- **`html` tags** — `html.div`, `html.button`, `html.h1`, … (like JSX; props use `className`, `onClick`).
- **`h()` / `Fragment`** — low-level `createElement` and fragment grouping (`<>...</>`).
- **Layout components** — `AppShell`, `Card`, `Stack`, `Row`, `MetricGrid`, `DataTable`, `Button`.
- **`render_app()` / `serve_app()`** — export a full HTML page or run a local dev server (stdlib).
- **Legacy reports** — `PageBuilder`, `build_experiment_dashboard()`, `build_dataset_report()`.
- **Hub & monitor** — `launch_hub()` / `pytekt start`, `launch_monitor()` (`[monitor]`).
- **Optional apps (`[ui]` extra)** — Gradio/Streamlit launchers.
- **CLI:** `pytekt ui --list`, `pytekt ui --report`, `pytekt ui --gradio`, `pytekt ui --streamlit`.
- **Install animation:** `pytekt welcome` — replay the animated module install screen ([see README](#pytekt-install-animation)).

### Tokenization (`pytekt.tokenizer`)
- **`BPETokenizer`** — Trainable byte-pair encoding: train on a corpus, encode/decode, save/load.
- **`WordPieceTokenizer`** — BERT-style sub-word tokenizer with `##` continuation tokens.
- **`Vocabulary`** — Bidirectional token↔id mapping with special tokens (`<pad>`, `<unk>`, `<bos>`, `<eos>`), save/load to JSON.

### Pipelines (`pytekt.pipeline`)
- **`Pipeline`** — Sequential chain of `Step` objects with per-step timing, retry, fallback, dry-run, and JSON serialization.
- **Built-in steps** — `FunctionStep`, `MapStep`, `FilterStep`, `BatchStep`.

### Persistent storage (`pytekt.store`)
- **`KeyValueStore`** — SQLite key-value store with namespace support.
- **`PersistentVectorStore`** — SQLite-backed vector store with brute-force cosine similarity search.
- **`ChatHistoryStore`** — Persistent conversation threads with message history, listing, and full-text search.

### Unified database (`pytekt.db`)
- **`connect(url)`** — One API for SQLite (core), MySQL, PostgreSQL, MongoDB, Redis (`pip install pytekt[db]`).
- **Dict API** — `conn.users.insert({...})`, `conn.users.find(name="Alice")`, `find(score__gte=5)`.
- **Query builder** — `conn.table("users").where(conn.col.age > 25).select("name").all()`.
- **PyTekt-only** — `hybrid_search`, `agent_memory`, `bulk_upsert`, `sync_usage`, pipeline `DbReadStep` / `DbWriteStep`.
- See [`pytekt/db/README.md`](pytekt/db/README.md).

### Astronomy (`pytekt.universe`)
- **Coordinates** — RA/Dec ↔ Alt/Az, galactic transform, angular separation.
- **Time** — Julian date, GMST/LST for observing.
- **Observing** — Moon phase, air mass, `whats_up()` with builtin bright-star catalog.
- **Orbits & cosmology** — Kepler elements, Hohmann transfer, flat ΛCDM distances.
- **CLI** — `pytekt universe moon|sky|coords|web` (`pytekt cosmos` is deprecated).
- **Web dashboard** — `pytekt universe web` (React sky map, moon, cosmology, observation log).
- **C++ fast path** — hot calculations in `pytekt._pytekt_universe` with Python fallbacks.
- See [`pytekt/universe/README.md`](pytekt/universe/README.md).

### Physics (`pytekt.physics`)
- **Mechanics & thermo** — force, energy, ideal gas, heat transfer formulas.
- **Simulations** — pendulum, spring-mass, projectile (RK4 integrator).
- **NL query router** — `solve_physics_query("kinetic energy mass=2 velocity=3")`.
- **CLI** — `pytekt physics query|pendulum|projectile|web`.
- **Web dashboard** — `pytekt physics web` (calculator, pendulum/projectile plots, port 3858).
- **C++ fast path** — integrators in `pytekt._pytekt_physics` with Python fallbacks.
- See [`pytekt/physics/README.md`](pytekt/physics/README.md).

### Experiment tracking (`pytekt.tracker`)
- **`Tracker` / `Run`** — Log parameters, metrics (with step tracking), tags, and artifacts to a local directory.
- **`compare_runs` / `best_run`** — Sort and compare runs by any metric.

### Core ML stack

Four NumPy-first modules for classical ML workflows (sklearn-style `fit` / `transform` / `predict`, no scikit-learn required):

#### Preprocessing (`pytekt.preprocessing`)
- **Scalers** — `StandardScaler`, `MinMaxScaler`, `RobustScaler`, `Normalizer`.
- **Encoders** — `LabelEncoder`, `OneHotEncoder`, `OrdinalEncoder`.
- **Imputers** — `SimpleImputer` (mean, median, most_frequent, constant).
- **Transforms** — `PolynomialFeatures`, `Binarizer`, `KBinsDiscretizer`.
- **Composition** — `ColumnTransformer`, `PreprocessingPipeline` (named steps, `fit_transform`).

#### Models (`pytekt.models`)
- **Regression** — `LinearRegression`.
- **Classification** — `LogisticRegression` (binary), `KNNClassifier`, `GaussianNB`, `DecisionTreeClassifier`.
- **Regression (nonlinear)** — `KNNRegressor`, `DecisionTreeRegressor`.
- **Clustering** — `KMeans`.
- **Decomposition** — `PCA`.
- All estimators expose `fit`, `predict`, and `score` (accuracy for classifiers, R² for regressors).

#### Metrics (`pytekt.metrics`)
- **Classification** — `accuracy_score`, `precision_score`, `recall_score`, `f1_score`, `confusion_matrix`, `roc_auc_score`, `matthews_corrcoef`, `classification_report`.
- **Regression** — `mean_squared_error`, `root_mean_squared_error`, `mean_absolute_error`, `mean_absolute_percentage_error`, `r2_score`, `adjusted_r2_score`, `explained_variance_score`.
- **Clustering** — `silhouette_score`, `adjusted_rand_score`.
- **NLP** — `bleu_score`, `rouge_l_score`, `perplexity`.
- **Ranking** — `ndcg_score`, `mrr_score`.
- Distinct from **`pytekt.evaluate`** (legacy helpers and file-based prediction evaluation).

#### Hyperparameter optimization (`pytekt.hyperopt`)
- **`GridSearch`** — Exhaustive search over a discrete parameter grid with k-fold CV.
- **`RandomSearch`** — Random sampling from the grid.
- **`BayesianSearch`** — Lightweight acquisition over past trials (good for small grids).
- **`EarlyStopping`** — Stop search when CV score plateaus.
- **`cross_val_score` / `kfold_indices`** — Standalone CV utilities.
- Optional **`tracker`** integration — each trial logs params and `cv_score` to `pytekt.tracker`.
- **`MLPipeline`** — chain preprocessing + estimator; **`save_model` / `load_model`** for checkpoints.

### Research experiments (`pytekt.experiments`)
- **`Experiment`** — context manager: fixed `seed`, `tracker` logging, `manifest.json` for reproduction.
- **`export_results_table`** — paper-ready **LaTeX**, CSV, Markdown, HTML from tracker runs.
- **`BenchmarkSuite`** — multi-seed baselines on iris, wine, breast cancer, digits (`pytekt benchmark` CLI).
- **`pytekt doctor`** — environment check (Python, numpy, optional extras, tracker dir, C++ extension).
- **Stats** — `bootstrap_ci`, `compare_models`, `mcnemar_test` in `pytekt.metrics`.

### LLM evaluation (`pytekt.llm_eval`)
- **Semantic similarity** — `semantic_similarity`, `batch_similarity`, `relevance_score` using embeddings.
- **Faithfulness** — `faithfulness_score`, `check_groundedness` to verify RAG outputs against source documents.
- **Safety** — `toxicity_check` (keyword-based), `contains_pii` (emails, phones, SSNs, credit cards, IPs).
- **Cost tracking** — `estimate_cost` per provider, `CostTracker` for cumulative usage and spend.

### Data structures (`pytekt.structures`)
- **`Trie`** — Prefix tree for autocomplete and prefix search.
- **`BloomFilter`** — Probabilistic membership testing with tunable false-positive rate.
- **`LRUCache`** — Bounded least-recently-used cache with O(1) get/set and hit-rate tracking.
- **`MinHeap` / `MaxHeap` / `PriorityQueue`** — Heap-based priority queues.
- **`UnionFind`** — Disjoint-set with path compression and union by rank.

### API serving (`pytekt.serve`)
- **`PyTektServer` / `create_app`** — FastAPI application exposing `/chat`, `/rag`, `/health` endpoints.
- Custom route registration, CORS enabled. Reuses the same `[serve]` / `[monitor]` FastAPI dependency.

### Bug fixes
- Fixed missing `matrix_transpose`, `matrix_multiply`, `z_score_normalization`, `min_max_scaling` functions in `pytekt.algorithms.arrays`.
- Fixed `a_star` and `pagerank` import name mismatches in `pytekt.algorithms.graphs`.

---

## Architecture and structure

This part of the README is the **structural map** of the Aqwel AI **PyTekt** product: conceptual layers (diagrams), design rules, and the **repository root** layout. For the full package map, see [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

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
  LLM --> LLMEval
  LLM --> Serve
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
    A["import pytekt"]
    B["pytekt.algorithms"]
    C["pytekt.visualization"]
    D["pytekt.providers"]
    E["pytekt.tools"]
    F["pytekt.rag"]
    H["pytekt.cache"]
    I["pytekt.data"]
    I2["pytekt.datasets"]
    J["pytekt.tokenizer"]
    K["pytekt.pipeline"]
    L["pytekt.store"]
    M["pytekt.tracker"]
    N["pytekt.llm_eval"]
    O["pytekt.serve"]
    P["pytekt.structures"]
    Q["pytekt.preprocessing"]
    R["pytekt.models"]
    S["pytekt.metrics"]
    T["pytekt.hyperopt"]
    U["pytekt.ui"]
  end
  A --> B
  A --> C
  A --> D
  D --> E
  A --> F
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

- **Single package:** Public APIs live under `pytekt`. Prefer `import pytekt` and attribute access, or explicit `from pytekt.X import …` for subpackages.
- **Core single-file modules:** `maths`, `code`, `embed`, `evaluate`, `files`, `git`, `parser`, `pdf`, `prompt`, `snippets`, `text`, `utils`, `watcher`, `cli`, plus **`_core`** (`fast_*` bridge to optional native code).
- **Data and control plane:** `io` (streaming, atomic writes, checksums), `config` (implementation in `config/core.py`), `env`.
- **Data processing:** `data` (CSV/JSON/JSONL loaders as row dicts, splitting, augmentation, schema validation), `datasets` (built-in benchmarks, synthetic generators, `Dataset` + pandas-style file I/O), `tokenizer` (BPE, WordPiece, vocabulary management).
- **Developer UI:** `pytekt start` launches **PyTekt Hub** (`pytekt/hub/`) — module explorer, dependency checker, and in-browser Python playground (stdlib server).
- **LLM surface:** `providers` (chat REST, `complete` and `complete_turn` where supported), `tools` (OpenAI-style tool JSON, registry, retries, token bucket, optional tiktoken).
- **Retrieval:** `rag` (chunking, `MemoryVectorStore`, optional `FaissVectorStore`, `SimpleRAGIndex`).
- **Evaluation:** `llm_eval` (semantic similarity, faithfulness, toxicity, PII detection, cost tracking).
- **Caching:** `cache` (in-memory, SQLite disk, LLM-specific; TTL; `@cached` decorator).
- **Storage:** `store` (SQLite key-value, persistent vector store, chat history).
- **Pipelines:** `pipeline` (step-based chains with retry, fallback, timing, serialization).
- **Tracking:** `tracker` (experiment run logger with metrics, params, artifacts, comparison).
- **Core ML:** `preprocessing` (scalers, encoders, imputers, pipelines), `models` (linear, KNN, trees, KMeans, PCA, Naive Bayes), `metrics` (classification, regression, clustering, NLP, ranking), `hyperopt` (grid/random/Bayesian search with CV and tracker hooks).
- **Data structures:** `structures` (Trie, Bloom filter, LRU cache, heaps, Union-Find).
- **Serving:** `serve` (FastAPI-based `/chat`, `/rag`, `/health` endpoints).
- **Algorithms and visualization:** `algorithms` (search, arrays, **graphs**: BFS, DFS, toposort, Dijkstra, A*, components, MST, max flow, PageRank), `visualization` (1D/2D/training/**3D**, `save_figures_pdf`, HTML figure bundles).
- **Former:** NumPy autograd transformer training (`pytekt.former.*`), including **`pytekt.former.datasets`** for tokenizer and text windows.
- **Quality:** `benchmarks`.
- **Optional dependencies:** Heavy stacks behind extras (`[viz]`, `[ai]`, `[docs]`, `[full]`, `[tools]`, `[rag]`, `[config]`, …). LLM calls need network + API keys. **No `eval`** in tool execution—arguments are JSON-parsed and passed to registered callables only.
- **Native extension:** `src/pytekt_core.cpp` + pybind11 produces `pytekt._pytekt_core`; otherwise NumPy fallbacks.
- **Config:** `pytekt config` / `~/.pytekt.yaml` (private; keys for providers when used from Python).
- **Entry points:** `pytekt.cli` (`pytekt` console script), package metadata on `pytekt`, repo `main.py`.

### Directory structure

Layout below matches the repository as shipped (file names only; omit your local `.venv`, build artifacts, and caches).

#### Repository root

```
.                              # Project root (clone / sdist)
├── README.md
├── logo/                      # Brand marks
├── 0.2.0v.png                 # Release banner (v0.2.0)
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── .env.example                 # Template only — copy to .env locally (gitignored)
├── docs/
│   └── PROJECT_STRUCTURE.md     # Research library package map
├── MANIFEST.in
├── pyproject.toml
├── setup.py
├── requirements.txt
├── example.py                 # Runnable demo (algorithms / visualization)
├── main.py                    # CLI entry script
├── src/
│   ├── pytekt_core.cpp          # C++ sources for optional pytekt._pytekt_core (pybind11)
│   ├── pytekt_bigdata.cpp       # Native big-data kernels for large-array workloads
│   ├── pytekt_universe.cpp      # C++ fast path for pytekt._pytekt_universe
│   ├── pytekt_physics.cpp       # C++ fast path for pytekt._pytekt_physics
│   └── native/
│       ├── array_utils.hpp    # Shared helpers for native extensions
│       └── bigdata_kernels.hpp # Prefix/rolling/histogram kernels
├── tests/                     # Pytest suite (Core ML, algorithms, io, maths, text, snippets, pdf, …)
│   ├── test_preprocessing.py
│   ├── test_models.py
│   ├── test_metrics.py
│   ├── test_hyperopt.py
│   ├── test_core_ml_integration.py
│   └── …
└── pytekt/                      # Python package
```

**Repo check:** The layout above is the **documented** shipping shape. The repository includes a **`tests/`** directory (run `pytest tests/` after `pip install -e ".[dev,ai]"`). If `import pytekt` fails after a partial checkout, restore package stubs with  
`git checkout HEAD -- pytekt/benchmarks/__init__.py`.  
The library surface is **`pytekt.code`** (`code.py` module only—not a `pytekt/code/` package). For the package map, see [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

### Design principles

- **Explicit imports:** Subpackages re-export stable symbols from `__init__.py` (e.g. `from pytekt.algorithms import binary_search` or `from pytekt.algorithms.search import binary_search`).
- **Backend-safe visualization:** Plotting APIs return matplotlib `Figure` objects and support `show=False` for servers and CI; 3D uses `mpl_toolkits.mplot3d` (still `[viz]` / matplotlib).
- **Layered dependencies:** Core + algorithms target NumPy and the standard library where possible. `io` avoids heavy deps. `providers`, `tools`, and `rag` may require network keys or optional FAISS / sentence-transformers. Never install `[full]` unless you need the whole research stack.
- **Safety:** Tool execution uses **JSON object** arguments mapped to registered callables—no arbitrary code execution from model output.

---

## Optional dependency matrix

| Extra | Purpose | Notable dependencies |
|-------|---------|----------------------|
| *(base)* | Core library (Core ML, data, datasets, cache, structures, pipeline, store, tracker, tokenizer, llm_eval, hub) | `numpy`, `watchdog`, `gitpython` |
| `[viz]` | Plots (1D/2D/3D, reports) | `matplotlib`, `seaborn` |
| `[former]` | PyTekt Former training | `matplotlib`, `pyyaml` |
| `[ai]` | ML / transformers / pandas | `torch`, `transformers`, `pandas`, `scikit-learn`, … |
| `[docs]` | PDF generation | `reportlab`, `pillow` |
| `[vision]` | Computer vision (image arrays) | `pillow`, `opencv-python-headless` |
| `[dev]` | Tests and formatters | `pytest`, `black`, `flake8` |
| `[tools]` | Token counting for prompts | `tiktoken` |
| `[rag]` | Embeddings + FAISS index | `sentence-transformers`, `faiss-cpu` |
| `[config]` | TOML on older Python + YAML | `tomli` (3.8–3.10), `pyyaml` |
| `[serve]` | REST API serving | `fastapi`, `uvicorn` |
| `[db]` | MySQL, Postgres, Mongo, Redis backends for `pytekt.db` | `pymysql`, `psycopg`, `pymongo`, `redis` |
| `[universe]` | Astronomy plots for `pytekt.universe` | `matplotlib` |
| `[viz3d]` | Plotly 3D + enhanced viz (post-0.2.0) | `plotly`, `matplotlib`, `seaborn` |
| `[monitor]` | Hardware dashboard | `psutil`, `fastapi`, `uvicorn`, `nvidia-ml-py` |
| `[ui]` | Gradio / Streamlit app launchers | `gradio`, `streamlit` |
| `[full]` | Convenience “everything” set | Combines most stacks above (+ OpenAI client, tiktoken, etc.) |

Combine extras as needed, e.g. `pip install "pytekt[viz,tools,serve]"` or editable `pip install -e ".[dev,full]"` from a clone.

---

## Requirements

- **Python:** 3.8 or higher (3.9 through 3.13 supported per package classifiers).
- **pip:** For installing the package and optional extras.
- **Core runtime:** `numpy>=1.21.0`, `watchdog>=2.1.0`, `gitpython>=3.1.0` (optional for Git features).
- **Optional:** SciPy, scikit-learn, pandas, matplotlib, ReportLab, sentence-transformers, PyTorch, vendor LLM credentials for `pytekt.providers`, etc. See [Installation](#installation) for extras.
- **Native extension (optional):** C++14 compiler and `pybind11` to build `pytekt._pytekt_core` from `src/pytekt_core.cpp`; otherwise fast helpers in `pytekt` use NumPy.
- **C++ tooling (optional):** Install `cmake` + `clang++`/`g++` if you build native extensions or work with C++ projects alongside PyTekt.

A virtual environment (e.g. `venv` or `conda`) is recommended to isolate dependencies.

---

## Installation

### Base install (required dependencies only)

```bash
pip install pytekt
```

This installs the core package with numpy, watchdog, and gitpython. Enough for maths, algorithms, parser, files, utils, text, and most of the code and evaluate modules.

### Optional dependency groups

```bash
pip install pytekt[viz]   # Visualization (matplotlib, seaborn)
pip install pytekt[former] # Transformer training (PyTekt Former: matplotlib, pyyaml)
pip install pytekt[ai]     # ML stack: scipy, scikit-learn, pandas, matplotlib, transformers, torch, sentence-transformers, openai
pip install pytekt[docs]   # PDF/docs: reportlab, pillow
pip install pytekt[vision] # Computer vision: pillow, opencv-python-headless
pip install pytekt[full]   # All optional dependencies including seaborn, faiss-cpu
pip install pytekt[dev]    # Development: pytest, black, flake8
pip install pytekt[tools]  # tiktoken for token estimates
pip install pytekt[rag]    # sentence-transformers + faiss-cpu
pip install pytekt[config] # tomli on Python 3.8–3.10 + PyYAML
pip install pytekt[serve]  # FastAPI + uvicorn for pytekt.serve
pip install pytekt[db]     # MySQL, Postgres, Mongo, Redis for pytekt.db
pip install pytekt[universe]  # Astronomy matplotlib plots
pip install pytekt[viz3d]  # Plotly 3D visualization
pip install pytekt[ui]     # Gradio + Streamlit for pytekt.ui apps
```

### Editable install (for development)

```bash
git clone https://github.com/aqwelai/pytekt.git
cd pytekt
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
   pip install pytekt
   ```

3. For visualization and full ML/docs, use extras:

   ```bash
   pip install pytekt[full]
   ```

4. Verify the install (you should see an **animated install screen** with large module names and ✓ INSTALLED lines):

   ```bash
   python -c "import pytekt; print(pytekt.__version__)"
   pytekt welcome    # replay the install animation anytime
   ```

   Disable the animation: `PYTEKT_NO_SPLASH=1 pip install pytekt` or `pytekt welcome --no-animation`.

   See [PyTekt install animation](#pytekt-install-animation) for the logo and a full preview of the welcome screen.

5. (Optional) Run smoke tests from a clone:

   ```bash
   pip install -e ".[dev]"
   pytest tests/
   ```

---

## PyTekt install animation

<p align="center">
  <strong>Replay the install celebration in your terminal</strong>
</p>

After `pip install pytekt` (or `pip install -e .` from a clone), PyTekt prints an animated screen: the **PYTEKT** banner, a large **INSTALLED** label, a progress bar, and each module name in **big spaced letters** with **✓ INSTALLED** (Core ML, datasets, UI, and more).

### Command

```bash
# After pip install -e .  (or pip install pytekt)
pytekt welcome
```

If `pytekt` is not on your `PATH` (common with conda / python.org installs):

```bash
python -m pytekt welcome
```

Static list (no animation delays, useful in CI or logs):

```bash
pytekt welcome --no-animation
# or
python -m pytekt welcome --no-animation
```

The PYTEKT logo animation runs automatically:

- after **`pip install -e .`** / editable installs (setuptools hook)
- once on the first **`pytekt`** command after a new install or version upgrade

To skip it:

```bash
PYTEKT_NO_SPLASH=1 pip install pytekt
# or
PYTEKT_NO_SPLASH=1 pytekt …
```

---

## Getting Started

### Verify installation

```python
import pytekt
print(pytekt.__version__)     # 0.2.0
print(pytekt.__author__)      # Aksel Aghajanyan
print(pytekt.__developer__)   # Aqwel AI Team (package metadata; main developer: Aksel Aghajanyan)
```

### Minimal example (no optional deps)

```python
import pytekt

# Mathematics (uses numpy; no optional deps)
r = pytekt.maths.addition(10, 5)           # 5
r = pytekt.maths.mean([1.0, 2.0, 3.0])    # 2.0
r = pytekt.maths.determinant([[1, 2], [3, 4]])  # -2.0

# Algorithms (stdlib only from pytekt.algorithms)
idx = pytekt.algorithms.binary_search([1, 3, 5, 7, 9], 7)  # 4
flat = pytekt.algorithms.flatten_array([[1, 2], [3, 4]])   # [1, 2, 3, 4]
```

### Minimal Core ML example (no scikit-learn)

```python
from pytekt.datasets import load_iris
from pytekt.preprocessing import StandardScaler
from pytekt.models import GaussianNB
from pytekt.metrics import accuracy_score

ds = load_iris()
X = StandardScaler().fit_transform(ds.data)
clf = GaussianNB().fit(X, ds.target)
print(accuracy_score(ds.target, clf.predict(X)))
```

### Run the CLI (if installed)

```bash
python -m pytekt.cli
# or, if entry point is installed:
pytekt --help
```

**High-value commands:**

| Command | Description |
|---------|-------------|
| `pytekt benchmark` | Run standard ML benchmark suite on built-in datasets |
| `pytekt doctor` | Environment check (Python, numpy, optional extras, tracker dir, C++ extension) |
| `pytekt vision` | Computer vision CLI — `info`, `convert`, `edges` (`[vision]` extra) |
| `pytekt physics` / `pytekt universe` | Physics toolkit / astronomy toolkit + dashboards |
| `pytekt usage` / `pytekt stats` | **Usage dashboard** (React) — tokens, cost, animated charts · [http://127.0.0.1:3847](http://127.0.0.1:3847) |
| `pytekt universe web` | Astronomy web dashboard (sky map, moon, cosmology) |
| `pytekt config` | CLI / library settings (`~/.pytekt.yaml`) |
| `pytekt start` / `pytekt ui` | Open **PyTekt Hub** (module explorer, playground, quick reference) |
| `pytekt ui --report DIR` | Build experiment HTML dashboard from tracker directory |
| `pytekt ui --list` | List all available UIs (hub, monitor, reports, Gradio, Streamlit) |
| `pytekt info` | Environment and optional dependency status |
| `pytekt monitor` / `pytekt dashboard` | Hardware metrics dashboard (`[monitor]` extra) |
| `pytekt embed <file>` | Embed a file or `--text` |
| `pytekt eval <preds> <answers>` | Evaluate predictions |
| `pytekt chat` | Interactive prompt REPL |
| `pytekt git status` | Git repository tools (needs GitPython) |

```bash
pytekt start                    # http://127.0.0.1:3000
pytekt start --port 8080        # custom port
pytekt start --no-browser      # server only
```

The repository includes root **`example.py`**: algorithms and visualization (sections 1–3), plus v0.1.9 areas ( **`pytekt.io`**, providers, tools, RAG, config, env, benchmarks, graphs, 3D/PDF, **`pytekt.pdf`** ). Run **`python example.py`** after installing dependencies for the sections you need (e.g. matplotlib for plots; **`[config]`** for the TOML sample in section 4).

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

- **572+ registered functions** across **21** categories — search, arrays, graphs, sorting, dynamic programming, trees, strings, math, queues/stacks, and more ([CATALOG.md](pytekt/algorithms/CATALOG.md)).
- **Discovery API:** `count_algorithms()`, `list_algorithms(category)`, `get_algorithm(name)`, `categories()`.
- **Core modules:** `search`, `arrays`, `graphs` — binary search, matrix ops, BFS/DFS, Dijkstra, PageRank, MST, max flow, and related helpers.
- Jupyter example notebooks in `pytekt/algorithms/examples/` with full API coverage and explanations.

### Visualization

- **1D arrays:** plot_array, plot_histogram, plot_scatter, plot_multiple_arrays, plot_array_with_mean, plot_running_mean; plot_boxplot, plot_density, plot_cdf; plot_error_bars, plot_rolling_std, plot_min_max_band; plot_autocorrelation, plot_quantiles, plot_scatter_with_fit, plot_dual_axis.
- **2D matrices:** plot_matrix_heatmap, plot_confusion_matrix (raw and normalized), plot_matrix_surface, plot_matrix_contour, plot_matrix_with_values; plot_correlation_matrix, plot_similarity_matrix; plot_matrix_histogram, plot_masked_heatmap; plot_attention_map, plot_matrix_sparsity.
- **Training:** plot_training_history, plot_metric, plot_train_vs_val, plot_learning_rate, plot_metric_with_best, plot_metrics_grid, plot_confidence_band, plot_early_stopping, plot_epoch_time.
- **3D & reports:** `plot_3d_scatter`, `plot_3d_surface`, `save_figures_pdf`, `figures_to_html_img_tags`; **seaborn** statistical plots (`[viz]`); **Plotly 3D** (`[viz3d]` extra).
- All matplotlib plotting functions return a `Figure`; use `pytekt.visualization.utils.save_plot(fig, path)` to save. Example notebooks in `pytekt/visualization/examples/`.

### AI Research and ML

- **Text embeddings:** Sentence-transformers integration and vector operations (e.g. cosine similarity).
- **Prompt engineering:** Specialized AI prompt templates and utilities for research workflows.
- **Code analysis:** Structural explanation, function/class/import extraction, comment stripping, cyclomatic complexity, docstring extraction, operator counts, code smell detection.
- **Model evaluation:** Classification metrics (accuracy, precision, recall, F1, confusion matrix, ROC-AUC), regression metrics (MSE, RMSE, MAE, R²); file-based evaluation (JSON/CSV) with automatic task detection.

### Documentation Generation

- **PDF and text:** Full API reference, user guides, changelogs, module dependency reports; configurable branding (colors, fonts, logo). ReportLab is optional—PDF entry points fall back to plain text when it is not installed.
- **Markdown and HTML:** `create_api_documentation_md` (TOC + per-module sections), `create_api_documentation_html` (self-contained static page, no extra deps).
- **Single module:** `create_module_reference_doc` writes Markdown, text, or PDF for one `pytekt.*` submodule; optional class and method listings.
- **Discovery:** `search_public_api(query)` finds public functions (and optionally classes) by name substring across documentable modules.
- **Exports:** `export_api_index` as JSON, CSV, or **Markdown table**; optional `include_classes=True`. `export_function_list`, dependency Mermaid snippets in text reports.
- **Introspection:** `generate_module_documentation(module, include_classes=False)` lists public functions; set `include_classes=True` for classes defined in that module and their public methods.

### Development and Infrastructure

- **File management:** Create, move, copy, delete; directory listing and organization helpers.
- **Safe I/O (`pytekt.io`):** `iter_lines`, `read_chunks`, atomic writes, SHA-256 `file_sha256` / `verify_sha256`. Runnable demo: `python -m pytekt.io.examples.demo_atomic_checksum`.
- **LLM providers (`pytekt.providers`):** `OpenAIProvider`, `GeminiProvider`, `AnthropicProvider`, `OpenAICompatibleProvider`, `create_provider`, `supported_providers`. OpenAI-shaped APIs also expose **`complete_turn`** → `AssistantTurn` with optional **`tool_calls`**; see `pytekt.providers.structured`. Offline demo: `python -m pytekt.providers.examples.demo_factory_parse`.
- **Tool calling (`pytekt.tools`, extra `[tools]` for tiktoken):** `function_tool`, `ToolRegistry`, `run_tool_loop`, `FakeToolProvider`, `make_tool_turn`, `post_json_with_retry`, `TokenBucket`, token estimation helpers. Offline demo: `python -m pytekt.tools.examples.demo_tool_loop`.
- **RAG (`pytekt.rag`, extra `[rag]`):** `chunk_text`, `MemoryVectorStore`, `FaissVectorStore`, `SimpleRAGIndex` over `pytekt.embed`. Local demo: `python -m pytekt.rag.examples.demo_simple_index`.
- **Config & runtime:** `pytekt.config` (TOML/YAML + env merge), `pytekt.env` (`.env` parsing). Use **`logging.basicConfig`** (stdlib) for log levels.
- **Benchmarks:** `pytekt.benchmarks` (timings, NumPy vs `fast_*` comparison).
- **Analytics:** Use **`pytekt.metrics`** for classification, regression, clustering, NLP, and ranking metrics; **`pytekt.evaluate`** remains for legacy/file-based workflows. Tabular ML prototyping uses **`pytekt.datasets`** (built-in sets + file I/O) with **`pytekt.models`** and **`pytekt.hyperopt`**; row-based ETL uses **`pytekt.data`**; full pandas/scikit-learn workflows are available via **`[ai]`** extras.
- **Former checkpoints:** `save_checkpoint_sidecar_meta` writes `.meta.json` via stdlib JSON.
- **Fast numerics (`pytekt` / `_core`):** Same `fast_*` API with or without the C++ extension—native build accelerates the hot paths; `using_native_extension` reports which path is active.
- **Visualization extras:** `plot_3d_scatter`, `plot_3d_surface`, `save_figures_pdf`, `figures_to_html_img_tags` in `pytekt.visualization` (matplotlib; `[viz]`).
- **Code parser:** Language detection and detailed analysis for 30+ programming languages (see [Supported Languages](#supported-languages)).
- **Real-time monitoring:** File change detection and callbacks via the watcher module.
- **Git integration:** Status, commit history, branches, diffs, file history (optional dependency: GitPython).
- **Utilities and CLI:** General helpers and command-line interface for common operations.

### Caching and Storage (new in 0.2.0)

- **Caching (`pytekt.cache`):** Thread-safe `MemoryCache` and SQLite `DiskCache` with per-key TTL; `LLMCache` for prompt-keyed response caching; `@cached` decorator for any function.
- **Persistent storage (`pytekt.store`):** `KeyValueStore` (SQLite with namespaces), `PersistentVectorStore` (cosine-similarity vector search), `ChatHistoryStore` (conversation threads with full-text search).

### Data Processing and Tokenization (new in 0.2.0)

- **Data (`pytekt.data`):** `load_csv`, `load_json`, `load_jsonl` loaders with matching savers; `train_test_split`, `train_val_test_split`, `kfold_split` with stratification; text augmentation (`random_delete`, `random_swap`, `random_insert`, `synonym_replace`, `augment_text`); schema validation (`Schema`, `Field`, `validate_record`, `validate_dataset`).
- **Datasets (`pytekt.datasets`):** 24 built-in benchmarks and generators; `Dataset` dataclass; `fetch`, `list_datasets`, `summary`; file I/O via `read_csv`, `read_file`, `read_parquet` (with `[ai]`), `to_dataframe`, `to_numpy` — see [What's new — Benchmark datasets](#benchmark-datasets-pytektdatasets).
- **Tokenization (`pytekt.tokenizer`):** Trainable `BPETokenizer` (byte-pair encoding) and `WordPieceTokenizer` (BERT-style `##` continuations); `Vocabulary` with special tokens, save/load to JSON.

### User interfaces (new in 0.2.0)

- **`pytekt.ui` (React-style):** Build frontends in Python with `Component`, `html.*` tags, `AppShell`, `MetricGrid`, and `render_app()` — no React/Node install required; renders to static HTML.
- **PyTekt Hub:** `pytekt start` or `pytekt ui` — browse modules, check deps, run playground code (stdlib server; serves `pytekt/hub/static/`).
- **HTML reports:** `PageBuilder`, `build_experiment_dashboard()`, `build_dataset_report()`.
- **Dev server:** `serve_app(MyApp(), port=8765)` for quick local preview.
- **Optional:** `pip install 'pytekt[ui]'` for Gradio and Streamlit app launchers.

### Data Structures (new in 0.2.0)

- **`pytekt.structures`:** `Trie` (prefix tree for autocomplete), `BloomFilter` (probabilistic membership), `LRUCache` (bounded O(1) cache), `MinHeap`/`MaxHeap`/`PriorityQueue`, `UnionFind` (disjoint-set with path compression).

### Pipelines and Tracking (new in 0.2.0)

- **Pipelines (`pytekt.pipeline`):** `Pipeline` with composable `Step` objects; built-in `FunctionStep`, `MapStep`, `FilterStep`, `BatchStep`; per-step timing, retry, fallback, dry-run, JSON serialization.
- **Experiment tracking (`pytekt.tracker`):** `Tracker`/`Run` for logging parameters, metrics (with step tracking), tags, and artifacts to local JSON files; `compare_runs`/`best_run` for experiment comparison.

### Core ML stack (`pytekt.preprocessing`, `pytekt.models`, `pytekt.metrics`, `pytekt.hyperopt`)

- **Preprocessing:** Scalers, encoders, imputers, polynomial/binning transforms; `PreprocessingPipeline` and `ColumnTransformer` for composed feature engineering.
- **Models:** NumPy implementations of linear/logistic regression, KNN, decision trees, KMeans, PCA, and Gaussian Naive Bayes — sklearn-like API without sklearn.
- **Metrics:** Full metric suite for supervised learning, clustering, NLP generation quality, and ranking; use alongside or instead of `pytekt.evaluate`.
- **Hyperopt:** `GridSearch`, `RandomSearch`, `BayesianSearch` with k-fold cross-validation, `EarlyStopping`, and optional `Tracker` logging per trial.

### LLM Evaluation (new in 0.2.0)

- **`pytekt.llm_eval`:** `semantic_similarity`/`batch_similarity` (embedding-based); `faithfulness_score`/`check_groundedness` for RAG output verification; `toxicity_check` and `contains_pii` for safety; `estimate_cost`/`CostTracker` for LLM spend tracking across providers.

### API Serving (new in 0.2.0)

- **`pytekt.serve`:** `PyTektServer`/`create_app` builds a FastAPI application with `/chat`, `/rag`, `/health` endpoints; custom route registration; CORS enabled. Install with `[serve]`.

### Unified database (new in 0.2.0)

- **`pytekt.db`:** One API for SQLite (core), MySQL, PostgreSQL, MongoDB, Redis (`[db]` extra).
- **Dict API** — `conn.users.insert({...})`, `find(name="Alice")`, `find(score__gte=5)`.
- **Query builder**, hybrid search, agent memory, pipeline `DbReadStep`/`DbWriteStep`. See [`pytekt/db/README.md`](pytekt/db/README.md).

### Astronomy / universe (new in 0.2.0)

- **`pytekt.universe`:** RA/Dec ↔ Alt/Az, moon phase, air mass, orbits, flat ΛCDM cosmology.
- **CLI:** `pytekt universe moon|sky|coords|web`.
- **Web dashboard:** `pytekt universe web` (React sky map, observation log).
- **C++ fast path** in `pytekt._pytekt_universe` with Python fallbacks. See [`pytekt/universe/README.md`](pytekt/universe/README.md).

### Big data kernels

- **`pytekt.bigdata`:** Prefix sums, rolling windows, rolling means, histograms, and chunk statistics for large numeric arrays.
- **Integration:** `pytekt.algorithms.arrays` now routes `rolling_sum` and `compute_prefix_sums` through the native backend when it is available.

### Research experiments (new in 0.2.0)

- **`pytekt.experiments`:** `Experiment` context manager (fixed seed, tracker logging, `manifest.json`).
- **`BenchmarkSuite`** — multi-seed baselines on iris, wine, breast cancer, digits (`pytekt benchmark` CLI).
- **`export_results_table`** — LaTeX, CSV, Markdown, HTML from tracker runs.
- **`pytekt doctor`** — environment and optional-dependency health check.

### Usage dashboard

- **`pytekt.usage`:** Token and cost tracking with browser dashboard (`pytekt usage` → http://127.0.0.1:3847).

### PyTekt Former — Transformer training

- **Decoder-only (GPT-style) transformers** with NumPy-backed autograd: no PyTorch/TF required for small-scale experiments.
- **Core:** `Tensor` with gradient tracking; `matmul`, `softmax`, `layer_norm`, `relu`, scaled dot-product attention.
- **Model:** Embedding, sinusoidal positional encoding, multi-head attention, feed-forward blocks, pre-norm stack, LM head.
- **Training:** Cross-entropy loss, Adam optimizer, `Trainer` with `train_step` / `train_epoch`.
- **Data:** Character- or word-level tokenizer, sliding-window text dataset, batch loader.
- **Visualization:** Attention heatmaps (per head/layer), training loss over epochs, weight eigenvalue/singular-value spectrum.
- **Install:** `pip install pytekt[former]`. Run: `python -m pytekt.former.experiments.train_small_model`, `python -m pytekt.former.examples.attention_demo`, `python -m pytekt.former.examples.text_generation`. Per-subpackage demos: `python -m pytekt.former.core.examples.demo_tensor`, `pytekt.former.datasets.examples.demo_tokenizer`, `pytekt.former.experiments.examples.demo_config`, `pytekt.former.models.examples.demo_forward`, `pytekt.former.training.examples.demo_loss`, `pytekt.former.visualization.examples.demo_attention_plot`.

---

## Usage Examples

The following examples are drawn from the library and the project’s `example.py` and notebooks. They show how to use the main modules after installation.

### Mathematics and statistics

```python
import pytekt

# Basic arithmetic and statistics
pytekt.maths.addition(10, 5)
pytekt.maths.mean([1, 2, 3, 4, 5])
pytekt.maths.variance([1, 2, 3, 4, 5])
pytekt.maths.std_dev([1, 2, 3, 4, 5])
pytekt.maths.correlation([1, 2, 3, 4], [2, 4, 6, 8])
pytekt.maths.min_max_scale([1, 2, 3, 4, 5])
pytekt.maths.z_score([1.0, 2.0, 3.0, 4.0, 5.0])

# Linear algebra
pytekt.maths.determinant([[1, 2], [3, 4]])
pytekt.maths.dot_product([1, 2, 3], [4, 5, 6])
pytekt.maths.transpose([[1, 2], [3, 4], [5, 6]])
pytekt.maths.matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
pytekt.maths.normalize_vector([3, 4], norm="l2")

# Activations and ML helpers
pytekt.maths.sigmoid([0, 1, -1])
pytekt.maths.relu([-1, 0, 1, 2])
pytekt.maths.softmax([1.0, 2.0, 3.0])
```

### Algorithms: search and arrays

```python
import pytekt
from pytekt.algorithms import binary_search, lower_bound, upper_bound, flatten_array, chunk_array
from pytekt.algorithms.search import is_sorted, jump_search, find_peak_element, exponential_search
from pytekt.algorithms.arrays import sliding_window, rolling_sum, remove_duplicates

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

from pytekt.io import atomic_write, file_sha256, iter_lines, verify_sha256

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
from pytekt.providers import OpenAIProvider, create_provider, supported_providers
from pytekt.providers.base import ChatMessage

# Explicit provider (set OPENAI_API_KEY in your environment)
p = OpenAIProvider()
reply = p.complete([ChatMessage(role="user", content="Summarize PyTekt in one sentence.")])
print(reply)

# Factory by name (see supported_providers() for strings)
# p2 = create_provider("openai")
```

### Fast numerics (NumPy fallback or native extension)

Native C++ extensions (`pytekt._pytekt_core`, physics, universe, …) accelerate hot paths when built; Python fallbacks always work.

```python
import pytekt

print("Native extension active:", pytekt.using_native_extension())
print("Any native backend active:", pytekt.using_any_native_extension())
print("Native backends:", pytekt.native_status())
x = [1.0, 2.0, 3.0]
print(pytekt.fast_sum(x), pytekt.fast_mean(x), pytekt.fast_softmax(x))
print(pytekt.fast_norm1([-1.0, 2.0]), pytekt.fast_clip(x, 0.0, 2.5))
sorted_keys = [0.0, 0.5, 1.0, 1.5]
print(pytekt.fast_lower_bound(sorted_keys, 1.0), pytekt.fast_upper_bound(sorted_keys, 1.0))
```

Library-wide C++ coverage is exposed through `pytekt.native_status()`, `pytekt.native_backends()`, and `pytekt.native_build_info()`. That covers the core numerics, astronomy, and physics backends.

### Visualization (requires matplotlib)

```python
import pytekt
from pytekt.visualization import (
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
from pytekt.visualization.utils import save_plot

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
from pytekt.visualization import plot_3d_scatter, plot_3d_surface, save_figures_pdf

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
from pytekt.datasets import load_iris
from pytekt.preprocessing import StandardScaler, PreprocessingPipeline
from pytekt.models import GaussianNB
from pytekt.metrics import accuracy_score, classification_report
from pytekt.hyperopt import GridSearch
from pytekt.tracker import Tracker

ds = load_iris()
X = StandardScaler().fit_transform(ds.data)
clf = GaussianNB()
clf.fit(X, ds.target)
print("accuracy:", accuracy_score(ds.target, clf.predict(X)))
print(classification_report(ds.target, clf.predict(X)))

# Hyperparameter search with experiment tracking
tracker = Tracker(".pytekt_experiments")
from pytekt.models import KNNClassifier
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
from pytekt.experiments import Experiment, BenchmarkSuite, export_results_table
from pytekt.experiments import export_results_file
from pytekt.tracker import Tracker
from pytekt.datasets import load_iris
from pytekt.models import GaussianNB, MLPipeline, save_model
from pytekt.preprocessing import StandardScaler
from pytekt.metrics import accuracy_score

# Reproducible run with manifest + tracker
with Experiment("iris_nb_v1", seed=42) as exp:
    ds = load_iris(seed=42)
    pipe = MLPipeline(StandardScaler(), GaussianNB())
    pipe.fit(ds.data, ds.target)
    exp.log_metrics(accuracy=accuracy_score(ds.target, pipe.predict(ds.data)))
    save_model(pipe.estimator, f"{exp.run_dir}/model", metadata={"dataset": "iris"})

# LaTeX table for a paper
runs = Tracker(".pytekt_experiments").list_runs()
print(export_results_table(runs, format="latex", metric_columns=["accuracy"]))

# Standard benchmark leaderboard
suite = BenchmarkSuite(seeds=[0, 1, 2, 3, 4])
print(suite.leaderboard_markdown(suite.run()))
```

```bash
python -m pytekt doctor
python -m pytekt benchmark --seeds 5 -o leaderboard.md
```

### Model evaluation (legacy `pytekt.evaluate`)

```python
import pytekt

# In-memory metrics (legacy API)
y_true = [0, 1, 1, 0, 1]
y_pred = [0, 1, 0, 0, 1]
metrics = pytekt.evaluate.calculate_classification_metrics(y_pred, y_true)

# Prefer pytekt.metrics for new code:
from pytekt.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
print(accuracy_score(y_true, y_pred), f1_score(y_true, y_pred))

pred_vals = [1.2, 2.1, 3.0]
true_vals = [1.0, 2.0, 3.2]
print(r2_score(true_vals, pred_vals), mean_squared_error(true_vals, pred_vals))

# File-based evaluation (JSON or CSV)
file_metrics = pytekt.evaluate.evaluate_predictions("preds.json", "answers.json")
```

### Code analysis

```python
import pytekt

source = """
def train_model(x, y):
    return x + y

class Trainer:
    pass
"""
pytekt.code.explain_code(source)
pytekt.code.extract_functions(source)
pytekt.code.extract_classes(source)
pytekt.code.extract_imports(source)
pytekt.code.strip_comments(source)
pytekt.code.analyze_complexity(source)
pytekt.code.extract_docstrings(source)
pytekt.code.count_operators(source)
pytekt.code.find_code_smells(source)
```

### File management and watcher

```python
import pytekt

pytekt.files.create_empty_file("research.txt")
# Other helpers: move, copy, delete, list files, etc.

def on_change(path):
    print("Changed:", path)
pytekt.watcher.watch_file_for_changes("data.csv", on_change_callback=on_change)
```

### Documentation generation (optional: reportlab for PDF)

```python
import pytekt

pytekt.pdf.generate_complete_documentation("my_docs")
pytekt.pdf.create_api_documentation("api_ref.pdf")
pytekt.pdf.create_api_documentation_html("api_ref.html")
pytekt.pdf.create_user_guide_pdf("user_guide.pdf")
pytekt.pdf.create_changelog_pdf("changelog.pdf")
pytekt.pdf.create_module_reference_doc("text", format="md")  # e.g. pytekt_text_reference.md
pytekt.pdf.export_api_index("api_index.md", format="md")
hits = pytekt.pdf.search_public_api("embed")  # [{"module", "kind", "name"}, ...]
# Also: create_api_documentation_md, create_text_documentation, create_module_dependency_doc,
# export_api_index(..., include_classes=True), validate_documentation, create_documentation_index, …
```

### Embeddings (optional: sentence-transformers)

```python
import pytekt

vec = pytekt.embed.embed_text("Machine learning research")
sim = pytekt.embed.cosine_similarity(vec1, vec2)
```

### Git (optional: gitpython)

```python
import pytekt

manager = pytekt.git.GitManager(".")
status = manager.status()
commits = manager.get_commit_history(limit=10)
```

### LLM tool loop (OpenAI or OpenAI-compatible, API keys required)

```python
from pytekt.providers import OpenAIProvider
from pytekt.tools import ToolRegistry, function_tool, run_tool_loop

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
from pytekt.rag import MemoryVectorStore, SimpleRAGIndex

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
from pytekt.cache import MemoryCache, DiskCache, LLMCache, cached

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
from pytekt.data import load_csv, load_jsonl, train_val_test_split, augment_text
from pytekt.data import Schema, Field, validate_dataset

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
from pytekt.datasets import (
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

**`pytekt.data` vs `pytekt.datasets`:** use **`pytekt.data`** when you need a list of row dicts for pipelines and schema validation; use **`pytekt.datasets`** when you need a **`Dataset`** with NumPy arrays for ML prototyping, built-in benchmarks, or file round-trips.

### User interfaces — React-style frontend

```python
from pytekt.ui import (
    Component,
    html,
    AppShell,
    MetricGrid,
    Card,
    Stack,
    render_app,
    function_component,
)
from pytekt.datasets import load_iris
from pytekt.models import GaussianNB
from pytekt.metrics import accuracy_score
from pytekt.preprocessing import StandardScaler

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
                        html.p({}, "Tune with pytekt.hyperopt or log runs to pytekt.tracker."),
                    ]),
                ]
            ),
        )

render_app(ExperimentDashboard(), output="dashboard.html", open_browser=True)
# serve_app(ExperimentDashboard(), port=8765)  # local dev server

# --- Imperative HTML reports (legacy) ---
from pytekt.ui import PageBuilder, build_experiment_dashboard, launch_hub

page = PageBuilder("Training summary", subtitle="Run 42")
page.add_metrics({"accuracy": 0.94, "loss": 0.08})
page.save("summary.html")
build_experiment_dashboard(".pytekt_experiments", output="runs.html")
# launch_hub()  # PyTekt Hub at http://127.0.0.1:3000
```

```bash
pytekt ui --list
pytekt ui --report .pytekt_experiments -o experiments.html
pytekt ui --gradio          # needs pip install 'pytekt[ui]'
pytekt ui --streamlit
```

### Tokenization

```python
from pytekt.tokenizer import BPETokenizer, WordPieceTokenizer

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
from pytekt.structures import Trie, BloomFilter, LRUCache, UnionFind, PriorityQueue

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
from pytekt.pipeline import Pipeline, MapStep, FilterStep, FunctionStep

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
from pytekt.store import KeyValueStore, PersistentVectorStore, ChatHistoryStore
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

### Unified database (`pytekt.db`)

```python
import pytekt.db as db

conn = db.connect("sqlite://./app.db")  # zero extra deps
conn.users.insert({"name": "Alice", "score": 10})
print(conn.users.find(name="Alice"))

# Query builder
rows = conn.table("users").where(conn.col.score > 5).select("name", "score").all()

# Remote DBs: pip install pytekt[db]
# conn = db.connect("mysql://user:pass@localhost/mydb")
# conn = db.connect("mongodb://localhost:27017/mydb")

# CLI: pytekt db status | sync-usage | sync-tracker
```

### Experiment tracking

```python
from pytekt.tracker import Tracker

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
from pytekt.llm_eval import toxicity_check, contains_pii, estimate_cost, CostTracker

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

### API serving (requires pip install pytekt[serve])

```python
from pytekt.serve import create_app
from pytekt.providers import OpenAIProvider

# Create a FastAPI app with /chat and /health endpoints
app = create_app(provider=OpenAIProvider())
# Run with: uvicorn module:app --port 8000
# POST /chat  {"messages": [{"role": "user", "content": "Hello"}]}
# GET  /health → {"status": "ok", "version": "0.2.0"}
```

### PyTekt Former — transformer training (optional: pip install pytekt[former])

```python
import pytekt
from pytekt.former import Transformer, Trainer
from pytekt.former.datasets import create_dataloader
from pytekt.former.visualization import plot_attention_map, plot_training_metrics

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

Run from command line: `python -m pytekt.former.experiments.train_small_model`, `python -m pytekt.former.examples.attention_demo`, `python -m pytekt.former.examples.text_generation`.

---

## Module Reference

| Module | Description |
|--------|-------------|
| `pytekt.maths` | Mathematics, statistics, linear algebra, ML helpers, signal processing. |
| `pytekt.io` | Streaming reads, atomic writes, SHA-256 checksum helpers. [`pytekt/io/README.md`](pytekt/io/README.md), [`pytekt/io/examples/`](pytekt/io/examples/). |
| `pytekt.providers` | Chat clients + `create_provider`; `complete` / **`complete_turn`**. [`pytekt/providers/README.md`](pytekt/providers/README.md), [`pytekt/providers/examples/`](pytekt/providers/examples/). |
| `pytekt` (`fast_*`, `using_native_extension`) | 1D/2D numerics: sums, dot/norms, mean/variance, argmin/max, min/max, ReLU/softmax/sigmoid/tanh/clip, cumsum, matvec, sorted `lower_bound` / `upper_bound`; C++ when `_pytekt_core` is built else NumPy. |
| `pytekt.bigdata` | Native big-data kernels: prefix sums, rolling windows, rolling means, histograms, and chunk statistics with Python fallbacks. |
| `pytekt.algorithms` | **572+** functions across 21 categories; catalog API; search, arrays, graphs, sorting, DP, trees, strings, … [`CATALOG.md`](pytekt/algorithms/CATALOG.md). |
| `pytekt.visualization` | 1D/2D/training plots; heatmaps, confusion matrices, attention maps; **3D** plots; seaborn (`[viz]`); Plotly 3D (`[viz3d]`); multi-page **PDF** / HTML figure reports. |
| `pytekt.vision` | Computer vision on NumPy arrays: I/O, transforms, color, filters, draw, metrics, OpenCV ops. Install with `[vision]`. See [`pytekt/vision/README.md`](pytekt/vision/README.md) and [`pytekt/vision/examples/`](pytekt/vision/examples/). Not plotting — use `pytekt.visualization` for charts. |
| `pytekt.former` | Transformer training: Transformer, Trainer, TextDataset, tokenizer, attention/training/weight-spectrum plots. Install with `[former]`. See [`pytekt/former/README.md`](pytekt/former/README.md) and per-subpackage `examples/` (e.g. `pytekt/former/core/examples/`). |
| `pytekt.embed` | Text embeddings and vector similarity (optional: sentence-transformers). |
| `pytekt.evaluate` | Legacy classification/regression metrics; file-based evaluation. Prefer `pytekt.metrics` for new code. |
| `pytekt.preprocessing` | Scalers, encoders, imputers, transforms; `PreprocessingPipeline`, `ColumnTransformer`. |
| `pytekt.models` | `LinearRegression`, `LogisticRegression`, `KNNClassifier`/`KNNRegressor`, `KMeans`, `PCA`, `GaussianNB`, decision trees. |
| `pytekt.metrics` | `accuracy_score`, `f1_score`, `confusion_matrix`, `r2_score`, `silhouette_score`, `bleu_score`, `ndcg_score`, … |
| `pytekt.hyperopt` | `GridSearch`, `RandomSearch`, `BayesianSearch`, `EarlyStopping`, `cross_val_score`; integrates with `pytekt.tracker`. |
| `pytekt.experiments` | `Experiment`, `BenchmarkSuite`, `export_results_table` (LaTeX/CSV/MD); research reproducibility. |
| `pytekt.code` | Code explanation, extraction, complexity, docstrings, code smells. |
| `pytekt.prompt` | Prompt templates and utilities. |
| `pytekt.snippets` | Code snippet utilities. |
| `pytekt.pdf` | API/user-guide/changelog (PDF, text, Markdown, **HTML**), module dependency reports, `search_public_api`, `create_module_reference_doc`, `export_api_index` (JSON/CSV/**MD**), class-aware introspection. Optional ReportLab for PDF. |
| `pytekt.parser` | Language detection and code parsing (30+ languages). |
| `pytekt.files` | File and directory operations. |
| `pytekt.watcher` | Real-time file change monitoring. |
| `pytekt.git` | Git repository operations (optional: GitPython). |
| `pytekt.utils` | General utilities. |
| `pytekt.text` | Text processing. |
| `pytekt.cli` | Command-line interface: `pytekt start` (Hub), `info`, `embed`, `eval`, `chat`, `monitor`, `git`, … |
| `pytekt.ui` | **React-style:** `Component`, `html`, `render_app`, `AppShell`, `MetricGrid`, …; **legacy:** `PageBuilder`, `launch_hub`, dashboards; optional Gradio/Streamlit (`[ui]`). |
| `pytekt.hub` | PyTekt Hub static server (used by `pytekt.ui.launch_hub` / `pytekt start`). |
| `pytekt.tools` | Tool schemas, registry, `run_tool_loop`, `FakeToolProvider` / `make_tool_turn`, retry/rate-limit, token estimates (`[tools]`). [`pytekt/tools/README.md`](pytekt/tools/README.md), [`pytekt/tools/examples/`](pytekt/tools/examples/). |
| `pytekt.rag` | Chunking, vector stores, `SimpleRAGIndex` (`[rag]`). [`pytekt/rag/README.md`](pytekt/rag/README.md), [`pytekt/rag/examples/`](pytekt/rag/examples/). |
| `pytekt.config` | TOML/YAML load, layered files, dotted keys, env merge, typed coercion (`[config]`). See [`pytekt/config/README.md`](pytekt/config/README.md) and [`pytekt/config/examples/`](pytekt/config/examples/). |
| `pytekt.env` | `.env` file parsing, `require_env`. |
| `pytekt.benchmarks` | `timed_run`, NumPy vs `fast_sum` comparison. |
| `pytekt.cache` | `MemoryCache`, `DiskCache` (SQLite), `LLMCache`, `@cached` decorator — all with TTL. |
| `pytekt.structures` | `Trie`, `BloomFilter`, `LRUCache`, `MinHeap`, `MaxHeap`, `PriorityQueue`, `UnionFind`. |
| `pytekt.data` | CSV/JSON/JSONL loaders (row dicts), `train_val_test_split`, `kfold_split`, text augmentation, `Schema` validation. |
| `pytekt.datasets` | Built-in benchmarks (Iris, Digits, Moons, Wine, …), NLP sets (sentiment, NER, spam, Q&A), `make_*` generators, `Dataset`, `fetch`/`list_datasets`/`summary`, file I/O (`read_csv`, `read_file`, `read_parquet`, `to_dataframe`). |
| `pytekt.tokenizer` | `BPETokenizer`, `WordPieceTokenizer`, `Vocabulary` (save/load, special tokens). |
| `pytekt.pipeline` | `Pipeline`, `Step`, `FunctionStep`, `MapStep`, `FilterStep`, `BatchStep` — retry, fallback, timing. |
| `pytekt.store` | `KeyValueStore` (SQLite), `PersistentVectorStore`, `ChatHistoryStore` (threads + search). |
| `pytekt.db` | Unified DB: SQLite, MySQL, Postgres, Mongo, Redis — dict API + query builder. [`pytekt/db/README.md`](pytekt/db/README.md). |
| `pytekt.universe` | Astronomy: coordinates, observing, orbits, cosmology, catalogs (C++ accelerated). [`pytekt/universe/README.md`](pytekt/universe/README.md). |
| `pytekt.physics` | Classical physics toolkit + CLI/dashboard. [`pytekt/physics/README.md`](pytekt/physics/README.md). |
| `pytekt.vision` | Computer vision on NumPy arrays (`[vision]`). [`pytekt/vision/README.md`](pytekt/vision/README.md). |
| `pytekt.monitor` | Hardware metrics dashboard (`[monitor]`). |
| `pytekt.tracker` | `Tracker`, `Run` — log params, metrics, artifacts; `compare_runs`, `best_run`. |
| `pytekt.llm_eval` | `semantic_similarity`, `faithfulness_score`, `check_groundedness`, `toxicity_check`, `contains_pii`, `estimate_cost`, `CostTracker`. |
| `pytekt.serve` | `PyTektServer`, `create_app` — FastAPI `/chat`, `/rag`, `/health` endpoints (`[serve]`). |
| `pytekt.usage` | Token/cost dashboard (`pytekt usage`). |

Package entry point and version:

```python
import pytekt
print(pytekt.__version__)  # 0.2.0
```

---

## Supported Languages

The parser and code analysis modules support the following (among others):

**Programming languages:** Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, Swift, Kotlin, Scala, Haskell, PHP, Ruby, Perl, Lua, Julia, R, MATLAB, Clojure, PowerShell, Bash.

**Markup and data:** HTML, CSS, SQL, JSON, XML, YAML, Markdown, Dockerfile, Terraform, Ansible.

See `pytekt.parser` and `pytekt.code` for language-specific behavior and APIs.

---

## Documentation and Resources

### Aqwel AI — official

| Resource | URL |
|----------|-----|
| **Aqwel AI (company & products)** | [https://aqwelai.xyz/](https://aqwelai.xyz/) |
| **PyTekt product documentation (web)** | [https://aqwelai.xyz/#/docs](https://aqwelai.xyz/#/docs) |
| **PyPI package** | [https://pypi.org/project/pytekt/](https://pypi.org/project/pytekt/) |

### Repository documentation (this project)

| Resource | Description |
|----------|-------------|
| [README.md](README.md) | **Primary doc** — product overview, install, features, module tree, examples |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Research library layout |
| [pytekt/physics/README.md](pytekt/physics/README.md) | Physics toolkit |
| [pytekt/vision/README.md](pytekt/vision/README.md) | Computer vision |
| [pytekt/algorithms/CATALOG.md](pytekt/algorithms/CATALOG.md) | Full algorithms catalog (572+ functions) |
| [pytekt/db/README.md](pytekt/db/README.md) | Unified database layer |
| [pytekt/universe/README.md](pytekt/universe/README.md) | Astronomy module |
| [SECURITY.md](SECURITY.md) | Secrets, `~/.pytekt.yaml`, publishing checklist |
| [.env.example](.env.example) | Env var template (private `.env` is gitignored) |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute to PyTekt |
| [pyproject.toml](pyproject.toml) | Version, extras (`[ai]`, `[full]`, …), PyPI metadata |

### In-package and generated docs

- **`pytekt.pdf`:** `generate_complete_documentation(output_dir)` — API + user-guide bundles; or `create_api_documentation_html` / `create_api_documentation_md` for a single reference.
- **Module READMEs:** [pytekt/algorithms/README.md](pytekt/algorithms/README.md), [pytekt/visualization/README.md](pytekt/visualization/README.md).

### Example notebooks and runnable demos

| Area | Path |
|------|------|
| Algorithms | `pytekt/algorithms/examples/` — search, arrays |
| Visualization | `pytekt/visualization/examples/` — arrays, matrices, training |
| Config | `pytekt/config/examples/` — TOML/YAML merge |
| I/O & LLM | `pytekt/io/examples/`, `pytekt/providers/examples/`, `pytekt/rag/examples/`, `pytekt/tools/examples/` |
| Former (transformers) | `pytekt/former/examples/` and `pytekt/former/*/examples/` |
| Root scripts | `example.py`, `main.py` |

### CLI reference (summary)

| Command | Product area |
|---------|----------------|
| `pytekt start` / `pytekt ui` | PyTekt Hub browser UI |
| `pytekt embed`, `pytekt eval`, `pytekt rag`, `pytekt prompt` | Research / LLM utilities |
| `pytekt benchmark`, `pytekt doctor` | ML benchmarks and environment check |
| `pytekt welcome` | Install animation overview |
| `pytekt --help` / `pytekt help` | Full command catalog |
| `pytekt agent` / `api` / `auth` | Not shipped in 0.2.0 — see [Not in 0.2.0](#not-in-020) |

### Testing

```bash
pip install -e ".[dev,ai]"
pytest tests/
```

Includes Core ML, providers, RAG, tools, physics, universe, and vision tests.

---

## What shows on GitHub

This repository is open source. The following **should show** (and are committed):

| Category | What shows |
|----------|------------|
| **Docs** | `README.md`, `docs/PROJECT_STRUCTURE.md`, `SECURITY.md`, `.env.example`, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, module READMEs under `pytekt/*/` |
| **Config** | `pyproject.toml`, `setup.py`, `MANIFEST.in`, `requirements.txt` |
| **Source** | `pytekt/**/*.py`, `src/pytekt_core.cpp`, `src/pytekt_bigdata.cpp`, `src/pytekt_universe.cpp`, `src/pytekt_physics.cpp`, `src/native/**/*.hpp` |
| **Tests** | `tests/` — pytest suite (algorithms, io, maths, text, snippets, pdf, Core ML stack); `pip install -e ".[dev]"` then `pytest tests/` |
| **Examples** | `example.py`, `main.py`; notebooks in `pytekt/algorithms/examples/`, `pytekt/visualization/examples/`, `pytekt/config/examples/`; `python -m` demos under `pytekt/io/examples/`, `pytekt/providers/examples/`, `pytekt/rag/examples/`, `pytekt/tools/examples/`, `pytekt/former/*/examples/` |
| **Example assets** | `pytekt/visualization/examples_visualization/*.png` (plot previews); `pytekt/former/examples/*.png` (attention demos); `pytekt/former/examples_results/*.png` when committed (see folder README) |
| **Repo meta** | `.gitignore` |

The following **do not show** (ignored via `.gitignore`):

- Build artifacts: `build/`, `dist/`, `*.egg`, `*.egg-info/`, compiled extension modules under `pytekt/_pytekt_core*.so` / `pytekt/_pytekt_core*.pyd` / `pytekt/_pytekt_bigdata*.so` / `pytekt/_pytekt_bigdata*.pyd`
- Python cache: `__pycache__/`, `*.pyc`, `*.pyo`
- Virtual environments: `.venv/`, `venv/`, `env/`
- Secrets: `.env`, `.env.*` (never commit; copy from [`.env.example`](.env.example))
- User config: `~/.pytekt.yaml`, `.pytekt.yaml`, `*.local.yaml` (API keys and CLI settings — **private**)
- Credentials: `secrets/`, `credentials/`, `*.pem`, `*.key`
- ML artifacts: `wandb/`, `checkpoints/`, `*.pt`, `*.pth`, `*.ckpt`, `mlruns/`, local `data/private/`
- IDE/editor: `.idea/`, `.vscode/`, `.cursor/`
- OS files: `.DS_Store`
- Test/coverage: `.coverage`, `htmlcov/`, `.pytest_cache/`, `.mypy_cache/`, `.ipynb_checkpoints/`
- Generated output: `example_output/`, optional `pytekt/former/examples_results/*.png`
- Native builds: `pytekt/_pytekt_core*.so`, `pytekt/_pytekt_core*.pyd`, `pytekt/_pytekt_bigdata*.so`, `pytekt/_pytekt_bigdata*.pyd`

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

**PyTekt** is an **Aqwel AI** open-source product.

- **Product:** PyTekt  
- **Created by:** [Aqwel AI](https://aqwelai.xyz/)  
- **Main developer:** Aksel Aghajanyan  
- **Company:** [Aqwel AI](https://aqwelai.xyz/) · **Contact:** aqwelai.company@gmail.com  
- **Copyright:** 2025–2026 Aqwel AI  
- **License:** Apache-2.0 (see [LICENSE](LICENSE))

---

## Library Statistics

- **`pytekt/`** ships research-library subpackages including **`db`**, **`universe`**, **`physics`**, **`vision`**, **`experiments`**, **`usage`**, **`providers`**, Core ML, **`former`**, **`hub`**, **`ui`**, and the rest listed in [Directory structure](#directory-structure).
- **Public exports** in `pytekt.__all__` include **`preprocessing`**, **`models`**, **`metrics`**, **`hyperopt`**, **`vision`**, **`physics`**, **`universe`**, and **`ui`**.
- **Pytest suite** in `tests/` (Core ML, algorithms catalog, universe, physics, vision, io, maths, text, snippets, pdf).
- **572 algorithms** across **21** categories via `pytekt.algorithms` catalog API.
- **24 built-in datasets** via `pytekt.datasets` (10 toy/tabular, 5 NLP, 9 generators) plus pandas-style file loaders.
- **Core ML stack:** 4 subpackages — preprocessing (12 transformers), models (10 estimators), metrics (22 functions), hyperopt (grid/random/Bayesian search + CV).
- **19 `fast_*` entry points** (plus `using_native_extension`) for 1D/2D vector numerics, re-exported from `pytekt`.
- **71+ mathematical functions** in the maths module.
- **PyTekt Former:** Decoder-only transformer training with NumPy autograd, multi-head attention, and visualization (optional `[former]` extra).
- **Full research pipeline** from data loading, tokenization, and augmentation through training, evaluation, caching, experiment tracking, and API serving — plus physics, astronomy, and classic CV.
- **Optional dependencies** for embeddings, PDF generation, serving, DB backends, astronomy, vision, Plotly 3D, Parquet/Excel file I/O, and full PyTorch/sklearn stack; core modules work with minimal dependencies (numpy + stdlib).

---

**PyTekt** is built so you can move from **numeric and algorithmic baselines** through **classical ML** (preprocess → train → evaluate → tune) to **LLM-assisted workflows**, **retrieval**, **experiment tracking**, **physics / astronomy / vision**, and **production serving**—all in one **Aqwel AI** product with clear optional extras.

*Aqwel AI product · Main developer: Aksel Aghajanyan · [Documentation](https://aqwelai.xyz/#/docs) · [PyPI](https://pypi.org/project/pytekt/)*
