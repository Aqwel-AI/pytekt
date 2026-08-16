"""
Full exercise script for pytekt.algorithms, pytekt.visualization, pdf helpers,
and post-0.1.9 / 0.2.0 library surface (I/O, LLM stack, RAG, config/env,
benchmarks, graphs, 3D/report plots). Compatible with PyTekt 0.2.0.

Output is printed for algorithms and infra; standard plots go to example_output/;
newer extras also write under example_output/v019_examples/.

Contents:
  - Section 1: pytekt.algorithms (search + arrays)
  - Section 2: pytekt.visualization (1D/2D/training plots)
  - Section 3: pytekt.pdf documentation helpers (stats, guides, validation)
  - Section 4: library surface demos (I/O, providers, tools, RAG, config, …)
    - fast_* numerics + using_native_extension
    - pytekt.io (atomic_write, iter_lines, file_sha256)
    - pytekt.providers (supported_providers, parse_chat_completion_response; no API keys)
    - pytekt.tools (run_tool_loop with FakeToolProvider; JSON sidecar pattern for checkpoints)
    - pytekt.rag (SimpleRAGIndex with local fake embedder)
    - pytekt.config (deep_merge, get_nested; optional sample TOML from package examples)
    - pytekt.env (load_dotenv_file on a temp .env)
    - stdlib logging.basicConfig (root logger level)
    - pytekt.benchmarks (timed_run, compare_sum_numpy_vs_fast)
    - pytekt.algorithms.graphs (dijkstra, connected_components, shortest_path_unweighted)
    - pytekt.visualization (plot_3d_scatter, plot_3d_surface, save_figures_pdf)
    - pytekt.pdf (search_public_api, export_api_index md, create_api_documentation_html)
    - pytekt.tools extras: TokenBucket (rate limit)
Run: python example.py
Requires: pip install pytekt[full] (or matplotlib + numpy at minimum for sections 1–2;
[config] for TOML sample load in section 4).
"""

import copy
import os
import tempfile
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# 1. pytekt.algorithms — search and array utilities
# ---------------------------------------------------------------------------
# All functions below are from pytekt.algorithms; they use only the standard
# library (and type hints). Search functions expect sorted lists unless
# otherwise noted (e.g. linear_search, first/last occurrence).
print("=" * 60)
print("pytekt.algorithms — tests")
print("=" * 60)

from pytekt.algorithms import (
    binary_search,
    lower_bound,
    upper_bound,
    is_sorted,
    jump_search,
    find_peak_element,
    exponential_search,
    linear_search,
    First_Occurrence,
    Last_Occurrence,
    First_Last_Occurrence,
    roatated_search,
    ternary_search,
    interpolation_search,
    flatten_array,
    chunk_array,
    remove_duplicates,
    moving_avarage,
    flatten_deep,
    sliding_window,
    pad_array,
    rolling_sum,
    pairwise,
)

# --- Core search (sorted list required): index or None / insertion points ---
# binary_search: O(log n); returns index if target found, else None.
# lower_bound: first index where element >= target (e.g. insertion point for bisect).
# upper_bound: first index where element > target.
arr = [10, 20, 30, 40, 50, 60, 70]
print("binary_search(arr, 50):", binary_search(arr, 50))
print("binary_search(arr, 55):", binary_search(arr, 55))
print("lower_bound(arr, 35):", lower_bound(arr, 35))
print("upper_bound(arr, 50):", upper_bound(arr, 50))
# is_sorted: True if list is non-decreasing or non-increasing.
print("is_sorted([1,2,3]):", is_sorted([1, 2, 3]))
print("is_sorted([1,3,2]):", is_sorted([1, 3, 2]))

# --- Alternative search methods (sorted list): jump, exponential, linear ---
# jump_search: step through list then linear scan; good when step cost is low.
# exponential_search: double range then binary search; O(log n).
# find_peak_element: elements strictly greater than both neighbours.
slist = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
print("jump_search(slist, step=3, target=13):", jump_search(slist, step=3, target=13))
print("exponential_search(slist, 9):", exponential_search(slist, 9))
print("find_peak_element([1, 3, 2, 4, 1]):", find_peak_element([1, 3, 2, 4, 1]))

