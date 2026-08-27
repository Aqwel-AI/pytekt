"""
Unit tests for professional modular bot scaffolding (pytekt bots new).
Tests file sets for every flag combination (--platform, --with-ai, --with-db, --minimal)
and verifies that the generated project's own pytest suite passes out of the box.
"""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch

from pytekt.bots.scaffold import generate_project, generate_readme_content
from pytekt.branding import spinner


def _run_project_pytest(project_dir: Path) -> subprocess.CompletedProcess:
    """Run pytest inside the generated project using current python executable."""
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{project_dir}:{env.get('PYTHONPATH', '')}"
    return subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-v"],
        cwd=str(project_dir),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


def test_scaffold_default_modular_structure():
    """Default scaffold must create professional multi-file structure without AI or DB."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("Alpha Bot", platform="telegram", target_dir=temp_dir)

        # Expected directories
        assert (project_dir / "bot").is_dir()
        assert (project_dir / "bot" / "handlers").is_dir()
        assert (project_dir / "bot" / "middlewares").is_dir()
        assert (project_dir / "bot" / "utils").is_dir()
        assert (project_dir / "tests").is_dir()

        # Expected files
        assert (project_dir / "bot" / "__init__.py").is_file()
        assert (project_dir / "bot" / "main.py").is_file()
        assert (project_dir / "bot" / "config.py").is_file()
        assert (project_dir / "bot" / "handlers" / "__init__.py").is_file()
        assert (project_dir / "bot" / "handlers" / "commands.py").is_file()
        assert (project_dir / "bot" / "handlers" / "messages.py").is_file()
        assert (project_dir / "bot" / "handlers" / "callbacks.py").is_file()
        assert (project_dir / "bot" / "middlewares" / "__init__.py").is_file()
        assert (project_dir / "bot" / "utils" / "__init__.py").is_file()
        assert (project_dir / "tests" / "__init__.py").is_file()
        assert (project_dir / "tests" / "test_handlers.py").is_file()
        assert (project_dir / ".env.example").is_file()
        assert (project_dir / ".gitignore").is_file()
        assert (project_dir / "pyproject.toml").is_file()
        assert (project_dir / "requirements.txt").is_file()
        assert (project_dir / "README.md").is_file()
        assert (project_dir / "SECURITY.md").is_file()

        # Unrequested modules must NOT exist
        assert not (project_dir / "bot" / "ai").exists()
        assert not (project_dir / "bot" / "models").exists()
        assert not (project_dir / "main.py").exists()

        # Check config contains typed Settings
        config_text = (project_dir / "bot" / "config.py").read_text()
        assert "class Settings:" in config_text
        assert "TELEGRAM_BOT_TOKEN" in config_text

        # Generated project pytest must pass out of the box
        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_with_ai():
    """Scaffolding with include_ai=True must generate bot/ai/ folder with default functions and pass pytest."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("AI Bot", platform="telegram", target_dir=temp_dir, include_ai=True)

        assert (project_dir / "bot" / "ai").is_dir()
        assert (project_dir / "bot" / "ai" / "__init__.py").is_file()
        assert (project_dir / "bot" / "ai" / "setup.py").is_file()
        assert (project_dir / "bot" / "ai" / "tools.py").is_file()
        assert (project_dir / "bot" / "ai" / "prompts.py").is_file()

        # AI tools registered and default functions available
        ai_code = (project_dir / "bot" / "ai" / "setup.py").read_text()
        assert "setup_ai" in ai_code
        assert "ask_ai" in ai_code

        tools_code = (project_dir / "bot" / "ai" / "tools.py").read_text()
        assert "@ai.tool" in tools_code
        assert "get_server_status" in tools_code
        assert "calculate_sum" in tools_code
        assert "get_current_time" in tools_code

        prompts_code = (project_dir / "bot" / "ai" / "prompts.py").read_text()
        assert "SYSTEM_PROMPT" in prompts_code

        # main.py connects AI
        main_code = (project_dir / "bot" / "main.py").read_text()
        assert "from bot.ai.setup import setup_ai" in main_code

        # /ask command present in commands.py
        commands_code = (project_dir / "bot" / "handlers" / "commands.py").read_text()
        assert '@bot.on_command("ask")' in commands_code

        # .env.example contains OPENAI_API_KEY
        env_text = (project_dir / ".env.example").read_text()
        assert "OPENAI_API_KEY" in env_text

        # DB must NOT be included
        assert not (project_dir / "bot" / "models").exists()

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_with_db():
    """Scaffolding with include_db=True must generate bot/models/ folder with default functions and pass pytest."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("Data Bot", platform="telegram", target_dir=temp_dir, include_db=True)

        assert (project_dir / "bot" / "models").is_dir()
        assert (project_dir / "bot" / "models" / "__init__.py").is_file()
        assert (project_dir / "bot" / "models" / "operations.py").is_file()
        assert (project_dir / "bot" / "models" / "schemas.py").is_file()

        models_code = (project_dir / "bot" / "models" / "__init__.py").read_text()
        assert "init_db" in models_code
        assert "pytekt.db" in models_code
        assert "save_user" in models_code
        assert "get_user_stats" in models_code

        ops_code = (project_dir / "bot" / "models" / "operations.py").read_text()
        assert "def save_user(" in ops_code
        assert "def get_user(" in ops_code
        assert "def get_user_stats(" in ops_code
        assert "def log_event(" in ops_code
        assert "def get_setting(" in ops_code

        schemas_code = (project_dir / "bot" / "models" / "schemas.py").read_text()
        assert "class UserRecord:" in schemas_code
        assert "class EventLog:" in schemas_code

        # main.py connects DB
        main_code = (project_dir / "bot" / "main.py").read_text()
        assert "from bot.models import init_db" in main_code

        # /stats command present in commands.py
        commands_code = (project_dir / "bot" / "handlers" / "commands.py").read_text()
        assert '@bot.on_command("stats")' in commands_code

        # .env.example contains DATABASE_URL
        env_text = (project_dir / ".env.example").read_text()
        assert "DATABASE_URL" in env_text

        # AI must NOT be included
        assert not (project_dir / "bot" / "ai").exists()

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_with_ai_and_db():
    """Scaffolding with both AI and DB must include both modules and pass pytest."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("Nexus Bot", platform="telegram", target_dir=temp_dir, include_ai=True, include_db=True)

        assert (project_dir / "bot" / "ai" / "setup.py").is_file()
        assert (project_dir / "bot" / "models" / "__init__.py").is_file()

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_discord_platform():
    """Scaffolding for Discord must generate DiscordBot and pass pytest."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("Discord Nexus", platform="discord", target_dir=temp_dir)

        main_code = (project_dir / "bot" / "main.py").read_text()
        assert "DiscordBot" in main_code

        env_code = (project_dir / ".env.example").read_text()
        assert "DISCORD_BOT_TOKEN" in env_code

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_minimal_single_file():
    """Scaffolding with minimal=True must generate flat single-file layout and pass pytest."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("Quick Bot", platform="telegram", target_dir=temp_dir, minimal=True)

        # Single-file layout
        assert (project_dir / "main.py").is_file()
        assert (project_dir / "tests" / "test_bot.py").is_file()
        assert not (project_dir / "bot").exists()

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "2 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_dynamic_readme_generation():
    """README generator must reflect exact features and platform."""
    # Modular Telegram with AI and DB
    readme_full = generate_readme_content("OmniBot", platform="telegram", with_ai=True, with_db=True, minimal=False)
    assert "OmniBot" in readme_full
    assert "Telegram" in readme_full
    assert "ai/" in readme_full
    assert "models/" in readme_full
    assert "python -m bot.main" in readme_full

    # Minimal Discord
    readme_min = generate_readme_content("MiniBot", platform="discord", minimal=True)
    assert "Discord" in readme_min
    assert "main.py" in readme_min
    assert "python main.py" in readme_min
    assert "bot/" not in readme_min


