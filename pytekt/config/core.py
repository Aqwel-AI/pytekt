"""TOML/YAML loading, deep merge, nested keys, and environment overlays."""

from __future__ import annotations

import copy
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional, Tuple, Union

PathLike = Union[str, os.PathLike[str]]

_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")
_TRUE = frozenset({"1", "true", "yes", "on"})
_FALSE = frozenset({"0", "false", "no", "off", ""})


def _load_toml_bytes(data: bytes) -> Dict[str, Any]:
    if sys.version_info >= (3, 11):
        import tomllib

        return tomllib.loads(data.decode("utf-8"))
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError as e:
        raise ImportError(
            "Reading TOML on Python <3.11 requires tomli. "
            "Install with: pip install pytekt[config]"
        ) from e
    return tomllib.loads(data.decode("utf-8"))


def load_toml_file(path: PathLike) -> Dict[str, Any]:
    """Load a TOML file into a nested dict."""
    p = Path(path)
    return _load_toml_bytes(p.read_bytes())


def load_yaml_file(path: PathLike) -> Dict[str, Any]:
    """Load a YAML file (requires PyYAML: pip install pytekt[config] or [former])."""
    try:
        import yaml
    except ImportError as e:
        raise ImportError(
            "YAML config requires PyYAML. Install with pip install pyyaml "
            "or pip install pytekt[config]"
        ) from e
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        out = yaml.safe_load(f)
    return out if isinstance(out, dict) else {}


def save_yaml_file(path: PathLike, data: Mapping[str, Any], *, default_flow_style: bool = False) -> Path:
    """
    Write ``data`` as YAML using ``yaml.safe_dump``. Requires PyYAML.
    Returns the resolved path.
    """
    try:
        import yaml
    except ImportError as e:
        raise ImportError(
            "Writing YAML requires PyYAML. Install with pip install pytekt[config]"
        ) from e
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            dict(data),
            f,
            default_flow_style=default_flow_style,
            allow_unicode=True,
            sort_keys=False,
        )
    return p


def merge_env_overrides(
    cfg: MutableMapping[str, Any],
    prefix: str = "AION_",
) -> MutableMapping[str, Any]:
    """
    For each env var ``PREFIX_KEY`` (nested keys as ``PREFIX_SECTION__KEY``),
    set string values on ``cfg`` (shallow merge only for top-level keys for
    non-nested names; nested uses ``section__key``).
    """
    plen = len(prefix)
    for k, v in os.environ.items():
        if not k.startswith(prefix):
            continue
        sub = k[plen:].lower()
        if "__" in sub:
            section, key = sub.split("__", 1)
            if section not in cfg or not isinstance(cfg[section], MutableMapping):
                cfg[section] = {}
            cfg[section][key] = v  # type: ignore[index]
        else:
            cfg[sub] = v
    return cfg


