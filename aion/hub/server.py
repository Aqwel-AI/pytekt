"""Lightweight HTTP server for Aion Hub (stdlib only — no FastAPI needed)."""

from __future__ import annotations

import json
import os
import sys
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Any, Dict, List


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def _get_library_info() -> Dict[str, Any]:
    try:
        from .. import __version__, __author__, __developer__, __license__
        return {
            "version": __version__,
            "author": __author__,
            "developer": __developer__,
            "license": __license__,
            "python": sys.version.split()[0],
            "platform": sys.platform,
        }
    except Exception as e:
        return {"version": "unknown", "error": str(e)}


def _get_modules_info() -> List[Dict[str, Any]]:
    modules = [
        {"name": "maths", "category": "Core", "desc": "71+ math, statistics, linear algebra, ML helpers, signal processing", "icon": "calc"},
        {"name": "algorithms", "category": "Core", "desc": "Search, arrays, graphs (BFS, DFS, Dijkstra, A*, MST, PageRank)", "icon": "graph"},
        {"name": "structures", "category": "Core", "desc": "Trie, Bloom filter, LRU cache, heaps, Union-Find", "icon": "blocks"},
        {"name": "data", "category": "Data", "desc": "CSV/JSON/JSONL loaders, train/val/test splitting, text augmentation, schema validation", "icon": "data"},
        {"name": "tokenizer", "category": "Data", "desc": "BPE and WordPiece tokenizers, vocabulary management", "icon": "text"},
        {"name": "pipeline", "category": "Data", "desc": "Step-based processing pipelines with retry, timing, serialization", "icon": "flow"},
        {"name": "providers", "category": "LLM", "desc": "Chat clients for OpenAI, Gemini, Anthropic, OpenAI-compatible APIs", "icon": "cloud"},
        {"name": "tools", "category": "LLM", "desc": "Tool schemas, registry, multi-turn tool loop, rate limiting", "icon": "wrench"},
        {"name": "rag", "category": "LLM", "desc": "Text chunking, vector stores (Memory + FAISS), SimpleRAGIndex", "icon": "search"},
        {"name": "agents", "category": "LLM", "desc": "ReAct, planning, multi-agent orchestration, conversation memory", "icon": "robot"},
        {"name": "llm_eval", "category": "LLM", "desc": "Semantic similarity, faithfulness, toxicity, PII detection, cost tracking", "icon": "check"},
        {"name": "cache", "category": "Infra", "desc": "Memory/disk/LLM response caching with TTL, @cached decorator", "icon": "cache"},
        {"name": "store", "category": "Infra", "desc": "SQLite key-value store, persistent vector store, chat history", "icon": "db"},
        {"name": "tracker", "category": "Infra", "desc": "Experiment tracking — log params, metrics, artifacts, compare runs", "icon": "chart"},
        {"name": "serve", "category": "Infra", "desc": "FastAPI server for /chat, /rag, /health endpoints", "icon": "server"},
        {"name": "datasets", "category": "Data", "desc": "Built-in benchmarks + synthetic generators; file I/O (CSV, JSON, Parquet, Excel) pandas-style", "icon": "data"},
        {"name": "preprocessing", "category": "ML", "desc": "Scalers, encoders, imputers, polynomial features, ColumnTransformer, PreprocessingPipeline", "icon": "gear"},
        {"name": "models", "category": "ML", "desc": "NumPy estimators: linear/logistic regression, KNN, KMeans, PCA, Naive Bayes, decision trees", "icon": "brain"},
        {"name": "metrics", "category": "ML", "desc": "Classification, regression, clustering, NLP (BLEU/ROUGE), ranking (NDCG/MRR) metrics", "icon": "check"},
        {"name": "hyperopt", "category": "ML", "desc": "GridSearch, RandomSearch, BayesianSearch with k-fold CV, early stopping, tracker logging", "icon": "chart"},
        {"name": "visualization", "category": "Viz", "desc": "1D/2D/3D plots, training metrics, heatmaps, PDF/HTML reports", "icon": "chart"},
        {"name": "former", "category": "ML", "desc": "NumPy-backed transformer training — Tensor autograd, attention, Trainer", "icon": "brain"},
        {"name": "embed", "category": "ML", "desc": "Text embeddings, cosine similarity, PCA, clustering, batch processing", "icon": "vector"},
        {"name": "evaluate", "category": "ML", "desc": "Classification and regression metrics, file-based evaluation", "icon": "check"},
        {"name": "code", "category": "Dev", "desc": "Code analysis, complexity, function/class extraction, smell detection", "icon": "code"},
        {"name": "io", "category": "Dev", "desc": "Streaming reads, atomic writes, SHA-256 checksums", "icon": "file"},
        {"name": "config", "category": "Dev", "desc": "TOML/YAML config loading, layered merge, env overrides", "icon": "gear"},
        {"name": "git", "category": "Dev", "desc": "Git status, commit history, branches, diffs via GitPython", "icon": "git"},
        {"name": "files", "category": "Dev", "desc": "File CRUD — create, move, copy, delete, directory listing", "icon": "folder"},
        {"name": "watcher", "category": "Dev", "desc": "Real-time file monitoring via watchdog", "icon": "eye"},
        {"name": "pdf", "category": "Dev", "desc": "API docs generation — PDF, HTML, Markdown, symbol search", "icon": "doc"},
        {"name": "parser", "category": "Dev", "desc": "Language detection for 30+ programming languages", "icon": "lang"},
        {"name": "text", "category": "Dev", "desc": "Text processing and manipulation utilities", "icon": "text"},
        {"name": "ui", "category": "Dev", "desc": "Hub, HTML dashboards, experiment reports; optional Gradio/Streamlit ([ui])", "icon": "chart"},
    ]
    return modules