def test_branding_spinner_context_manager():
    """pytekt.cli.branding.spinner context manager executes and prints completion."""
    buf = io.StringIO()
    executed = False
    with spinner("Testing spinner helper", stream=buf):
        executed = True

    assert executed is True
    out = buf.getvalue()
    assert "Testing spinner helper" in out
    assert "✓" in out


def test_interactive_ai_selection():
    """Verify AI interactive prompt."""
    from unittest.mock import patch
    from pytekt.branding import select_ai_interactive

    buf = io.StringIO()
    # Default/empty -> False
    with patch("builtins.input", return_value=""):
        assert select_ai_interactive(stream=buf, interactive=True) is False

    # "2" -> True
    with patch("builtins.input", return_value="2"):
        assert select_ai_interactive(stream=buf, interactive=True) is True

    # "yes" -> True
    with patch("builtins.input", return_value="yes"):
        assert select_ai_interactive(stream=buf, interactive=True) is True

    # Non-interactive -> default
    assert select_ai_interactive(default=False, stream=buf, interactive=False) is False


def test_interactive_db_selection():
    """Verify DB interactive prompt."""
    from unittest.mock import patch
    from pytekt.branding import select_db_interactive

    buf = io.StringIO()
    # Default/empty -> False
    with patch("builtins.input", return_value=""):
        assert select_db_interactive(stream=buf, interactive=True) is False

    # "2" -> True
    with patch("builtins.input", return_value="2"):
        assert select_db_interactive(stream=buf, interactive=True) is True

    # Non-interactive -> default
    assert select_db_interactive(default=False, stream=buf, interactive=False) is False


