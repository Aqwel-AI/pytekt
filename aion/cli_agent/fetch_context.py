"""Fetch @web and @docs context with SSRF guards."""

from __future__ import annotations

import ipaddress
import re
import socket
import urllib.error
import urllib.request
from html import unescape
from typing import Optional, Tuple
from urllib.parse import urlparse

_MAX_CHARS = 12000

_DOCS_MAP = {
    "python:asyncio": "https://docs.python.org/3/library/asyncio.html",
    "python:typing": "https://docs.python.org/3/library/typing.html",
    "python:pathlib": "https://docs.python.org/3/library/pathlib.html",
}


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = unescape(re.sub(r"\s+", " ", text)).strip()
    return text


def _is_private_host(host: str) -> bool:
    if not host:
        return True
    host = host.lower().strip(".")
    if host in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        return True
    if host.endswith(".local") or host.endswith(".internal"):
        return True
    try:
        for info in socket.getaddrinfo(host, None):
            addr = info[4][0]
            ip = ipaddress.ip_address(addr)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return True
    except OSError:
        return True
    return False


def _validate_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return "Only http/https URLs are allowed."
    if _is_private_host(parsed.hostname or ""):
        return "Private or localhost URLs are blocked."
    return None


def fetch_url(url: str, *, max_chars: int = _MAX_CHARS) -> Tuple[str, str]:
    """Fetch URL and return (label, text block)."""
    err = _validate_url(url)
    if err:
        return url, f"<web-error url=\"{url}\">{err}</web-error>"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Aion-Agent/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read(500_000)
            ctype = resp.headers.get("Content-Type", "")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return url, f'<web-error url="{url}">{e}</web-error>'

    if "html" in ctype.lower():
        text = _strip_html(raw.decode("utf-8", errors="replace"))
    else:
        text = raw.decode("utf-8", errors="replace")
    if len(text) > max_chars:
        text = text[:max_chars] + "\n[... truncated ...]"
    block = f'<web url="{url}">\n{text}\n</web>'
    return url, block


def fetch_docs(key: str, *, max_chars: int = _MAX_CHARS) -> Tuple[str, str]:
    """Resolve curated @docs:key to fetched content."""
    url = _DOCS_MAP.get(key.lower())
    if not url:
        return key, f'<docs-error key="{key}">Unknown docs key. Try python:asyncio</docs-error>'
    label, block = fetch_url(url, max_chars=max_chars)
    return f"docs:{key}", block.replace("<web ", "<docs ").replace("</web>", "</docs>")


def is_web_token(token: str) -> bool:
    return token.startswith("web:") or token.startswith("http://") or token.startswith("https://")


def is_docs_token(token: str) -> bool:
    return token.startswith("docs:")


def expand_web_token(token: str) -> Tuple[str, str]:
    if token.startswith("web:"):
        url = token[4:]
    else:
        url = token
    return fetch_url(url)


def expand_docs_token(token: str) -> Tuple[str, str]:
    key = token[5:] if token.startswith("docs:") else token
    return fetch_docs(key)