def _get_deps_status() -> List[Dict[str, Any]]:
    import io
    import contextlib
    import warnings
    deps = []
    checks = [
        ("numpy", "numpy"),
        ("watchdog", "watchdog"),
        ("gitpython", "git"),
        ("matplotlib", "matplotlib"),
        ("sentence-transformers", "sentence_transformers"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("psutil", "psutil"),
        ("tiktoken", "tiktoken"),
        ("faiss-cpu", "faiss"),
        ("reportlab", "reportlab"),
        ("pyyaml", "yaml"),
        ("openai", "openai"),
        ("torch", "torch"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("seaborn", "seaborn"),
    ]
    for display_name, import_name in checks:
        try:
            with warnings.catch_warnings(), contextlib.redirect_stderr(io.StringIO()):
                warnings.simplefilter("ignore")
                mod = __import__(import_name)
            ver = getattr(mod, "__version__", "installed")
            deps.append({"name": display_name, "installed": True, "version": str(ver)})
        except Exception:
            deps.append({"name": display_name, "installed": False, "version": ""})
    try:
        from ..native import native_backends

        for status in native_backends().values():
            deps.append(
                {
                    "name": f"{status.module_name} (C++)",
                    "installed": status.available,
                    "version": "native" if status.available else f"{status.fallback.lower()} fallback",
                }
            )
    except Exception:
        deps.append({"name": "native C++ backends", "installed": False, "version": "unavailable"})
    return deps


def _run_snippet(code: str) -> Dict[str, Any]:
    """Execute a Python snippet and capture stdout + result."""
    import io
    import contextlib
    buf = io.StringIO()
    result = None
    error = None
    try:
        with contextlib.redirect_stdout(buf):
            exec_globals: Dict[str, Any] = {}
            exec(code, exec_globals)
            if "_result" in exec_globals:
                result = exec_globals["_result"]
    except Exception:
        error = traceback.format_exc()
    return {
        "stdout": buf.getvalue()[:5000],
        "result": str(result)[:2000] if result is not None else None,
        "error": error[:3000] if error else None,
    }


class HubHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/info":
            self._json_response(_get_library_info())
        elif self.path == "/api/modules":
            self._json_response(_get_modules_info())
        elif self.path == "/api/deps":
            self._json_response(_get_deps_status())
        elif self.path == "/" or self.path == "":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/run":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                code = data.get("code", "")
                result = _run_snippet(code)
                self._json_response(result)
            except Exception as e:
                self._json_response({"error": str(e)}, status=400)
        else:
            self.send_error(404)

    def _json_response(self, data: Any, status: int = 200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def run_server(host: str = "127.0.0.1", port: int = 3000) -> None:
    server = HTTPServer((host, port), HubHandler)
    print(f"Aion Hub running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
