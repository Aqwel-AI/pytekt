"""``html.div``, ``html.button``, … — JSX-like tag factories."""

from __future__ import annotations

from typing import Any

from .vdom import Child, Props, VNode, h


class HtmlTags:
    """
    Namespace of HTML tag factories (use like JSX tags).

    Examples
    --------
    >>> from aion.ui import html
    >>> html.div({"className": "app"}, html.p({}, "hi")).tag
    'div'
    """

    def __getattr__(self, tag: str) -> Any:
        def tag_fn(props: Props = None, *children: Child) -> VNode:
            return h(tag, props, *children)

        tag_fn.__name__ = tag
        return tag_fn

    # Common tags as explicit attributes (IDE autocomplete)
    def div(self, props: Props = None, *children: Child) -> VNode:
        return h("div", props, *children)

    def span(self, props: Props = None, *children: Child) -> VNode:
        return h("span", props, *children)

    def p(self, props: Props = None, *children: Child) -> VNode:
        return h("p", props, *children)

    def h1(self, props: Props = None, *children: Child) -> VNode:
        return h("h1", props, *children)

    def h2(self, props: Props = None, *children: Child) -> VNode:
        return h("h2", props, *children)

    def h3(self, props: Props = None, *children: Child) -> VNode:
        return h("h3", props, *children)

    def button(self, props: Props = None, *children: Child) -> VNode:
        return h("button", props, *children)

    def a(self, props: Props = None, *children: Child) -> VNode:
        return h("a", props, *children)

    def input(self, props: Props = None, *children: Child) -> VNode:
        return h("input", props, *children)

    def label(self, props: Props = None, *children: Child) -> VNode:
        return h("label", props, *children)

    def ul(self, props: Props = None, *children: Child) -> VNode:
        return h("ul", props, *children)

    def li(self, props: Props = None, *children: Child) -> VNode:
        return h("li", props, *children)

    def table(self, props: Props = None, *children: Child) -> VNode:
        return h("table", props, *children)

    def thead(self, props: Props = None, *children: Child) -> VNode:
        return h("thead", props, *children)

    def tbody(self, props: Props = None, *children: Child) -> VNode:
        return h("tbody", props, *children)

    def tr(self, props: Props = None, *children: Child) -> VNode:
        return h("tr", props, *children)

    def th(self, props: Props = None, *children: Child) -> VNode:
        return h("th", props, *children)

    def td(self, props: Props = None, *children: Child) -> VNode:
        return h("td", props, *children)

    def pre(self, props: Props = None, *children: Child) -> VNode:
        return h("pre", props, *children)

    def code(self, props: Props = None, *children: Child) -> VNode:
        return h("code", props, *children)

    def section(self, props: Props = None, *children: Child) -> VNode:
        return h("section", props, *children)

    def header(self, props: Props = None, *children: Child) -> VNode:
        return h("header", props, *children)

    def footer(self, props: Props = None, *children: Child) -> VNode:
        return h("footer", props, *children)

    def main(self, props: Props = None, *children: Child) -> VNode:
        return h("main", props, *children)

    def nav(self, props: Props = None, *children: Child) -> VNode:
        return h("nav", props, *children)

    def img(self, props: Props = None, *children: Child) -> VNode:
        return h("img", props, *children)

    def form(self, props: Props = None, *children: Child) -> VNode:
        return h("form", props, *children)


html = HtmlTags()