def test_interactive_layout_selection():
    """Verify layout interactive prompt."""
    from unittest.mock import patch
    from pytekt.branding import select_layout_interactive

    buf = io.StringIO()
    # Default/empty -> False (modular)
    with patch("builtins.input", return_value=""):
        assert select_layout_interactive(stream=buf, interactive=True) is False

    # "2" -> True (minimal)
    with patch("builtins.input", return_value="2"):
        assert select_layout_interactive(stream=buf, interactive=True) is True

    # Non-interactive -> default
    assert select_layout_interactive(default=False, stream=buf, interactive=False) is False


def test_prompt_scaffold_wizard_flow():
    """Verify end-to-end prompt_scaffold_wizard flow with line input for templates and None custom fallback."""
    from unittest.mock import patch
    from pytekt.branding import prompt_scaffold_wizard

    buf = io.StringIO()
    # Case A: User selects a starter template: Platform 1 (Telegram), Template 3 (AI Chatbot)
    with patch("builtins.input", side_effect=["1", "3"]):
        opts = prompt_scaffold_wizard("MyBot", stream=buf, interactive=True)

    assert opts["platform"] == "telegram"
    assert opts["template"] == "ai-chatbot"
    assert opts["with_ai"] is True
    assert opts["scaffold_mode"] == "auto"

    # Case B: User selects 'None' (Custom Features) in template picker -> falls back to multiselect like in the past!
    # Input: Platform 1 (Telegram), Template 1 (None - Custom Features), Features "1, 2" (AI, DB)
    with patch("builtins.input", side_effect=["1", "1", "1, 2"]):
        opts_custom = prompt_scaffold_wizard("CustomBot", stream=buf, interactive=True)

    assert opts_custom["platform"] == "telegram"
    assert opts_custom["template"] is None
    assert opts_custom["with_ai"] is True
    assert opts_custom["with_db"] is True
    assert opts_custom["minimal"] is False
    assert opts_custom["scaffold_mode"] == "auto"

    # Pre-specified flags or skip_prompts skips prompts
    opts2 = prompt_scaffold_wizard(
        "MyBot", platform="telegram", template="echo", skip_prompts=True, stream=buf, interactive=True
    )
    assert opts2["platform"] == "telegram"
    assert opts2["template"] == "echo"
    assert opts2["scaffold_mode"] == "auto"


def test_keyboard_arrow_and_spacebar_multiselect():
    """Verify choosing with top and bottom arrow buttons and toggling with spacebar (prabel)."""
    from pytekt.branding import prompt_scaffold_wizard, select_features_multiselect

    # 1. Test multiselect directly with keyboard navigation:
    # Keys: space (toggle AI on), down (to DB), space (toggle DB on), enter (confirm)
    keys1 = ["space", "down", "space", "enter"]
    res = select_features_multiselect(
        stream=io.StringIO(),
        interactive=True,
        key_reader=lambda: keys1.pop(0),
    )
    assert res["with_ai"] is True
    assert res["with_db"] is True
    assert res["minimal"] is False

    # 2. Test full scaffold wizard with arrow keys:
    # Platform select: down (Discord - blocked), up (Telegram), enter (select Telegram)
    # Template select: default is Echo (idx 1). Press down once -> AI Chatbot (idx 2), enter (select AI Chatbot)
    keys2 = ["down", "enter", "up", "enter", "down", "enter"]
    opts = prompt_scaffold_wizard(
        "ArrowBot",
        stream=io.StringIO(),
        interactive=True,
        key_reader=lambda: keys2.pop(0),
    )
    assert opts["platform"] == "telegram"
    assert opts["template"] == "ai-chatbot"
    assert opts["with_ai"] is True
    assert opts["scaffold_mode"] == "auto"