# --- First / last occurrence (return human-readable strings) ---
# linear_search and First_Occurrence/Last_Occurrence/First_Last_Occurrence
# work on any list; they return descriptive strings (or tuple of strings).
print("linear_search(slist, 7):", linear_search(slist, 7))
ulist_dup = [2, 4, 4, 4, 6, 8, 8, 10]
print("First_Occurrence(ulist_dup, 4):", First_Occurrence(ulist_dup, 4))
print("Last_Occurrence(ulist_dup, 4):", Last_Occurrence(ulist_dup, 4))
print("First_Last_Occurrence(ulist_dup, 8):", First_Last_Occurrence(ulist_dup, 8))

# --- Specialized search: rotated sorted array, ternary, interpolation ---
# roatated_search: list is a rotated sorted array (e.g. [4,5,6,7,1,2,3]).
# ternary_search: divides range into three parts; returns string.
# interpolation_search: suited to uniformly distributed data; returns string.
rotated = [4, 5, 6, 7, 1, 2, 3]
print("roatated_search(rotated, 2):", roatated_search(rotated, 2))
print("ternary_search([10,20,30,40,50], 30):", ternary_search([10, 20, 30, 40, 50], 30))
print("interpolation_search([10,20,30,40,50], 40):", interpolation_search([10, 20, 30, 40, 50], 40))

# --- Array utilities: flatten, chunk, dedupe, windowing, rolling, pairwise ---
# flatten_array: one-level flatten (list of lists -> list).
# flatten_deep: recursive flatten to any depth.
# chunk_array: consecutive chunks of given size; last chunk may be smaller.
# remove_duplicates: first occurrence kept, order preserved.
# moving_avarage: arithmetic mean of numeric list.
# sliding_window: generator of consecutive sublists of given size.
# rolling_sum: list of sums of each consecutive window (integers).
# pairwise: consecutive pairs as list of tuples (needs at least 2 elements).
print("flatten_array([[1,2],[3,4],[5]]):", flatten_array([[1, 2], [3, 4], [5]]))
print("flatten_deep([1, [2, [3, 4], 5], 6]):", flatten_deep([1, [2, [3, 4], 5], 6]))
print("chunk_array([1,2,3,4,5,6,7], size=3):", chunk_array([1, 2, 3, 4, 5, 6, 7], size=3))
print("remove_duplicates([3,1,2,1,4,2,3]):", remove_duplicates([3, 1, 2, 1, 4, 2, 3]))
print("moving_avarage([1.0, 2.0, 3.0, 4.0, 5.0]):", moving_avarage([1.0, 2.0, 3.0, 4.0, 5.0]))
print("list(sliding_window([1,2,3,4,5,6], 3)):", list(sliding_window([1, 2, 3, 4, 5, 6], 3)))
print("rolling_sum([1,2,3,4,5,6], 3):", rolling_sum([1, 2, 3, 4, 5, 6], 3))
print("pairwise([10, 20, 30, 40]):", pairwise([10, 20, 30, 40]))

# pad_array: extends list in-place to min_len by appending item. Use a copy if needed.
padded = copy.copy([1, 2, 3])
pad_array(padded, 6, 0)
print("pad_array([1,2,3], 6, 0) ->", padded)

print()

# ---------------------------------------------------------------------------
# 2. pytekt.visualization — all plot functions (saved to example_output/)
# ---------------------------------------------------------------------------
# Every plot function returns a matplotlib Figure. We save each to a file
# and close the figure to avoid "too many figures" warnings and keep the
# script suitable for headless/CI environments. Requires matplotlib (and
# numpy for some plots).
print("=" * 60)
print("pytekt.visualization — tests (plots saved to example_output/)")
print("=" * 60)

OUTPUT_DIR = "example_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

from pytekt.visualization import (
    plot_array,
    plot_histogram,
    plot_scatter,
    plot_multiple_arrays,
    plot_array_with_mean,
    plot_running_mean,
    plot_boxplot,
    plot_density,
    plot_cdf,
    plot_error_bars,
    plot_rolling_std,
    plot_min_max_band,
    plot_autocorrelation,
    plot_quantiles,
    plot_scatter_with_fit,
    plot_dual_axis,
    plot_matrix_heatmap,
    plot_confusion_matrix,
    plot_matrix_surface,
    plot_matrix_contour,
    plot_matrix_with_values,
    plot_correlation_matrix,
    plot_similarity_matrix,
    plot_matrix_histogram,
    plot_masked_heatmap,
    plot_confusion_matrix_normalized,
    plot_attention_map,
    plot_matrix_sparsity,
    plot_training_history,
    plot_metric,
    plot_train_vs_val,
    plot_learning_rate,
    plot_metric_with_best,
    plot_metrics_grid,
    plot_confidence_band,
    plot_early_stopping,
    plot_epoch_time,
)
from pytekt.visualization.utils import save_plot, close_figure


