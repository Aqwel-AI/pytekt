"""Aggregate usage events for the dashboard API."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from ..llm_eval.cost import estimate_cost
from .store import UsageStore

_LOCAL_PROVIDERS = frozenset({"ollama", "local", "localhost"})


def _event_cost_usd(event: Dict[str, Any]) -> float:
    """Recalculate cost so local Ollama is $0 (stored logs may have old estimates)."""
    prov = str(event.get("provider") or "unknown").lower()
    prompt = int(event.get("prompt_tokens") or 0)
    completion = int(event.get("completion_tokens") or 0)
    if prov in _LOCAL_PROVIDERS:
        return 0.0
    return float(
        estimate_cost(prov, prompt_tokens=prompt, completion_tokens=completion)["cost_usd"]
    )


def _parse_ts(ts: str) -> Optional[datetime]:
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None


def _in_range(dt: datetime, start: datetime, end: datetime) -> bool:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return start <= dt < end


def _range_bounds(range_key: str) -> tuple[datetime, datetime, str]:
    now = datetime.now(timezone.utc)
    if range_key == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now + timedelta(seconds=1), "Today"
    if range_key == "week":
        start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now + timedelta(seconds=1), "Last 7 days"
    if range_key == "month":
        start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now + timedelta(seconds=1), "Last 30 days"
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, now + timedelta(seconds=1), "Today"


def filter_events(
    events: List[Dict[str, Any]],
    *,
    range_key: str = "today",
) -> List[Dict[str, Any]]:
    start, end, _ = _range_bounds(range_key)
    out: List[Dict[str, Any]] = []
    for e in events:
        ts = e.get("ts")
        if not ts:
            continue
        dt = _parse_ts(str(ts))
        if dt and _in_range(dt, start, end):
            out.append(e)
    return out


def build_summary(
    events: List[Dict[str, Any]],
    *,
    range_key: str = "today",
) -> Dict[str, Any]:
    """KPI cards: tokens, cost, calls, by provider."""
    filtered = filter_events(events, range_key=range_key)
    _, _, label = _range_bounds(range_key)

    total_prompt = sum(int(e.get("prompt_tokens") or 0) for e in filtered)
    total_completion = sum(int(e.get("completion_tokens") or 0) for e in filtered)
    cloud_cost = 0.0
    local_tokens = 0
    by_provider: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"tokens": 0, "cost_usd": 0.0, "calls": 0, "is_local": False}
    )
    by_model: Dict[str, int] = defaultdict(int)

    for e in filtered:
        prov = str(e.get("provider") or "unknown")
        prov_key = prov.lower()
        model = str(e.get("model") or "unknown")
        tok = int(e.get("total_tokens") or 0)
        cost = _event_cost_usd(e)
        is_local = prov_key in _LOCAL_PROVIDERS
        if is_local:
            local_tokens += tok
        else:
            cloud_cost += cost
        by_provider[prov]["tokens"] += tok
        by_provider[prov]["cost_usd"] += cost
        by_provider[prov]["calls"] += 1
        by_provider[prov]["is_local"] = is_local
        by_model[f"{prov}/{model}"] += tok

    provider_rows = [
        {
            "provider": k,
            "tokens": v["tokens"],
            "cost_usd": round(v["cost_usd"], 6),
            "calls": v["calls"],
            "is_local": bool(v.get("is_local")),
        }
        for k, v in sorted(by_provider.items(), key=lambda x: -x[1]["tokens"])
    ]

    only_local = bool(filtered) and cloud_cost == 0.0 and local_tokens > 0
    if only_local:
        cost_label = "Cloud API cost"
        cost_note = "Local models (Ollama) — no API charge"
    elif cloud_cost > 0 and local_tokens > 0:
        cost_label = "Est. cloud cost (USD)"
        cost_note = "Ollama is free · cloud uses public list prices (not your invoice)"
    elif cloud_cost > 0:
        cost_label = "Est. cloud cost (USD)"
        cost_note = "Approximate from public pricing — not your actual bill"
    else:
        cost_label = "Cloud API cost"
        cost_note = "No usage logged yet"

    return {
        "range": range_key,
        "range_label": label,
        "total_tokens": total_prompt + total_completion,
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_cost_usd": round(cloud_cost, 6),
        "cloud_cost_usd": round(cloud_cost, 6),
        "local_tokens": local_tokens,
        "cost_label": cost_label,
        "cost_note": cost_note,
        "only_local": only_local,
        "call_count": len(filtered),
        "by_provider": provider_rows,
        "top_models": sorted(by_model.items(), key=lambda x: -x[1])[:8],
    }


def build_timeseries(
    events: List[Dict[str, Any]],
    *,
    range_key: str = "today",
) -> Dict[str, Any]:
    """Hourly token and cost buckets for charts."""
    filtered = filter_events(events, range_key=range_key)
    buckets: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"tokens": 0, "cost_usd": 0.0, "calls": 0}
    )

    for e in filtered:
        ts = e.get("ts")
        if not ts:
            continue
        dt = _parse_ts(str(ts))
        if not dt:
            continue
        key = dt.strftime("%Y-%m-%d %H:00")
        buckets[key]["tokens"] += int(e.get("total_tokens") or 0)
        buckets[key]["cost_usd"] += _event_cost_usd(e)
        buckets[key]["calls"] += 1

    labels = sorted(buckets.keys())
    return {
        "labels": labels,
        "tokens": [buckets[k]["tokens"] for k in labels],
        "cost_usd": [round(buckets[k]["cost_usd"], 6) for k in labels],
        "calls": [buckets[k]["calls"] for k in labels],
    }


def build_week_comparison(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Daily totals for the last 7 days (bar chart)."""
    now = datetime.now(timezone.utc)
    days: List[str] = []
    tokens: List[int] = []
    costs: List[float] = []

    for i in range(6, -1, -1):
        day_start = (now - timedelta(days=i)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        day_end = day_start + timedelta(days=1)
        label = day_start.strftime("%a %m/%d")
        days.append(label)
        day_events = [
            e
            for e in events
            if (dt := _parse_ts(str(e.get("ts", ""))))
            and _in_range(dt, day_start, day_end)
        ]
        tokens.append(sum(int(e.get("total_tokens") or 0) for e in day_events))
        costs.append(round(sum(_event_cost_usd(e) for e in day_events), 6))

    return {"labels": days, "tokens": tokens, "cost_usd": costs}
