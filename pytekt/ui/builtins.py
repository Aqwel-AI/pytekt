"""Pre-built React-style layout and display components."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

from .component import Component, function_component
from .html_tags import html
from .vdom import Child, VNode, h

MetricDict = Dict[str, Union[int, float, str]]


@function_component
def Text(props: Dict[str, Any]) -> VNode:
    tag = props.get("as", "p")
    class_name = props.get("className", "pytekt-text")
    children = props.get("children", props.get("text", ""))
    return h(tag, {"className": class_name}, children)


@function_component
def Button(props: Dict[str, Any]) -> VNode:
    variant = props.get("variant", "primary")
    cls = "pytekt-btn" if variant == "primary" else "pytekt-btn pytekt-btn-secondary"
    attrs = {"className": cls, "type": props.get("type", "button")}
    if props.get("href"):
        return html.a({**attrs, "href": props["href"]}, *props.get("children", []))
    if props.get("onClick"):
        attrs["onClick"] = props["onClick"]
    return html.button(attrs, *props.get("children", []))


@function_component
def Card(props: Dict[str, Any]) -> VNode:
    title = props.get("title")
    children = list(props.get("children", []))
    inner: List[Any] = []
    if title:
        inner.append(html.h3({}, title))
    inner.extend(children)
    return html.div({"className": "pytekt-card"}, *inner)


@function_component
def Stack(props: Dict[str, Any]) -> VNode:
    return html.div({"className": "pytekt-stack"}, *props.get("children", []))


@function_component
def Row(props: Dict[str, Any]) -> VNode:
    return html.div({"className": "pytekt-row"}, *props.get("children", []))


@function_component
def Metric(props: Dict[str, Any]) -> VNode:
    value = props.get("value", "")
    label = props.get("label", "")
    display = f"{value:.4g}" if isinstance(value, float) else str(value)
    return html.div(
        {"className": "pytekt-metric"},
        html.div({"className": "val"}, display),
        html.div({"className": "lbl"}, label),
    )


@function_component
def MetricGrid(props: Dict[str, Any]) -> VNode:
    metrics: MetricDict = props.get("metrics", {})
    items = [Metric(value=v, label=k) for k, v in metrics.items()]
    return html.div({"className": "pytekt-metrics"}, *items)


class AppShell(Component):
    """Page layout with header, main content, and footer (like a root ``<App>``)."""

    def render(self):
        title = self.props.get("title", "PyTekt App")
        subtitle = self.props.get("subtitle", "")
        footer = self.props.get("footer", "Built with pytekt.ui")
        children = self.props.get("children", [])
        if callable(children):
            children = [children]
        elif not isinstance(children, (list, tuple)):
            children = [children]

        sub = html.p({"className": "pytekt-subtitle"}, subtitle) if subtitle else None
        return html.div(
            {"className": "pytekt-app"},
            html.header(
                {"className": "pytekt-header"},
                html.h1({}, title),
                sub,
            ),
            html.main({}, *children),
            html.footer({"className": "pytekt-footer"}, footer),
        )


class DataTable(Component):
    """Table component from headers + rows."""

    def render(self):
        headers = self.props.get("headers", [])
        rows = self.props.get("rows", [])
        head = html.thead(
            {},
            html.tr({}, *[html.th({}, str(h)) for h in headers]),
        )
        body_rows = []
        for row in rows:
            body_rows.append(
                html.tr({}, *[html.td({}, str(c)) for c in row])
            )
        return html.table({}, head, html.tbody({}, *body_rows))
