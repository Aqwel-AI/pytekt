#!/usr/bin/env python3
"""
PyTekt v0.2.0 - AI Research Library
=======================================

Open-source Python library by Aqwel AI for AI research, machine learning,
data science, physics, astronomy, and classic computer vision.

This package provides:
- Mathematical and statistical operations
- Algorithm utilities (search, arrays, graphs) for research and education
- Visualization (1D/2D/3D plots, training metrics, matrices, heatmaps)
- Core ML stack (preprocessing, classical models, metrics, hyperparameter search)
- Text embeddings, prompts, RAG, and LLM provider clients
- Physics and astronomy toolkits (optional C++ acceleration)
- Computer vision helpers on NumPy arrays (`[vision]` extra)
- Documentation generation, code analysis, files/Git utilities
- Caching, data structures, data loaders, tokenizers, pipelines
- Persistent stores, experiment tracking, LLM evaluation
- REST serving (FastAPI) and Hub / usage dashboards

Terminal coding agent (`pytekt agent`) is not available in this release.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI

For documentation and examples, visit:
https://aqwelai.xyz/
"""
# Config and environment
from . import config
from . import env
# Import the utilities module for general helper functions
from . import utils

# Define the current version of the package
__version__ = "0.2.1"

# Define the author information
__author__ = "Aksel Aghajanyan"
__developer__ = "Aqwel AI Team"

# Define the license type for the package
__license__ = "Apache-2.0"

# Define the copyright information
__copyright__ = "2025 Aqwel AI"

# Import the text processing module for text analysis and manipulation
from . import text

# Import the file management module for file operations and organization
from . import files

# Safe I/O primitives
from . import io

# Remote LLM APIs (OpenAI, Gemini, Anthropic, OpenAI-compatible servers)
from . import providers

# Tool-calling helpers and RAG primitives
from . import tools
from . import rag



# Timing / benchmarks
from . import benchmarks
from . import bench

# Import the code parsing module for language detection and code analysis
from . import parser

# Import the file watching module for real-time file monitoring
from . import watcher





# Import the Git integration module for repository management
from . import git

# Import the mathematics and statistics module for numerical computations
from . import maths

# Import additional AI/ML modules
from . import code
from . import embed
from . import evaluate
from . import prompt
from . import snippets
from . import pdf

# Import algorithms (search, arrays, graphs) and visualization (plots)
from . import algorithms

# Optional extras — soft-import so `import pytekt` works with base deps only
try:
    from . import visualization
except ImportError:  # e.g. missing matplotlib ([viz])
    visualization = None  # type: ignore[assignment]

try:
    from . import former
except ImportError:  # e.g. missing matplotlib via former.visualization
    former = None  # type: ignore[assignment]

try:
    from . import vision
except ImportError:  # e.g. missing pillow ([vision])
    vision = None  # type: ignore[assignment]

# Caching (memory, disk, LLM response cache, @cached decorator)
from . import cache

# Advanced data structures (Trie, Bloom filter, LRU, heaps, Union-Find)
from . import structures

# Data processing (loaders, splitting, augmentation, schema validation)
from . import data

# Tokenization (BPE, WordPiece, vocabulary management)
from . import tokenizer

# Step-based pipelines
from . import pipeline

# Persistent storage (key-value, vector, chat history)
from . import store

# Unified database layer (SQLite, MySQL, PostgreSQL, MongoDB, Redis)
from . import db

# Lightweight astronomy toolkit (coordinates, observing, orbits, cosmology; C++ fast path)
from . import universe

# Experiment tracking (runs, metrics, comparison)
from . import tracker

# LLM output evaluation (similarity, faithfulness, toxicity, cost)
from . import llm_eval

# REST API serving (FastAPI-based model/chat/RAG endpoints)
try:
    from . import serve
except ImportError:  # e.g. missing fastapi ([serve])
    serve = None  # type: ignore[assignment]

# Built-in benchmark datasets (Iris, Digits, Housing, Moons, NER, generators)
from . import datasets

# UI: Hub, HTML dashboards, optional Gradio/Streamlit
from . import ui

# Core ML stack: preprocessing, classical models, metrics, hyperparameter search
from . import preprocessing
from . import models
from . import metrics
from . import hyperopt

# Research experiments: reproducibility, benchmarks, paper exports
from . import experiments
from . import physics
from . import native
from . import bigdata

# Optional C++ extension (fast numerical ops; fallback to NumPy if not built)
from ._core import (
    fast_sum,
    fast_dot,
    fast_norm2,
    fast_norm1,
    fast_mean,
    fast_variance,
    fast_argmax,
    fast_argmin,
    fast_min,
    fast_max,
    fast_relu,
    fast_softmax,
    fast_sigmoid,
    fast_tanh,
    fast_clip,
    fast_cumsum,
    fast_matrix_vector_mul,
    fast_lower_bound,
    fast_upper_bound,
    using_native_extension,
)
from .native import (
    native_backends,
    native_status,
    native_build_info,
    native_status_report,
    using_any_native_extension,
)