def save(name):
    return os.path.join(OUTPUT_DIR, name)


def save_and_close(fig, path):
    """Save figure to path and close it to free memory."""
    save_plot(fig, path)
    close_figure(fig)


# --- 1D array plots (index vs value, distributions, multi-series) ---
# 01–04: Basic line, histogram, scatter, multiple curves (e.g. loss vs val_loss).
save_and_close(plot_array([1, 3, 2, 5, 4], title="Array", show=False), save("01_plot_array.png"))
save_and_close(plot_histogram([1, 2, 2, 3, 3, 3, 4, 4, 4, 4], bins=4, title="Histogram", show=False), save("02_plot_histogram.png"))
save_and_close(plot_scatter([1, 2, 3, 4, 5], [5, 4, 3, 2, 1], title="Scatter", show=False), save("03_plot_scatter.png"))
save_and_close(
    plot_multiple_arrays(arrays=[[1, 2, 3, 4], [4, 3, 2, 1]], labels=["A", "B"], title="Multiple arrays", show=False),
    save("04_plot_multiple_arrays.png"),
)
# 05–06: Mean line overlay; running (moving) mean with window.
save_and_close(plot_array_with_mean([10, 12, 9, 11, 10, 13], title="Array with mean", show=False), save("05_plot_array_with_mean.png"))
save_and_close(
    plot_running_mean([15, 16, 14, 17, 18, 20, 19, 21, 22, 20, 18, 17], window_size=6, title="Running mean", show=False),
    save("06_plot_running_mean.png"),
)
# 07–09: Distribution views: boxplot, density curve, CDF.
save_and_close(plot_boxplot([1, 2, 2, 3, 3, 3, 4, 4, 5], title="Boxplot", show=False), save("07_plot_boxplot.png"))
save_and_close(plot_density([1.0, 1.2, 1.1, 2.0, 2.1, 2.2, 3.0], bins=5, title="Density", show=False), save("08_plot_density.png"))
save_and_close(plot_cdf([1, 2, 2, 3, 3, 4], title="CDF", show=False), save("09_plot_cdf.png"))
# 10–12: Uncertainty and rolling: error bars (x, y, yerr), rolling std, min-max band.
save_and_close(
    plot_error_bars([0, 1, 2, 3, 4], [1.0, 0.8, 0.6, 0.5, 0.4], [0.1, 0.12, 0.08, 0.07, 0.06], title="Error bars", show=False),
    save("10_plot_error_bars.png"),
)
save_and_close(plot_rolling_std([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], window_size=4, title="Rolling std", show=False), save("11_plot_rolling_std.png"))
save_and_close(plot_min_max_band([1, 2, 1.5, 3, 2.5, 4, 3.5], window_size=3, title="Min-max band", show=False), save("12_plot_min_max_band.png"))
# 13–16: Autocorrelation, quantiles (e.g. 0.25, 0.5, 0.75), scatter with linear fit, dual y-axis.
save_and_close(plot_autocorrelation([1, 2, 1, 2, 1, 2, 1], title="Autocorrelation", show=False), save("13_plot_autocorrelation.png"))
save_and_close(plot_quantiles([1, 2, 3, 4, 5, 6, 7, 8, 9], qs=[0.25, 0.5, 0.75], title="Quantiles", show=False), save("14_plot_quantiles.png"))
save_and_close(plot_scatter_with_fit([1, 2, 3, 4, 5], [2, 4, 5, 4, 6], title="Scatter with fit", show=False), save("15_plot_scatter_with_fit.png"))
save_and_close(
    plot_dual_axis([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [100, 80, 60, 40, 20], label1="Left", label2="Right", title="Dual axis", show=False),
    save("16_plot_dual_axis.png"),
)

# --- 2D matrix plots (heatmaps, confusion, surface, contour, derived matrices) ---
# 17–18: Generic heatmap; confusion matrix with optional class labels.
save_and_close(plot_matrix_heatmap([[1, 2, 3], [4, 5, 6], [7, 8, 9]], title="Matrix heatmap", show=False), save("17_plot_matrix_heatmap.png"))
save_and_close(
    plot_confusion_matrix([[50, 5], [8, 37]], labels=["Neg", "Pos"], title="Confusion matrix", show=False),
    save("18_plot_confusion_matrix.png"),
)
# 19–21: 3D surface, 2D contour, heatmap with cell value annotations.
save_and_close(plot_matrix_surface([[1, 2], [3, 4]], title="Matrix surface", show=False), save("19_plot_matrix_surface.png"))
save_and_close(plot_matrix_contour([[1, 2], [3, 4]], title="Matrix contour", show=False), save("20_plot_matrix_contour.png"))
save_and_close(plot_matrix_with_values([[1, 2], [3, 4]], title="Matrix with values", show=False), save("21_plot_matrix_with_values.png"))
# 22–23: Correlation matrix (rows = samples, cols = features); similarity matrix (cosine or dot).
save_and_close(
    plot_correlation_matrix([[1, 2], [2, 4], [3, 5], [4, 6]], labels=["F1", "F2"], title="Correlation matrix", show=False),
    save("22_plot_correlation_matrix.png"),
)
save_and_close(
    plot_similarity_matrix([[1, 0], [0.9, 0.1], [0, 1]], metric="cosine", title="Similarity matrix", show=False),
    save("23_plot_similarity_matrix.png"),
)
# 24–28: Histogram of matrix values; masked heatmap (True = hidden); normalized confusion; attention map; sparsity pattern.
save_and_close(plot_matrix_histogram([[1, 2], [3, 4]], bins=5, title="Matrix histogram", show=False), save("24_plot_matrix_histogram.png"))
save_and_close(
    plot_masked_heatmap([[1, 2], [3, 4]], [[False, True], [True, False]], title="Masked heatmap", show=False),
    save("25_plot_masked_heatmap.png"),
)
save_and_close(
    plot_confusion_matrix_normalized([[50, 5], [8, 37]], labels=["Neg", "Pos"], title="Confusion normalized", show=False),
    save("26_plot_confusion_matrix_normalized.png"),
)
save_and_close(plot_attention_map([[0.8, 0.2], [0.3, 0.7]], tokens=["A", "B"], title="Attention map", show=False), save("27_plot_attention_map.png"))
save_and_close(plot_matrix_sparsity([[1, 0, 0], [0, 1, 0], [0, 0, 1]], title="Matrix sparsity", show=False), save("28_plot_matrix_sparsity.png"))

# --- Training plots (metrics over epochs, learning rate, early stopping) ---
# history: dict of metric name -> list of values per epoch (e.g. from Keras/Torch).
history = {"loss": [1.0, 0.7, 0.5, 0.35, 0.25], "val_loss": [1.1, 0.8, 0.55, 0.4, 0.3], "accuracy": [0.5, 0.65, 0.75, 0.82, 0.88]}
# 29–31: All metrics on one axes; single metric; train vs validation curves.
save_and_close(plot_training_history(history, show=False), save("29_plot_training_history.png"))
save_and_close(plot_metric(history, "accuracy", title="Metric: accuracy", show=False), save("30_plot_metric.png"))
save_and_close(plot_train_vs_val(history["loss"], history["val_loss"], title="Train vs val", show=False), save("31_plot_train_vs_val.png"))
# 32–34: Learning rate schedule; one metric with best value highlighted; grid of all metrics.
save_and_close(plot_learning_rate([1e-3, 8e-4, 6e-4, 4e-4, 2e-4], title="Learning rate", show=False), save("32_plot_learning_rate.png"))
save_and_close(
    plot_metric_with_best(history, "val_loss", mode="min", title="Metric with best", show=False),
    save("33_plot_metric_with_best.png"),
)
save_and_close(plot_metrics_grid(history, cols=2, title="Metrics grid", show=False), save("34_plot_metrics_grid.png"))
# 35–37: Mean ± std band (e.g. across runs); early-stopping marker (patience, min/max); per-epoch duration.
save_and_close(
    plot_confidence_band([1.0, 0.7, 0.5, 0.35], [0.1, 0.08, 0.06, 0.05], title="Confidence band", show=False),
    save("35_plot_confidence_band.png"),
)
save_and_close(
    plot_early_stopping(history, "val_loss", patience=2, mode="min", title="Early stopping", show=False),
    save("36_plot_early_stopping.png"),
)
save_and_close(plot_epoch_time([12.1, 11.8, 11.9, 12.0, 11.7], title="Epoch time", show=False), save("37_plot_epoch_time.png"))

print("All algorithm tests completed.")
print("All visualization plots saved to", OUTPUT_DIR)

# ---------------------------------------------------------------------------
# 3. What's new in v0.1.8 — pytekt.pdf documentation helpers (for team visibility)
# ---------------------------------------------------------------------------
# New in this version: five functions for docs stats, installation guide,
# quick reference, docstring validation, and documentation index.
# Outputs go to example_output/ so other developers can see generated files.
print()
print("=" * 60)
print("What's new in v0.1.8 — pytekt.pdf documentation helpers")
print("=" * 60)

import pytekt
DOCS_DIR = os.path.join(OUTPUT_DIR, "v018_docs")
os.makedirs(DOCS_DIR, exist_ok=True)

# 3.1 get_documentation_statistics() — module/function counts and per-module stats
from pytekt.pdf import get_documentation_statistics
stats = get_documentation_statistics()
print("get_documentation_statistics():")
print("  module_count:", stats["module_count"])
print("  total_functions:", stats["total_functions"])
print("  sample modules:", [m["name"] for m in stats["modules"][:5]], "...")
if stats["modules_with_errors"]:
    print("  modules_with_errors:", stats["modules_with_errors"])

# 3.2 create_installation_guide() — installation and setup guide (TXT; PDF if ReportLab)
from pytekt.pdf import create_installation_guide
install_txt = os.path.join(DOCS_DIR, "pytekt_installation_guide.txt")
create_installation_guide(output_file=install_txt, format="txt")
print("create_installation_guide() ->", install_txt)

# 3.3 create_quick_reference() — compact function names by module (TXT; PDF if ReportLab)
from pytekt.pdf import create_quick_reference
quick_txt = os.path.join(DOCS_DIR, "pytekt_quick_reference.txt")
create_quick_reference(output_file=quick_txt, format="txt")
print("create_quick_reference() ->", quick_txt)

# 3.4 validate_documentation() — report which public functions lack docstrings
from pytekt.pdf import validate_documentation
validation = validate_documentation(module_name=None)
print("validate_documentation():")
print("  total_functions:", validation["summary"]["total_functions"])
print("  total_missing docstrings:", validation["summary"]["total_missing"])
if validation["missing_docstrings"]:
    sample = list(validation["missing_docstrings"].items())[:2]
    print("  sample missing:", dict(sample))

# 3.5 create_documentation_index() — INDEX.md listing all generated docs
from pytekt.pdf import create_documentation_index
index_path = create_documentation_index(output_dir=DOCS_DIR)
print("create_documentation_index() ->", index_path)

# Package metadata (section 3 reference)
print()
print("Package metadata:")
print("  __version__:", pytekt.__version__)
print("  __author__:", pytekt.__author__)
print("  __developer__:", pytekt.__developer__)

print()
print("All v0.1.8 doc outputs saved to", DOCS_DIR)

# ---------------------------------------------------------------------------
# 4. What's new in v0.1.9 — I/O, LLM stack, RAG, infra, graphs, 3D, PDF
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("What's new in v0.1.9 — full examples")
print("=" * 60)

V019_DIR = os.path.join(OUTPUT_DIR, "v019_examples")
os.makedirs(V019_DIR, exist_ok=True)
_ROOT = Path(__file__).resolve().parent

# 4.1 Native / NumPy fast_* API (re-exported on pytekt)
print()
print("4.1 pytekt fast_* + using_native_extension")
x = [0.5, 1.0, 1.5]
print("  using_native_extension:", pytekt.using_native_extension())
print("  fast_sum:", pytekt.fast_sum(x), "fast_mean:", pytekt.fast_mean(x))
print("  fast_softmax (3):", [round(float(v), 4) for v in pytekt.fast_softmax(x)])
print("  fast_lower_bound / fast_upper_bound on sorted:", pytekt.fast_lower_bound([0.0, 0.5, 1.0], 0.5), pytekt.fast_upper_bound([0.0, 0.5, 1.0], 0.5))

# 4.2 pytekt.io — atomic write, line iteration, SHA-256
print()
print("4.2 pytekt.io")
from pytekt.io import atomic_write, file_sha256, iter_lines, verify_sha256

with tempfile.TemporaryDirectory() as _td:
    p = Path(_td) / "state.txt"
    atomic_write(p, "a\nb\n")
    print("  iter_lines:", list(iter_lines(p)))
    h = file_sha256(p)
    print("  file_sha256 prefix:", h[:12], "…")
    print("  verify_sha256:", verify_sha256(p, h))

# 4.3 JSON sidecar metadata (same shape as former training checkpoints)
print()
print("4.3 JSON checkpoint-style metadata (stdlib json)")
import json

_meta_path = Path(V019_DIR) / "run_meta.json"
_meta = {
    "format": "pytekt_checkpoint_meta_v1",
    "epoch": 1,
    "model_type": "demo",
    "note": "example.py",
}
_meta_path.write_text(json.dumps(_meta, indent=2), encoding="utf-8")
_loaded = json.loads(_meta_path.read_text(encoding="utf-8"))
print("  meta keys:", sorted(_loaded.keys()))
print("  json.dumps with default=str:", json.dumps({"t": (1, 2)}, default=str)[:40], "…")

# 4.4 pytekt.providers — factory names + response parsing (no HTTP)
print()
print("4.4 pytekt.providers (offline)")
from pytekt.providers import parse_chat_completion_response, supported_providers

print("  supported_providers (sample):", supported_providers()[:4])
_stub = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "Stub reply for example.py.",
            }
        }
    ]
}
_turn = parse_chat_completion_response(_stub)
print("  parse_chat_completion_response content:", _turn.content[:40], "…")

