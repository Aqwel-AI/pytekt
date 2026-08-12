"""React-style class and function components."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, TypeVar, Union

from .vdom import Child, VNode, h, render_vnode

Renderable = Union[VNode, str, int, float, None, list]
PropsDict = Dict[str, Any]

T = TypeVar("T", bound="Component")


class Component:
    """
    Base class for declarative UI (like ``React.Component``).

    Subclass and implement :meth:`render`. Pass data via ``props`` in ``__init__``.

    Examples
    --------
    >>> from pytekt.ui import Component, html
    >>> class Hello(Component):
    ...     def render(self):
    ...         return html.div({}, html.h1({}, self.props.get("name", "World")))
    >>> Hello(name="PyTekt").render().tag
    'div'
    """

    def __init__(self, **props: Any) -> None:
        self.props: PropsDict = props
        self._state: PropsDict = {}

    @property
    def state(self) -> PropsDict:
        return self._state

    def set_state(self, updates: Dict[str, Any]) -> None:
        """Update local state (server render: re-call ``render`` after updates)."""
        self._state.update(updates)

    def render(self) -> Renderable:
        raise NotImplementedError(f"{type(self).__name__} must implement render()")

    def __call__(self) -> str:
        return render_vnode(self.render())


def function_component(
    fn: Callable[[PropsDict], Renderable],
) -> Callable[..., Renderable]:
    """
    Decorator for function components (like React function components).

    Examples
    --------
    >>> from pytekt.ui import html, function_component
    >>> @function_component
    ... def Title(props):
    ...     return html.h2({}, props["text"])
    >>> Title(text="Metrics").tag
    'h2'
    """

    def wrapper(**props: Any) -> Renderable:
        return fn(props)

    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    wrapper._is_pytekt_component = True  # type: ignore[attr-defined]
    return wrapper


def render_component(component: Any) -> str:
    """Render any component instance, VNode, or function component."""
    if hasattr(component, "render") and callable(component.render):
        return render_vnode(component.render())
    if callable(component) and getattr(component, "_is_pytekt_component", False):
        return render_vnode(component())
    if callable(component):
        return render_vnode(component())
    return render_vnode(component)
