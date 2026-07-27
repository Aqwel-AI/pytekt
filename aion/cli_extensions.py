"""Additional high-level commands for the Aion terminal CLI.

The functions in this module intentionally keep optional imports inside command
handlers so ``aion --help`` remains usable with the core installation.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
from typing import Any


def add_extended_parsers(subparsers: Any) -> None:
    """Register the project, AI, data, experiment, and operations commands."""
    ask = subparsers.add_parser("ask", help="Ask an LLM one question and exit")
    ask.add_argument("text")
    ask.add_argument("--provider", default="openai")
    ask.add_argument("--model", default=None)
    ask.add_argument("--temperature", type=float, default=0.7)
    ask.add_argument("--max-tokens", type=int, default=1024)

    project = subparsers.add_parser("project", help="Create and inspect Aion projects")
    project_sub = project.add_subparsers(dest="project_action")
    init = project_sub.add_parser("init", help="Create a project skeleton")
    init.add_argument("path", nargs="?", default=".")
    init.add_argument("--name", default=None)
    project_sub.add_parser("info", help="Show project configuration")
    project_sub.add_parser("validate", help="Validate the project configuration")
    clean = project_sub.add_parser("clean", help="Remove generated project files")
    clean.add_argument("--yes", action="store_true", help="Confirm removal")
    template = project_sub.add_parser("template", help="Manage project templates")
    template_sub = template.add_subparsers(dest="template_action")
    template_sub.add_parser("list", help="List built-in templates")
    template_create = template_sub.add_parser("create", help="Create a template project")
    template_create.add_argument("name", choices=("research", "service", "library"))
    template_create.add_argument("path", nargs="?", default=".")

    run = subparsers.add_parser(
        "run", help="Run a Python script with optional experiment tracking"
    )
    run.add_argument("script")
    run.add_argument("script_args", nargs="*")
    run.add_argument("--experiment", default=None)
    run.add_argument("--seed", type=int, default=42)
    run.add_argument("--tracker-dir", default=".aion_experiments")

    exp = subparsers.add_parser(
        "experiment", help="List, compare, and export tracked experiments"
    )
    exp_sub = exp.add_subparsers(dest="experiment_action")
    for action in ("list", "compare"):
        p = exp_sub.add_parser(action)
        p.add_argument("--tracker-dir", default=".aion_experiments")
        p.add_argument("--metric", default=None)
        p.add_argument("--json", action="store_true")
    show = exp_sub.add_parser("show")
    show.add_argument("run_id")
    show.add_argument("--tracker-dir", default=".aion_experiments")
    show.add_argument("--json", action="store_true")
    export = exp_sub.add_parser("export")
    export.add_argument("output")
    export.add_argument("--tracker-dir", default=".aion_experiments")
    export.add_argument(
        "--format", choices=("markdown", "csv", "latex", "html"), default=None
    )
    diff = exp_sub.add_parser("diff", help="Compare two experiment runs")
    diff.add_argument("run_a")
    diff.add_argument("run_b")
    diff.add_argument("--tracker-dir", default=".aion_experiments")
    tag = exp_sub.add_parser("tag", help="Add a tag to an experiment run")
    tag.add_argument("run_id")
    tag.add_argument("name")
    tag.add_argument("value", nargs="?", default="true")
    tag.add_argument("--tracker-dir", default=".aion_experiments")
    delete = exp_sub.add_parser("delete", help="Delete an experiment run")
    delete.add_argument("run_id")
    delete.add_argument("--tracker-dir", default=".aion_experiments")
    delete.add_argument("--yes", action="store_true", help="Confirm deletion")
    reproduce = exp_sub.add_parser(
        "reproduce", help="Show the reproducibility manifest for a run"
    )
    reproduce.add_argument("run_id")
    reproduce.add_argument("--tracker-dir", default=".aion_experiments")

    data = subparsers.add_parser(
        "data", help="Inspect tabular, JSON, and JSONL datasets"
    )
    data_sub = data.add_subparsers(dest="data_action")
    inspect = data_sub.add_parser("inspect")
    inspect.add_argument("path")
    inspect.add_argument("--json", action="store_true")
    sample = data_sub.add_parser("sample", help="Print a representative data sample")
    sample.add_argument("path")
    sample.add_argument("--rows", type=int, default=20)
    convert = data_sub.add_parser("convert", help="Convert CSV, JSON, or JSONL data")
    convert.add_argument("input")
    convert.add_argument("output")
    validate = data_sub.add_parser("validate", help="Validate required data columns")
    validate.add_argument("path")
    validate.add_argument("--required", nargs="+", default=[])
    split = data_sub.add_parser("split", help="Create deterministic train/validation/test files")
    split.add_argument("path")
    split.add_argument("--output-dir", default="splits")
    split.add_argument("--seed", type=int, default=42)

    model = subparsers.add_parser(
        "model", help="List providers and inspect saved models"
    )
    model_sub = model.add_subparsers(dest="model_action")
    model_sub.add_parser("list", help="List supported LLM providers")
    test = model_sub.add_parser("test", help="Test an LLM provider connection")
    test.add_argument("--provider", default="openai")
    test.add_argument("--model", default=None)
    model_info = model_sub.add_parser("info", help="Inspect a saved Aion model")
    model_info.add_argument("path")

    pipeline = subparsers.add_parser(
        "pipeline", help="Run a simple JSON/YAML command pipeline"
    )
    pipeline_sub = pipeline.add_subparsers(dest="pipeline_action")
    pipe_run = pipeline_sub.add_parser("run")
    pipe_run.add_argument("path")
    pipe_run.add_argument("--dry-run", action="store_true", help="Print steps without executing them")
    pipe_validate = pipeline_sub.add_parser("validate", help="Validate a pipeline without running it")
    pipe_validate.add_argument("path")

    test_cmd = subparsers.add_parser("test", help="Run the project test suite")
    test_cmd.add_argument("paths", nargs="*", default=["tests"])
    test_cmd.add_argument("-k", dest="keyword", default=None)

    logs = subparsers.add_parser("logs", help="Show recent Aion log files")
    logs.add_argument("path", nargs="?", default="~/.aion/logs")
    logs.add_argument("--tail", type=int, default=40)

    cache = subparsers.add_parser("cache", help="Inspect or clear the disk cache")
    cache_sub = cache.add_subparsers(dest="cache_action")
    for action in ("status", "clear"):
        p = cache_sub.add_parser(action)
        p.add_argument("--path", default=".aion_cache.db")

    serve = subparsers.add_parser("serve", help="Start the local Aion API server")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8080)
    serve.add_argument("--provider", default=None)
    serve.add_argument("--model", default=None)
    serve.add_argument(
        "--watch",
        action="store_true",
        help="Reload the server when source files change",
    )

    security = subparsers.add_parser(
        "security", help="Scan files for likely leaked secrets"
    )
    security.add_argument("path", nargs="?", default=".")
    security.add_argument("--all", action="store_true", help="Include hidden files")

    subparsers.add_parser("upgrade", help="Upgrade Aion with pip")

    agent = subparsers.add_parser(
        "agent", help="Inspect a workspace with the Aion coding tools"
    )
    agent.add_argument("request", nargs="*", help="read/search request")
    agent.add_argument("--root", default=".")
    agent.add_argument(
        "--write",
        action="store_true",
        help="Enable write mode for future agent actions",
    )
    api = subparsers.add_parser(
        "api", help="Start the local API server (alias for serve)"
    )
    api.add_argument("--host", default="127.0.0.1")
    api.add_argument("--port", type=int, default=8080)
    api.add_argument("--provider", default=None)
    api.add_argument("--model", default=None)
    api.add_argument("--watch", action="store_true")
    auth = subparsers.add_parser("auth", help="Check configured provider credentials")
    auth.add_argument("provider", nargs="?", default=None)
    env = subparsers.add_parser("env", help="Create and validate environment configuration")
    env_sub = env.add_subparsers(dest="env_action")
    env_init = env_sub.add_parser("init", help="Create a safe .env.example file")
    env_init.add_argument("--output", default=".env.example")
    env_check = env_sub.add_parser("check", help="Check provider credentials without displaying values")
    env_check.add_argument("--provider", default=None)
    env_sub.add_parser("export", help="Print shell setup instructions")

    notebook = subparsers.add_parser("notebook", help="Create or run Jupyter notebooks")
    notebook_sub = notebook.add_subparsers(dest="notebook_action")
    nb_create = notebook_sub.add_parser("create")
    nb_create.add_argument("path", nargs="?", default="research.ipynb")
    nb_create.add_argument("--title", default="Aion Research Notebook")
    nb_run = notebook_sub.add_parser("run")
    nb_run.add_argument("path")
    nb_run.add_argument("--output", default=None)

    explain = subparsers.add_parser("explain", help="Explain a Python file")
    explain.add_argument("path")
    explain.add_argument("--json", action="store_true")
    summarize = subparsers.add_parser(
        "summarize", help="Summarize a text, PDF, or data file"
    )
    summarize.add_argument("path")
    summarize.add_argument("--lines", type=int, default=20)

    rag = subparsers.add_parser("rag", help="Index and search local documents")
    rag_sub = rag.add_subparsers(dest="rag_action")
    rag_index = rag_sub.add_parser("index")
    rag_index.add_argument("directory")
    rag_index.add_argument("--output", default=".aion_rag.json")
    rag_query = rag_sub.add_parser("query")
    rag_query.add_argument("question")
    rag_query.add_argument("--index", default=".aion_rag.json")
    rag_query.add_argument("--limit", type=int, default=5)

    visualize = subparsers.add_parser(
        "visualize", help="Create a chart from CSV or JSON data"
    )
    visualize.add_argument("path")
    visualize.add_argument("--output", "-o", default="aion-plot.png")
    visualize.add_argument(
        "--kind", choices=("line", "hist", "scatter"), default="line"
    )

    model_bench = model_sub.add_parser("benchmark")
    model_bench.add_argument("script")
    model_bench.add_argument("--repeat", type=int, default=3)
    model_eval = model_sub.add_parser("evaluate")
    model_eval.add_argument("model")
    model_eval.add_argument("data")
    model_eval.add_argument("--target", required=True)

    exp_report = exp_sub.add_parser("report")
    exp_report.add_argument("output", default="experiment-report.html", nargs="?")
    exp_report.add_argument("--tracker-dir", default=".aion_experiments")

    observe = subparsers.add_parser("observe", help="List visible astronomical objects")
    observe.add_argument("--lat", type=float, default=40.18)
    observe.add_argument("--lon", type=float, default=44.51)
    observe.add_argument("--min-alt", type=float, default=10.0)
    observe.add_argument("--limit", type=int, default=20)

    hardware = subparsers.add_parser(
        "hardware", help="Show CPU, memory, disk, and GPU information"
    )
    hardware.add_argument("action", nargs="?", choices=("info",), default="info")
    hardware.add_argument("--json", action="store_true")
    profile = subparsers.add_parser("profile", help="Profile a Python script")
    profile.add_argument("script")
    profile.add_argument("script_args", nargs="*")
    profile.add_argument("--output", default="aion-profile.prof")

    performance = subparsers.add_parser(
        "performance", help="Performance profiling utilities"
    )
    performance_sub = performance.add_subparsers(dest="performance_action")
    performance_profile = performance_sub.add_parser("profile")
    performance_profile.add_argument("script")
    performance_profile.add_argument("script_args", nargs="*")
    performance_profile.add_argument("--output", default="aion-profile.prof")

    lint = subparsers.add_parser(
        "lint", help="Run formatting, linting, typing, and tests"
    )
    lint.add_argument("paths", nargs="*", default=["aion", "tests"])
    lint.add_argument("--no-tests", action="store_true")
    audit = subparsers.add_parser(
        "dependency-audit", help="Check installed packages for updates"
    )
    audit.add_argument("--outdated", action="store_true")
    dependency = subparsers.add_parser(
        "dependency", help="Dependency management utilities"
    )
    dependency_sub = dependency.add_subparsers(dest="dependency_action")
    dependency_audit = dependency_sub.add_parser("audit")
    dependency_audit.add_argument("--outdated", action="store_true")

    snapshot = subparsers.add_parser(
        "snapshot", help="Create or restore a project archive"
    )
    snapshot_sub = snapshot.add_subparsers(dest="snapshot_action")
    snap_create = snapshot_sub.add_parser("create")
    snap_create.add_argument("output", default="aion-snapshot.zip", nargs="?")
    snap_restore = snapshot_sub.add_parser("restore")
    snap_restore.add_argument("archive")
    snap_restore.add_argument("--root", default=".")

    session = subparsers.add_parser(
        "session", help="Manage local CLI session transcripts"
    )
    session_sub = session.add_subparsers(dest="session_action")
    for action in ("list", "open", "export"):
        p = session_sub.add_parser(action)
        p.add_argument("name", nargs="?", default=None)
        p.add_argument("--output", default=None)

    release = subparsers.add_parser("release", help="Validate package release metadata")
    release.add_argument("action", choices=("check",), nargs="?", default="check")
    changelog = subparsers.add_parser(
        "changelog", help="Generate changelog text from Git history"
    )
    changelog.add_argument(
        "action", choices=("generate",), nargs="?", default="generate"
    )
    changelog.add_argument("--limit", type=int, default=20)
    completion_install = subparsers.add_parser(
        "completion-install", help="Print shell completion installation instructions"
    )
    completion_install.add_argument(
        "shell", choices=("bash", "zsh", "fish", "powershell")
    )


def _load_rows(path: str):
    from .data import load_csv, load_json, load_jsonl

    suffix = pathlib.Path(path).suffix.lower()
    if suffix == ".csv":
        return load_csv(path)
    if suffix == ".jsonl":
        return load_jsonl(path)
    if suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError as exc:
            raise SystemExit(
                "YAML input requires PyYAML. Install the config extra."
            ) from exc
        return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
    return load_json(path)


def physics_fit_command(path: str, x_name: str = "x", y_name: str = "y") -> None:
    rows = _load_rows(path)
    if not isinstance(rows, list):
        raise SystemExit("Physics fitting expects a list of records.")
    import numpy as np

    x = np.asarray([float(row[x_name]) for row in rows])
    y = np.asarray([float(row[y_name]) for row in rows])
    slope, intercept = np.polyfit(x, y, 1)
    predicted = slope * x + intercept
    ss_res = float(np.sum((y - predicted) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 1.0
    print(
        json.dumps(
            {
                "model": "y = slope*x + intercept",
                "slope": float(slope),
                "intercept": float(intercept),
                "r2": r2,
            },
            indent=2,
        )
    )


def run_extended_command(args: Any) -> bool:
    """Dispatch an extended command. Return ``True`` when handled."""
    command = getattr(args, "command", None)
    if command == "ask":
        from .providers import ChatMessage, create_provider

        kwargs = {"model": args.model} if args.model else {}
        provider = create_provider(args.provider, **kwargs)
        print(
            provider.complete(
                [ChatMessage(role="user", content=args.text)],
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
        )
        return True
    if command == "project":
        root = pathlib.Path(getattr(args, "path", ".")).resolve()
        if args.project_action == "init":
            root.mkdir(parents=True, exist_ok=True)
            name = args.name or root.name
            for directory in ("src", "tests", "data", "runs"):
                (root / directory).mkdir(exist_ok=True)
            config = {
                "project": {"name": name},
                "aion": {"tracker_dir": ".aion_experiments"},
            }
            (root / "aion.yaml").write_text(
                json.dumps(config, indent=2) + "\n", encoding="utf-8"
            )
            (root / "README.md").write_text(
                f"# {name}\n\nCreated with `aion project init`.\n", encoding="utf-8"
            )
            print(f"Initialized Aion project: {root}")
        elif args.project_action == "validate":
            config = pathlib.Path("aion.yaml")
            issues = []
            if not config.exists():
                issues.append("missing aion.yaml")
            for directory in ("src", "tests", "data"):
                if not pathlib.Path(directory).exists():
                    issues.append(f"missing {directory}/")
            if issues:
                print("Project validation failed: " + ", ".join(issues))
                raise SystemExit(1)
            print("Project validation: OK")
        elif args.project_action == "clean":
            targets = [pathlib.Path(".aion_cache.db"), pathlib.Path(".aion_experiments")]
            present = [path for path in targets if path.exists()]
            if not args.yes:
                print("Would remove: " + (", ".join(map(str, present)) or "nothing"))
                print("Re-run with --yes to confirm.")
                return True
            import shutil
            for path in present:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            print("Removed: " + (", ".join(map(str, present)) or "nothing"))
        elif args.project_action == "template":
            templates = {
                "research": ("src", "tests", "data", "notebooks", "runs"),
                "service": ("src", "tests", "configs"),
                "library": ("src", "tests", "docs"),
            }
            if args.template_action in (None, "list"):
                print("\n".join(templates))
            else:
                target = pathlib.Path(args.path).resolve()
                target.mkdir(parents=True, exist_ok=True)
                for directory in templates[args.name]:
                    (target / directory).mkdir(exist_ok=True)
                (target / "README.md").write_text(
                    f"# {target.name}\n\nAion {args.name} template.\n", encoding="utf-8"
                )
                print(f"Created {args.name} template: {target}")
        else:
            print(
                json.dumps(
                    {
                        "path": str(pathlib.Path.cwd()),
                        "config": "aion.yaml"
                        if pathlib.Path("aion.yaml").exists()
                        else None,
                    },
                    indent=2,
                )
            )
        return True
    if command == "run":
        env = os.environ.copy()
        env["AION_SEED"] = str(args.seed)
        cmd = [sys.executable, args.script, *args.script_args]
        if args.experiment:
            from .experiments import Experiment

            with Experiment(
                args.experiment, seed=args.seed, tracker_dir=args.tracker_dir
            ):
                result = subprocess.run(cmd, env=env)
        else:
            result = subprocess.run(cmd, env=env)
        raise SystemExit(result.returncode)
    if command == "experiment":
        from .experiments import export_results_table
        from .tracker import Tracker

        if not getattr(args, "experiment_action", None):
            print("Use: aion experiment {list|show|compare|export} --help")
            return True
        tracker = Tracker(args.tracker_dir)
        if args.experiment_action == "list":
            rows = tracker.list_runs()
        elif args.experiment_action == "compare":
            rows = tracker.compare_runs(args.metric)
        elif args.experiment_action == "report":
            rows = tracker.list_runs()
            body = export_results_table(rows, format="html")
            pathlib.Path(args.output).write_text(
                f"<!doctype html><html><body><h1>Aion Experiment Report</h1>{body}</body></html>",
                encoding="utf-8",
            )
            print(f"Saved: {args.output}")
            return True
        elif args.experiment_action == "show":
            row = tracker.get_run(args.run_id)
            if row is None:
                raise SystemExit(f"Run not found: {args.run_id}")
            rows = row
        elif args.experiment_action == "diff":
            first, second = tracker.get_run(args.run_a), tracker.get_run(args.run_b)
            if first is None or second is None:
                raise SystemExit("Both run IDs must exist.")
            result = {
                "runs": [args.run_a, args.run_b],
                "params": {
                    key: [first.get("params", {}).get(key), second.get("params", {}).get(key)]
                    for key in sorted(set(first.get("params", {})) | set(second.get("params", {})))
                    if first.get("params", {}).get(key) != second.get("params", {}).get(key)
                },
                "metrics": {
                    key: [first.get("metrics", {}).get(key), second.get("metrics", {}).get(key)]
                    for key in sorted(set(first.get("metrics", {})) | set(second.get("metrics", {})))
                    if first.get("metrics", {}).get(key) != second.get("metrics", {}).get(key)
                },
            }
            print(json.dumps(result, indent=2))
            return True
        elif args.experiment_action == "tag":
            path = pathlib.Path(args.tracker_dir, args.run_id, "meta.json")
            if not path.exists():
                raise SystemExit(f"Run not found: {args.run_id}")
            row = json.loads(path.read_text(encoding="utf-8"))
            row.setdefault("tags", {})[args.name] = args.value
            path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            print(f"Tagged {args.run_id}: {args.name}={args.value}")
            return True
        elif args.experiment_action == "delete":
            if not args.yes:
                print(f"Would delete run {args.run_id}. Re-run with --yes to confirm.")
                return True
            if not tracker.delete_run(args.run_id):
                raise SystemExit(f"Run not found: {args.run_id}")
            print(f"Deleted run: {args.run_id}")
            return True
        elif args.experiment_action == "reproduce":
            manifest = pathlib.Path(args.tracker_dir, args.run_id, "manifest.json")
            if not manifest.exists():
                raise SystemExit(
                    f"No reproducibility manifest for run: {args.run_id}. "
                    "Run scripts with aion run --experiment NAME first."
                )
            print(manifest.read_text(encoding="utf-8"))
            return True
        else:
            rows = tracker.list_runs()
            fmt = (
                args.format
                or pathlib.Path(args.output).suffix.lstrip(".")
                or "markdown"
            )
            if fmt in ("md", "mkd"):
                fmt = "markdown"
            if fmt == "tex":
                fmt = "latex"
            table = export_results_table(rows, format=fmt)
            pathlib.Path(args.output).write_text(table, encoding="utf-8")
            print(f"Saved: {args.output}")
            return True
        print(
            json.dumps(rows, indent=2, default=str)
            if getattr(args, "json", False)
            else export_results_table(rows)
        )
        return True
    if command == "data":
        if not getattr(args, "data_action", None):
            print("Use: aion data {inspect|sample|convert|validate|split} --help")
            return True
        if args.data_action == "convert":
            rows = _load_rows(args.input)
            from .data import save_csv, save_json, save_jsonl
            writers = {".csv": save_csv, ".json": save_json, ".jsonl": save_jsonl}
            writer = writers.get(pathlib.Path(args.output).suffix.lower())
            if writer is None:
                raise SystemExit("Output must end with .csv, .json, or .jsonl")
            writer(args.output, rows)
            print(f"Converted: {args.output}")
            return True
        rows = _load_rows(args.path)
        records = rows if isinstance(rows, list) else [rows]
        if args.data_action == "sample":
            print(json.dumps(records[: max(0, args.rows)], indent=2, default=str))
            return True
        if args.data_action == "validate":
            keys = {key for row in records if isinstance(row, dict) for key in row}
            missing = sorted(set(args.required) - keys)
            if missing:
                print("Missing required columns: " + ", ".join(missing))
                raise SystemExit(1)
            print(f"Data validation: OK ({len(records)} records)")
            return True
        if args.data_action == "split":
            from .data import save_json, train_val_test_split
            train, validation, test = train_val_test_split(records, seed=args.seed)
            output = pathlib.Path(args.output_dir)
            output.mkdir(parents=True, exist_ok=True)
            for name, subset in (("train", train), ("validation", validation), ("test", test)):
                save_json(str(output / f"{name}.json"), subset)
            print(f"Created splits in: {output}")
            return True
        keys = sorted({key for row in records if isinstance(row, dict) for key in row})
        summary = {
            "path": args.path,
            "rows": len(records),
            "columns": keys,
            "missing": {
                k: sum(not row.get(k) for row in records if isinstance(row, dict))
                for k in keys
            },
        }
        print(
            json.dumps(summary, indent=2)
            if args.json
            else "\n".join(
                [f"Rows: {summary['rows']}", f"Columns: {', '.join(keys)}"]
                + [f"Missing {k}: {v}" for k, v in summary["missing"].items()]
            )
        )
        return True
    if command == "model":
        if not getattr(args, "model_action", None):
            print("Use: aion model {list|test|info|benchmark|evaluate} --help")
            return True
        if args.model_action == "list":
            from .providers import supported_providers

            print("\n".join(supported_providers()))
        elif args.model_action == "test":
            from .providers import ChatMessage, create_provider

            provider = create_provider(
                args.provider, **({"model": args.model} if args.model else {})
            )
            print(
                provider.complete(
                    [ChatMessage(role="user", content="Reply with: ok")], max_tokens=8
                )
            )
            print("Provider connection: OK")
        elif args.model_action == "benchmark":
            timings = []
            for _ in range(max(1, args.repeat)):
                start = __import__("time").perf_counter()
                result = subprocess.run(
                    [sys.executable, args.script], capture_output=True
                )
                timings.append(__import__("time").perf_counter() - start)
                if result.returncode:
                    raise SystemExit(result.returncode)
            print(
                json.dumps(
                    {
                        "script": args.script,
                        "runs": len(timings),
                        "mean_seconds": sum(timings) / len(timings),
                        "min_seconds": min(timings),
                    },
                    indent=2,
                )
            )
        elif args.model_action == "evaluate":
            from .models.io import load_model

            rows = _load_rows(args.data)
            model = load_model(args.model)
            if not isinstance(rows, list) or not rows:
                raise SystemExit("Model evaluation expects a non-empty list dataset.")
            target = [row.pop(args.target) for row in rows]
            features = [[value for value in row.values()] for row in rows]
            predictions = model.predict(features)
            matches = sum(
                actual == predicted for actual, predicted in zip(target, predictions)
            )
            print(
                json.dumps(
                    {"rows": len(target), "accuracy": matches / len(target)}, indent=2
                )
            )
        elif args.model_action == "info":
            print(pathlib.Path(args.path, "meta.json").read_text(encoding="utf-8"))
        return True
    if command == "pipeline":
        if not getattr(args, "pipeline_action", None):
            print("Use: aion pipeline {validate|run} pipeline.json")
            return True
        spec = _load_rows(args.path)
        steps = spec.get("steps", []) if isinstance(spec, dict) else []
        errors = [
            f"step {index + 1} needs a non-empty command"
            for index, step in enumerate(steps)
            if not isinstance(step, dict) or not isinstance(step.get("command"), str) or not step["command"].strip()
        ]
        if errors:
            raise SystemExit("Invalid pipeline: " + "; ".join(errors))
        if args.pipeline_action == "validate":
            print(f"Pipeline validation: OK ({len(steps)} steps)")
            return True
        for step in steps:
            print(f"→ {step.get('name', step.get('command', 'step'))}")
            if args.dry_run:
                print(f"  {step['command']}")
                continue
            subprocess.run(step["command"], shell=True, check=True)
        return True
    if command == "test":
        cmd = [sys.executable, "-m", "pytest", *args.paths]
        if args.keyword:
            cmd += ["-k", args.keyword]
        raise SystemExit(subprocess.run(cmd).returncode)
    if command == "logs":
        root = pathlib.Path(args.path).expanduser()
        files = sorted(
            root.rglob("*.log"), key=lambda p: p.stat().st_mtime if p.exists() else 0
        )
        if not files:
            print(f"No logs found in {root}")
        else:
            print(
                "\n".join(
                    files[-1]
                    .read_text(encoding="utf-8", errors="replace")
                    .splitlines()[-args.tail :]
                )
            )
        return True
    if command == "cache":
        if not getattr(args, "cache_action", None):
            print("Use: aion cache {status|clear} --help")
            return True
        from .cache import DiskCache

        cache = DiskCache(args.path)
        if args.cache_action == "clear":
            cache.clear()
            print(f"Cleared cache: {args.path}")
        else:
            print(json.dumps({"path": args.path, "entries": cache.size()}, indent=2))
        return True
    if command in ("serve", "api"):
        try:
            import uvicorn
            from .providers import create_provider

            provider = (
                create_provider(args.provider, model=args.model)
                if args.provider
                else None
            )
            from .serve import create_app

            uvicorn.run(
                create_app(provider=provider),
                host=args.host,
                port=args.port,
                reload=getattr(args, "watch", False),
            )
        except ImportError as exc:
            raise SystemExit(
                f"Serving requires optional dependencies: {exc}. Install the monitor extra."
            )
        return True
    if command == "security":
        import re

        patterns = re.compile(
            r"(api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]", re.I
        )
        root = pathlib.Path(args.path)
        hits = []
        for path in root.rglob("*"):
            if path.is_file() and (
                args.all or not any(part.startswith(".") for part in path.parts)
            ):
                try:
                    for line_no, line in enumerate(
                        path.read_text(errors="ignore").splitlines(), 1
                    ):
                        if patterns.search(line):
                            hits.append(f"{path}:{line_no}")
                except OSError:
                    pass
        print("Potential secrets:" if hits else "No obvious secrets found.")
        print("\n".join(hits))
        return True
    if command == "upgrade":
        raise SystemExit(
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "aqwel-aion"]
            ).returncode
        )
    if command == "agent":
        from .tools.code_agent import grep_search, list_files, read_file
        from .tools.workspace import Workspace

        workspace = Workspace(args.root)
        request = " ".join(args.request)
        if request.startswith("read "):
            print(read_file(workspace, request[5:].strip()))
        elif request.startswith("search "):
            print(grep_search(workspace, request[7:].strip()))
        else:
            print(list_files(workspace, recursive=True))
            print(
                "Tip: use `aion agent read path/to/file.py` or `aion agent search pattern`."
            )
        return True
    if command == "auth":
        names = (
            [args.provider]
            if args.provider
            else ["openai", "gemini", "anthropic", "deepseek", "nvidia"]
        )
        envs = {
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "nvidia": "NVIDIA_API_KEY",
        }
        for name in names:
            state = "configured" if os.environ.get(envs.get(name, "")) else "missing"
            print(f"{name}: {state} ({envs.get(name, 'provider key')})")
        return True
    if command == "env":
        providers = {
            "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY", "deepseek": "DEEPSEEK_API_KEY",
            "nvidia": "NVIDIA_API_KEY",
        }
        if not getattr(args, "env_action", None):
            print("Use: aion env {init|check|export} --help")
        elif args.env_action == "init":
            output = pathlib.Path(args.output)
            output.write_text(
                "# Add values locally; never commit secrets.\n" +
                "\n".join(f"{key}=" for key in providers.values()) + "\n",
                encoding="utf-8",
            )
            print(f"Created: {output}")
        elif args.env_action == "check":
            selected = {args.provider: providers.get(args.provider)} if args.provider else providers
            if args.provider and selected[args.provider] is None:
                raise SystemExit(f"Unknown provider: {args.provider}")
            missing = [name for name, key in selected.items() if not os.environ.get(key)]
            for name, key in selected.items():
                print(f"{name}: {'configured' if name not in missing else 'missing'} ({key})")
            if args.provider and missing:
                raise SystemExit(1)
        else:
            print("export OPENAI_API_KEY='…'  # replace with your provider key")
        return True
    if command == "notebook":
        if not getattr(args, "notebook_action", None):
            print("Use: aion notebook {create|run} --help")
            return True
        if args.notebook_action == "create":
            notebook = {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [f"# {args.title}\n"],
                    },
                    {
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": ["import aion\n"],
                    },
                ],
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3",
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 5,
            }
            pathlib.Path(args.path).write_text(
                json.dumps(notebook, indent=2) + "\n", encoding="utf-8"
            )
            print(f"Created notebook: {args.path}")
        else:
            cmd = [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                args.path,
                "--output",
                args.output or pathlib.Path(args.path).name,
            ]
            try:
                raise SystemExit(subprocess.run(cmd).returncode)
            except FileNotFoundError as exc:
                raise SystemExit(
                    "Notebook execution requires Jupyter. Install notebook or jupyterlab."
                ) from exc
        return True
    if command in ("explain", "summarize"):
        path = pathlib.Path(args.path)
        text = (
            path.read_text(encoding="utf-8", errors="replace")
            if path.suffix.lower() not in (".pdf",)
            else "PDF summarization requires the optional PDF extractor."
        )
        if command == "explain":
            import ast

            tree = ast.parse(text, filename=str(path))
            result = {
                "file": str(path),
                "imports": [
                    n.names[0].name
                    for n in ast.walk(tree)
                    if isinstance(n, ast.Import) and n.names
                ],
                "functions": [
                    n.name
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ],
                "classes": [
                    n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
                ],
                "lines": len(text.splitlines()),
            }
            print(
                json.dumps(result, indent=2)
                if args.json
                else "\n".join(f"{key}: {value}" for key, value in result.items())
            )
        else:
            lines = text.splitlines()
            print("\n".join(lines[: args.lines]))
            if len(lines) > args.lines:
                print(f"\n… ({len(lines) - args.lines} more lines)")
        return True
    if command == "rag":
        if not getattr(args, "rag_action", None):
            print("Use: aion rag {index|query} --help")
            return True
        index_path = pathlib.Path(
            getattr(args, "output", getattr(args, "index", ".aion_rag.json"))
        )
        if args.rag_action == "index":
            documents = []
            for path in pathlib.Path(args.directory).rglob("*"):
                if path.is_file() and path.suffix.lower() in (
                    ".txt",
                    ".md",
                    ".py",
                    ".json",
                    ".csv",
                ):
                    documents.append(
                        {
                            "path": str(path),
                            "text": path.read_text(encoding="utf-8", errors="ignore"),
                        }
                    )
            index_path.write_text(
                json.dumps(documents, ensure_ascii=False), encoding="utf-8"
            )
            print(f"Indexed {len(documents)} documents: {index_path}")
        else:
            documents = json.loads(index_path.read_text(encoding="utf-8"))
            terms = set(args.question.casefold().split())
            ranked = sorted(
                documents,
                key=lambda row: sum(term in row["text"].casefold() for term in terms),
                reverse=True,
            )
            for row in ranked[: args.limit]:
                score = sum(term in row["text"].casefold() for term in terms)
                if score:
                    print(f"[{score}] {row['path']}")
        return True
    if command == "visualize":
        rows = _load_rows(args.path)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
            columns = [
                key for key, value in rows[0].items() if isinstance(value, (int, float))
            ]
            values = [
                [float(row[key]) for row in rows if row.get(key) is not None]
                for key in columns
            ]
        else:
            values, columns = [[float(value) for value in rows]], ["value"]
        if args.kind == "hist":
            plt.hist(values[0], bins=10)
        elif args.kind == "scatter" and len(values) >= 2:
            plt.scatter(values[0], values[1])
        else:
            for label, series in zip(columns, values):
                plt.plot(np.arange(len(series)), series, label=label)
            if len(values) > 1:
                plt.legend()
        plt.tight_layout()
        plt.savefig(args.output, dpi=150)
        plt.close()
        print(f"Saved: {args.output}")
        return True
    if command == "physics-fit":
        physics_fit_command(args.path, args.x, args.y)
        return True
    if command == "observe":
        from .universe.observing import whats_up

        objects = whats_up(args.lat, args.lon, min_altitude=args.min_alt)
        for obj in objects[: args.limit]:
            print(
                f"{obj.get('name', obj.get('id', '?'))}: alt={obj['altitude']:.1f}° az={obj['azimuth']:.1f}°"
            )
        return True
    if command == "hardware":
        from .monitor.hardware import get_cpu_detailed, get_disk, get_ram

        result = {
            "cpu": get_cpu_detailed(interval=0.1),
            "memory": get_ram(),
            "disk": get_disk(),
        }
        print(
            json.dumps(result, indent=2)
            if args.json
            else f"CPU: {result['cpu']['percent']:.1f}%\nRAM: {result['memory']['percent']:.1f}%\nDisk: {result['disk']['percent']:.1f}%"
        )
        return True
    if command in ("profile", "performance"):
        if command == "performance" and args.performance_action != "profile":
            print("Use: aion performance profile SCRIPT --help")
            return True
        import cProfile

        cProfile.runctx(
            "runpy.run_path(script, run_name='__main__')",
            {"runpy": __import__("runpy"), "script": args.script},
            {},
            args.output,
        )
        print(f"Saved profile: {args.output}")
        return True
    if command == "lint":
        tools = [
            ["ruff", "check", *args.paths],
            [sys.executable, "-m", "black", "--check", *args.paths],
        ]
        if not args.no_tests:
            tools.append([sys.executable, "-m", "pytest", "-q"])
        for tool in tools:
            try:
                result = subprocess.run(tool)
            except FileNotFoundError:
                print(f"Skipped unavailable tool: {tool[0]}")
                continue
            if result.returncode:
                raise SystemExit(result.returncode)
        return True
    if command in ("dependency-audit", "dependency"):
        if command == "dependency" and args.dependency_action != "audit":
            print("Use: aion dependency audit --help")
            return True
        tool = (
            [sys.executable, "-m", "pip", "list", "--outdated"]
            if args.outdated
            else [sys.executable, "-m", "pip", "check"]
        )
        raise SystemExit(subprocess.run(tool).returncode)
    if command == "snapshot":
        import zipfile

        if not getattr(args, "snapshot_action", None):
            print("Use: aion snapshot {create|restore} --help")
            return True
        if args.snapshot_action == "create":
            with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as archive:
                for path in pathlib.Path(".").rglob("*"):
                    if path.is_file() and not any(
                        part in {".git", "__pycache__", ".aion"} for part in path.parts
                    ):
                        archive.write(path)
            print(f"Created snapshot: {args.output}")
        else:
            with zipfile.ZipFile(args.archive) as archive:
                archive.extractall(args.root)
            print(f"Restored snapshot into: {args.root}")
        return True
    if command == "session":
        root = pathlib.Path("~/.aion/sessions").expanduser()
        root.mkdir(parents=True, exist_ok=True)
        if not getattr(args, "session_action", None):
            print("Use: aion session {list|open|export} --help")
            return True
        if args.session_action == "list":
            print("\n".join(path.name for path in sorted(root.glob("*.jsonl"))))
        elif args.session_action == "open":
            print(f"Session file: {root / (args.name or 'default.jsonl')}")
        else:
            source = root / (args.name or "default.jsonl")
            target = pathlib.Path(args.output or source.name)
            target.write_text(
                source.read_text(encoding="utf-8") if source.exists() else "",
                encoding="utf-8",
            )
            print(f"Exported: {target}")
        return True
    if command == "release":
        required = ["pyproject.toml", "README.md", "LICENSE"]
        missing = [path for path in required if not pathlib.Path(path).exists()]
        print(
            "Release check: OK"
            if not missing
            else f"Missing release files: {', '.join(missing)}"
        )
        return not missing
    if command == "changelog":
        result = subprocess.run(
            ["git", "log", f"-n{args.limit}", "--pretty=format:- %s"],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        return True
    if command == "completion-install":
        print(f"Run: aion completion {args.shell} >> your shell startup file")
        return True
    return False