# 4.5 pytekt.tools — tool loop without network (FakeToolProvider)
print()
print("4.5 pytekt.tools (offline loop)")
from pytekt.providers.structured import AssistantTurn, NormalizedToolCall
from pytekt.tools import FakeToolProvider, ToolRegistry, function_tool, make_tool_turn, run_tool_loop
from pytekt.tools.rate_limit import TokenBucket


def _add(a: float, b: float) -> float:
    return float(a) + float(b)


_reg = ToolRegistry()
_reg.register("add", _add, required_arg_keys=["a", "b"])
_tools = [
    function_tool(
        "add",
        "Add two numbers.",
        properties={
            "a": {"type": "number"},
            "b": {"type": "number"},
        },
        required=["a", "b"],
    )
]
_tc = NormalizedToolCall(id="ex1", name="add", arguments_json='{"a": 2, "b": 3}')
_provider = FakeToolProvider(
    [
        make_tool_turn([_tc], content=None),
        AssistantTurn(content="Sum is 5.", tool_calls=[], raw={}),
    ]
)
_msgs: list = [{"role": "user", "content": "2+3?"}]
_final, _ = run_tool_loop(_provider, _msgs, _tools, _reg, max_rounds=4)
print("  run_tool_loop final:", _final)
_bucket = TokenBucket(rate_per_sec=100.0, capacity=10.0)
_bucket.acquire(3.0)
print("  TokenBucket: acquire(3) completed (100 tokens/s refill, capacity 10)")

