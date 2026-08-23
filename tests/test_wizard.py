"""
Tests for PyTekt Post-Install Dependency Selector (pytekt init)
"""

from unittest.mock import patch
import pytest

from pytekt.wizard import (
    DEPENDENCY_GROUPS,
    GROUP_IDS,
    GROUP_MAP,
    LOGO_LINES,
    LOGO_GRADIENT,
    InteractiveMenu,
    play_logo_reveal,
    play_loading_spinner,
    run_install_cascade,
    play_summary_panel,
    run_non_interactive,
    run_wizard,
)
from pytekt.cli import _build_parser


def test_dependency_groups_structure():
    assert len(DEPENDENCY_GROUPS) == 7
    expected_ids = ["data", "ml", "dl", "viz", "nlp", "vision", "stats"]
    assert GROUP_IDS == expected_ids
    for group in DEPENDENCY_GROUPS:
        assert "id" in group
        assert "name" in group
        assert "desc" in group
        assert "packages" in group
        assert group["id"] in GROUP_MAP


def test_logo_structure():
    assert len(LOGO_LINES) == 6
    assert len(LOGO_GRADIENT) == 6


def test_static_logo_and_spinner(capsys):
    from rich.console import Console
    console = Console(record=True, force_terminal=False)
    play_logo_reveal(console, skip_animation=True)
    out = console.export_text()
    assert "Your Python toolkit, assembled." in out

    play_loading_spinner(console, skip_animation=True)


def test_animated_logo_and_spinner():
    from rich.console import Console
    console = Console(record=True, force_terminal=False)
    play_logo_reveal(console, skip_animation=False)
    play_loading_spinner(console, duration=0.05, skip_animation=False)


def test_install_cascade_and_summary_panel():
    from rich.console import Console
    console = Console(record=True, force_terminal=False)
    with patch("pytekt.wizard._verify_or_install_group"):
        run_install_cascade(console, ["data", "ml", "viz"], skip_animation=True)
    out = console.export_text()
    assert "Data handling" in out
    assert "Machine Learning" in out
    assert "Visualization" in out

    play_summary_panel(console, ["data", "ml", "viz"], skip_animation=True)
    out2 = console.export_text()
    assert "PyTekt Setup Complete" in out2
    assert "Data handling" in out2


def test_install_cascade_none():
    from rich.console import Console
    console = Console(record=True, force_terminal=False)
    run_install_cascade(console, [], skip_animation=True)
    out = console.export_text()
    assert "base environment is ready" in out


def test_run_non_interactive(capsys):
    with patch("pytekt.wizard._verify_or_install_group"):
        run_non_interactive(["data", "viz"])
    captured = capsys.readouterr()
    assert "PyTekt Post-Install Dependency Selector" in captured.out
    assert "data, viz" in captured.out
    assert "[OK] Data handling (pandas, numpy) — installed" in captured.out
    assert "[OK] Visualization (matplotlib, seaborn) — installed" in captured.out


def test_run_non_interactive_none(capsys):
    run_non_interactive([], core_only=True)
    captured = capsys.readouterr()
    assert "Core base only" in captured.out
    assert "[OK] Core PyTekt library — ready" in captured.out


def test_run_wizard_all(capsys):
    with patch("pytekt.wizard._verify_or_install_group"):
        res = run_wizard(all_modules=True)
    assert res == 0
    captured = capsys.readouterr()
    assert "PyTekt Post-Install Dependency Selector" in captured.out
    assert "data, ml, dl, viz, nlp, vision, stats" in captured.out


def test_run_wizard_none(capsys):
    res = run_wizard(none_modules=True)
    assert res == 0
    captured = capsys.readouterr()
    assert "Core base only" in captured.out


def test_run_wizard_only(capsys):
    with patch("pytekt.wizard._verify_or_install_group"):
        res = run_wizard(only_modules="ml,viz")
    assert res == 0
    captured = capsys.readouterr()
    assert "ml, viz" in captured.out


def test_cli_parser_init():
    parser, _ = _build_parser()
    args = parser.parse_args(["init", "--all"])
    assert args.command == "init"
    assert args.all is True

    args2 = parser.parse_args(["init", "--none"])
    assert args2.command == "init"
    assert args2.none is True

    args3 = parser.parse_args(["init", "--only", "ml,viz"])
    assert args3.command == "init"
    assert args3.only == "ml,viz"


def test_interactive_menu_logic():
    from rich.console import Console
    console = Console(record=True, force_terminal=False)
    menu = InteractiveMenu(console)
    assert menu.all_selected is False
    assert len(menu.selected_ids) == 0

    panel = menu._render_ui()
    assert panel is not None
