"""Render React-style components to full HTML pages and optional dev server."""

from __future__ import annotations

import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Optional, Union

from .component import Component, render_component
from .html import escape_html
from .theme import REACT_THEME_CSS
from .vdom import render_vnode

PathLike = Union[str, Path]


def render(
    root: Any,
    *,
    title: str = "PyTekt App",
    extra_css: str = "",
    include_theme: bool = True,
) -> str:
    """
    Render a component tree to an HTML document body fragment (no ``<html>`` wrapper).

    Use :func:`render_app` for a complete page.
    """
    body = render_component(root)
    return body


def render_app(
    root: Any,
    *,
    title: str = "PyTekt App",
    output: Optional[PathLike] = None,
    extra_css: str = "",
    include_theme: bool = True,
    footer: str = "",
    open_browser: bool = False,
) -> str:
    """
    Render a React-style app to a self-contained HTML file.

    Parameters
    ----------
    root : Component, VNode, or callable
        Root component (class instance, function component, or VNode tree).
    title : str
        Document ``<title>`` and default header when using :class:`~pytekt.ui.AppShell`.
    output : path, optional
        If set, write HTML to this path.
    open_browser : bool
        Open the file in the default browser after save.

    Returns
    -------
    str
        Full HTML document string (and file path if ``output`` was given).
    """
    body = render_component(root)
    css = (REACT_THEME_CSS + extra_css) if include_theme else extra_css
    doc = (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
        f"<title>{escape_html(title)}</title>"
        f"<style>{css}</style></head><body>"
        f"{body}"
        + (f'<footer class="pytekt-footer">{escape_html(footer)}</footer>' if footer else "")
        + "</body></html>"
    )
    if output is not None:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(doc, encoding="utf-8")
        if open_browser:
            webbrowser.open(path.resolve().as_uri())
        return str(path)
    return doc


def serve_app(
    root: Any,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    title: str = "PyTekt App",
) -> None:
    """Serve a rendered app over HTTP (stdlib only, for local dev)."""
    html_doc = render_app(root, title=title, include_theme=True)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_doc.encode("utf-8"))

        def log_message(self, fmt, *args):
            pass

    server = HTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"
    print(f"PyTekt UI dev server: {url}")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
