"""Unit conversions and angle formatting."""

from __future__ import annotations

import math
import re
from typing import Tuple

from .constants import AU, LIGHT_YEAR, PARSEC

_DEG_TO_RAD = math.pi / 180.0


def deg_to_rad(degrees: float) -> float:
    return degrees * _DEG_TO_RAD


def rad_to_deg(radians: float) -> float:
    return radians / _DEG_TO_RAD


def hours_to_deg(hours: float) -> float:
    return hours * 15.0


def deg_to_hours(degrees: float) -> float:
    return degrees / 15.0


def ly_to_pc(light_years: float) -> float:
    return light_years * LIGHT_YEAR / PARSEC


def pc_to_ly(parsecs: float) -> float:
    return parsecs * PARSEC / LIGHT_YEAR


def au_to_km(au: float) -> float:
    return au * AU / 1000.0


def km_to_au(km: float) -> float:
    return km * 1000.0 / AU


def flux_to_magnitude(flux: float, flux_zero: float = 1.0) -> float:
    """Pogson magnitude from flux (relative to flux_zero)."""
    if flux <= 0:
        raise ValueError("flux must be positive")
    return -2.5 * math.log10(flux / flux_zero)


def magnitude_to_flux(magnitude: float, flux_zero: float = 1.0) -> float:
    return flux_zero * 10.0 ** (-0.4 * magnitude)


def parse_ra(text: str) -> float:
    """
    Parse right ascension to decimal hours.

    Accepts ``12h 30m 15s``, ``12:30:15``, or decimal hours.
    """
    text = text.strip()
    if "h" in text.lower() or "m" in text.lower():
        h = re.search(r"(\d+)\s*h", text, re.I)
        m = re.search(r"(\d+)\s*m", text, re.I)
        s = re.search(r"([\d.]+)\s*s", text, re.I)
        hours = float(h.group(1)) if h else 0.0
        minutes = float(m.group(1)) if m else 0.0
        seconds = float(s.group(1)) if s else 0.0
        return hours + minutes / 60.0 + seconds / 3600.0
    parts = text.replace(":", " ").split()
    if len(parts) == 3:
        return float(parts[0]) + float(parts[1]) / 60.0 + float(parts[2]) / 3600.0
    return float(text)


def parse_dec(text: str) -> float:
    """Parse declination to decimal degrees (supports +/- and d m s)."""
    text = text.strip()
    sign = -1.0 if text.startswith("-") else 1.0
    text = text.lstrip("+-").strip()
    if "d" in text.lower() or "°" in text:
        d = re.search(r"(\d+)\s*d", text, re.I) or re.search(r"(\d+)\s*°", text)
        m = re.search(r"(\d+)\s*m", text, re.I)
        s = re.search(r"([\d.]+)\s*s", text, re.I)
        deg = float(d.group(1)) if d else 0.0
        minutes = float(m.group(1)) if m else 0.0
        seconds = float(s.group(1)) if s else 0.0
        return sign * (deg + minutes / 60.0 + seconds / 3600.0)
    parts = text.replace(":", " ").split()
    if len(parts) == 3:
        val = float(parts[0]) + float(parts[1]) / 60.0 + float(parts[2]) / 3600.0
        return sign * val
    return sign * float(text)


def format_ra(hours: float) -> str:
    h = int(hours)
    rem = (hours - h) * 60.0
    m = int(rem)
    s = (rem - m) * 60.0
    return f"{h:02d}h {m:02d}m {s:05.2f}s"


def format_dec(degrees: float) -> str:
    sign = "+" if degrees >= 0 else "-"
    d = abs(degrees)
    deg = int(d)
    rem = (d - deg) * 60.0
    m = int(rem)
    s = (rem - m) * 60.0
    return f"{sign}{deg:02d}d {m:02d}m {s:05.2f}s"


def sexagesimal_to_decimal(parts: Tuple[float, float, float]) -> float:
    h, m, s = parts
    return h + m / 60.0 + s / 3600.0