# 4.6 pytekt.rag — in-memory index + fake embeddings
print()
print("4.6 pytekt.rag")
from pytekt.rag import SimpleRAGIndex


def _fake_embed(text: str) -> np.ndarray:
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    return rng.standard_normal(12).astype(np.float64)


_ridx = SimpleRAGIndex(embed_fn=_fake_embed)
_n = _ridx.index_texts(["alpha beta gamma.", "delta epsilon."], chunk_size=64, overlap=0)
_hits = _ridx.query("alpha", k=2)
print("  SimpleRAGIndex chunks indexed:", _n, "query hits:", len(_hits))

# 4.7 pytekt.config — dict merge + optional package sample TOML
print()
print("4.7 pytekt.config")
from pytekt.config import deep_merge, get_nested, set_nested

_cfg = {"app": {"name": "demo"}, "db": {"host": "localhost"}}
_cfg = deep_merge(_cfg, {"app": {"debug": True}, "logging": {"level": "INFO"}})
set_nested(_cfg, "app.version", "0.1.9")
print("  get_nested app.debug:", get_nested(_cfg, "app.debug"))
_sample_toml = _ROOT / "pytekt" / "config" / "examples" / "sample.toml"
if _sample_toml.is_file():
    try:
        from pytekt.config import load_toml_file

        _loaded = load_toml_file(_sample_toml)
        print("  load_toml_file sample keys:", list(_loaded.keys())[:5])
    except ImportError as e:
        print("  load_toml_file skipped (install [config]):", e)
