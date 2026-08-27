"""
PyTekt Bot Templates System.
Declarative manifest-based templates providing ready-made starting points for bots.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# ==============================================================================
# 1. Template Manifest Dataclass
# ==============================================================================

@dataclass
class TemplateManifest:
    """
    Metadata and feature requirements for a PyTekt bot starter template.
    """
    id: str
    name: str
    description: str
    platforms: List[str] = field(default_factory=lambda: ["telegram", "discord"])
    with_ai: bool = False
    with_db: bool = False
    with_roles: bool = False
    with_i18n: bool = False
    with_scheduler: bool = False
    with_payments: bool = False
    with_ui: bool = False
    minimal: bool = False
    extra_env: Dict[str, str] = field(default_factory=dict)
    extra_deps: List[str] = field(default_factory=list)
    template_dir: Optional[Path] = None

    def is_compatible_with(self, platform: str) -> bool:
        """Check if template supports the given platform."""
        plat = platform.lower().strip()
        return plat in [p.lower().strip() for p in self.platforms]


# ==============================================================================
# 2. Manifest Parser
# ==============================================================================

def _fallback_yaml_parse(text: str) -> Dict[str, Any]:
    """
    Lightweight fallback parser for template.yaml if PyYAML is not installed.
    Supports scalars, lists, and simple nested dictionaries.
    """
    result: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_section: Optional[str] = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List item
        if stripped.startswith("- "):
            val = stripped[2:].strip().strip('"').strip("'")
            if current_key and isinstance(result.get(current_key), list):
                result[current_key].append(val)
            continue

        # Key-value or section header
        if ":" in stripped:
            key, raw_val = stripped.split(":", 1)
            key = key.strip()
            raw_val = raw_val.strip().strip('"').strip("'")

            # Check indentation for sub-dict
            indent = len(line) - len(line.lstrip())
            if indent > 0 and current_section:
                if not isinstance(result.get(current_section), dict):
                    result[current_section] = {}
                result[current_section][key] = raw_val
                continue

            if not raw_val:
                # Could be a list or dict section
                if key in ("platforms", "extra_deps", "dependencies"):
                    result[key] = []
                    current_key = key
                    current_section = None
                elif key in ("extra_env", "env"):
                    result[key] = {}
                    current_section = key
                    current_key = None
                else:
                    result[key] = None
                    current_key = key
                    current_section = None
            else:
                current_key = None
                current_section = None
                # Boolean & Number conversions
                low = raw_val.lower()
                if low in ("true", "yes", "on"):
                    result[key] = True
                elif low in ("false", "no", "off"):
                    result[key] = False
                elif raw_val.isdigit():
                    result[key] = int(raw_val)
                else:
                    result[key] = raw_val

    return result


def load_manifest(manifest_path_or_dir: Union[str, Path]) -> TemplateManifest:
    """
    Load and parse a template manifest from template.yaml or directory containing it.
    """
    p = Path(manifest_path_or_dir)
    if p.is_dir():
        file_path = p / "template.yaml"
        if not file_path.exists():
            file_path = p / "template.yml"
    else:
        file_path = p

    if not file_path.exists():
        raise FileNotFoundError(f"Template manifest not found at {file_path}")

    content = file_path.read_text(encoding="utf-8")
    if yaml is not None:
        try:
            data = yaml.safe_load(content) or {}
        except Exception:
            data = _fallback_yaml_parse(content)
    else:
        data = _fallback_yaml_parse(content)

    t_id = data.get("id") or file_path.parent.name
    name = data.get("name", t_id.replace("-", " ").title())
    description = data.get("description", "")
    platforms = data.get("platforms", ["telegram", "discord"])
    if isinstance(platforms, str):
        platforms = [p.strip() for p in platforms.split(",")]

    extra_env = dict(data.get("extra_env") or data.get("env") or {})
    extra_deps = list(data.get("extra_deps") or data.get("dependencies") or [])

    return TemplateManifest(
        id=t_id,
        name=name,
        description=description,
        platforms=platforms,
        with_ai=bool(data.get("with_ai", False)),
        with_db=bool(data.get("with_db", False)),
        with_roles=bool(data.get("with_roles", False)),
        with_i18n=bool(data.get("with_i18n", False)),
        with_scheduler=bool(data.get("with_scheduler", False)),
        with_payments=bool(data.get("with_payments", False)),
        with_ui=bool(data.get("with_ui", False)),
        minimal=bool(data.get("minimal", False)),
        extra_env=extra_env,
        extra_deps=extra_deps,
        template_dir=file_path.parent,
    )


# ==============================================================================
# 3. Template Discovery & Filtering
# ==============================================================================

TEMPLATES_DIR = Path(__file__).resolve().parent

DEFAULT_TEMPLATE_ORDER = [
    "echo",
    "ai-chatbot",
    "faq-support",
    "moderation",
    "reminder-scheduler",
    "ecommerce-payments",
]


def list_templates(platform: Optional[str] = None) -> List[TemplateManifest]:
    """
    List all available starter templates, optionally filtering by target platform.
    """
    manifests: Dict[str, TemplateManifest] = {}

    if TEMPLATES_DIR.is_dir():
        for entry in TEMPLATES_DIR.iterdir():
            if entry.is_dir() and ((entry / "template.yaml").exists() or (entry / "template.yml").exists()):
                try:
                    m = load_manifest(entry)
                    manifests[m.id] = m
                except Exception:
                    continue

    # Order templates according to standard catalog sequence, then any custom templates
    ordered: List[TemplateManifest] = []
    for tid in DEFAULT_TEMPLATE_ORDER:
        if tid in manifests:
            ordered.append(manifests.pop(tid))
    ordered.extend(manifests.values())

    if platform:
        plat = platform.lower().strip()
        return [m for m in ordered if m.is_compatible_with(plat)]
    return ordered


def get_template(template_id: str, platform: Optional[str] = None) -> Optional[TemplateManifest]:
    """
    Retrieve template manifest by ID, validating platform compatibility if platform given.
    """
    clean_id = template_id.strip().lower()
    for m in list_templates():
        if m.id.lower() == clean_id:
            if platform and not m.is_compatible_with(platform):
                return None
            return m
    return None


# ==============================================================================
# 4. Manual Setup Guide Generator
# ==============================================================================

def generate_manual_setup(
    manifest: Optional[TemplateManifest] = None,
    project_name: str = "my_bot",
    platform: str = "telegram",
    template: Optional[str] = None,
    with_ai: bool = False,
    with_db: bool = False,
    with_roles: bool = False,
    with_i18n: bool = False,
    with_scheduler: bool = False,
    with_payments: bool = False,
    with_ui: bool = False,
    minimal: bool = False,
) -> str:
    """
    Generate comprehensive copy-paste ready manual setup instructions with fenced
    code blocks for integrating the template or custom features into an existing project.
    """
    from pytekt.bots.scaffold import generate_project_files

    if manifest is not None:
        t_id = manifest.id
        t_name = manifest.name
        t_desc = manifest.description
        with_ai = manifest.with_ai or with_ai
        with_db = manifest.with_db or with_db
        with_roles = manifest.with_roles or with_roles
        with_i18n = manifest.with_i18n or with_i18n
        with_scheduler = manifest.with_scheduler or with_scheduler
        with_payments = manifest.with_payments or with_payments
        with_ui = manifest.with_ui or with_ui
        minimal = manifest.minimal or minimal
        extra_deps = list(manifest.extra_deps)
    else:
        t_id = template or "custom"
        t_name = "Custom Bot" if not template else template.capitalize()
        t_desc = "Custom configured bot with selected features"
        extra_deps = []

    files = generate_project_files(
        name=project_name,
        platform=platform,
        template=manifest.id if manifest else template,
        include_ai=with_ai,
        include_db=with_db,
        include_roles=with_roles,
        include_i18n=with_i18n,
        include_scheduler=with_scheduler,
        include_payments=with_payments,
        include_ui=with_ui,
        minimal=minimal,
    )

    plat_title = platform.capitalize()
    deps = ["pytekt>=0.2.1", "pytest>=8.0.0"]
    if with_ai or "openai>=1.0.0" in extra_deps:
        deps.append("openai>=1.0.0")
    for d in extra_deps:
        if d not in deps:
            deps.append(d)

    pip_cmd = f"pip install {' '.join(deps)}"
    env_content = files.get(".env.example", "TELEGRAM_BOT_TOKEN=your_token_here\n")
    run_cmd = "python main.py" if minimal else "python -m bot.main"

    doc_lines = [
        f"# Manual Setup Guide: {t_name} ({plat_title})",
        "",
        f"> **Template / Architecture:** `{t_id}` — {t_desc}",
        "> Follow these exact steps to integrate this template into your existing codebase or build it manually.",
        "",
        "## 1. Install Dependencies",
        "Run the following command to install required packages:",
        "```bash",
        pip_cmd,
        "```",
        "",
        "## 2. Configure Environment Variables",
        "Add the following keys to your `.env` file:",
        "```env",
        env_content.strip(),
        "```",
        "",
        "## 3. Files to Create",
        "",
    ]

    # Render each file in clean fenced code blocks
    file_order = sorted(files.keys(), key=lambda k: (
        0 if k in ("main.py", "bot/main.py") else
        1 if "config.py" in k else
        2 if "ai/" in k or "models/" in k or "roles/" in k or "scheduler/" in k or "payments/" in k else
        3 if "handlers/" in k else
        4 if k.endswith(".md") else
        5 if "tests/" in k else 6,
        k
    ))

    for rel_path in file_order:
        if rel_path in (".env.example", ".gitignore", "requirements.txt", "pyproject.toml", "README.md", "SECURITY.md"):
            continue

        content = files[rel_path]
        if rel_path.endswith(".py"):
            lang = "python"
        elif rel_path.endswith(".json"):
            lang = "json"
        elif rel_path.endswith(".md"):
            lang = "markdown"
        elif rel_path.endswith(".toml"):
            lang = "toml"
        else:
            lang = "text"

        doc_lines.extend([
            f"### 📄 `{rel_path}`",
            f"Create the file `{rel_path}` with the following content:",
            f"```{lang}",
            content.strip(),
            "```",
            "",
        ])

    doc_lines.extend([
        "## 4. Run & Verify",
        "Launch the bot:",
        "```bash",
        run_cmd,
        "```",
        "",
        "Run tests:",
        "```bash",
        "pytest tests/",
        "```",
        "",
        "> [!NOTE]",
        "> **Existing Project Integration**:",
        "> If you are adding this template to an already existing project, copy the relevant handler functions",
        "> from the files above into your existing bot dispatch module and ensure the required environment variables are set.",
    ])

    return "\n".join(doc_lines) + "\n"
