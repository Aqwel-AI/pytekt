"""
Unit tests for pytekt.cli.branding terminal helper and no-TTY fallback.
"""

import io
import re
import shutil
import sys
import tempfile
from pathlib import Path
import pytest

from pytekt.branding import (
    Palette,
    StepTask,
    animate_bot_scaffold,
    detect_compiler,
    is_interactive,
    print_banner,
    print_closing_banner,
    print_metadata_box,
    run_task_sequence,
)
import pytekt.cli.branding as cli_branding


# Regex pattern detecting ANSI escape sequences
ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def test_palette_constants():
    """Verify PyTekt official terminal palette constants."""
    assert Palette.ELECTRIC_BLUE == "#3D8BFD"
    assert Palette.MATRIX_GREEN == "#3ECF8E"
    assert Palette.NEON_CYAN == "#22D3EE"
    assert Palette.COSMIC_PURPLE == "#C084FC"
    assert Palette.CYBER_PINK == "#F472B6"
    assert Palette.CRISP_WHITE == "#E7EDF4"
    assert Palette.DARK_VOID == "#0A0E14"
    assert Palette.MUTED_SLATE == "#8B9CB3"
    assert Palette.BORDER_SLATE == "#2D3A4D"
    assert Palette.AMBER == "#F5A524"
    assert Palette.RED == "#F14C4C"

    # Also verify accessible via pytekt.cli.branding
    assert cli_branding.Palette.ELECTRIC_BLUE == "#3D8BFD"


def test_is_interactive_non_tty():
    """Verify StringIO (non-TTY) is detected as non-interactive."""
    buf = io.StringIO()
    assert is_interactive(buf) is False


def test_banner_no_tty_clean_plain_text():
    """Assert banner produces clean plain text without ANSI escapes on non-TTY."""
    buf = io.StringIO()
    print_banner(stream=buf, animated=False)
    output = buf.getvalue()

    assert len(output) > 0
    assert "██" in output
    # Ensure zero ANSI escape codes are emitted
    assert not ANSI_ESCAPE_RE.search(output), f"Found ANSI escape in banner output: {output!r}"
    assert "\033[" not in output
    assert "\x1b[" not in output


def test_metadata_box_no_tty_clean_plain_text():
    """Assert metadata box produces clean plain text without ANSI escapes on non-TTY."""
    buf = io.StringIO()
    print_metadata_box(
        name="alpha_bot",
        platform="telegram",
        target_path=Path("/tmp/alpha_bot"),
        compiler="Clang 16.0",
        stream=buf,
    )
    output = buf.getvalue()

    assert "alpha_bot" in output
    assert "Telegram" in output
    assert "Clang 16.0" in output
    # Ensure zero ANSI escape codes
    assert not ANSI_ESCAPE_RE.search(output), f"Found ANSI escape in metadata output: {output!r}"
    assert "\033[" not in output
    assert "\x1b[" not in output


def test_task_sequence_no_tty_clean_plain_text():
    """Assert task sequence executes actions and emits clean plain text without ANSI."""
    buf = io.StringIO()
    executed = []

    tasks = [
        StepTask("step1", "Creating files", action=lambda: executed.append("step1")),
        StepTask("step2", "Writing environment", action=lambda: executed.append("step2")),
        StepTask("ai", "bots.ai layer configured", is_ai=True),
        StepTask("warn", "Optional compiler note", is_warning=True),
    ]

    run_task_sequence(tasks, animated=False, stream=buf)
    output = buf.getvalue()

    # All actions executed
    assert executed == ["step1", "step2"]
    # Contains expected plain indicators
    assert "✓ Creating files" in output
    assert "✓ Writing environment" in output
    assert "✦ bots.ai layer configured" in output
    assert "⚠ Optional compiler note" in output

    # Ensure zero ANSI escape codes
    assert not ANSI_ESCAPE_RE.search(output), f"Found ANSI escape in task output: {output!r}"
    assert "\033[" not in output


def test_closing_banner_no_tty_clean_plain_text():
    """Assert closing banner emits clean plain text on non-TTY."""
    buf = io.StringIO()
    print_closing_banner(project_dir=Path("/tmp/my_bot"), run_cmd="python main.py", stream=buf)
    output = buf.getvalue()

    assert "Bot ready → python main.py" in output
    assert "cd my_bot" in output
    assert "cp .env.example .env" in output
    assert not ANSI_ESCAPE_RE.search(output)


