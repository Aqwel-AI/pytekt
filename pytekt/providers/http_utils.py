"""Minimal JSON HTTP using the standard library (no extra deps)."""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from .errors import ProviderError


def ssl_context() -> ssl.SSLContext:
    """Return an SSL context; prefer certifi's CA bundle when installed."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def get_json(
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """
    GET JSON and parse the response.

    Raises
    ------
    ProviderError
        On network failure or non-2xx response.
    """
    h = {"Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h, method="GET")
    ctx = ssl_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
            if not raw.strip():
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise ProviderError(
            f"HTTP {e.code}: {e.reason}",
            status=e.code,
            body=body[:4000],
        ) from e
    except TimeoutError as e:
        raise ProviderError(
            "Request timed out waiting for the provider.",
        ) from e
    except urllib.error.URLError as e:
        reason = str(getattr(e, "reason", e))
        if "timed out" in reason.lower():
            raise ProviderError(
                "Request timed out waiting for the provider.",
            ) from e
        raise ProviderError(f"Request failed: {e.reason}") from e


def post_json(
    url: str,
    payload: Dict[str, Any],
    *,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 120.0,
) -> Dict[str, Any]:
    """
    POST JSON and parse JSON response.

    Raises
    ------
    ProviderError
        On network failure or non-2xx response.
    """
    data = json.dumps(payload).encode("utf-8")
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    ctx = ssl_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
            if not raw.strip():
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise ProviderError(
            f"HTTP {e.code}: {e.reason}",
            status=e.code,
            body=body[:4000],
        ) from e
    except TimeoutError as e:
        raise ProviderError("Request timed out waiting for the provider.") from e
    except urllib.error.URLError as e:
        reason = str(getattr(e, "reason", e))
        if "timed out" in reason.lower():
            raise ProviderError("Request timed out waiting for the provider.") from e
        raise ProviderError(f"Request failed: {e.reason}") from e
