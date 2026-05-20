"""Local date/time and region for agent UI (no network)."""

from __future__ import annotations

import locale
import os
from datetime import datetime
from typing import Any, Dict, Optional

# ISO 3166-1 alpha-2 → common country names (subset)
_COUNTRY_NAMES: Dict[str, str] = {
    "US": "United States",
    "GB": "United Kingdom",
    "UK": "United Kingdom",
    "DE": "Germany",
    "FR": "France",
    "AM": "Armenia",
    "RU": "Russia",
    "CA": "Canada",
    "AU": "Australia",
    "IN": "India",
    "CN": "China",
    "JP": "Japan",
    "BR": "Brazil",
    "MX": "Mexico",
    "IT": "Italy",
    "ES": "Spain",
    "NL": "Netherlands",
    "SE": "Sweden",
    "NO": "Norway",
    "PL": "Poland",
    "TR": "Turkey",
    "AE": "United Arab Emirates",
    "SG": "Singapore",
    "KR": "South Korea",
    "IL": "Israel",
    "CH": "Switzerland",
    "AT": "Austria",
    "BE": "Belgium",
    "PT": "Portugal",
    "GR": "Greece",
    "UA": "Ukraine",
    "RO": "Romania",
    "CZ": "Czechia",
    "HU": "Hungary",
    "FI": "Finland",
    "DK": "Denmark",
    "IE": "Ireland",
    "NZ": "New Zealand",
    "ZA": "South Africa",
    "AR": "Argentina",
    "CL": "Chile",
    "CO": "Colombia",
    "PH": "Philippines",
    "TH": "Thailand",
    "VN": "Vietnam",
    "ID": "Indonesia",
    "MY": "Malaysia",
    "TW": "Taiwan",
    "HK": "Hong Kong",
}


def _normalize_locale_tag(raw: str) -> Optional[str]:
    tag = raw.strip().split(".")[0]
    if not tag or tag.upper() in ("C", "POSIX"):
        return None
    return tag


def _locale_tag() -> Optional[str]:
    for key in ("LC_ALL", "LC_ADDRESS", "LANG", "LC_CTYPE"):
        raw = os.environ.get(key, "").strip()
        tag = _normalize_locale_tag(raw) if raw else None
        if tag:
            return tag
    try:
        tag = locale.getlocale()[0]
        if tag and tag.upper() != "C":
            return tag
    except Exception:
        pass
    try:
        tag = locale.getdefaultlocale()[0]
        if tag and tag.upper() != "C":
            return tag
    except Exception:
        pass
    if os.name == "posix" and os.uname().sysname == "Darwin":
        try:
            import subprocess

            out = subprocess.run(
                ["defaults", "read", "-g", "AppleLocale"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
            tag = (out.stdout or "").strip()
            if tag:
                return tag.split("@")[0]
        except Exception:
            pass
    return None


def get_country_display() -> Dict[str, str]:
    """
    Best-effort country from system locale (not GPS/IP).

    Returns ``code``, ``name``, ``locale``.
    """
    tag = _locale_tag() or ""
    code = ""
    if "_" in tag:
        code = tag.rsplit("_", 1)[-1].upper()
        if len(code) > 2:
            code = code[:2]
    elif len(tag) == 2:
        code = tag.upper()
    name = _COUNTRY_NAMES.get(code, code or "—")
    return {"code": code, "name": name, "locale": tag or "—"}


def get_timezone_display() -> str:
    """Local timezone name or offset."""
    tz_env = os.environ.get("TZ", "").strip()
    if tz_env:
        return tz_env
    now = datetime.now().astimezone()
    tz = now.tzinfo
    if tz is None:
        return "UTC"
    name = tz.tzname(None) if hasattr(tz, "tzname") else None
    if name:
        return str(name)
    offset = now.strftime("%z")
    if offset:
        h = int(offset[:3])
        m = int(offset[0] + offset[3:5])
        return f"UTC{h:+03d}:{m:02d}"
    return "local"


def get_datetime_display() -> Dict[str, str]:
    """Human-readable local date and time."""
    now = datetime.now().astimezone()
    return {
        "iso": now.isoformat(timespec="seconds"),
        "day": now.strftime("%A"),
        "date": now.strftime("%B %d, %Y"),
        "time": now.strftime("%H:%M:%S"),
        "short": now.strftime("%a, %b %d · %H:%M"),
        "full": now.strftime("%A, %B %d, %Y · %H:%M:%S"),
    }


def _country_label(country: Dict[str, str]) -> str:
    code = country.get("code", "")
    name = country.get("name", "")
    if code and name and name != code:
        return f"{name} ({code})"
    if code:
        return code
    if name and name != "—":
        return name
    return ""


def get_agent_context() -> Dict[str, Any]:
    """Bundle for dashboard, API, and status line."""
    dt = get_datetime_display()
    country = get_country_display()
    tz = get_timezone_display()
    place = _country_label(country)
    parts_full = [dt["full"]]
    parts_short = [dt["short"]]
    if place:
        parts_full.append(place)
        parts_short.append(country.get("code") or place)
    parts_full.append(tz)
    parts_short.append(tz)
    return {
        "datetime": dt,
        "country": country,
        "timezone": tz,
        "line": " · ".join(parts_full),
        "line_short": " · ".join(parts_short),
    }