def test_scaffold_minimal_with_ai_and_db():
    """When choosing AI and DB in flat/minimal layout, ai/ and db/ folders must be created and connected."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("Combo Bot", platform="telegram", target_dir=temp_dir, include_ai=True, include_db=True, minimal=True)

        assert (project_dir / "main.py").is_file()
        assert (project_dir / "ai").is_dir()
        assert (project_dir / "ai" / "__init__.py").is_file()
        assert (project_dir / "ai" / "setup.py").is_file()
        assert (project_dir / "ai" / "tools.py").is_file()
        assert (project_dir / "ai" / "prompts.py").is_file()

        assert (project_dir / "db").is_dir()
        assert (project_dir / "db" / "__init__.py").is_file()
        assert (project_dir / "db" / "operations.py").is_file()
        assert (project_dir / "db" / "schemas.py").is_file()

        main_text = (project_dir / "main.py").read_text()
        assert "from ai import setup_ai" in main_text
        assert "from db import init_db" in main_text
        assert "ai = setup_ai()" in main_text
        assert "db = init_db()" in main_text
        assert '@bot.on_command("ask")' in main_text
        assert '@bot.on_command("stats")' in main_text

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "2 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_with_roles():
    """Scaffolding with include_roles=True generates roles/ folder with permissions and commands."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("Roles Bot", platform="telegram", target_dir=temp_dir, include_roles=True)

        assert (project_dir / "bot" / "roles").is_dir()
        assert (project_dir / "bot" / "roles" / "__init__.py").is_file()
        assert (project_dir / "bot" / "roles" / "permissions.py").is_file()
        assert (project_dir / "bot" / "roles" / "admin_commands.py").is_file()

        perm_code = (project_dir / "bot" / "roles" / "permissions.py").read_text()
        assert "setup_roles" in perm_code
        assert "is_admin" in perm_code

        admin_code = (project_dir / "bot" / "roles" / "admin_commands.py").read_text()
        assert "@admin_only" in admin_code
        assert "handle_ban" in admin_code

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_with_i18n():
    """Scaffolding with include_i18n=True generates locales/ with en, ru, es translation files."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("i18n Bot", platform="telegram", target_dir=temp_dir, include_i18n=True)

        assert (project_dir / "bot" / "locales").is_dir()
        assert (project_dir / "bot" / "locales" / "__init__.py").is_file()
        assert (project_dir / "bot" / "locales" / "translator.py").is_file()
        assert (project_dir / "bot" / "locales" / "en.json").is_file()
        assert (project_dir / "bot" / "locales" / "ru.json").is_file()
        assert (project_dir / "bot" / "locales" / "es.json").is_file()

        trans_code = (project_dir / "bot" / "locales" / "translator.py").read_text()
        assert "setup_i18n" in trans_code
        assert "get_text" in trans_code
        assert "handle_lang_cmd" in trans_code

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_with_scheduler():
    """Scaffolding with include_scheduler=True generates scheduler/ with jobs.py."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("Cron Bot", platform="telegram", target_dir=temp_dir, include_scheduler=True)

        assert (project_dir / "bot" / "scheduler").is_dir()
        assert (project_dir / "bot" / "scheduler" / "__init__.py").is_file()
        assert (project_dir / "bot" / "scheduler" / "jobs.py").is_file()

        jobs_code = (project_dir / "bot" / "scheduler" / "jobs.py").read_text()
        assert "setup_scheduler" in jobs_code
        assert "health_check_job" in jobs_code
        assert "daily_digest_job" in jobs_code

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_with_payments():
    """Scaffolding with include_payments=True generates payments/ with invoices.py & checkout.py."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("Shop Bot", platform="telegram", target_dir=temp_dir, include_payments=True)

        assert (project_dir / "bot" / "payments").is_dir()
        assert (project_dir / "bot" / "payments" / "__init__.py").is_file()
        assert (project_dir / "bot" / "payments" / "invoices.py").is_file()
        assert (project_dir / "bot" / "payments" / "checkout.py").is_file()

        inv_code = (project_dir / "bot" / "payments" / "invoices.py").read_text()
        assert "create_stars_invoice" in inv_code
        assert "VIP_PLANS" in inv_code

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_with_ui():
    """Scaffolding with include_ui=True generates ui_components/ with pagination, surveys & confirmation."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("UI Bot", platform="telegram", target_dir=temp_dir, include_ui=True)

        assert (project_dir / "bot" / "ui_components").is_dir()
        assert (project_dir / "bot" / "ui_components" / "__init__.py").is_file()
        assert (project_dir / "bot" / "ui_components" / "pagination.py").is_file()
        assert (project_dir / "bot" / "ui_components" / "survey_wizard.py").is_file()
        assert (project_dir / "bot" / "ui_components" / "confirmation.py").is_file()

        pag_code = (project_dir / "bot" / "ui_components" / "pagination.py").read_text()
        assert "class Paginator:" in pag_code

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scaffold_all_features_together():
    """Scaffolding with all 7 features enabled generates all folders and passes tests."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project(
            "Ultra Bot",
            platform="telegram",
            target_dir=temp_dir,
            include_ai=True,
            include_db=True,
            include_roles=True,
            include_i18n=True,
            include_scheduler=True,
            include_payments=True,
            include_ui=True,
        )

        assert (project_dir / "bot" / "ai").is_dir()
        assert (project_dir / "bot" / "models").is_dir()
        assert (project_dir / "bot" / "roles").is_dir()
        assert (project_dir / "bot" / "locales").is_dir()
        assert (project_dir / "bot" / "scheduler").is_dir()
        assert (project_dir / "bot" / "payments").is_dir()
        assert (project_dir / "bot" / "ui_components").is_dir()

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ==============================================================================
# Template Picker & Manifest Tests
# ==============================================================================

def test_template_manifest_parsing():
    """Verify loading and parsing of template manifests."""
    from pytekt.bots.templates import load_manifest, TEMPLATES_DIR

    echo_manifest = load_manifest(TEMPLATES_DIR / "echo")
    assert echo_manifest.id == "echo"
    assert "Echo" in echo_manifest.name
    assert echo_manifest.minimal is True
    assert "telegram" in echo_manifest.platforms
    assert "discord" in echo_manifest.platforms

    faq_manifest = load_manifest(TEMPLATES_DIR / "faq-support")
    assert faq_manifest.id == "faq-support"
    assert faq_manifest.with_ai is True
    assert faq_manifest.with_db is True
    assert "openai>=1.0.0" in faq_manifest.extra_deps
    assert "OPENAI_API_KEY" in faq_manifest.extra_env

    pay_manifest = load_manifest(TEMPLATES_DIR / "ecommerce-payments")
    assert pay_manifest.id == "ecommerce-payments"
    assert pay_manifest.with_payments is True
    assert pay_manifest.with_ui is True
    assert pay_manifest.platforms == ["telegram"]


def test_template_listing_and_filtering():
    """Verify templates are filtered according to target platform."""
    from pytekt.bots.templates import list_templates, get_template

    all_templates = list_templates()
    assert len(all_templates) >= 6
    ids = [t.id for t in all_templates]
    assert "echo" in ids
    assert "ai-chatbot" in ids
    assert "faq-support" in ids
    assert "moderation" in ids
    assert "reminder-scheduler" in ids
    assert "ecommerce-payments" in ids

    # Telegram includes payments
    tg_templates = list_templates(platform="telegram")
    tg_ids = [t.id for t in tg_templates]
    assert "ecommerce-payments" in tg_ids

    # Discord excludes telegram-only payments template
    dc_templates = list_templates(platform="discord")
    dc_ids = [t.id for t in dc_templates]
    assert "ecommerce-payments" not in dc_ids
    assert "echo" in dc_ids
    assert "ai-chatbot" in dc_ids

    # get_template platform filter check
    assert get_template("ecommerce-payments", platform="telegram") is not None
    assert get_template("ecommerce-payments", platform="discord") is None


def test_generated_output_for_echo_template():
    """Verify project generated from 'echo' template passes test suite."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("EchoTestBot", platform="telegram", target_dir=temp_dir, template="echo")

        assert (project_dir / "main.py").is_file()
        assert (project_dir / "tests" / "test_bot.py").is_file()

        main_text = (project_dir / "main.py").read_text()
        assert '@bot.on_command("ping")' in main_text
        assert '@bot.on_message()' in main_text

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "3 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_generated_output_for_faq_support_template():
    """Verify project generated from 'faq-support' template contains knowledge base and passes tests."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        project_dir = generate_project("SupportBot", platform="telegram", target_dir=temp_dir, template="faq-support")

        assert (project_dir / "faq.md").is_file()
        assert (project_dir / "bot" / "main.py").is_file()
        assert (project_dir / "bot" / "ai" / "setup.py").is_file()
        assert (project_dir / "bot" / "handlers" / "commands.py").is_file()

        setup_code = (project_dir / "bot" / "ai" / "setup.py").read_text()
        assert "knowledge_base" in setup_code

        cmds_code = (project_dir / "bot" / "handlers" / "commands.py").read_text()
        assert '@bot.on_command("faq")' in cmds_code
        assert '@bot.on_command("ticket")' in cmds_code

        res = _run_project_pytest(project_dir)
        assert res.returncode == 0, f"Pytest failed:\n{res.stdout}\n{res.stderr}"
        assert "4 passed" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_manual_setup_output_contains_valid_python_syntax():
    """Verify that every file printed in manual setup output parses as valid Python code."""
    import ast
    import re
    from pytekt.bots.templates import get_template, generate_manual_setup

    templates_to_test = ["echo", "faq-support", "moderation", "ecommerce-payments"]

    for tid in templates_to_test:
        manifest = get_template(tid, platform="telegram")
        assert manifest is not None, f"Template {tid} should exist"

        guide = generate_manual_setup(manifest, project_name=f"Test_{tid}", platform="telegram")

        # Must include pip install and environment variables
        assert "pip install" in guide
        assert "```env" in guide

        # Extract all python fenced code blocks
        py_blocks = re.findall(r"```python\n(.*?)\n```", guide, re.DOTALL)
        assert len(py_blocks) > 0, f"Manual guide for {tid} should contain python code blocks"

        for idx, block in enumerate(py_blocks):
            code = block.strip()
            if not code:
                continue
            try:
                ast.parse(code)
            except SyntaxError as e:
                pytest.fail(f"SyntaxError in {tid} manual setup python block #{idx+1}:\n{code}\nError: {e}")


def test_cli_template_non_interactive_yes_flag():
    """Verify pytekt bots new <name> --platform telegram --template ai-chatbot --yes skips prompts."""
    from pytekt.cli import main
    temp_dir = Path(tempfile.mkdtemp())
    try:
        test_args = [
            "pytekt", "bots", "new", "ci_bot",
            "--platform", "telegram",
            "--template", "ai-chatbot",
            "--yes",
            "--no-animation",
            "--dir", str(temp_dir)
        ]
        with patch("sys.argv", test_args):
            main()

        created = temp_dir / "ci_bot"
        assert created.is_dir()
        assert (created / "bot" / "main.py").is_file()
        assert (created / "bot" / "ai" / "setup.py").is_file()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_cli_manual_flag_prints_setup():
    """Verify pytekt bots new <name> --manual outputs copy-paste guide."""
    from pytekt.cli import main
    buf = io.StringIO()
    test_args = [
        "pytekt", "bots", "new", "manual_guide_bot",
        "--platform", "telegram",
        "--template", "echo",
        "--manual",
        "--yes",
        "--no-animation",
    ]
    with patch("sys.argv", test_args), patch("sys.stdout", buf):
        main()

    output = buf.getvalue()
    assert "Manual Setup Guide: Echo / Starter (Telegram)" in output
    assert "pip install pytekt>=0.2.1" in output
    assert "main.py" in output
    assert "```python" in output