def test_animate_bot_scaffold_no_tty_end_to_end():
    """Test full animate_bot_scaffold with non-TTY stream creates runnable files and clean text."""
    temp_dir = Path(tempfile.mkdtemp())
    buf = io.StringIO()
    try:
        created_path = animate_bot_scaffold(
            name="branded_test_bot",
            platform="telegram",
            target_dir=temp_dir,
            include_ai=True,
            animated=False,
            stream=buf,
        )

        assert created_path.is_dir()
        assert (created_path / "bot" / "main.py").is_file()
        assert (created_path / "bot" / "config.py").is_file()
        assert (created_path / "bot" / "ai" / "setup.py").is_file()
        assert (created_path / ".env.example").is_file()
        assert (created_path / "tests" / "test_handlers.py").is_file()

        # Check AI inclusion
        main_text = (created_path / "bot" / "main.py").read_text()
        assert "setup_ai" in main_text

        # Check plain-text output
        output = buf.getvalue()
        assert "branded_test_bot" in output
        assert "Configuring bot/ai/setup.py" in output
        assert "Bot ready → python -m bot.main" in output
        assert not ANSI_ESCAPE_RE.search(output)
        # Verify large ASCII wordmark is NOT printed
        assert "██████╗" not in output
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_format_green_progress_line():
    """Verify green progress line formatting."""
    from pytekt.branding import format_green_progress_line

    plain_line = format_green_progress_line(50, 100, color_on=False)
    assert "scaffold" in plain_line
    assert "50%" in plain_line
    assert "\033[" not in plain_line

    colored_line = format_green_progress_line(100, 100, color_on=True)
    assert "\033[92m" in colored_line
    assert "complete" in colored_line
    assert "100%" in colored_line


def test_select_platform_interactive_defaults_non_interactive():
    """Verify non-interactive call to select_platform_interactive defaults to telegram."""
    from pytekt.branding import select_platform_interactive

    buf = io.StringIO()
    res = select_platform_interactive(stream=buf, interactive=False)
    assert res == "telegram"


def test_select_platform_interactive_coming_soon_rejection():
    """Verify Discord and Slack are marked coming soon and cannot be chosen."""
    from unittest.mock import patch
    from pytekt.branding import select_platform_interactive

    buf = io.StringIO()
    # User tries Discord (2), then Slack (3), then selects Telegram (1)
    with patch("builtins.input", side_effect=["2", "3", "1"]):
        res = select_platform_interactive(stream=buf, interactive=True)

    assert res == "telegram"
    out = buf.getvalue()
    assert "Discord" in out
    assert "Slack" in out
    assert "coming soon" in out
    assert "⚠️" in out or "coming soon" in out


def test_read_single_key_arrow_keys_and_ws():
    """Verify top/bottom buttons (arrow keys), w/s, and space/enter key parsing."""
    from unittest.mock import patch
    from pytekt.branding import read_single_key

    # Test top/up buttons and aliases
    for up_input in ["up", "top", "w", "W", "k", "K", "↑", "\x1b[A"]:
        with patch("builtins.input", return_value=up_input):
            assert read_single_key(stream=io.StringIO()) == "up"

    # Test bottom/down buttons and aliases
    for down_input in ["down", "bottom", "s", "S", "j", "J", "↓", "\x1b[B"]:
        with patch("builtins.input", return_value=down_input):
            assert read_single_key(stream=io.StringIO()) == "down"

    # Test space / toggle aliases
    for space_input in ["space", " ", "toggle", "t", "prabel", "p", "x", "check"]:
        with patch("builtins.input", return_value=space_input):
            assert read_single_key(stream=io.StringIO()) == "space"

    # Test enter / confirm aliases
    for enter_input in ["enter", "ok", "done", "confirm", "return", ""]:
        with patch("builtins.input", return_value=enter_input):
            assert read_single_key(stream=io.StringIO()) == "enter"


