"""Virtual DOM nodes and element factory (React-style ``createElement``)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union

from .html import escape_html

Child = Union[str, int, float, "VNode", "ComponentLike", None]
Props = Optional[Dict[str, Any]]

# Forward reference for Component
ComponentLike = Any


@dataclass
class VNode:
    """A virtual DOM node — analogous to a React element."""

    tag: str
    props: Dict[str, Any] = field(default_factory=dict)
    children: List[Any] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"VNode({self.tag!r}, children={len(self.children)})"


def Fragment(*children: Child) -> VNode:
    """Group children without a wrapper element (React ``<>...</>``)."""
    return VNode("__fragment__", {}, _flatten_children(children))


def h(tag: str, props: Props = None, *children: Child) -> VNode:
    """
    Create a virtual DOM node (like ``React.createElement``).

    Examples
    --------
    >>> from aion.ui.vdom import h
    >>> h("div", {"className": "card"}, h("p", {}, "Hello")).tag
    'motion'
    """
    tag = tag.replace("_", "-") if tag not in ("__fragment__",) else tag
    props = dict(props or {})
    prop_children = props.pop("children", None)
    all_children: List[Any] = []
    if prop_children is not None:
        all_children.extend(_normalize_child(prop_children))
    all_children.extend(_flatten_children(children))
    return VNode(tag, props, all_children)


def _normalize_child(child: Any) -> List[Any]:
    if child is None or child is False:
        return []
    if isinstance(child, (list, tuple)):
        return _flatten_children(child)
    return [child]


def _flatten_children(children: Sequence[Any]) -> List[Any]:
    out: List[Any] = []
    for c in children:
        if c is None or c is False:
            continue
        if isinstance(c, (list, tuple)):
            out.extend(_flatten_children(c))
        else:
            out.append(c)
    return out


def _props_to_attrs(props: Dict[str, Any]) -> str:
    parts: List[str] = []
    for key, value in props.items():
        if value is None or value is False:
            continue
        if key == "children":
            continue
        if key == "className":
            key = "class"
        elif key.startswith("on") and len(key) > 2 and key[2].isupper():
            # onClick -> onclick
            key = key[0].lower() + key[1:2] + key[2:].lower()
        if key == "style" and isinstance(value, dict):
            style = "; ".join(f"{_camel_to_kebab(k)}: {v}" for k, v in value.items())
            parts.append(f'style="{escape_html(style)}"')
        elif isinstance(value, bool):
            if value:
                parts.append(key)
        else:
            parts.append(f'{key}="{escape_html(value)}"')
    return " ".join(parts)


def _camel_to_kebab(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            out.append("-")
        out.append(ch.lower())
    return "".join(out)


def render_vnode(node: Any) -> str:
    """Render a VNode tree (or string) to an HTML string."""
    if node is None or node is False:
        return ""
    if isinstance(node, (str, int, float)):
        return escape_html(node)
    if hasattr(node, "render") and callable(node.render):
        return render_vnode(node.render())
    if not isinstance(node, VNode):
        return escape_html(node)

    if node.tag == "__fragment__":
        return "".join(render_vnode(c) for c in node.children)

    inner = "".join(render_vnode(c) for c in node.children)
    attrs = _props_to_attrs(node.props)
    if node.tag in ("input", "img", "br", "hr", "meta", "link"):
        return f"<{node.tag} {attrs}/>" if attrs else f"<{node.tag}/>"
    if attrs:
        return f"<{node.tag} {attrs}>{inner}</{node.tag}>"
    return f"<{node.tag}>{inner}</{node.tag}>"