# Import the command-line interface module for CLI functionality
from . import cli

# Define the public API exports for the package
__all__ = [
    "__version__",      # Version information
    "__author__",       # Author information
    "__developer__",    # Developing team
    "__license__",      # License information
    "__copyright__",    # Copyright information
    "text",             # Text processing module
    "files",            # File management module
    "io",               # Streaming, atomic writes, checksums
    "providers",        # OpenAI / Gemini / Anthropic / compatible APIs
    "tools",            # LLM tool schemas, registry, loop, retry, tokens
    "rag",              # Chunking, vector stores, simple RAG index
    "config",           # TOML/YAML config loading
    "env",              # Dotenv-style and required env vars
    "benchmarks",       # Timing and fast_* comparison helpers
    "bench",            # Benchmarking + reproducibility utilities
    "parser",           # Code parsing module
    "watcher",          # File watching module
    "utils",            # Utilities module
    "cli",              # Command-line interface module
    "git",              # Git integration module
    "maths",            # Mathematics and statistics module
    "code",             # Code analysis module
    "embed",            # Embedding utilities module
    "evaluate",         # Evaluation metrics module
    "prompt",           # Prompt management module
    "snippets",         # Code snippets module
    "pdf",              # PDF documentation module
    "algorithms",       # Search, arrays, graph utilities
    "visualization",    # Array/matrix/training plotting
    "former",          # Transformer training (decoder-only, NumPy autograd)
    "vision",           # Computer vision (image arrays; [vision] extra)
    "cache",            # Memory/disk/LLM caching with TTL and @cached
    "structures",       # Trie, Bloom filter, LRU cache, heaps, Union-Find
    "data",             # CSV/JSON/JSONL loaders, splitting, augmentation
    "tokenizer",        # BPE, WordPiece tokenizers, vocabulary management
    "pipeline",         # Step-based data/ML pipelines
    "store",            # SQLite key-value, vector store, chat history
    "db",               # Unified DB: SQLite, MySQL, Postgres, Mongo, Redis
    "universe",         # Astronomy: coordinates, observing, orbits, cosmology (C++ optional)
    "tracker",          # Experiment tracking (runs, metrics, comparison)
    "llm_eval",         # LLM output evaluation and cost tracking
    "serve",            # FastAPI-based model/chat/RAG serving
    "datasets",         # Built-in benchmark datasets and generators
    "ui",               # Hub launchers, HTML reports, optional Gradio/Streamlit
    "preprocessing",    # Scalers, encoders, imputers, preprocessing pipelines
    "models",           # Classical ML estimators (linear, KNN, trees, PCA, …)
    "metrics",          # Classification, regression, clustering, NLP, ranking metrics
    "hyperopt",         # Grid/random/Bayesian search with CV and tracker integration
    "experiments",      # Experiment context, benchmark suite, LaTeX/CSV export
    "physics",          # Physics MVP: mechanics, thermo, units, integrators, query pipeline
    "bigdata",          # Native big-data kernels and fallbacks
    "native",           # Library-wide optional C++ backend inspection
    "fast_sum",         # Fast 1D sum (C++ when built)
    "fast_dot",         # Fast dot product (C++ when built)
    "fast_norm2",       # Fast L2 norm (C++ when built)
    "fast_norm1",       # Fast L1 norm (C++ when built)
    "fast_mean",        # Fast mean (C++ when built)
    "fast_variance",    # Fast variance (C++ when built)
    "fast_argmax",      # Fast argmax (C++ when built)
    "fast_argmin",      # Fast argmin (C++ when built)
    "fast_min",         # Fast min reduction (C++ when built)
    "fast_max",         # Fast max reduction (C++ when built)
    "fast_relu",        # Fast ReLU (C++ when built)
    "fast_softmax",     # Fast softmax (C++ when built)
    "fast_sigmoid",     # Fast sigmoid (C++ when built)
    "fast_tanh",        # Fast tanh (C++ when built)
    "fast_clip",        # Fast clip to interval (C++ when built)
    "fast_cumsum",      # Fast cumulative sum (C++ when built)
    "fast_matrix_vector_mul",  # Fast matrix-vector product (C++ when built)
    "fast_lower_bound",  # Fast lower_bound on sorted array (C++ when built)
    "fast_upper_bound",  # Fast upper_bound on sorted array (C++ when built)
    "using_native_extension",
    "native_backends",
    "native_status",
    "native_build_info",
    "native_status_report",
    "using_any_native_extension",
]
