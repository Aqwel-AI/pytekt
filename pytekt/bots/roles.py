"""
Role-Based Access Control (RBAC) & Permission Registry for PyTekt Bots.
Provides per-chat role assignment, @bot.admin_only, and @bot.requires_role decorators.
"""

from __future__ import annotations

import functools
import inspect
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set

if TYPE_CHECKING:
    from .base import Bot, Context

logger = logging.getLogger("pytekt.bots.roles")


class RoleRegistry:
    """
    Per-chat and global role registry for users.
    Backed by bot.db if available, with in-process memory fallback.
    """

    def __init__(self, bot: Optional[Bot] = None) -> None:
        self.bot = bot
        self._in_memory_roles: Dict[str, Set[str]] = {}  # key: "chat_id:user_id" -> {roles}
        self._global_admins: Set[str] = set()

    def _key(self, chat_id: str, user_id: str) -> str:
        return f"{chat_id}:{user_id}"

    def set_admin(self, user_id: str, chat_id: Optional[str] = None) -> None:
        """Designate a user as an administrator globally or in a chat."""
        if chat_id:
            self.grant(chat_id, user_id, "admin")
        else:
            self._global_admins.add(str(user_id))
            self.grant("*", user_id, "admin")

    def grant(self, chat_id: str, user_id: str, role: str) -> None:
        """Grant a role to a user in a specific chat (or '*' for global)."""
        r = role.lower().strip()
        k = self._key(chat_id, user_id)
        if k not in self._in_memory_roles:
            self._in_memory_roles[k] = set()
        self._in_memory_roles[k].add(r)

        if self.bot and getattr(self.bot, "db", None):
            self.bot.db.grant_role(chat_id, user_id, r)

    def revoke(self, chat_id: str, user_id: str, role: str) -> None:
        """Revoke a role from a user."""
        r = role.lower().strip()
        k = self._key(chat_id, user_id)
        if k in self._in_memory_roles:
            self._in_memory_roles[k].discard(r)

        if self.bot and getattr(self.bot, "db", None):
            self.bot.db.revoke_role(chat_id, user_id, r)

    def has_role(self, chat_id: str, user_id: str, role: str) -> bool:
        """Check if a user possesses a specific role in a chat or globally."""
        r = role.lower().strip()
        uid = str(user_id)

        # Global admin bypass
        if uid in self._global_admins and r != "owner":
            return True

        # Check in-memory store
        k_chat = self._key(chat_id, uid)
        k_glob = self._key("*", uid)

        if k_chat in self._in_memory_roles and r in self._in_memory_roles[k_chat]:
            return True
        if k_glob in self._in_memory_roles and r in self._in_memory_roles[k_glob]:
            return True

        # Check persistent DB if available
        if self.bot and getattr(self.bot, "db", None):
            roles = self.bot.db.get_roles(chat_id, uid)
            return r in [x.lower() for x in roles]

        return False

    def is_admin(self, chat_id: str, user_id: str) -> bool:
        """Check if user is an administrator."""
        uid = str(user_id)
        if uid in self._global_admins:
            return True
        return self.has_role(chat_id, uid, "admin") or self.has_role(chat_id, uid, "administrator")


def _extract_ctx(*args: Any, **kwargs: Any) -> Optional[Context]:
    for arg in args:
        if hasattr(arg, "chat_id") and hasattr(arg, "bot"):
            return arg
    return kwargs.get("ctx")


def requires_role(
    role: str,
    on_forbidden: Optional[Callable[[Context], Any]] = None,
) -> Callable[..., Any]:
    """Decorator requiring the user to have a specified role."""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = _extract_ctx(*args, **kwargs)
            if ctx is None:
                res = fn(*args, **kwargs)
                return (await res) if inspect.iscoroutine(res) else res

            has_perm = ctx.bot.roles.has_role(ctx.chat_id, ctx.user_id, role)
            if not has_perm:
                if on_forbidden:
                    res = on_forbidden(ctx)
                    return (await res) if inspect.iscoroutine(res) else res
                await ctx.reply("⛔ <i>Access denied: required role '%s'.</i>" % role, parse_mode="HTML")
                return None
            res = fn(*args, **kwargs)
            return (await res) if inspect.iscoroutine(res) else res
        return wrapper
    return decorator


def admin_only(
    on_forbidden: Optional[Callable[[Context], Any]] = None,
) -> Callable[..., Any]:
    """Decorator restricting command access to chat or bot administrators."""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = _extract_ctx(*args, **kwargs)
            if ctx is None:
                res = fn(*args, **kwargs)
                return (await res) if inspect.iscoroutine(res) else res

            # Check bot roles registry or platform metadata
            is_adm = ctx.bot.roles.is_admin(ctx.chat_id, ctx.user_id) or ctx.metadata.get("is_admin") == "true"
            if not is_adm:
                if on_forbidden:
                    res = on_forbidden(ctx)
                    return (await res) if inspect.iscoroutine(res) else res
                await ctx.reply("⛔ <i>Access denied: administrator privileges required.</i>", parse_mode="HTML")
                return None
            res = fn(*args, **kwargs)
            return (await res) if inspect.iscoroutine(res) else res
        return wrapper
    return decorator
