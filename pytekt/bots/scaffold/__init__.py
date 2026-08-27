"""
PyTekt Bots Scaffolding Engine.
Generates immediately runnable, professional, modular bot project skeletons
with separated handlers, typed settings, optional AI and DB models, and in-memory tests.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional


# ==============================================================================
# 1. Modular Professional Project Templates
# ==============================================================================

CONFIG_TEMPLATE = '''"""
Application Configuration & Settings.
Loads credentials and options from .env and environment variables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """Lightweight .env loader without external dependencies."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key, val = key.strip(), val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        os.environ.setdefault(key, val)


# Auto-load .env from project root
_env_file = Path(__file__).resolve().parent.parent / ".env"
_load_dotenv(_env_file)


@dataclass
class Settings:
    """Typed application settings."""
    project_name: str = "{project_name}"
    platform: str = "{platform}"
    bot_token: str = field(
        default_factory=lambda: os.environ.get("{token_env_var}", "{default_token}")
    )
    environment: str = field(
        default_factory=lambda: os.environ.get("ENV", "development")
    )
    debug: bool = field(
        default_factory=lambda: os.environ.get("DEBUG", "true").lower() in ("true", "1", "yes")
    ){extra_settings_fields}


def load_settings() -> Settings:
    """Load settings instance."""
    return Settings()
'''

HANDLERS_INIT_TEMPLATE = '''"""
Modular Handler Registry.
"""

from __future__ import annotations

from .commands import register_commands
from .messages import register_messages
from .callbacks import register_callbacks


def register_all_handlers(bot, settings, ai=None, db=None) -> None:
    """Register all modular handlers onto the given bot."""
    register_commands(bot, settings, ai=ai, db=db)
    register_messages(bot, settings, ai=ai, db=db)
    register_callbacks(bot, settings, ai=ai, db=db)
'''

HANDLERS_COMMANDS_TEMPLATE = '''"""
Command Handlers (@bot.on_command).
"""

from __future__ import annotations

from pytekt.bots import Context
from pytekt.bots.ui import Button, Card, Keyboard


def register_commands(bot, settings, ai=None, db=None) -> None:
    """Register all slash/prefix command handlers onto the bot."""

    @bot.on_command("start")
    async def handle_start(ctx: Context) -> None:
        user_name = ctx.metadata.get("first_name") or ctx.user_id or "there"
        kb = Keyboard([
            [Button("📚 Documentation", url="https://aqwelai.xyz"), Button("⚙️ Settings", callback_id="btn_settings")]
        ])
        card = Card(
            title=f"Welcome, {user_name}!",
            description="Your bot is running with high-performance C++ dispatch and modular handlers.",
            fields={
                "Platform": settings.platform.capitalize(),
                "Environment": settings.environment,
                "Status": "Active",
            },
            color="success",
            keyboard=kb,
        )
        await ctx.reply(ui=card)

    @bot.on_command("help")
    async def handle_help(ctx: Context) -> None:
        help_text = (
            "🤖 **{project_name} Commands:**\\n"
            "• `/start` — Welcome message and quick actions\\n"
            "• `/help` — Show available commands"
            "{extra_help_commands}"
        )
        await ctx.reply(help_text)
{extra_command_handlers}
'''

HANDLERS_MESSAGES_TEMPLATE = '''"""
Message Handlers (@bot.on_message).
"""

from __future__ import annotations

from pytekt.bots import Context


def register_messages(bot, settings, ai=None, db=None) -> None:
    """Register incoming message handlers."""

    @bot.on_message()
    async def handle_message(ctx: Context) -> None:
        # Optional persistence tracking if DB is configured
        if db is not None and ctx.user_id:
            try:
                users = db.collection("users")
                users.update(
                    {"user_id": ctx.user_id},
                    {"user_id": ctx.user_id, "last_seen": ctx.timestamp},
                    upsert=True,
                )
            except Exception:
                pass

        await ctx.reply(f"Echo: {ctx.text}")
'''

HANDLERS_CALLBACKS_TEMPLATE = '''"""
Callback Query / Button Handlers (@bot.on_button).
"""

from __future__ import annotations

from pytekt.bots import Context


def register_callbacks(bot, settings, ai=None, db=None) -> None:
    """Register inline keyboard button callback handlers."""

    @bot.on_button("btn_settings")
    async def handle_settings_button(ctx: Context) -> None:
        await ctx.reply("⚙️ Settings panel: All modules operating normally.")
'''

AI_INIT_TEMPLATE = '''"""
AI Assistant Module for {project_name}.
Provides LLM assistant initialization, custom tools, and conversational memory helpers.
"""

from __future__ import annotations

from .setup import setup_ai, ask_ai
from .tools import register_default_tools
from .prompts import SYSTEM_PROMPT, format_context_prompt

__all__ = [
    "setup_ai",
    "ask_ai",
    "register_default_tools",
    "SYSTEM_PROMPT",
    "format_context_prompt",
]
'''

AI_SETUP_TEMPLATE = '''"""
AI Layer Setup and Tool Registrations.
"""

from __future__ import annotations

import os
from typing import Any, Optional
from pytekt.bots.ai import AI
from .prompts import SYSTEM_PROMPT
from .tools import register_default_tools


def setup_ai(settings: Any = None) -> AI:
    """Initialize and configure the PyTekt bots.ai assistant with default tools."""
    if settings is not None and hasattr(settings, "openai_api_key"):
        api_key = settings.openai_api_key
    else:
        api_key = os.environ.get("OPENAI_API_KEY", "")
    ai = AI(
        system=SYSTEM_PROMPT,
        api_key=api_key or None,
        model="gpt-4o",
    )
    register_default_tools(ai)
    return ai


async def ask_ai(ai: AI, prompt: str, user_id: Optional[str] = None) -> str:
    """Query the AI assistant with conversational memory."""
    session = ai.session(user_id) if user_id else ai
    return await session.ask(prompt)
'''

AI_TOOLS_TEMPLATE = '''"""
Default AI Function Tools (@ai.tool).
Add custom business logic tools here for the AI assistant to call automatically.
"""

from __future__ import annotations

import datetime
import sys
from typing import Any, Dict


def register_default_tools(ai) -> None:
    """Register built-in productivity and utility tools onto the AI instance."""

    @ai.tool
    def get_server_status() -> str:
        """Return the current server and bot runtime health."""
        return f"All systems operational. C++ dispatch latency < 1ms (Python {sys.version.split()[0]})."

    @ai.tool
    def calculate_sum(a: float, b: float) -> float:
        """Add two numbers together."""
        return str(a + b)

    @ai.tool
    def get_current_time(timezone: str = "UTC") -> str:
        """Get the current server UTC datetime string."""
        now = datetime.datetime.now(datetime.timezone.utc)
        return now.strftime("%Y-%m-%d %H:%M:%S UTC")

    @ai.tool
    def format_bullet_points(items: str) -> str:
        """Format comma-separated text into clean Markdown bullet points."""
        parts = [p.strip() for p in items.split(",") if p.strip()]
        return "\\n".join(f"• {p}" for p in parts)
'''

AI_PROMPTS_TEMPLATE = '''"""
System Prompts and Prompt Templates for AI Assistant.
"""

SYSTEM_PROMPT = (
    "You are a smart, friendly, and concise bot assistant powered by PyTekt. "
    "Help the user answer questions and use available tools."
)


def format_context_prompt(user_name: str, topic: str) -> str:
    """Format contextual prompt with user identity."""
    return f"User {user_name} is asking: {topic}"
'''

MODELS_INIT_TEMPLATE = '''"""
Database Models & Persistence Layer using pytekt.db.
"""

from __future__ import annotations

import os
from typing import Any, Optional
from pytekt.db import connect
from .operations import (
    save_user,
    get_user,
    get_all_users,
    get_user_stats,
    log_event,
    get_user_state,
    set_user_state,
    get_setting,
    set_setting,
)
from .schemas import UserRecord, EventLog

__all__ = [
    "init_db",
    "save_user",
    "get_user",
    "get_all_users",
    "get_user_stats",
    "log_event",
    "get_user_state",
    "set_user_state",
    "get_setting",
    "set_setting",
    "UserRecord",
    "EventLog",
]


def init_db(settings: Any = None):
    """Initialize database connection and primary collections."""
    if settings is not None and hasattr(settings, "database_url"):
        db_url = settings.database_url
    else:
        db_url = os.environ.get("DATABASE_URL", "sqlite:///bot_data.db")
    conn = connect(db_url)
    # Ensure standard collections exist
    conn.collection("users")
    conn.collection("sessions")
    conn.collection("events")
    conn.collection("settings")
    return conn
'''

MODELS_OPERATIONS_TEMPLATE = '''"""
Database Operations and Helper Functions for Bot Data.
Provides ready-to-use CRUD helpers for users, sessions, events, and key-value settings.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def save_user(
    db,
    user_id: str,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Save or update user profile and interaction timestamp in DB."""
    users = db.collection("users")
    now = time.time()
    existing = users.find_one({"user_id": str(user_id)})
    if existing:
        msg_count = existing.get("msg_count", 0) + 1
        doc = {
            "user_id": str(user_id),
            "username": username or existing.get("username"),
            "first_name": first_name or existing.get("first_name"),
            "last_seen": now,
            "msg_count": msg_count,
        }
        users.update({"user_id": str(user_id)}, doc, upsert=True)
        return doc
    else:
        doc = {
            "user_id": str(user_id),
            "username": username,
            "first_name": first_name,
            "first_seen": now,
            "last_seen": now,
            "msg_count": 1,
        }
        users.insert(doc)
        return doc


def get_user(db, user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by ID."""
    return db.collection("users").find_one({"user_id": str(user_id)})


def get_all_users(db) -> List[Dict[str, Any]]:
    """Retrieve all registered users."""
    return list(db.collection("users").find())


def get_user_stats(db) -> Dict[str, Any]:
    """Return high-level persistence metrics."""
    users = list(db.collection("users").find())
    total_msgs = sum(u.get("msg_count", 0) for u in users)
    return {
        "total_users": len(users),
        "total_messages": total_msgs,
    }


def log_event(db, user_id: str, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """Log an audit/analytics event to the events collection."""
    events = db.collection("events")
    events.insert({
        "user_id": str(user_id),
        "event_type": event_type,
        "payload": payload or {},
        "timestamp": time.time(),
    })


def get_user_state(db, user_id: str) -> Dict[str, Any]:
    """Retrieve persistent user session or FSM state."""
    session = db.collection("sessions").find_one({"user_id": str(user_id)})
    return session.get("state", {}) if session else {}


def set_user_state(db, user_id: str, state_data: Dict[str, Any]) -> None:
    """Save persistent user session or FSM state."""
    db.collection("sessions").update(
        {"user_id": str(user_id)},
        {"user_id": str(user_id), "state": state_data, "updated_at": time.time()},
        upsert=True,
    )


def get_setting(db, key: str, default: Any = None) -> Any:
    """Get a key-value setting from the database."""
    doc = db.collection("settings").find_one({"key": str(key)})
    return doc.get("value", default) if doc else default


def set_setting(db, key: str, value: Any) -> None:
    """Set a key-value setting in the database."""
    db.collection("settings").update(
        {"key": str(key)},
        {"key": str(key), "value": value, "updated_at": time.time()},
        upsert=True,
    )
'''

MODELS_SCHEMAS_TEMPLATE = '''"""
Dataclass Schemas for Type-Safe Models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class UserRecord:
    """Representation of a registered bot user."""
    user_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    first_seen: float = 0.0
    last_seen: float = 0.0
    msg_count: int = 0


@dataclass
class EventLog:
    """Audit event log record."""
    user_id: str
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
'''

# ==============================================================================
# Roles & RBAC Templates
# ==============================================================================

ROLES_INIT_TEMPLATE = '''"""
Role-Based Access Control (RBAC) & Permissions.
"""

from __future__ import annotations

from .permissions import setup_roles, is_admin, grant_role, revoke_role, requires_role, admin_only
from .admin_commands import register_admin_commands

__all__ = [
    "setup_roles",
    "is_admin",
    "grant_role",
    "revoke_role",
    "requires_role",
    "admin_only",
    "register_admin_commands",
]
'''

ROLES_PERMISSIONS_TEMPLATE = '''"""
Permissions Registry and Role-Checking Utilities.
"""

from __future__ import annotations

import os
from typing import Optional, Set
from pytekt.bots.roles import requires_role, admin_only

_GLOBAL_ADMINS: Set[str] = set()


def setup_roles(bot, admin_ids: Optional[list[str]] = None) -> None:
    """Initialize role registry and seed admin IDs from environment."""
    env_admins = os.environ.get("ADMIN_USER_IDS", "")
    if env_admins:
        for aid in env_admins.split(","):
            aid = aid.strip()
            if aid:
                _GLOBAL_ADMINS.add(aid)
                bot.roles.set_admin(aid)

    if admin_ids:
        for aid in admin_ids:
            _GLOBAL_ADMINS.add(str(aid))
            bot.roles.set_admin(str(aid))


def is_admin(user_id: str) -> bool:
    """Check if user is a registered administrator."""
    return str(user_id) in _GLOBAL_ADMINS


def grant_role(bot, chat_id: str, user_id: str, role: str) -> None:
    """Grant a role to a user in a specific chat."""
    bot.roles.grant(str(chat_id), str(user_id), role)


def revoke_role(bot, chat_id: str, user_id: str, role: str) -> None:
    """Revoke a role from a user."""
    bot.roles.revoke(str(chat_id), str(user_id), role)
'''

ROLES_ADMIN_COMMANDS_TEMPLATE = '''"""
Administrative commands restricted by RBAC.
"""

from __future__ import annotations

from pytekt.bots import Context
from pytekt.bots.roles import admin_only


def register_admin_commands(bot) -> None:
    """Register administrative commands restricted to bot admins."""

    @bot.on_command("admin")
    @admin_only()
    async def handle_admin_panel(ctx: Context):
        await ctx.reply(
            "🛡️ **Admin Panel Access Granted**\\n"
            "• `/ban <user_id>` — Restrict user access\\n"
            "• `/unban <user_id>` — Lift user restrictions\\n"
            "• `/broadcast <msg>` — Send announcement to users"
        )

    @bot.on_command("ban")
    @admin_only()
    async def handle_ban(ctx: Context):
        if not ctx.args:
            await ctx.reply("Usage: `/ban <user_id>`")
            return
        target = ctx.args[0]
        bot.roles.grant(str(ctx.chat_id), target, "banned")
        await ctx.reply(f"🚫 User `{target}` has been restricted.")

    @bot.on_command("broadcast")
    @admin_only()
    async def handle_broadcast(ctx: Context):
        msg = " ".join(ctx.args)
        if not msg:
            await ctx.reply("Usage: `/broadcast <message>`")
            return
        await ctx.reply(f"📢 **Announcement Broadcast:** {msg}")
'''

# ==============================================================================
# i18n Multi-Language Templates
# ==============================================================================

I18N_INIT_TEMPLATE = '''"""
Internationalization (i18n) Multi-Language Module.
"""

from __future__ import annotations

from .translator import (
    setup_i18n,
    get_text,
    set_user_language,
    get_user_language,
    get_language_keyboard,
    register_i18n_handlers,
)

__all__ = [
    "setup_i18n",
    "get_text",
    "set_user_language",
    "get_user_language",
    "get_language_keyboard",
    "register_i18n_handlers",
]
'''

I18N_TRANSLATOR_TEMPLATE = '''"""
i18n Manager Setup and Translation Helpers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from pytekt.bots.i18n import I18nManager
from pytekt.bots.ui import Keyboard, Button

_user_langs: Dict[str, str] = {}
_i18n_instance: I18nManager = I18nManager(default_lang="en")


def setup_i18n(bot=None, locales_dir: Path | None = None) -> I18nManager:
    """Initialize i18n manager and load JSON translation files."""
    d = locales_dir or Path(__file__).parent
    _i18n_instance.load_directory(d)
    return _i18n_instance


def get_text(key: str, user_id: str | None = None, **kwargs: Any) -> str:
    """Lookup translated text in user preferred language."""
    lang = _user_langs.get(str(user_id), "en") if user_id else "en"
    return _i18n_instance.translate(key, lang=lang, **kwargs)


def set_user_language(user_id: str, lang: str) -> None:
    """Set preferred language for user."""
    _user_langs[str(user_id)] = lang.lower().strip()


def get_user_language(user_id: str) -> str:
    """Get preferred language for user."""
    return _user_langs.get(str(user_id), "en")


def get_language_keyboard() -> Keyboard:
    """Inline keyboard for switching languages."""
    return Keyboard([
        [
            Button("🇬🇧 English", callback_data="lang_en"),
            Button("🇷🇺 Русский", callback_data="lang_ru"),
            Button("🇪🇸 Español", callback_data="lang_es"),
        ]
    ])


def register_i18n_handlers(bot) -> None:
    """Register /lang command and language selection button callbacks."""
    from pytekt.bots import Context

    @bot.on_command("lang")
    async def handle_lang_cmd(ctx: Context):
        kb = get_language_keyboard()
        await ctx.reply(get_text("choose_lang", user_id=ctx.user_id), keyboard=kb)

    @bot.on_button(r"^lang_(en|ru|es)$")
    async def handle_lang_button(ctx: Context):
        code = ctx.data.split("_")[1]
        if ctx.user_id:
            set_user_language(ctx.user_id, code)
        await ctx.reply(get_text("lang_changed", user_id=ctx.user_id))
'''

LOCALE_EN_JSON = '''{
  "welcome": "Welcome, {name}! 🚀",
  "help": "Available commands:\\n• /start — Welcome\\n• /help — Help info\\n• /lang — Change language",
  "choose_lang": "🌐 Please choose your preferred language:",
  "lang_changed": "✅ Language changed to English 🇬🇧!"
}
'''

LOCALE_RU_JSON = '''{
  "welcome": "Добро пожаловать, {name}! 🚀",
  "help": "Доступные команды:\\n• /start — Приветствие\\n• /help — Справка\\n• /lang — Выбрать язык",
  "choose_lang": "🌐 Пожалуйста, выберите язык:",
  "lang_changed": "✅ Язык успешно изменен на Русский 🇷🇺!"
}
'''

LOCALE_ES_JSON = '''{
  "welcome": "¡Bienvenido/a, {name}! 🚀",
  "help": "Comandos disponibles:\\n• /start — Bienvenida\\n• /help — Ayuda\\n• /lang — Cambiar idioma",
  "choose_lang": "🌐 Por favor selecciona tu idioma:",
  "lang_changed": "✅ ¡Idioma cambiado a Español 🇪🇸!"
}
'''

# ==============================================================================
# Background Scheduler Templates
# ==============================================================================

SCHEDULER_INIT_TEMPLATE = '''"""
Background Cron & Task Scheduler.
"""

from __future__ import annotations

from .jobs import setup_scheduler, register_default_jobs

__all__ = ["setup_scheduler", "register_default_jobs"]
'''

SCHEDULER_JOBS_TEMPLATE = '''"""
Background recurring cron and interval jobs.
"""

from __future__ import annotations

import logging
from pytekt.bots.scheduler import Scheduler

logger = logging.getLogger("bot.scheduler")


def health_check_job(bot) -> None:
    """Periodic health-check task running every 5 minutes."""
    logger.info("💓 [Scheduler] Bot health check: event loop healthy, bot active.")


def daily_digest_job(bot) -> None:
    """Daily digest broadcast scheduled via cron (e.g. 09:00 AM)."""
    logger.info("📰 [Scheduler] Daily maintenance and stats digest trigger.")


def register_default_jobs(scheduler: Scheduler) -> None:
    """Attach standard background tasks to the scheduler."""
    scheduler.add_interval_job("5m", health_check_job)
    scheduler.add_cron_job("0 9 * * *", daily_digest_job)


def setup_scheduler(bot) -> Scheduler:
    """Initialize and start background task scheduler."""
    sched = Scheduler(bot)
    register_default_jobs(sched)
    sched.start()
    return sched
'''

# ==============================================================================
# Payments & Subscriptions Templates
# ==============================================================================

PAYMENTS_INIT_TEMPLATE = '''"""
Payments & Subscriptions Layer.
"""

from __future__ import annotations

from .invoices import create_stars_invoice, create_crypto_invoice, get_pricing_plans
from .checkout import register_payment_handlers

__all__ = [
    "create_stars_invoice",
    "create_crypto_invoice",
    "get_pricing_plans",
    "register_payment_handlers",
]
'''

PAYMENTS_INVOICES_TEMPLATE = '''"""
Invoice Generation and Plan Catalogs.
"""

from __future__ import annotations

from typing import Any, Dict

VIP_PLANS = {
    "pro_monthly": {"title": "Pro Tier (Monthly)", "price_stars": 250, "price_usd": 4.99},
    "vip_yearly": {"title": "VIP Club (Yearly)", "price_stars": 1500, "price_usd": 29.99},
}


def get_pricing_plans() -> Dict[str, Any]:
    """Return available subscription and purchase plans."""
    return VIP_PLANS


def create_stars_invoice(plan_id: str) -> Dict[str, Any]:
    """Create Telegram Stars invoice payload."""
    plan = VIP_PLANS.get(plan_id, VIP_PLANS["pro_monthly"])
    return {
        "title": plan["title"],
        "description": f"Access to {plan['title']} features",
        "currency": "XTR",
        "prices": [{"label": plan["title"], "amount": plan["price_stars"]}],
        "payload": f"order_{plan_id}",
    }


def create_crypto_invoice(plan_id: str, currency: str = "USDT") -> Dict[str, Any]:
    """Generate crypto invoice payload."""
    plan = VIP_PLANS.get(plan_id, VIP_PLANS["pro_monthly"])
    return {
        "plan": plan_id,
        "amount": plan["price_usd"],
        "currency": currency,
        "status": "pending",
    }
'''

PAYMENTS_CHECKOUT_TEMPLATE = '''"""
Payment flow handlers (invoices, verification, subscriptions).
"""

from __future__ import annotations

from pytekt.bots import Context
from pytekt.bots.ui import Keyboard, Button, Card
from .invoices import get_pricing_plans


def register_payment_handlers(bot) -> None:
    """Register payment commands and checkout flow."""

    @bot.on_command("plans")
    @bot.on_command("buy")
    async def handle_plans(ctx: Context):
        plans = get_pricing_plans()
        kb = Keyboard([
            [Button(f"💎 {p['title']} ({p['price_stars']} ⭐)", callback_data=f"buy_{k}")]
            for k, p in plans.items()
        ])
        card = Card(
            title="Premium Membership Plans",
            color="warning",
            keyboard=kb,
        )
        await ctx.reply("Choose a subscription plan to upgrade your account:", ui=card)

    @bot.on_button(r"^buy_(pro_monthly|vip_yearly)$")
    async def handle_buy_button(ctx: Context):
        plan_id = ctx.data.replace("buy_", "")
        await ctx.reply(f"💳 Initializing checkout for `{plan_id}`. Confirm payment in chat.")
'''

# ==============================================================================
# Interactive UI Components Templates
# ==============================================================================

UI_INIT_TEMPLATE = '''"""
Rich Interactive UI Components Module.
"""

from __future__ import annotations

from .pagination import Paginator
from .survey_wizard import create_feedback_survey
from .confirmation import create_confirmation_dialog

__all__ = [
    "Paginator",
    "create_feedback_survey",
    "create_confirmation_dialog",
]
'''

UI_PAGINATION_TEMPLATE = '''"""
Interactive paginated item catalog with Previous/Next buttons.
"""

from __future__ import annotations

from typing import Any, List
from pytekt.bots.ui import Keyboard, Button, Card


class Paginator:
    """Paginated list renderer."""

    def __init__(self, items: List[Any], page_size: int = 5) -> None:
        self.items = items
        self.page_size = page_size

    @property
    def total_pages(self) -> int:
        return max(1, (len(self.items) + self.page_size - 1) // self.page_size)

    def get_page_items(self, page: int) -> List[Any]:
        p = max(0, min(page, self.total_pages - 1))
        start = p * self.page_size
        return self.items[start : start + self.page_size]

    def render(self, page: int = 0, title: str = "Item Catalog") -> Card:
        items = self.get_page_items(page)
        lines = [f"{i+1}. {it}" for i, it in enumerate(items)]
        body = "\\n".join(lines) if lines else "No items available."

        buttons = []
        if page > 0:
            buttons.append(Button("◀️ Prev", callback_data=f"page_{page-1}"))
        buttons.append(Button(f"📄 {page+1}/{self.total_pages}", callback_data="page_noop"))
        if page < self.total_pages - 1:
            buttons.append(Button("Next ▶️", callback_data=f"page_{page+1}"))

        kb = Keyboard([buttons])
        return Card(title=f"{title} (Page {page+1}/{self.total_pages})", color="primary", keyboard=kb)
'''

UI_SURVEY_TEMPLATE = '''"""
Multi-step guided questionnaire / survey wizard.
"""

from __future__ import annotations

from pytekt.bots.ui import Wizard, WizardStep


def create_feedback_survey() -> Wizard:
    """Create interactive multi-step feedback questionnaire."""
    steps = [
        WizardStep("rating", "Step 1/3: How would you rate your experience? (1-5 ⭐)"),
        WizardStep("feature", "Step 2/3: What feature would you like to see next?"),
        WizardStep("comments", "Step 3/3: Any additional thoughts or comments?"),
    ]
    return Wizard(steps=steps)
'''

UI_CONFIRMATION_TEMPLATE = '''"""
Interactive binary confirmation dialogs.
"""

from __future__ import annotations

from pytekt.bots.ui import Keyboard, Button, Card


def create_confirmation_dialog(action_name: str, payload: str = "") -> Card:
    """Build a standard Yes/Cancel confirmation card."""
    kb = Keyboard([
        [
            Button("✅ Confirm", callback_data=f"confirm_{payload}"),
            Button("❌ Cancel", callback_data="cancel_action"),
        ]
    ])
    return Card(
        title=f"Confirm Action: {action_name}",
        color="danger",
        keyboard=kb,
    )
'''

MIDDLEWARES_INIT_TEMPLATE = '''"""
Bot Middlewares (rate limiting, metrics, logging, auth).
"""

from __future__ import annotations

import logging
import time
from pytekt.bots import Context

logger = logging.getLogger("bot.middleware")


def setup_middlewares(bot, settings) -> None:
    """Register global middleware pipeline hooks."""

    @bot.use
    async def logging_middleware(ctx: Context, next_handler):
        start = time.perf_counter()
        try:
            return await next_handler()
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            if settings.debug:
                logger.debug("[%s] Event %s processed in %.2fms", settings.platform, ctx.event_type, elapsed_ms)
'''

UTILS_INIT_TEMPLATE = '''"""
Utility Helpers and Common Functions.
"""

from __future__ import annotations


def truncate_string(text: str, max_len: int = 100) -> str:
    """Safely truncate text for chat messages."""
    return text if len(text) <= max_len else text[: max_len - 3] + "..."
'''

MAIN_MODULAR_TEMPLATE = '''"""
{project_name} — Entry Point
Generated by pytekt bots new
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is in sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from bot.config import load_settings
from pytekt.bots import {bot_class}
from bot.handlers import register_all_handlers
from bot.middlewares import setup_middlewares
{ai_import}
{db_import}

settings = load_settings()

# Initialize bot instance with typed configuration
bot = {bot_class}(token=settings.bot_token)

# Setup middlewares
setup_middlewares(bot, settings)

# Initialize optional layers
{ai_init}
{db_init}

# Register all modular handlers
register_all_handlers(bot, settings{ai_arg}{db_arg})


def main() -> None:
    """Start the bot."""
    print(f"🚀 Starting {settings.project_name} on {settings.platform.capitalize()}...")
    bot.run()


if __name__ == "__main__":
    main()
'''

TEST_HANDLERS_TEMPLATE = '''"""
Unit tests for {project_name} using bot.test_client().
Runs completely in-memory with zero network or external token dependencies.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
import pytest

# Ensure project root is in sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from bot.main import bot


def test_start_command():
    """Verify /start command handler returns welcome card with user's name and buttons."""
    async def _run():
        client = bot.test_client()
        responses = await client.send_command("start", user_id="user_123", metadata={"first_name": "Alice"})
        assert len(responses) >= 1
        resp = responses[0]
        assert resp.has_text("Alice")
        assert resp.has_button("Documentation")

    asyncio.run(_run())


def test_help_command():
    """Verify /help command lists available commands."""
    async def _run():
        client = bot.test_client()
        responses = await client.send_command("help", user_id="user_123")
        assert len(responses) >= 1
        assert responses[0].has_text("/start")
        assert responses[0].has_text("/help")

    asyncio.run(_run())


def test_echo_message():
    """Verify regular messages receive replies."""
    async def _run():
        client = bot.test_client()
        responses = await client.send_message("Hello from PyTekt test!", user_id="user_123")
        assert len(responses) >= 1
        text = responses[0].text
        assert "Hello from PyTekt test!" in text or "Echo" in text or "Support" in text or len(text) > 0

    asyncio.run(_run())


def test_settings_button_callback():
    """Verify settings button callback returns confirmation reply."""
    async def _run():
        client = bot.test_client()
        responses = await client.send_button("btn_settings", user_id="user_123")
        assert len(responses) >= 1
        assert responses[0].has_text("Settings panel")

    asyncio.run(_run())
'''

GITIGNORE_TEMPLATE = """# Environment & Secrets
.env
.env.local
*.env

# Python Bytecode & Cache
__pycache__/
*.py[cod]
*$py.class
*.so

# Testing & Coverage
.pytest_cache/
.coverage
htmlcov/

# Databases
*.db
*.sqlite3

# Packaging
dist/
build/
*.egg-info/
"""

SECURITY_TEMPLATE = """# Security Policy for {project_name}

## Handling Bot Tokens & Secrets
- **Never commit `.env` or hardcoded tokens** into version control.
- All credentials are read via `bot/config.py` from environment variables or a local `.env` file.
- The `.gitignore` file automatically excludes `.env` files.

## Reporting Vulnerabilities
If you discover a security issue or vulnerability, please report it privately to the maintainers.
"""


# ==============================================================================
# 2. Minimal Single-File Templates (--minimal fallback)
# ==============================================================================

MINIMAL_BOT_TEMPLATE = '''"""
{project_name} — PyTekt {platform_title} Bot
Generated by pytekt bots new --minimal
"""

from __future__ import annotations

import os
from pytekt.bots import {bot_class}, Context
from pytekt.bots.ui import Keyboard, Button, Card
{ai_import}
{db_import}

bot = {bot_class}(token=os.environ.get("{token_env_var}", "{default_token}"))
{ai_init}
{db_init}


@bot.on_command("start")
async def handle_start(ctx: Context):
    name = ctx.metadata.get("first_name", "there")
    kb = Keyboard([[Button("📚 Docs", url="https://aqwelai.xyz")]])
    card = Card(title=f"Welcome, " + name + "!", color="success", keyboard=kb)
    await ctx.reply(ui=card)


@bot.on_command("help")
async def handle_help(ctx: Context):
    help_text = (
        "🤖 **{project_name} Commands:**\\n"
        "• `/start` — Welcome message and docs\\n"
        "• `/help` — Show available commands"
        "{extra_help_commands}"
    )
    await ctx.reply(help_text)
{extra_commands}

@bot.on_message()
async def handle_echo(ctx: Context):
{extra_message_tracking}
    await ctx.reply(f"Echo: {ctx.text}")


if __name__ == "__main__":
    print("🚀 Starting {project_name} on {platform_title}...")
    bot.run()
'''

MINIMAL_TELEGRAM_TEMPLATE = MINIMAL_BOT_TEMPLATE
MINIMAL_DISCORD_TEMPLATE = MINIMAL_BOT_TEMPLATE

MINIMAL_TEST_TEMPLATE = '''"""
Unit tests for {project_name} using bot.test_client().
"""

import asyncio
import pytest
from main import bot

def test_start_command():
    async def _run():
        client = bot.test_client()
        responses = await client.send_command("start", user_id="user_123", metadata={"first_name": "Alice"})
        assert len(responses) >= 1
        assert responses[0].has_text("Alice")

    asyncio.run(_run())

def test_echo_message():
    async def _run():
        client = bot.test_client()
        responses = await client.send_message("Hello PyTekt!")
        assert len(responses) >= 1
        assert "Hello PyTekt!" in responses[0].text

    asyncio.run(_run())
'''


# ==============================================================================
# 3. Dynamic README Generator
# ==============================================================================

def generate_readme_content(
    project_name: str,
    platform: str,
    with_ai: bool = False,
    with_db: bool = False,
    with_roles: bool = False,
    with_i18n: bool = False,
    with_scheduler: bool = False,
    with_payments: bool = False,
    with_ui: bool = False,
    minimal: bool = False,
) -> str:
    """Generate professional, dynamically tailored README.md."""
    plat_title = platform.capitalize()

    if minimal:
        layout_section = """```text
.
├── main.py              # Bot implementation & registered handlers
├── tests/
│   └── test_bot.py      # In-memory test client test suite
├── .env.example         # Environment credentials template
├── .gitignore
├── pyproject.toml
├── README.md
└── SECURITY.md
```"""
        run_cmd = "python main.py"
    else:
        tree_lines = [
            f"{project_name}/",
            "├── bot/",
            "│   ├── __init__.py",
            "│   ├── main.py              # Entry point: initializes bot & handlers",
            "│   ├── config.py            # Typed settings loaded from .env",
            "│   ├── handlers/            # Modular dispatch handlers",
            "│   │   ├── __init__.py",
            "│   │   ├── commands.py       # @bot.on_command handlers",
            "│   │   ├── messages.py       # @bot.on_message handlers",
            "│   │   └── callbacks.py      # @bot.on_button query handlers",
        ]
        if with_ai:
            tree_lines.extend([
                "│   ├── ai/                  # AI assistant, default tools & prompts",
                "│   │   ├── __init__.py",
                "│   │   ├── setup.py         # AI assistant initialization & ask_ai helper",
                "│   │   ├── tools.py         # Custom @ai.tool function definitions",
                "│   │   └── prompts.py       # System instructions & prompt templates",
            ])
        tree_lines.extend([
            "│   ├── middlewares/         # Pipeline hooks (logging, rate-limits)",
            "│   │   └── __init__.py",
        ])
        if with_db:
            tree_lines.extend([
                "│   ├── models/              # pytekt.db persistence & operations",
                "│   │   ├── __init__.py",
                "│   │   ├── operations.py    # CRUD helpers for users, sessions & events",
                "│   │   └── schemas.py       # Type-safe dataclass schemas",
            ])
        if with_roles:
            tree_lines.extend([
                "│   ├── roles/               # Role-based access control & permissions",
                "│   │   ├── __init__.py",
                "│   │   ├── permissions.py   # @admin_only & role registry",
                "│   │   └── admin_commands.py# /admin, /ban & broadcast handlers",
            ])
        if with_i18n:
            tree_lines.extend([
                "│   ├── locales/             # Multi-language translations & /lang",
                "│   │   ├── __init__.py",
                "│   │   ├── translator.py    # i18n lookup & language switcher",
                "│   │   ├── en.json          # English locale strings",
                "│   │   ├── ru.json          # Russian locale strings",
                "│   │   └── es.json          # Spanish locale strings",
            ])
        if with_scheduler:
            tree_lines.extend([
                "│   ├── scheduler/           # Background recurring cron & interval jobs",
                "│   │   ├── __init__.py",
                "│   │   └── jobs.py          # Scheduled periodic tasks",
            ])
        if with_payments:
            tree_lines.extend([
                "│   ├── payments/            # Telegram Stars & Crypto invoices",
                "│   │   ├── __init__.py",
                "│   │   ├── invoices.py      # Plan catalog & invoice generator",
                "│   │   └── checkout.py      # Payment confirmation handlers",
            ])
        if with_ui:
            tree_lines.extend([
                "│   ├── ui_components/       # Declarative UI helpers",
                "│   │   ├── __init__.py",
                "│   │   ├── pagination.py    # Paginated item catalog",
                "│   │   ├── survey_wizard.py # Multi-step form wizards",
                "│   │   └── confirmation.py  # Confirmation dialogs",
            ])
        tree_lines.extend([
            "│   └── utils/",
            "│       └── __init__.py",
            "├── tests/",
            "│   ├── __init__.py",
            "│   └── test_handlers.py     # In-memory pytest test suite",
            "├── .env.example",
            "├── .gitignore",
            "├── pyproject.toml",
            "├── README.md",
            "└── SECURITY.md",
        ])
        layout_section = "```text\n" + "\n".join(tree_lines) + "\n```"
        run_cmd = "python -m bot.main"

    features = [f"- **C++ Event Dispatch**: High-throughput native event processing on {plat_title}"]
    if with_ai:
        features.append("- **AI Layer**: Conversational LLM assistant with `@ai.tool` function calling")
    if with_db:
        features.append("- **Persistence**: Embedded database collections powered by `pytekt.db`")
    if with_roles:
        features.append("- **Role-Based Access (RBAC)**: Protected admin commands (`/admin`, `/ban`, `/broadcast`)")
    if with_i18n:
        features.append("- **Multi-Language (i18n)**: Instant locale translation with `/lang` switcher")
    if with_scheduler:
        features.append("- **Scheduler**: In-process cron and interval recurring background tasks")
    if with_payments:
        features.append("- **Payments**: Telegram Stars & digital checkout (`/plans`, `/buy`)")
    if with_ui:
        features.append("- **Interactive UI**: Paginated catalogs, survey wizards & confirmation modals")
    features.append("- **In-Memory Testing**: Complete test coverage using `bot.test_client()` without network tokens")

    features_block = "\n".join(features)

    return f"""# {project_name}

High-performance {plat_title} Bot built with [PyTekt](https://github.com/Aqwel-AI/pytekt).

## Features
{features_block}

## Project Structure
{layout_section}

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Credentials
```bash
cp .env.example .env
# Edit .env and supply your bot token
```

### 3. Run Bot
```bash
{run_cmd}
# Or with hot-reload in development:
# pytekt bots dev {'main.py' if minimal else 'bot/main.py'}
```

### 4. Run Test Suite
```bash
pytest tests/
```
"""


# ==============================================================================
# 4. Project Scaffolding Engine
# ==============================================================================

# ==============================================================================
# 4. Project Scaffolding Engine
# ==============================================================================

def generate_project_files(
    name: str,
    platform: str = "telegram",
    template: Optional[str] = None,
    include_ai: bool = False,
    include_db: bool = False,
    include_roles: bool = False,
    include_i18n: bool = False,
    include_scheduler: bool = False,
    include_payments: bool = False,
    include_ui: bool = False,
    minimal: bool = False,
) -> Dict[str, str]:
    """
    Generate the complete dictionary of relative file paths to file contents
    for a PyTekt bot project or starter template.
    """
    from pytekt.bots.templates import get_template

    plat = platform.lower().strip()
    if plat not in ("telegram", "discord"):
        plat = "telegram"

    clean_name = name.strip()
    slug = clean_name.lower().replace(" ", "_").replace("-", "_")

    manifest = get_template(template, platform=plat) if template else None
    if manifest:
        include_ai = manifest.with_ai if not include_ai else True
        include_db = manifest.with_db if not include_db else True
        include_roles = manifest.with_roles if not include_roles else True
        include_i18n = manifest.with_i18n if not include_i18n else True
        include_scheduler = manifest.with_scheduler if not include_scheduler else True
        include_payments = manifest.with_payments if not include_payments else True
        include_ui = manifest.with_ui if not include_ui else True
        if manifest.minimal:
            minimal = True

    token_var = "TELEGRAM_BOT_TOKEN" if plat == "telegram" else "DISCORD_BOT_TOKEN"
    default_token = "123456:TEST_TOKEN" if plat == "telegram" else "MOCK_DISCORD_TEST_TOKEN"
    bot_class = "TelegramBot" if plat == "telegram" else "DiscordBot"

    files: Dict[str, str] = {}

    # 1. Environment template
    env_lines = [
        f"# {clean_name} Credentials",
        f"{token_var}={default_token}",
        "ENV=development",
        "DEBUG=true",
    ]
    if include_ai:
        env_lines.append("OPENAI_API_KEY=sk-example-key-for-ai")
    if include_db:
        env_lines.append("DATABASE_URL=sqlite:///bot_data.db")
    if include_roles:
        env_lines.append("ADMIN_USER_IDS=123456789,user_admin")
    if manifest and manifest.extra_env:
        for k, v in manifest.extra_env.items():
            line = f"{k}={v}"
            if not any(l.startswith(f"{k}=") for l in env_lines):
                env_lines.append(line)

    files[".env.example"] = "\n".join(env_lines) + "\n"

    # 2. .gitignore & SECURITY.md
    files[".gitignore"] = GITIGNORE_TEMPLATE
    files["SECURITY.md"] = SECURITY_TEMPLATE.replace("{project_name}", clean_name)

    # 3. requirements.txt & pyproject.toml
    reqs = ["pytekt>=0.2.1", "pytest>=8.0.0"]
    if include_ai:
        reqs.append("openai>=1.0.0")
    if manifest and manifest.extra_deps:
        for d in manifest.extra_deps:
            if d not in reqs:
                reqs.append(d)

    files["requirements.txt"] = "\n".join(reqs) + "\n"

    pyproject_deps = ',\n'.join(f'    "{r}"' for r in reqs)
    files["pyproject.toml"] = f"""[project]
name = "{slug}"
version = "0.1.0"
description = "High-performance PyTekt Bot"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
{pyproject_deps}
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
"""

    # 4. README.md
    files["README.md"] = generate_readme_content(
        clean_name,
        platform=plat,
        with_ai=include_ai,
        with_db=include_db,
        with_roles=include_roles,
        with_i18n=include_i18n,
        with_scheduler=include_scheduler,
        with_payments=include_payments,
        with_ui=include_ui,
        minimal=minimal,
    )

    # ==========================================================================
    # Branch A: Minimal Single-File Layout
    # ==========================================================================
    if minimal:
        # Echo template special case: clean starter with echo and ping
        if template == "echo":
            files["main.py"] = f'''"""
{clean_name} - Echo / Starter Bot.
High-performance event-driven bot built with PyTekt.
"""

import os
from pytekt.bots import {bot_class}, Context

bot = {bot_class}(token=os.environ.get("{token_var}", "{default_token}"))


@bot.on_command("start")
async def handle_start(ctx: Context):
    """Welcome command handler."""
    user = ctx.metadata.get("first_name") or ctx.user_id or "User"
    await ctx.reply(f"👋 Hello {{user}}! Welcome to {clean_name}. Send me any text to echo it back, or type /ping.")


@bot.on_command("ping")
async def handle_ping(ctx: Context):
    """Health check ping command."""
    await ctx.reply("🏓 Pong! Native event loop is active.")


@bot.on_message()
async def handle_echo(ctx: Context):
    """Echo incoming messages."""
    if ctx.text and not ctx.text.startswith("/"):
        await ctx.reply(f"🔊 Echo: {{ctx.text}}")


if __name__ == "__main__":
    bot.run()
'''
            files["tests/__init__.py"] = ""
            files["tests/test_bot.py"] = f'''"""
Unit tests for {clean_name} echo bot using bot.test_client().
"""

import asyncio
import pytest
from main import bot


def test_start():
    async def _run():
        client = bot.test_client()
        responses = await client.send_command("start")
        assert len(responses) >= 1
        assert "Welcome" in responses[0].text

    asyncio.run(_run())


def test_ping():
    async def _run():
        client = bot.test_client()
        responses = await client.send_command("ping")
        assert len(responses) >= 1
        assert "Pong" in responses[0].text

    asyncio.run(_run())


def test_echo():
    async def _run():
        client = bot.test_client()
        responses = await client.send_message("Hello PyTekt!")
        assert len(responses) >= 1
        assert "Echo: Hello PyTekt!" in responses[0].text

    asyncio.run(_run())
'''
            return files

        # Feature directories in minimal layout
        if include_ai:
            files["ai/__init__.py"] = AI_INIT_TEMPLATE.replace("{project_name}", clean_name)
            files["ai/setup.py"] = AI_SETUP_TEMPLATE
            files["ai/tools.py"] = AI_TOOLS_TEMPLATE
            files["ai/prompts.py"] = AI_PROMPTS_TEMPLATE

        if include_db:
            files["db/__init__.py"] = MODELS_INIT_TEMPLATE
            files["db/operations.py"] = MODELS_OPERATIONS_TEMPLATE
            files["db/schemas.py"] = MODELS_SCHEMAS_TEMPLATE

        if include_roles:
            files["roles/__init__.py"] = ROLES_INIT_TEMPLATE
            files["roles/permissions.py"] = ROLES_PERMISSIONS_TEMPLATE
            files["roles/admin_commands.py"] = ROLES_ADMIN_COMMANDS_TEMPLATE

        if include_i18n:
            files["locales/__init__.py"] = I18N_INIT_TEMPLATE
            files["locales/translator.py"] = I18N_TRANSLATOR_TEMPLATE
            files["locales/en.json"] = LOCALE_EN_JSON
            files["locales/ru.json"] = LOCALE_RU_JSON
            files["locales/es.json"] = LOCALE_ES_JSON

        if include_scheduler:
            files["scheduler/__init__.py"] = SCHEDULER_INIT_TEMPLATE
            files["scheduler/jobs.py"] = SCHEDULER_JOBS_TEMPLATE

        if include_payments:
            files["payments/__init__.py"] = PAYMENTS_INIT_TEMPLATE
            files["payments/invoices.py"] = PAYMENTS_INVOICES_TEMPLATE
            files["payments/checkout.py"] = PAYMENTS_CHECKOUT_TEMPLATE

        if include_ui:
            files["ui_components/__init__.py"] = UI_INIT_TEMPLATE
            files["ui_components/pagination.py"] = UI_PAGINATION_TEMPLATE
            files["ui_components/survey_wizard.py"] = UI_SURVEY_TEMPLATE
            files["ui_components/confirmation.py"] = UI_CONFIRMATION_TEMPLATE

        imports = []
        inits = []
        extra_help = ""
        extra_cmds = []

        if include_ai:
            imports.append("from ai import setup_ai, ask_ai")
            inits.append("ai = setup_ai()")
            extra_help += "\\n• `/ask <query>` — Ask built-in AI assistant"
            extra_cmds.append("""
@bot.on_command("ask")
async def handle_ask(ctx: Context):
    query = " ".join(ctx.args) if ctx.args else "Introduce yourself briefly."
    await ctx.reply_ai(ai, prompt=query)
""")

        if include_db:
            imports.append("from db import init_db, save_user, get_user_stats")
            inits.append("db = init_db()")
            extra_help += "\\n• `/stats` — View bot persistence stats"
            extra_cmds.append("""
@bot.on_command("stats")
async def handle_stats(ctx: Context):
    stats = get_user_stats(db)
    await ctx.reply(f"📊 Persistent Storage: {stats['total_users']} users registered, {stats['total_messages']} messages.")
""")

        if include_roles:
            imports.append("from roles import setup_roles, register_admin_commands")
            inits.append("setup_roles(bot)\nregister_admin_commands(bot)")
            extra_help += "\\n• `/admin` — Access admin controls"

        if include_i18n:
            imports.append("from locales import setup_i18n, register_i18n_handlers")
            inits.append("setup_i18n(bot)\nregister_i18n_handlers(bot)")
            extra_help += "\\n• `/lang` — Switch language"

        if include_scheduler:
            imports.append("from scheduler import setup_scheduler")
            inits.append("scheduler = setup_scheduler(bot)")

        if include_payments:
            imports.append("from payments import register_payment_handlers")
            inits.append("register_payment_handlers(bot)")
            extra_help += "\\n• `/plans` or `/buy` — Premium plans"

        if include_ui:
            imports.append("from ui_components import Paginator, create_confirmation_dialog")
            extra_help += "\\n• `/catalog` — View interactive paginated catalog"
            extra_cmds.append("""
@bot.on_command("catalog")
async def handle_catalog(ctx: Context):
    items = ["🚀 High-Performance C++ Core", "🤖 Bots.ai LLM Memory", "🗄️ SQLite Database Collections", "🛡️ RBAC Permissions", "🌐 Multi-Language i18n", "⏰ Background Scheduler", "💳 Telegram Stars Payments"]
    paginator = Paginator(items, page_size=3)
    card = paginator.render(page=0, title="PyTekt Features")
    await ctx.reply(ui=card)
""")

        extra_msg = ""
        if include_db:
            extra_msg = """    if ctx.user_id:
        try:
            save_user(db, ctx.user_id, first_name=ctx.metadata.get("first_name"))
        except Exception:
            pass
"""

        ai_import_str = ("\n" + "\n".join(imports)) if imports else ""
        ai_init_str = ("\n" + "\n".join(inits)) if inits else ""
        extra_cmds_str = "\n".join(extra_cmds)

        files["main.py"] = (
            MINIMAL_BOT_TEMPLATE.replace("{project_name}", clean_name)
            .replace("{platform_title}", plat.capitalize())
            .replace("{bot_class}", bot_class)
            .replace("{token_env_var}", token_var)
            .replace("{default_token}", default_token)
            .replace("{ai_import}", ai_import_str)
            .replace("{db_import}", "")
            .replace("{ai_init}", ai_init_str)
            .replace("{db_init}", "")
            .replace("{extra_help_commands}", extra_help)
            .replace("{extra_commands}", extra_cmds_str)
            .replace("{extra_message_tracking}", extra_msg)
        )

        files["tests/__init__.py"] = ""
        files["tests/test_bot.py"] = MINIMAL_TEST_TEMPLATE.replace("{project_name}", clean_name)
        return files

    # ==========================================================================
    # Branch B: Professional Multi-File Modular Structure
    # ==========================================================================
    files["bot/__init__.py"] = f'"""{clean_name} Bot Package."""\n'

    # Config
    extra_settings_fields = ""
    if include_ai:
        extra_settings_fields += '\n    openai_api_key: str = field(\n        default_factory=lambda: os.environ.get("OPENAI_API_KEY", "")\n    )'
    if include_db:
        extra_settings_fields += '\n    database_url: str = field(\n        default_factory=lambda: os.environ.get("DATABASE_URL", "sqlite:///bot_data.db")\n    )'
    if include_roles:
        extra_settings_fields += '\n    admin_user_ids: str = field(\n        default_factory=lambda: os.environ.get("ADMIN_USER_IDS", "")\n    )'

    files["bot/config.py"] = (
        CONFIG_TEMPLATE.replace("{project_name}", clean_name)
        .replace("{platform}", plat)
        .replace("{token_env_var}", token_var)
        .replace("{default_token}", default_token)
        .replace("{extra_settings_fields}", extra_settings_fields)
    )

    # Handlers Init
    files["bot/handlers/__init__.py"] = HANDLERS_INIT_TEMPLATE

    # Template-specific Command & Message Logic
    extra_help = ""
    extra_cmds = ""

    if include_ai:
        extra_help += "\\n• `/ask <query>` — Ask the built-in AI assistant"
        extra_cmds += """
    if ai is not None:
        @bot.on_command("ask")
        async def handle_ask(ctx: Context) -> None:
            query = " ".join(ctx.args) if ctx.args else "Introduce yourself briefly."
            await ctx.reply_ai(ai, prompt=query)
"""

    if template == "faq-support":
        extra_help += "\\n• `/faq <query>` — Search knowledge base"
        extra_help += "\\n• `/ticket <issue>` — Submit support ticket"
        extra_cmds += """
    if ai is not None:
        @bot.on_command("faq")
        async def handle_faq(ctx: Context) -> None:
            query = " ".join(ctx.args) if ctx.args else "What services do you offer?"
            await ctx.reply_ai(ai, prompt=f"Answer from knowledge base: {query}", use_kb=True)

    @bot.on_command("ticket")
    async def handle_ticket(ctx: Context) -> None:
        issue = " ".join(ctx.args) if ctx.args else "General inquiry"
        if db is not None:
            tickets = db.collection("tickets")
            tickets.insert({"user_id": ctx.user_id, "issue": issue, "status": "open"})
        await ctx.reply(f"🎫 Support Ticket Created: #{ctx.user_id or 1001}\\nIssue: {issue}\\nOur team will respond shortly.")
"""

    if template == "reminder-scheduler":
        extra_help += "\\n• `/remind <text>` — Set in-memory reminder"
        extra_help += "\\n• `/reminders` — List active scheduled reminders"
        extra_cmds += """
    @bot.on_command("remind")
    async def handle_remind(ctx: Context) -> None:
        reminder_text = " ".join(ctx.args) if ctx.args else "Check system health"
        if db is not None:
            db.collection("reminders").insert({"user_id": ctx.user_id, "text": reminder_text, "status": "active"})
        await ctx.reply(f"⏰ Reminder registered: '{reminder_text}'. Scheduler will notify you.")

    @bot.on_command("reminders")
    async def handle_list_reminders(ctx: Context) -> None:
        count = len(db.collection("reminders").find()) if db else 0
        await ctx.reply(f"📋 You have {count} active scheduled reminder(s).")
"""

    if template == "ecommerce-payments":
        extra_help += "\\n• `/catalog` — View interactive shop catalog"
        extra_help += "\\n• `/buy <plan>` — Purchase plan with Telegram Stars"
        extra_cmds += """
    @bot.on_command("catalog")
    async def handle_catalog(ctx: Context) -> None:
        from bot.ui_components import Paginator
        items = ["⭐ Pro Membership (100 Stars)", "💎 VIP Lifetime (500 Stars)", "🚀 Developer Pass (250 Stars)"]
        paginator = Paginator(items, page_size=2)
        card = paginator.render(page=0, title="Store Products")
        await ctx.reply(ui=card)

    @bot.on_command("buy")
    async def handle_buy(ctx: Context) -> None:
        from pytekt.bots.payments import LabeledPrice
        plan = ctx.args[0].lower() if ctx.args else "pro"
        amount = 500 if plan == "vip" else 100
        try:
            await ctx.send_invoice(
                title=f"PyTekt {plan.upper()} Plan",
                description=f"Instant access to {plan.upper()} features.",
                payload=f"order_{plan}_{ctx.user_id}",
                currency="XTR",
                prices=[LabeledPrice(label=f"{plan.upper()} Access", amount=amount)],
                provider_token=settings.bot_token,
            )
        except Exception:
            await ctx.reply(f"💳 Invoice generated for {plan.upper()} plan ({amount} Stars). Complete checkout in Telegram.")
"""

    if include_db and template != "faq-support" and template != "reminder-scheduler":
        extra_help += "\\n• `/stats` — View bot persistence stats"
        extra_cmds += """
    if db is not None:
        @bot.on_command("stats")
        async def handle_stats(ctx: Context) -> None:
            users_col = db.collection("users")
            user_count = len(users_col.find())
            await ctx.reply(f"📊 Persistent Storage: {user_count} registered users in database.")
"""

    files["bot/handlers/commands.py"] = (
        HANDLERS_COMMANDS_TEMPLATE.replace("{project_name}", clean_name)
        .replace("{extra_help_commands}", extra_help)
        .replace("{extra_command_handlers}", extra_cmds)
    )

    # Template-specific Messages Handler
    if template == "ai-chatbot":
        files["bot/handlers/messages.py"] = f'''"""
Conversational AI Message Handler for {clean_name}.
"""

from __future__ import annotations
from pytekt.bots import Context


def register_messages(bot, settings, ai=None, db=None) -> None:
    """Register conversational AI fallback message handler."""
    @bot.on_message()
    async def handle_message(ctx: Context) -> None:
        if not ctx.text or ctx.text.startswith("/"):
            return
        if ai is not None:
            await ctx.reply_ai(ai, prompt=ctx.text)
        else:
            await ctx.reply(f"Echo: {{ctx.text}}")
'''
    elif template == "faq-support":
        files["bot/handlers/messages.py"] = f'''"""
FAQ & Support Knowledge-Base Message Handler for {clean_name}.
"""

from __future__ import annotations
from pytekt.bots import Context


def register_messages(bot, settings, ai=None, db=None) -> None:
    """Answer customer questions from FAQ knowledge base."""
    @bot.on_message()
    async def handle_support_message(ctx: Context) -> None:
        if not ctx.text or ctx.text.startswith("/"):
            return
        if ai is not None:
            await ctx.reply_ai(ai, prompt=ctx.text, use_kb=True)
        else:
            await ctx.reply(f"Support received: {{ctx.text}}")
'''
    elif template == "moderation":
        files["bot/handlers/messages.py"] = f'''"""
AI Content Moderation Message Handler for {clean_name}.
"""

from __future__ import annotations
import time
from pytekt.bots import Context


def register_messages(bot, settings, ai=None, db=None) -> None:
    """Inspect and moderate incoming user messages."""
    @bot.on_message()
    async def handle_moderated_message(ctx: Context) -> None:
        if not ctx.text:
            return

        is_flagged = False
        if ai is not None:
            try:
                is_flagged = await ai.moderate(ctx.text)
            except Exception:
                is_flagged = False

        if is_flagged:
            if db is not None:
                db.collection("violations").insert({{
                    "user_id": ctx.user_id,
                    "text": ctx.text,
                    "timestamp": time.time(),
                }})
            await ctx.reply("⚠️ [Moderation Alert]: Your message was flagged for violating community safety policies.")
            return

        if not ctx.text.startswith("/"):
            await ctx.reply(f"Message received: {{ctx.text}}")
'''
    else:
        files["bot/handlers/messages.py"] = HANDLERS_MESSAGES_TEMPLATE

    files["bot/handlers/callbacks.py"] = HANDLERS_CALLBACKS_TEMPLATE
    files["bot/middlewares/__init__.py"] = MIDDLEWARES_INIT_TEMPLATE
    files["bot/utils/__init__.py"] = UTILS_INIT_TEMPLATE

    # AI Setup
    if include_ai:
        files["bot/ai/__init__.py"] = AI_INIT_TEMPLATE.replace("{project_name}", clean_name)
        if template == "faq-support":
            files["bot/ai/setup.py"] = '''"""
AI Setup with Knowledge Base integration.
"""

from pathlib import Path
from pytekt.bots.ai import AI


def setup_ai(settings=None) -> AI:
    """Initialize AI assistant and load FAQ knowledge base."""
    ai = AI(
        provider="openai",
        system="You are an official customer support AI assistant. Answer customer questions accurately using the knowledge base.",
    )
    faq_file = Path(__file__).resolve().parent.parent.parent / "faq.md"
    if faq_file.exists():
        try:
            ai.knowledge_base([str(faq_file)])
        except Exception:
            pass
    return ai


async def ask_ai(ai: AI, prompt: str) -> str:
    """Send user query to AI assistant and return response."""
    return await ai.reply(prompt)
'''
        else:
            files["bot/ai/setup.py"] = AI_SETUP_TEMPLATE
        files["bot/ai/tools.py"] = AI_TOOLS_TEMPLATE
        files["bot/ai/prompts.py"] = AI_PROMPTS_TEMPLATE

    # DB Models
    if include_db:
        files["bot/models/__init__.py"] = MODELS_INIT_TEMPLATE
        files["bot/models/operations.py"] = MODELS_OPERATIONS_TEMPLATE
        files["bot/models/schemas.py"] = MODELS_SCHEMAS_TEMPLATE

        files["bot/db/__init__.py"] = MODELS_INIT_TEMPLATE
        files["bot/db/operations.py"] = MODELS_OPERATIONS_TEMPLATE
        files["bot/db/schemas.py"] = MODELS_SCHEMAS_TEMPLATE

    # Roles
    if include_roles:
        files["bot/roles/__init__.py"] = ROLES_INIT_TEMPLATE
        files["bot/roles/permissions.py"] = ROLES_PERMISSIONS_TEMPLATE
        files["bot/roles/admin_commands.py"] = ROLES_ADMIN_COMMANDS_TEMPLATE

    # i18n
    if include_i18n:
        files["bot/locales/__init__.py"] = I18N_INIT_TEMPLATE
        files["bot/locales/translator.py"] = I18N_TRANSLATOR_TEMPLATE
        files["bot/locales/en.json"] = LOCALE_EN_JSON
        files["bot/locales/ru.json"] = LOCALE_RU_JSON
        files["bot/locales/es.json"] = LOCALE_ES_JSON

    # Scheduler
    if include_scheduler:
        files["bot/scheduler/__init__.py"] = SCHEDULER_INIT_TEMPLATE
        if template == "reminder-scheduler":
            files["bot/scheduler/jobs.py"] = '''"""
Reminder and Cron Scheduled Jobs.
"""

from pytekt.bots.scheduler import Scheduler


def setup_scheduler(bot) -> Scheduler:
    """Register periodic interval and cron tasks on bot scheduler."""
    sched = bot.scheduler

    @bot.every("10s")
    async def process_reminders():
        """Process pending reminders."""
        pass

    @bot.cron("0 9 * * *")
    async def daily_morning_digest():
        """Morning daily announcement."""
        pass

    sched.start()
    return sched
'''
        else:
            files["bot/scheduler/jobs.py"] = SCHEDULER_JOBS_TEMPLATE

    # Payments
    if include_payments:
        files["bot/payments/__init__.py"] = PAYMENTS_INIT_TEMPLATE
        files["bot/payments/invoices.py"] = PAYMENTS_INVOICES_TEMPLATE
        files["bot/payments/checkout.py"] = PAYMENTS_CHECKOUT_TEMPLATE

    # UI Components
    if include_ui:
        files["bot/ui_components/__init__.py"] = UI_INIT_TEMPLATE
        files["bot/ui_components/pagination.py"] = UI_PAGINATION_TEMPLATE
        files["bot/ui_components/survey_wizard.py"] = UI_SURVEY_TEMPLATE
        files["bot/ui_components/confirmation.py"] = UI_CONFIRMATION_TEMPLATE

    # Main Entry Point in bot/main.py
    modular_imports = []
    modular_inits = []

    if include_ai:
        modular_imports.append("from bot.ai.setup import setup_ai")
        modular_inits.append("ai = setup_ai(settings)")
    else:
        modular_inits.append("ai = None")

    if include_db:
        modular_imports.append("from bot.models import init_db")
        modular_inits.append("db = init_db(settings)")
    else:
        modular_inits.append("db = None")

    if include_roles:
        modular_imports.append("from bot.roles import setup_roles, register_admin_commands")
        modular_inits.append("setup_roles(bot)\nregister_admin_commands(bot)")

    if include_i18n:
        modular_imports.append("from bot.locales import setup_i18n, register_i18n_handlers")
        modular_inits.append("setup_i18n(bot, locales_dir=Path(__file__).parent / 'locales')\nregister_i18n_handlers(bot)")

    if include_scheduler:
        modular_imports.append("from bot.scheduler import setup_scheduler")
        modular_inits.append("scheduler = setup_scheduler(bot)")

    if include_payments:
        modular_imports.append("from bot.payments import register_payment_handlers")
        modular_inits.append("register_payment_handlers(bot)")

    ai_import = "\n".join(modular_imports)
    ai_init = "\n".join(modular_inits)
    ai_arg = ", ai=ai"
    db_arg = ", db=db"

    files["bot/main.py"] = (
        MAIN_MODULAR_TEMPLATE.replace("{project_name}", clean_name)
        .replace("{bot_class}", bot_class)
        .replace("{ai_import}", ai_import)
        .replace("{db_import}", "")
        .replace("{ai_init}", ai_init)
        .replace("{db_init}", "")
        .replace("{ai_arg}", ai_arg)
        .replace("{db_arg}", db_arg)
    )

    # Unit Tests
    files["tests/__init__.py"] = '"""Unit tests package."""\n'
    files["tests/test_handlers.py"] = TEST_HANDLERS_TEMPLATE.replace("{project_name}", clean_name)

    # Copy / overlay any static files from the template package directory (e.g. faq.md)
    if manifest and manifest.template_dir and manifest.template_dir.is_dir():
        for p in manifest.template_dir.iterdir():
            if p.is_file() and p.name not in ("template.yaml", "template.yml") and not p.name.startswith("."):
                content = p.read_text(encoding="utf-8")
                rendered = (
                    content.replace("{project_name}", clean_name)
                    .replace("{platform}", plat)
                    .replace("{bot_class}", bot_class)
                )
                files[p.name] = rendered

    return files


def generate_project(
    name: str,
    platform: str = "telegram",
    target_dir: Optional[Path] = None,
    template: Optional[str] = None,
    include_ai: bool = False,
    include_db: bool = False,
    include_roles: bool = False,
    include_i18n: bool = False,
    include_scheduler: bool = False,
    include_payments: bool = False,
    include_ui: bool = False,
    minimal: bool = False,
) -> Path:
    """
    Generate a complete, working project skeleton for a PyTekt bot or starter template.
    """
    clean_name = name.strip()
    slug = clean_name.lower().replace(" ", "_").replace("-", "_")

    base = (target_dir or Path.cwd()) / slug
    base.mkdir(parents=True, exist_ok=True)

    files = generate_project_files(
        name=clean_name,
        platform=platform,
        template=template,
        include_ai=include_ai,
        include_db=include_db,
        include_roles=include_roles,
        include_i18n=include_i18n,
        include_scheduler=include_scheduler,
        include_payments=include_payments,
        include_ui=include_ui,
        minimal=minimal,
    )

    for rel_path, content in files.items():
        file_path = base / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    return base