else:
    print("  load_toml_file skipped (sample.toml not found)")

# 4.8 pytekt.env — parse a temp .env
print()
print("4.8 pytekt.env")
from pytekt.env import load_dotenv_file

with tempfile.TemporaryDirectory() as _td:
    _envp = Path(_td) / ".env"
    _envp.write_text('DEMO_FOO=bar\nDEMO_N=42\n', encoding="utf-8")
    _parsed = load_dotenv_file(_envp, override=False)
    print("  load_dotenv_file keys:", sorted(_parsed.keys()))

# 4.9 stdlib logging (configure root logger)
print()
print("4.9 logging.basicConfig")
import logging

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
print("  basicConfig(level=WARNING) applied")

# 4.10 pytekt.benchmarks
print()
print("4.10 pytekt.benchmarks")
from pytekt.benchmarks import compare_sum_numpy_vs_fast, timed_run

_, _stats = timed_run(lambda: sum(range(500)), repeats=3, warmup=1)
print("  timed_run sum(range(500)) mean_s:", round(_stats["mean_s"], 8))
_cmp = compare_sum_numpy_vs_fast(np.arange(10_000, dtype=np.float64), repeats=3)
print("  compare_sum_numpy_vs_fast native:", _cmp["using_native_extension"])

# 4.11 pytekt.algorithms.graphs — Dijkstra, components, unweighted shortest path
print()
print("4.11 pytekt.algorithms graphs (weighted + unweighted)")
from pytekt.algorithms import connected_components, dijkstra, shortest_path_unweighted

