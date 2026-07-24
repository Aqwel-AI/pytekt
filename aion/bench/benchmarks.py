#!/usr/bin/env python3
"""
Benchmarking and reproducibility utilities.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

import numpy as np


def set_seed(seed: int, deterministic: bool = False) -> Dict[str, Any]:
    """
    Set global RNG seeds for reproducibility.

    Returns a dict describing what was configured.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    info: Dict[str, Any] = {
        "seed": seed,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
        "random": True,
        "numpy": True,
        "torch": False,
        "torch_deterministic": False,
    }

    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        info["torch"] = True
        if deterministic:
            torch.use_deterministic_algorithms(True)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            info["torch_deterministic"] = True
    except Exception:
        pass

    return info


@contextmanager
def seed_context(seed: int, deterministic: bool = False) -> Iterator[None]:
    """
    Context manager that sets seeds and restores RNG state on exit.
    """
    py_state = random.getstate()
    np_state = np.random.get_state()
    torch_state = None
    torch_cuda_state = None
    torch_was_available = False

    try:
        import torch  # type: ignore

        torch_was_available = True
        torch_state = torch.get_rng_state()
        if torch.cuda.is_available():
            torch_cuda_state = torch.cuda.get_rng_state_all()
    except Exception:
        pass

    set_seed(seed, deterministic=deterministic)
    try:
        yield
    finally:
        random.setstate(py_state)
        np.random.set_state(np_state)
        if torch_was_available:
            try:
                import torch  # type: ignore

                if torch_state is not None:
                    torch.set_rng_state(torch_state)
                if torch_cuda_state is not None:
                    torch.cuda.set_rng_state_all(torch_cuda_state)
            except Exception:
                pass


def _hash_file(path: Path, algo: str = "sha256", chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def snapshot_dataset(
    path: Union[str, Path, Iterable[Union[str, Path]]],
    out_dir: Union[str, Path],
    name: Optional[str] = None,
    copy: bool = False,
    include_hidden: bool = False,
    max_files: Optional[int] = None,
    hash_algo: str = "sha256",
) -> Path:
    """
    Create a dataset snapshot manifest (and optionally copy files).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if name is None:
        if isinstance(path, (str, Path)):
            name = Path(path).name
        else:
            name = f"dataset_{int(time.time())}"

    snapshot_dir = out_dir / name
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    files: List[Path] = []
    if isinstance(path, (str, Path)):
        p = Path(path)
        if p.is_file():
            files = [p]
        else:
            for root, _, filenames in os.walk(p):
                for fn in filenames:
                    if not include_hidden and fn.startswith("."):
                        continue
                    files.append(Path(root) / fn)
    else:
        files = [Path(p) for p in path]

    if max_files is not None:
        files = files[:max_files]

    manifest_files = []
    total_bytes = 0
    for f in files:
        if not f.is_file():
            continue
        rel_path = f.name if isinstance(path, (list, tuple, set)) else f.relative_to(Path(path))
        size = f.stat().st_size
        total_bytes += size
        digest = _hash_file(f, algo=hash_algo)
        manifest_files.append(
            {
                "path": str(rel_path),
                "size": size,
                "hash": digest,
            }
        )
        if copy:
            target = snapshot_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                target.unlink()
            target.write_bytes(f.read_bytes())

    manifest = {
        "name": name,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": str(path),
        "file_count": len(manifest_files),
        "total_bytes": total_bytes,
        "hash_algo": hash_algo,
        "files": manifest_files,
    }

    manifest_path = snapshot_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path


@dataclass
class BenchmarkResult:
    name: str
    mean_s: float
    min_s: float
    max_s: float
    runs: int


def _timeit(fn, runs: int = 3) -> BenchmarkResult:
    times: List[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    return BenchmarkResult(
        name=getattr(fn, "__name__", "benchmark"),
        mean_s=sum(times) / len(times),
        min_s=min(times),
        max_s=max(times),
        runs=runs,
    )


def run_baseline_suite(
    out_dir: Optional[Union[str, Path]] = None,
    seed: int = 1337,
    size: int = 1_000_000,
    runs: int = 3,
) -> Dict[str, Any]:
    """
    Run a small, deterministic baseline benchmark suite and return results.
    """
    set_seed(seed)
    arr = np.random.rand(size).astype(np.float64)
    vec = arr.tolist()

    results: List[BenchmarkResult] = []

    results.append(_timeit(lambda: np.sum(arr), runs=runs))
    results.append(_timeit(lambda: sum(vec), runs=runs))

    try:
        from .._core import fast_sum, fast_dot  # type: ignore

        results.append(_timeit(lambda: fast_sum(arr), runs=runs))
        results.append(_timeit(lambda: fast_dot(arr, arr), runs=runs))
    except Exception:
        pass

    results.append(_timeit(lambda: float(np.dot(arr, arr)), runs=runs))

    payload = {
        "seed": seed,
        "size": size,
        "runs": runs,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": [
            {
                "name": r.name,
                "mean_s": r.mean_s,
                "min_s": r.min_s,
                "max_s": r.max_s,
                "runs": r.runs,
            }
            for r in results
        ],
    }

    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "baseline_suite.json"
        out_path.write_text(json.dumps(payload, indent=2))

    return payload


__all__ = [
    "set_seed",
    "seed_context",
    "snapshot_dataset",
    "run_baseline_suite",
    "BenchmarkResult",
]
