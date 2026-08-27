"""
Plugin & Extension Architecture for PyTekt Bots.
Allows developers and third parties to package and distribute modular bot features,
commands, handlers, and scheduled tasks as reusable components.
"""

from __future__ import annotations

import functools
import importlib
import inspect
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type

if TYPE_CHECKING:
    from .base import Bot

logger = logging.getLogger("pytekt.bots.extension")


class Extension:
    """
    Base class for modular PyTekt bot extensions and plugins.

    Parameters
    ----------
    bot : Bot
        The parent Bot instance.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self._registered_handlers: List[Tuple[str, str, Callable[..., Any]]] = []

    async def on_load(self) -> None:
        """Lifecycle hook called when extension is loaded into bot."""
        pass

    async def on_unload(self) -> None:
        """Lifecycle hook called when extension is unloaded from bot."""
        pass

    @classmethod
    def command(cls, name: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a slash/exclamation command within an extension."""
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            cmd_name = name or fn.__name__
            setattr(fn, "__bot_ext_type__", "command")
            setattr(fn, "__bot_ext_name__", cmd_name)
            return fn
        return decorator

    @classmethod
    def on_message(cls, pattern: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a message handler within an extension."""
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            setattr(fn, "__bot_ext_type__", "message")
            setattr(fn, "__bot_ext_name__", pattern)
            return fn
        return decorator

    @classmethod
    def on_button(cls, callback_id: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a button click handler within an extension."""
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            cb_id = callback_id or fn.__name__
            setattr(fn, "__bot_ext_type__", "button")
            setattr(fn, "__bot_ext_name__", cb_id)
            return fn
        return decorator

    @classmethod
    def every(cls, interval: Union[str, int, float]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a recurring scheduled job within an extension."""
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            setattr(fn, "__bot_ext_type__", "every")
            setattr(fn, "__bot_ext_name__", interval)
            return fn
        return decorator


class ExtensionManager:
    """Manages loading, registration, and unloading of Bot extensions."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.extensions: Dict[str, Extension] = {}

    def add_extension(self, ext: Extension) -> None:
        """Register an Extension instance with the bot."""
        name = ext.__class__.__name__
        self.extensions[name] = ext

        # Scan methods for extension decorators
        for attr_name in dir(ext):
            attr = getattr(ext, attr_name, None)
            if callable(attr) and hasattr(attr, "__bot_ext_type__"):
                ext_type = getattr(attr, "__bot_ext_type__")
                ext_val = getattr(attr, "__bot_ext_name__")

                # Bind method to extension instance
                bound_method = getattr(ext, attr_name)

                if ext_type == "command":
                    self.bot.on_command(ext_val)(bound_method)
                elif ext_type == "message":
                    self.bot.on_message(ext_val)(bound_method)
                elif ext_type == "button":
                    self.bot.on_button(ext_val)(bound_method)
                elif ext_type == "every":
                    self.bot.every(ext_val)(bound_method)

        logger.info("Loaded extension: %s", name)

    def load_extension(self, module_path: str) -> None:
        """
        Dynamically import a module and invoke its setup(bot) function
        or discover Extension subclasses.
        """
        mod = importlib.import_module(module_path)

        # 1. If module has setup(bot) function, call it
        if hasattr(mod, "setup") and callable(mod.setup):
            res = mod.setup(self.bot)
            if inspect.iscoroutine(res):
                import asyncio
                asyncio.create_task(res)
            return

        # 2. Otherwise scan module for Extension subclasses
        for _, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, Extension) and obj is not Extension:
                ext_instance = obj(self.bot)
                self.add_extension(ext_instance)
                break