def test_interactive_select_with_top_bottom_arrow_keys():
    """Verify single-select menu navigation with top and bottom arrow buttons."""
    from pytekt.branding import interactive_select

    options = [
        ("opt1", "Option 1", "First option", True),
        ("opt2", "Option 2", "Second option", True),
        ("opt3", "Option 3", "Third option", True),
    ]

    # Navigate down, down, up, enter -> should select opt2
    keys = ["down", "down", "up", "enter"]
    res = interactive_select(
        title="Test Menu",
        prompt="Choose an option:",
        options=options,
        stream=io.StringIO(),
        interactive=True,
        key_reader=lambda: keys.pop(0),
    )
    assert res == "opt2"

    # Navigate with w / s buttons: s (down), s (down), w (up), enter -> opt2
    keys_ws = ["s", "w", "s", "enter"]
    res_ws = interactive_select(
        title="Test Menu",
        prompt="Choose an option:",
        options=options,
        stream=io.StringIO(),
        interactive=True,
        key_reader=lambda: keys_ws.pop(0),
    )
    assert res_ws == "opt2"


def test_cancellation_with_esc_and_ctrl_c():
    """Verify user can cancel with ESC or Ctrl+C, resulting in WizardCancelled and red text output."""
    from pytekt.branding import (
        interactive_select,
        interactive_multiselect,
        read_single_key,
        WizardCancelled,
    )
    from unittest.mock import patch

    options = [
        ("opt1", "Option 1", "First option", True),
        ("opt2", "Option 2", "Second option", True),
    ]

    # 1. Cancel single-select with ESC
    buf_esc = io.StringIO()
    try:
        interactive_select(
            title="Menu",
            prompt="Choose:",
            options=options,
            stream=buf_esc,
            interactive=True,
            key_reader=lambda: "esc",
        )
        assert False, "Should have raised WizardCancelled"
    except WizardCancelled:
        pass
    out_esc = buf_esc.getvalue()
    assert "✖ Bot creation cancelled." in out_esc
    assert "\033[1;91m" in out_esc or "#F14C4C" in out_esc or "red" in out_esc

    # 2. Cancel single-select with Ctrl+C
    buf_ctrl = io.StringIO()
    try:
        interactive_select(
            title="Menu",
            prompt="Choose:",
            options=options,
            stream=buf_ctrl,
            interactive=True,
            key_reader=lambda: "ctrl_c",
        )
        assert False, "Should have raised WizardCancelled"
    except WizardCancelled:
        pass
    out_ctrl = buf_ctrl.getvalue()
    assert "✖ Bot creation cancelled." in out_ctrl

    # 3. Cancel multi-select with ESC
    buf_multi_esc = io.StringIO()
    try:
        interactive_multiselect(
            title="Features",
            prompt="Select:",
            options=[("feat1", "Feature 1", "desc", False)],
            stream=buf_multi_esc,
            interactive=True,
            key_reader=lambda: "escape",
        )
        assert False, "Should have raised WizardCancelled"
    except WizardCancelled:
        pass
    out_multi = buf_multi_esc.getvalue()
    assert "✖ Bot creation cancelled." in out_multi

    # 4. Cancel multi-select with Ctrl+C
    buf_multi_ctrl = io.StringIO()
    try:
        interactive_multiselect(
            title="Features",
            prompt="Select:",
            options=[("feat1", "Feature 1", "desc", False)],
            stream=buf_multi_ctrl,
            interactive=True,
            key_reader=lambda: "ctrl_c",
        )
        assert False, "Should have raised WizardCancelled"
    except WizardCancelled:
        pass
    assert "✖ Bot creation cancelled." in buf_multi_ctrl.getvalue()

    # 5. read_single_key recognizes esc and ctrl_c aliases
    for esc_alias in ["esc", "escape", "cancel", "q", "exit", "\x1b"]:
        with patch("builtins.input", return_value=esc_alias):
            assert read_single_key(stream=io.StringIO()) == "escape"

    for ctrl_alias in ["ctrl_c", "ctrl-c"]:
        with patch("builtins.input", return_value=ctrl_alias):
            assert read_single_key(stream=io.StringIO()) == "ctrl_c"

    # KeyboardInterrupt in input() maps to ctrl_c
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        assert read_single_key(stream=io.StringIO()) == "ctrl_c"



