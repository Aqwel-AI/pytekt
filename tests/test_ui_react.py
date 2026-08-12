"""Tests for React-style aion.ui components."""

from pytekt.ui import (
    AppShell,
    Component,
    MetricGrid,
    Stack,
    Card,
    html,
    render_app,
    render_component,
    render_vnode,
    function_component,
    Fragment,
    h,
)


@function_component
def Greeting(props):
    return html.p({}, f"Hello, {props['name']}!")


class SimpleApp(Component):
    def render(self):
        return html.div(
            {"className": "app"},
            html.h1({}, "Test"),
            Greeting(name="Aion"),
        )


def test_h_and_html_tags():
    node = html.div({"className": "x"}, html.span({}, "hi"))
    assert node.tag == "div"
    out = render_vnode(node)
    assert 'class="x"' in out
    assert "<span>hi</span>" in out


def test_fragment():
    out = render_vnode(Fragment(html.p({}, "a"), html.p({}, "b")))
    assert out.count("<p>") == 2


def test_class_component():
    out = render_component(SimpleApp())
    assert "Hello, Aion" in out


def test_app_shell_and_metrics():
    app = AppShell(
        title="ML",
        children=Stack(
            children=[
                MetricGrid(metrics={"acc": 0.9, "loss": 0.1}),
                Card(title="Notes", children=[html.p({}, "Done.")]),
            ]
        ),
    )
    html_doc = render_app(app, title="ML")
    assert "ML" in html_doc
    assert "acc" in html_doc.lower() or "0.9" in html_doc


def test_render_app_save(tmp_path):
    path = tmp_path / "app.html"
    render_app(SimpleApp(), output=str(path), title="T")
    text = path.read_text()
    assert "<html" in text
    assert "Test" in text
