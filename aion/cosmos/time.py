"""Julian date and sidereal time utilities."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Union

from .constants import J2000


def datetime_to_jd(dt: datetime) -> float:
    """Convert timezone-aware or naive UTC datetime to Julian Date."""
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    year = dt.year
    month = dt.month
    day = dt.day + (
        dt.hour + (dt.minute + dt.second / 60.0) / 60.0
    ) / 24.0
    if month <= 2:
        year -= 1
        month += 12
    a = int(year / 100)
    b = 2 - a + int(a / 4)
    return (
        int(365.25 * (year + 4716))
        + int(30.6001 * (month + 1))
        + day
        + b
        - 1524.5
    )


def jd_to_datetime(jd: float) -> datetime:
    """Julian Date to UTC datetime (approximate inverse)."""
    z = int(jd + 0.5)
    f = jd + 0.5 - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - int(alpha / 4)
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    day_int = int(day)
    frac = day - day_int
    hours = frac * 24.0
    hour = int(hours)
    minutes = (hours - hour) * 60.0
    minute = int(minutes)
    second = int((minutes - minute) * 60.0)
    return datetime(year, month, day_int, hour, minute, second)


def mjd(jd: float) -> float:
    return jd - 2400000.5


def jd_from_mjd(mjd_val: float) -> float:
    return mjd_val + 2400000.5


def now_jd() -> float:
    return datetime_to_jd(datetime.now(timezone.utc))


def gmst(jd: float) -> float:
    """Greenwich Mean Sidereal Time in hours."""
    t = (jd - J2000) / 36525.0
    theta = (
        280.46061837
        + 360.98564736629 * (jd - J2000)
        + 0.000387933 * t * t
        - t * t * t / 38710000.0
    )
    return (theta % 360.0) / 15.0


def lst(jd: float, longitude_deg: float) -> float:
    """Local Sidereal Time in hours."""
    return (gmst(jd) + longitude_deg / 15.0) % 24.0


def julian_centuries(jd: float) -> float:
    return (jd - J2000) / 36525.0


def epoch_to_jd(epoch_year: float) -> float:
    """Approximate JD for Jan 1.0 of epoch year."""
    return datetime_to_jd(datetime(int(epoch_year), 1, 1, 0, 0, 0))