_wg = {"A": [("B", 1.0), ("C", 4.0)], "B": [("C", 2.0), ("D", 5.0)], "C": [("D", 1.0)], "D": []}
print("  dijkstra A->:", dijkstra(_wg, "A"))
_ug = {"a": ["b"], "b": ["c", "a"], "c": []}
print("  connected_components count:", len(connected_components(_ug)))
_dag = {"s": ["a", "b"], "a": ["t"], "b": ["t"], "t": []}
print("  shortest_path_unweighted s->t:", shortest_path_unweighted(_dag, "s", "t"))

# 4.12 pytekt.visualization — 3D plots + multi-page PDF of figures
print()
print("4.12 pytekt.visualization 3D + save_figures_pdf")
from pytekt.visualization import figures_to_html_img_tags, plot_3d_scatter, plot_3d_surface, save_figures_pdf

_fig_s = plot_3d_scatter([0, 1, 2], [0, 1, 0], [0, 0, 1], title="3D scatter (v0.1.9)", show=False)
_xs = np.linspace(0.0, 1.0, 5)
_ys = np.linspace(0.0, 1.0, 5)
_Z = np.outer(_ys, _xs)  # shape (5, 5) for meshgrid(xs, ys)
_fig_u = plot_3d_surface(_xs, _ys, _Z, title="3D surface (v0.1.9)", show=False)
_pdf_path = os.path.join(V019_DIR, "v019_3d_bundle.pdf")
save_figures_pdf([_fig_s, _fig_u], _pdf_path)
_html_snip = figures_to_html_img_tags([_fig_s], fmt="png")
print("  save_figures_pdf ->", _pdf_path)
print("  figures_to_html_img_tags length:", len(_html_snip))
from pytekt.visualization.utils import close_figure

close_figure(_fig_s)
close_figure(_fig_u)

# 4.13 pytekt.pdf — symbol search, Markdown API index, static HTML API page
print()
print("4.13 pytekt.pdf (v0.1.9-style helpers)")
from pytekt.pdf import create_api_documentation_html, export_api_index, search_public_api

_hits = search_public_api("binary_search", include_classes=False)
print("  search_public_api binary_search hits:", len(_hits))
_idx_md = os.path.join(V019_DIR, "api_index_slice.md")
export_api_index(output_file=_idx_md, format="md", include_classes=False)
print("  export_api_index ->", _idx_md)
_html_api = os.path.join(V019_DIR, "pytekt_api_min.html")
create_api_documentation_html(output_file=_html_api)
print("  create_api_documentation_html ->", _html_api)

print()
print("All v0.1.9 examples finished; artifacts under", V019_DIR)
print("Done.")