def load_config(
    path: PathLike,
    *,
    merge_env: bool = True,
    env_prefix: str = "AION_",
) -> Dict[str, Any]:
    """Load ``.toml`` or ``.yaml`` / ``.yml`` from path."""
    p = Path(path)
    suf = p.suffix.lower()
    if suf in (".toml",):
        cfg = dict(load_toml_file(p))
    elif suf in (".yaml", ".yml"):
        cfg = dict(load_yaml_file(p))
    else:
        raise ValueError(f"Unsupported config extension: {suf}")
    if merge_env:
        merge_env_overrides(cfg, prefix=env_prefix)
    return cfg


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge ``override`` into a copy of ``base``. Dict values are
    merged recursively; scalars and lists are replaced by ``override``.
    """
    dst = copy.deepcopy(dict(base))
    for key, val in override.items():
        if key in dst and isinstance(dst[key], dict) and isinstance(val, Mapping):
            dst[key] = deep_merge(dst[key], val)
        else:
            dst[key] = copy.deepcopy(val)
    return dst


def get_nested(cfg: Mapping[str, Any], dotted_path: str, default: Any = None) -> Any:
    """
    Read a value using a dotted path (e.g. ``\"db.host\"``). Missing segments
    return ``default``.
    """
    cur: Any = cfg
    for part in dotted_path.split("."):
        if not part:
            continue
        if isinstance(cur, Mapping) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def set_nested(cfg: MutableMapping[str, Any], dotted_path: str, value: Any) -> None:
    """
    Set a value under a dotted path, creating intermediate dicts as needed.
    """
    parts = [p for p in dotted_path.split(".") if p]
    if not parts:
        raise ValueError("dotted_path must contain at least one segment")
    cur: MutableMapping[str, Any] = cfg
    for p in parts[:-1]:
        nxt = cur.get(p)
        if not isinstance(nxt, MutableMapping):
            nxt = {}
            cur[p] = nxt
        cur = nxt
    cur[parts[-1]] = value


def coerce_string_scalar(s: str) -> Union[str, int, float, bool]:
    """
    Convert common string forms to bool, int, or float; otherwise return the
    original string. Intended for env overlays and untyped config files.
    """
    sl = s.strip()
    low = sl.lower()
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    if _INT_RE.match(sl):
        return int(sl)
    if _FLOAT_RE.match(sl):
        return float(sl)
    return s


def coerce_string_values(obj: Any) -> Any:
    """
    Recursively walk dicts/lists and coerce string leaves with
    :func:`coerce_string_scalar`. Returns a new structure (does not mutate).
    """
    if isinstance(obj, dict):
        return {k: coerce_string_values(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [coerce_string_values(v) for v in obj]
    if isinstance(obj, str):
        return coerce_string_scalar(obj)
    return obj


def load_config_typed(
    path: PathLike,
    *,
    merge_env: bool = True,
    env_prefix: str = "AION_",
) -> Dict[str, Any]:
    """Like :func:`load_config`, then apply :func:`coerce_string_values`."""
    cfg = load_config(path, merge_env=merge_env, env_prefix=env_prefix)
    out = coerce_string_values(cfg)
    return out if isinstance(out, dict) else dict(cfg)


def load_first_existing(
    paths: Iterable[PathLike],
    *,
    merge_env: bool = True,
    env_prefix: str = "AION_",
) -> Tuple[Dict[str, Any], Optional[Path]]:
    """
    Load the first path in ``paths`` that exists. Returns ``({}, None)`` if
    none exist (still applies env overrides to the empty dict when
    ``merge_env`` is True).
    """
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            cfg = load_config(p, merge_env=False, env_prefix=env_prefix)
            if merge_env:
                merge_env_overrides(cfg, prefix=env_prefix)
            return cfg, p
    cfg: Dict[str, Any] = {}
    if merge_env:
        merge_env_overrides(cfg, prefix=env_prefix)
    return cfg, None


def load_layered(
    *paths: PathLike,
    merge_env: bool = True,
    env_prefix: str = "AION_",
) -> Dict[str, Any]:
    """
    Load each existing file in order and deep-merge later files over earlier
    ones. Environment overlay is applied once at the end if ``merge_env``.
    """
    merged: Dict[str, Any] = {}
    for raw in paths:
        p = Path(raw)
        if not p.is_file():
            continue
        layer = load_config(p, merge_env=False, env_prefix=env_prefix)
        merged = deep_merge(merged, layer)
    if merge_env:
        merge_env_overrides(merged, prefix=env_prefix)
    return merged


class _Missing:
    pass


_MISSING = _Missing()


def require_keys(cfg: Mapping[str, Any], *dotted_keys: str) -> None:
    """
    Raise ``KeyError`` if any dotted path is missing or not a leaf value
    (intermediate missing key). A present value of ``None`` is allowed.
    """
    for dk in dotted_keys:
        if get_nested(cfg, dk, default=_MISSING) is _MISSING:
            raise KeyError(f"Required config key missing or incomplete: {dk!r}")


def pick_subset(cfg: Mapping[str, Any], *dotted_keys: str) -> Dict[str, Any]:
    """Build a flat dict ``{dotted_key: value}`` for keys that exist."""
    out: Dict[str, Any] = {}
    for dk in dotted_keys:
        v = get_nested(cfg, dk, default=_MISSING)
        if v is not _MISSING:
            out[dk] = v
    return out


def config_as_dict(cfg: Mapping[str, Any]) -> Dict[str, Any]:
    """Deep copy of a mapping for safe mutation or logging."""
    return copy.deepcopy(dict(cfg))
