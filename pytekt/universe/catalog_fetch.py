"""Optional remote catalog fetch (stdlib HTTP)."""

from __future__ import annotations

import csv
import io
import os
import urllib.request
from typing import Any, Dict, List, Optional


EXOPLANET_CSV_URL = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?"
    "query=select+pl_name,hostname,discoverymethod,disc_year+from+pscomppars&format=csv"
)


def fetch_exoplanet_table(
    *,
    url: str = EXOPLANET_CSV_URL,
    cache_path: Optional[str] = None,
    timeout: float = 30.0,
) -> List[Dict[str, Any]]:
    """
    Fetch a small exoplanet table from NASA Exoplanet Archive.

    Requires network. Caches to *cache_path* when provided.
    """
    cache_path = cache_path or os.path.expanduser("~/.aion/universe/exoplanets.csv")
    if os.path.isfile(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    req = urllib.request.Request(url, headers={"User-Agent": "pytekt/universe"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8")
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(text)
    return list(csv.DictReader(io.StringIO(text)))
