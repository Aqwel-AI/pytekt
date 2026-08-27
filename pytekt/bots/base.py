"""
Platform-agnostic Bot and Context base classes.
High-performance core dispatching delegating to C++ _core with Python decorators
and declarative cross-platform UI rendering (Keyboards, Cards, Modals, Wizards).
"""

from __future__ import annotations

import asyncio
import fnmatch
import functools
import inspect
import json
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List, Optional, Sequence, Tuple, Union

from ._core import (
    AntiSpam,
    Cache,
    Dispatcher,
    FSM,
    Metrics,
    RateLimiter,
    UniversalEvent,
    WebhookServer,
)
from .persistence import BotDB
from .roles import RoleRegistry, admin_only as _admin_only_dec, requires_role as _requires_role_dec
from .i18n import I18nManager
from .scheduler import Scheduler
from .extension import Extension, ExtensionManager
from .testing import BotTestClient
from .payments import Invoice, LabeledPrice, NotSupportedError, PreCheckoutQuery, SuccessfulPayment

if TYPE_CHECKING:
    from .ui.card import Card
    from .ui.components import UIComponent
    from .ui.keyboard import Keyboard
    from .ui.modal import Modal
    from .ui.wizard import Wizard

logger = logging.getLogger("pytekt.bots")

HandlerFunc = Callable[..., Any]
MiddlewareFunc = Callable[..., Any]


class Context:
    """
    Context wrapping a normalized UniversalEvent and providing convenience methods
    for replying, sending media, declarative UI rendering, managing FSM state,
    and streaming AI responses.
    """

    def __init__(self, bot: "Bot", event: UniversalEvent) -> None:
        self.bot = bot
        self.event = event

    @property
    def id(self) -> str:
        return self.event.id

    @property
    def chat_id(self) -> str:
        return self.event.chat_id

    @property
    def user_id(self) -> str:
        return self.event.user_id

    @property
    def text(self) -> str:
        return self.event.text

    @property
    def command(self) -> str:
        return self.event.command

    @property
    def args(self) -> List[str]:
        return self.event.args

    @property
    def platform(self) -> str:
        return self.event.platform

    @property
    def event_type(self) -> str:
        return self.event.event_type

    @property
    def raw(self) -> str:
        return self.event.raw

    @property
    def metadata(self) -> Dict[str, str]:
        return self.event.metadata

    @property
    def image(self) -> Optional[str]:
        return self.metadata.get("url") or self.metadata.get("file_id")

    @property
    def audio(self) -> Optional[str]:
        return self.metadata.get("url") or self.metadata.get("file_id")

    @property
    def lang(self) -> str:
        """Return user's language code from platform metadata, or 'en'."""
        return (
            self.event.metadata.get("language_code")
            or self.event.metadata.get("locale")
            or self.event.metadata.get("lang")
            or "en"
        )

    def t(self, key: str, **kwargs: Any) -> str:
        """Translate a string key using the bot's i18n manager."""
        return self.bot.t(key, lang=self.lang, **kwargs)

    def _fsm_key(self) -> str:
        return f"{self.chat_id}:{self.user_id}" if self.user_id else self.chat_id

    # ------------------------------------------------------------------
    # FSM State & Session helpers
    # ------------------------------------------------------------------

    async def get_state(self) -> str:
        k = self._fsm_key()
        st = self.bot.fsm.get_state(k)
        if not st and self.bot.db is not None:
            st = self.bot.db.get_state(k)
            if st:
                self.bot.fsm.set_state(k, st, 0.0)
        return st

    async def set_state(self, state: str, ttl: float = 0.0, persistent: bool = False) -> None:
        k = self._fsm_key()
        if persistent and self.bot.db is not None:
            self.bot.db.set_state(k, state, ttl)
        self.bot.fsm.set_state(k, state, ttl)

    async def clear_state(self) -> None:
        k = self._fsm_key()
        if self.bot.db is not None:
            self.bot.db.clear_state(k)
        self.bot.fsm.clear_state(k)

    async def get_data(self, key: str) -> str:
        k = self._fsm_key()
        val = self.bot.fsm.get_data(k, key)
        if not val and self.bot.db is not None:
            val = self.bot.db.get_data(k, key)
            if val:
                self.bot.fsm.set_data(k, key, val, 0.0)
        return val

    async def set_data(self, key: str, value: str, ttl: float = 0.0, persistent: bool = False) -> None:
        k = self._fsm_key()
        if persistent and self.bot.db is not None:
            self.bot.db.set_data(k, key, value, ttl)
        self.bot.fsm.set_data(k, key, value, ttl)

    async def get_all_data(self) -> Dict[str, str]:
        k = self._fsm_key()
        data = self.bot.fsm.get_all_data(k)
        if not data and self.bot.db is not None:
            data = self.bot.db.get_all_data(k)
        return data

    async def clear_data(self) -> None:
        k = self._fsm_key()
        if self.bot.db is not None:
            self.bot.db.clear_data(k)
        self.bot.fsm.clear_data(k)

    async def send_invoice(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: Sequence[Any],
        **kwargs: Any,
    ) -> Any:
        """Send an in-chat payment invoice to the current chat."""
        return await self.bot.send_invoice(
            chat_id=self.chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Messaging & Action helpers
    # ------------------------------------------------------------------

    async def reply(
        self,
        text: str = "",
        ui: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Send a reply to the originating chat, optionally attaching a cross-platform
        UI component (Keyboard, Card, etc.).
        """
        from .ui.card import Card
        from .ui.components import UIComponent
        from .ui.keyboard import Keyboard

        if ui is not None:
            if isinstance(ui, Card):
                compiled = ui.compile(self.platform)
                if self.platform == "discord":
                    embeds = [compiled["embed"]] if "embed" in compiled else kwargs.get("embeds", [])
                    components = compiled.get("components") or kwargs.get("components")
                    return await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=text or compiled.get("text", ""),
                        reply_to_message_id=self.id or None,
                        embeds=embeds,
                        components=components,
                        **kwargs,
                    )
                else:  # Telegram or generic fallback
                    photo = compiled.get("photo")
                    reply_markup = compiled.get("reply_markup") or kwargs.get("reply_markup")
                    parse_mode = compiled.get("parse_mode", "HTML")
                    card_text = compiled.get("text", "")
                    body_text = f"{text}\n\n{card_text}".strip() if text and card_text else (text or card_text)
                    if photo:
                        return await self.bot.send_photo(
                            chat_id=self.chat_id,
                            photo=photo,
                            caption=body_text,
                            parse_mode=parse_mode,
                            reply_markup=reply_markup,
                            reply_to_message_id=self.id or None,
                            **kwargs,
                        )
                    else:
                        return await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=body_text,
                            parse_mode=parse_mode,
                            reply_markup=reply_markup,
                            reply_to_message_id=self.id or None,
                            **kwargs,
                        )

            elif isinstance(ui, Keyboard):
                if self.platform == "discord":
                    components = ui.to_discord()
                    return await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=text,
                        reply_to_message_id=self.id or None,
                        components=components,
                        **kwargs,
                    )
                else:  # Telegram
                    reply_markup = ui.to_telegram()
                    return await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=text or " ",
                        reply_to_message_id=self.id or None,
                        reply_markup=reply_markup,
                        **kwargs,
                    )

            elif isinstance(ui, UIComponent):
                compiled = ui.compile(self.platform)
                return await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text or compiled.get("text", ""),
                    reply_to_message_id=self.id or None,
                    **{**compiled, **kwargs},
                )

        return await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_to_message_id=self.id or None,
            **kwargs,
        )

    async def show_modal(self, modal: "Modal") -> Any:
        """
        Display an interactive Modal form.
        Compiles to a native Modal interaction response on Discord,
        or degrades gracefully to a ForceReply conversational prompt on Telegram.
        """
        if self.platform == "discord":
            compiled = modal.to_discord()
            if hasattr(self.bot, "show_modal"):
                return await self.bot.show_modal(
                    chat_id=self.chat_id,
                    modal_payload=compiled,
                    interaction_id=self.id,
                )
            return await self.bot.send_message(
                chat_id=self.chat_id,
                text=f"📋 **{modal.title}**",
                **compiled,
            )
        else:
            compiled = modal.to_telegram()
            return await self.bot.send_message(
                chat_id=self.chat_id,
                text=compiled["text"],
                reply_markup=compiled["reply_markup"],
                parse_mode=compiled["parse_mode"],
                reply_to_message_id=self.id or None,
            )

    async def start_wizard(self, wizard: "Wizard") -> Any:
        """
        Start an interactive multi-step Wizard flow for the user.
        Renders step 0 and sets up automatic in-place message navigation.
        """
        self.bot.register_wizard(wizard)
        rendered = wizard.render_step(0, self.platform)

        # Save wizard session in FSM
        await self.set_data(f"wiz:{wizard.id}:step", "0")

        if self.platform == "discord":
            msg = await self.bot.send_message(
                chat_id=self.chat_id,
                text=rendered.get("text", ""),
                embeds=[rendered["embed"]] if "embed" in rendered else None,
                components=rendered.get("components"),
            )
        else:
            if rendered.get("photo"):
                msg = await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=rendered["photo"],
                    caption=rendered.get("caption") or rendered.get("text", ""),
                    parse_mode=rendered.get("parse_mode", "HTML"),
                    reply_markup=rendered.get("reply_markup"),
                )
            else:
                msg = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=rendered.get("text", ""),
                    parse_mode=rendered.get("parse_mode", "HTML"),
                    reply_markup=rendered.get("reply_markup"),
                )

        msg_id = getattr(msg, "id", None) or getattr(msg, "message_id", None)
        if msg_id is None and isinstance(msg, dict):
            msg_id = msg.get("id") or msg.get("message_id")
        if msg_id:
            await self.set_data(f"wiz:{wizard.id}:msg_id", str(msg_id))
        return msg

    async def send_typing(self) -> Any:
        """Send typing action indicator to chat."""
        return await self.bot.send_chat_action(chat_id=self.chat_id, action="typing")

    async def send_photo(self, photo: Union[str, bytes], caption: Optional[str] = None, **kwargs: Any) -> Any:
        """Send a photo to the originating chat."""
        return await self.bot.send_photo(chat_id=self.chat_id, photo=photo, caption=caption, **kwargs)

    async def send_voice(self, voice: Union[str, bytes], caption: Optional[str] = None, **kwargs: Any) -> Any:
        """Send voice audio to the originating chat."""
        return await self.bot.send_voice(chat_id=self.chat_id, voice=voice, caption=caption, **kwargs)

    async def delete(self) -> Any:
        """Delete the triggering message."""
        if self.id:
            return await self.bot.delete_message(chat_id=self.chat_id, message_id=self.id)
        return False

    async def reply_ai(self, ai: Any, prompt: Optional[str] = None, **kwargs: Any) -> Any:
        """
        Stream or reply with an AI response, throttled through rate limiter
        so that live streamed message edits never exceed platform limits.
        """
        text_prompt = prompt or self.text
        # Trigger typing indicator
        try:
            await self.send_typing()
        except Exception:
            pass

        # Check if AI object has stream capability
        if hasattr(ai, "ask_stream"):
            first_msg = None
            accumulated = ""
            last_edit_time = 0.0
            edit_throttle = kwargs.pop("stream_throttle", 0.7)  # max 1 edit per 700ms

            async for chunk in ai.ask_stream(text_prompt, chat_id=self.chat_id, **kwargs):
                accumulated += chunk
                now = time.monotonic()
                if first_msg is None and len(accumulated.strip()) > 0:
                    first_msg = await self.reply(accumulated + " ▍")
                    last_edit_time = now
                elif first_msg is not None and (now - last_edit_time) >= edit_throttle:
                    msg_id = getattr(first_msg, "id", None) or getattr(first_msg, "message_id", None)
                    if msg_id is None and isinstance(first_msg, dict):
                        msg_id = first_msg.get("id") or first_msg.get("message_id")
                    try:
                        await self.bot.edit_message_text(
                            chat_id=self.chat_id,
                            message_id=str(msg_id),
                            text=accumulated + " ▍",
                        )
                        last_edit_time = now
                    except Exception:
                        pass

            # Final edit without cursor
            if first_msg is not None:
                msg_id = getattr(first_msg, "id", None) or getattr(first_msg, "message_id", None)
                if msg_id is None and isinstance(first_msg, dict):
                    msg_id = first_msg.get("id") or first_msg.get("message_id")
                try:
                    return await self.bot.edit_message_text(
                        chat_id=self.chat_id,
                        message_id=str(msg_id),
                        text=accumulated or "...",
                    )
                except Exception:
                    return first_msg
            else:
                return await self.reply(accumulated or "...")

        # Fallback to direct ask
        response = await ai.ask(text_prompt, chat_id=self.chat_id, **kwargs)
        return await self.reply(str(response))


class Bot:
    """
    Platform-agnostic Bot base class with compiled C++ core components:
    Dispatcher, RateLimiter, FSM, in-process Cache, WebhookServer, AntiSpam, Metrics,
    and cross-platform UI rendering (Keyboards, Cards, Modals, Wizards).
    """

    def __init__(self, platform: str = "generic") -> None:
        self.platform = platform
        self.dispatcher = Dispatcher()
        self.rate_limiter = RateLimiter()
        self.fsm = FSM()
        self.cache = Cache()
        self.antispam = AntiSpam()
        self.metrics = Metrics()
        self.webhook_server = WebhookServer()

        self.db: Optional[BotDB] = None
        self.roles = RoleRegistry(self)
        self.i18n = I18nManager()
        self.scheduler = Scheduler(self)
        self.extension_manager = ExtensionManager(self)
        self._pre_checkout_handlers: List[Callable[..., Any]] = []
        self._payment_handlers: List[Callable[..., Any]] = []

        self._handlers: Dict[str, HandlerFunc] = {}
        self._button_handlers: List[Tuple[Optional[str], HandlerFunc]] = []
        self._modal_handlers: List[Tuple[Optional[str], HandlerFunc]] = []
        self._wizards: Dict[str, "Wizard"] = {}
        self._middlewares: List[MiddlewareFunc] = []
        self._handler_counter = 0

    def init_db(self, source: Union[str, Any] = "sqlite:///./bot.db") -> BotDB:
        """Initialize database persistence for FSM, roles, and long-term facts."""
        self.db = BotDB(source)
        return self.db

    def test_client(self) -> BotTestClient:
        """Create an in-memory client for testing handlers without network connections."""
        return BotTestClient(self)

    def every(self, interval: Union[str, int, float]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a periodic scheduled task running on the bot event loop."""
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.scheduler.add_interval_job(interval, fn)
            return fn
        return decorator

    def cron(self, cron_expr: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a cron-scheduled recurring task running on the bot event loop."""
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.scheduler.add_cron_job(cron_expr, fn)
            return fn
        return decorator

    def admin_only(
        self,
        fn: Optional[Callable[..., Any]] = None,
        on_forbidden: Optional[Callable[[Context], Any]] = None,
    ) -> Any:
        """Restrict handler access to administrators."""
        dec = _admin_only_dec(on_forbidden=on_forbidden)
        if fn is not None:
            return dec(fn)
        return dec

    def requires_role(
        self,
        role: str,
        on_forbidden: Optional[Callable[[Context], Any]] = None,
    ) -> Callable[..., Any]:
        """Restrict handler access to users possessing a specific role."""
        return _requires_role_dec(role, on_forbidden=on_forbidden)

    def t(self, key: str, lang: Optional[str] = None, **kwargs: Any) -> str:
        """Translate a string key using the configured i18n translation tables."""
        return self.i18n.translate(key, lang=lang, **kwargs)

    def load_translations(self, dir_path: Union[str, Path]) -> None:
        """Load translation JSON/YAML files from a directory."""
        self.i18n.load_directory(dir_path)

    def add_translations(self, lang: str, table: Dict[str, Any]) -> None:
        """Add translations for a language code."""
        self.i18n.add_translations(lang, table)

    def add_extension(self, ext: Extension) -> None:
        """Attach a reusable Extension plugin instance to the bot."""
        self.extension_manager.add_extension(ext)

    def load_extension(self, module_path: str) -> None:
        """Dynamically import and load an Extension module or cog."""
        self.extension_manager.load_extension(module_path)

    def on_pre_checkout(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register a handler for Telegram pre-checkout payment confirmation queries."""
        self._pre_checkout_handlers.append(fn)
        return fn

    def on_payment(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register a handler for successful payment confirmations."""
        self._payment_handlers.append(fn)
        return fn

    async def send_invoice(
        self,
        chat_id: str,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: Sequence[Any],
        **kwargs: Any,
    ) -> Any:
        """Send a native payment invoice (Telegram only)."""
        raise NotSupportedError(f"Payments API is not supported on platform '{self.platform}'.")

    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool = True,
        error_message: Optional[str] = None,
    ) -> Any:
        """Confirm or reject a pre-checkout payment query."""
        raise NotSupportedError(f"Payments API is not supported on platform '{self.platform}'.")

    def _next_handler_id(self, prefix: str = "h") -> str:
        self._handler_counter += 1
        return f"{prefix}_{self._handler_counter}"

    # ------------------------------------------------------------------
    # Decorators
    # ------------------------------------------------------------------

    def on_command(self, command: str) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a command handler (e.g. 'start', '/help', '!info')."""
        def decorator(fn: HandlerFunc) -> HandlerFunc:
            hid = self._next_handler_id(f"cmd_{command}")
            self._handlers[hid] = fn
            self.dispatcher.add_command_handler(command, hid)
            return fn
        return decorator

    def on_message(self, pattern: Optional[str] = None) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a message handler, optionally matching a regex pattern."""
        def decorator(fn: HandlerFunc) -> HandlerFunc:
            if pattern:
                hid = self._next_handler_id("pattern")
                self._handlers[hid] = fn
                self.dispatcher.add_pattern_handler(pattern, hid)
            else:
                hid = self._next_handler_id("msg")
                self._handlers[hid] = fn
                self.dispatcher.add_event_handler("message", hid)
            return fn
        return decorator

    def on_button(self, callback_id: Optional[str] = None) -> Callable[[HandlerFunc], HandlerFunc]:
        """
        Register a handler for button clicks and interactive callbacks.
        Supports exact callback_id, glob wildcards ('wiz:*'), or all buttons (None / '*').
        """
        def decorator(fn: HandlerFunc) -> HandlerFunc:
            self._button_handlers.append((callback_id, fn))
            # Also register in dispatcher under callback/interaction event
            hid = self._next_handler_id(f"btn_{callback_id or 'all'}")
            self._handlers[hid] = fn
            self.dispatcher.add_event_handler("callback", hid)
            self.dispatcher.add_event_handler("interaction", hid)
            return fn
        return decorator

    def on_modal_submit(self, custom_id: Optional[str] = None) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a handler for modal form submissions."""
        def decorator(fn: HandlerFunc) -> HandlerFunc:
            self._modal_handlers.append((custom_id, fn))
            hid = self._next_handler_id(f"modal_{custom_id or 'all'}")
            self._handlers[hid] = fn
            self.dispatcher.add_event_handler("modal_submit", hid)
            return fn
        return decorator

    def on_voice(self) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a handler for incoming voice and audio messages."""
        def decorator(fn: HandlerFunc) -> HandlerFunc:
            hid = self._next_handler_id("voice")
            self._handlers[hid] = fn
            self.dispatcher.add_event_handler("voice", hid)
            return fn
        return decorator

    def on_photo(self) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a handler for incoming photo and image messages."""
        def decorator(fn: HandlerFunc) -> HandlerFunc:
            hid = self._next_handler_id("photo")
            self._handlers[hid] = fn
            self.dispatcher.add_event_handler("photo", hid)
            return fn
        return decorator

    def on_event(self, event_type: str) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a handler for a specific event type (e.g. 'callback', 'interaction')."""
        def decorator(fn: HandlerFunc) -> HandlerFunc:
            hid = self._next_handler_id(f"evt_{event_type}")
            self._handlers[hid] = fn
            self.dispatcher.add_event_handler(event_type, hid)
            return fn
        return decorator

    def state(self, state_name: str) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a handler for when a user or chat is in a specific FSM state."""
        def decorator(fn: HandlerFunc) -> HandlerFunc:
            hid = self._next_handler_id(f"state_{state_name}")
            self._handlers[hid] = fn
            self.dispatcher.add_state_handler(state_name, hid)
            return fn
        return decorator

    def rate_limit(
        self,
        user: Optional[str] = None,
        chat: Optional[str] = None,
        global_: Optional[str] = None,
        on_limited: Optional[Callable[[Context, float], Any]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """
        Configure rate limiting for handlers using token buckets in C++.
        Example: @bot.rate_limit(user="5/10s", chat="20/60s")
        """
        if user:
            self.rate_limiter.set_rule("user", user)
        if chat:
            self.rate_limiter.set_rule("chat", chat)
        if global_:
            self.rate_limiter.set_rule("global", global_)

        def decorator(fn: HandlerFunc) -> HandlerFunc:
            @functools.wraps(fn)
            async def wrapper(ctx: Context, *args: Any, **kwargs: Any) -> Any:
                allowed, retry_after = self.rate_limiter.check_and_acquire(
                    user_id=ctx.user_id,
                    chat_id=ctx.chat_id,
                    tokens=1.0,
                )
                if not allowed:
                    if on_limited:
                        res = on_limited(ctx, retry_after)
                        if inspect.iscoroutine(res):
                            return await res
                        return res
                    logger.warning("Rate limit exceeded for user %s (retry after %.2fs)", ctx.user_id, retry_after)
                    return None
                res = fn(ctx, *args, **kwargs)
                if inspect.iscoroutine(res):
                    return await res
                return res
            return wrapper
        return decorator

    def middleware(self, fn: MiddlewareFunc) -> MiddlewareFunc:
        """Register a middleware function (async fn(ctx, next_handler))."""
        self._middlewares.append(fn)
        return fn

    # GramMY / Express / Koa style alias
    use = middleware

    # ------------------------------------------------------------------
    # Wizard Navigation Engine
    # ------------------------------------------------------------------

    def register_wizard(self, wizard: "Wizard") -> None:
        """Register wizard flow handlers for automatic step navigation."""
        if wizard.id in self._wizards:
            return
        self._wizards[wizard.id] = wizard

        @self.on_button(f"wiz:{wizard.id}:*")
        async def handle_wizard_nav(ctx: Context) -> Any:
            cb_data = ctx.text  # contains "wiz:<id>:<action>:<step>"
            parts = cb_data.split(":")
            if len(parts) < 4:
                return

            wiz_id, action, step_str = parts[1], parts[2], parts[3]
            current_step = int(step_str)
            wiz = self._wizards.get(wiz_id)
            if not wiz:
                return

            msg_id = ctx.metadata.get("message_id") or ctx.id

            if action == "next":
                new_step = current_step + 1
                if new_step < len(wiz.steps):
                    rendered = wiz.render_step(new_step, ctx.platform)
                    await self._edit_wizard_message(ctx, msg_id, rendered)
                    await ctx.set_data(f"wiz:{wiz_id}:step", str(new_step))

            elif action == "back":
                new_step = max(0, current_step - 1)
                rendered = wiz.render_step(new_step, ctx.platform)
                await self._edit_wizard_message(ctx, msg_id, rendered)
                await ctx.set_data(f"wiz:{wiz_id}:step", str(new_step))

            elif action == "cancel":
                await ctx.clear_data()
                if wiz.on_cancel:
                    res = wiz.on_cancel(ctx)
                    if inspect.iscoroutine(res):
                        await res
                else:
                    await self.edit_message_text(
                        chat_id=ctx.chat_id,
                        message_id=msg_id,
                        text="❌ <i>Flow cancelled.</i>",
                        parse_mode="HTML",
                        reply_markup={"inline_keyboard": []},
                    )

            elif action == "finish":
                await ctx.clear_data()
                if wiz.on_finish:
                    res = wiz.on_finish(ctx)
                    if inspect.iscoroutine(res):
                        await res
                else:
                    await self.edit_message_text(
                        chat_id=ctx.chat_id,
                        message_id=msg_id,
                        text="✅ <i>Flow completed successfully!</i>",
                        parse_mode="HTML",
                        reply_markup={"inline_keyboard": []},
                    )

    async def _edit_wizard_message(self, ctx: Context, message_id: str, rendered: Dict[str, Any]) -> Any:
        """Helper to edit a wizard step message in place across platforms."""
        if ctx.platform == "discord":
            return await self.edit_message_text(
                chat_id=ctx.chat_id,
                message_id=message_id,
                text=rendered.get("text", ""),
                embeds=[rendered["embed"]] if "embed" in rendered else None,
                components=rendered.get("components"),
            )
        else:
            return await self.edit_message_text(
                chat_id=ctx.chat_id,
                message_id=message_id,
                text=rendered.get("text", ""),
                parse_mode=rendered.get("parse_mode", "HTML"),
                reply_markup=rendered.get("reply_markup"),
            )

    # ------------------------------------------------------------------
    # Built-in WebApp Server Helper
    # ------------------------------------------------------------------

    def serve_web_app(
        self,
        path: str,
        html_content: Union[str, Callable[[], str]],
    ) -> str:
        """
        Serve a custom HTML/CSS/JS WebApp using the built-in C++ WebhookServer.
        Returns the registered URL path.
        """
        clean_path = "/" + path.lstrip("/")

        def web_app_handler(method: str, req_path: str, body: str) -> str:
            if callable(html_content):
                return html_content()
            return str(html_content)

        self.webhook_server.add_route(clean_path, web_app_handler)
        logger.info("Serving WebApp on path %s", clean_path)
        return clean_path

    # ------------------------------------------------------------------
    # AI Commands Declarative Generator
    # ------------------------------------------------------------------

    def ai_commands(self, ai: Any, commands: Dict[str, str]) -> None:
        """
        Declarative natural-language command menu to handler generator.
        Turns a dictionary of command descriptions into working handlers.
        """
        for cmd_name, cmd_desc in commands.items():
            clean_name = cmd_name.lstrip("/!")

            def make_handler(name: str, desc: str) -> HandlerFunc:
                async def handler(ctx: Context) -> Any:
                    target_text = ctx.text
                    # Check if replied-to message text exists in metadata
                    reply_text = ctx.metadata.get("reply_to_text", "")
                    prompt_parts = [
                        f"Execute command '/{name}': {desc}.",
                    ]
                    if reply_text:
                        prompt_parts.append(f"Replied-to message content: \"{reply_text}\"")
                    if ctx.args:
                        prompt_parts.append(f"Command arguments: {' '.join(ctx.args)}")
                    elif target_text and target_text.strip() != f"/{name}":
                        prompt_parts.append(f"User input: {target_text}")

                    full_prompt = "\n".join(prompt_parts)
                    await ctx.reply_ai(ai, prompt=full_prompt)

                return handler

            h = make_handler(clean_name, cmd_desc)
            self.on_command(clean_name)(h)

    # ------------------------------------------------------------------
    # Event Dispatching & Execution
    # ------------------------------------------------------------------

    def normalize_event(self, raw_data: Union[str, dict, UniversalEvent]) -> UniversalEvent:
        """Convert string, dict, or UniversalEvent into a UniversalEvent."""
        if isinstance(raw_data, UniversalEvent):
            return raw_data
        if isinstance(raw_data, dict):
            # Check if it's already structured as a generic/mock UniversalEvent
            if "event_type" in raw_data or (
                "chat_id" in raw_data and "update_id" not in raw_data and "t" not in raw_data and "d" not in raw_data
            ):
                return self.dispatcher.parse_generic(json.dumps(raw_data), self.platform)
            raw_str = json.dumps(raw_data)
        else:
            raw_str = str(raw_data)

        if self.platform == "telegram":
            return self.dispatcher.parse_telegram(raw_str)
        elif self.platform == "discord":
            return self.dispatcher.parse_discord(raw_str)
        else:
            return self.dispatcher.parse_generic(raw_str, self.platform)

    async def handle_event(self, raw_event: Union[str, dict, UniversalEvent]) -> List[Any]:
        """Dispatch a single event through rate limiters, middlewares, and matching handlers."""
        t0 = time.monotonic()
        event = self.normalize_event(raw_event)
        ctx = Context(self, event)

        # 1. Global rate limiter check
        allowed, retry_after = self.rate_limiter.check_and_acquire(
            user_id=ctx.user_id,
            chat_id=ctx.chat_id,
            tokens=1.0,
        )
        if not allowed:
            logger.warning("Event dropped by rate limiter: retry after %.2fs", retry_after)
            return []

        # 2. Get active FSM state
        current_state = await ctx.get_state()

        # 3. Match handlers in C++ Dispatcher
        handler_ids = self.dispatcher.match(event, current_state)

        # 4. Check button handlers if event is callback or interaction
        target_handlers: List[HandlerFunc] = []
        for hid in handler_ids:
            if hid in self._handlers:
                target_handlers.append(self._handlers[hid])

        if event.event_type in ("callback", "interaction"):
            btn_id = event.text
            for pattern, h_fn in self._button_handlers:
                if pattern is None or pattern == "*" or pattern == btn_id or fnmatch.fnmatch(btn_id, pattern):
                    if h_fn not in target_handlers:
                        target_handlers.append(h_fn)

        if event.event_type == "modal_submit":
            m_id = event.text
            for pattern, h_fn in self._modal_handlers:
                if pattern is None or pattern == "*" or pattern == m_id or fnmatch.fnmatch(m_id, pattern):
                    if h_fn not in target_handlers:
                        target_handlers.append(h_fn)

        if event.event_type == "pre_checkout_query":
            for h in self._pre_checkout_handlers:
                if h not in target_handlers:
                    target_handlers.append(h)

        if event.event_type == "successful_payment":
            for h in self._payment_handlers:
                if h not in target_handlers:
                    target_handlers.append(h)

        if not target_handlers:
            return []

        results: List[Any] = []

        # 5. Execute matched handlers through middleware chain
        for handler in target_handlers:
            async def run_handler(c: Context = ctx, target_fn: HandlerFunc = handler) -> Any:
                res = target_fn(c)
                if inspect.iscoroutine(res):
                    return await res
                return res

            chain = run_handler
            for mw in reversed(self._middlewares):
                next_fn = chain

                def make_step(m: MiddlewareFunc, n: Callable[[], Coroutine[Any, Any, Any]]) -> Callable[[], Coroutine[Any, Any, Any]]:
                    async def step() -> Any:
                        r = m(ctx, n)
                        if inspect.iscoroutine(r):
                            return await r
                        return r
                    return step

                chain = make_step(mw, next_fn)

            try:
                res = await chain()
                results.append(res)
            except Exception as e:
                logger.error("Error running handler %s: %s", getattr(handler, "__name__", str(handler)), e, exc_info=True)

        duration = time.monotonic() - t0
        cmd_name = event.command or event.event_type or "message"
        self.metrics.record_latency(cmd_name, duration)

        return results

    # ------------------------------------------------------------------
    # Abstract / Subclass Interface (to be implemented by platform adapters)
    # ------------------------------------------------------------------

    async def send_message(self, chat_id: str, text: str, **kwargs: Any) -> Any:
        raise NotImplementedError("Platform adapter must implement send_message")

    async def edit_message_text(self, chat_id: str, message_id: str, text: str, **kwargs: Any) -> Any:
        raise NotImplementedError("Platform adapter must implement edit_message_text")

    async def send_photo(self, chat_id: str, photo: Union[str, bytes], caption: Optional[str] = None, **kwargs: Any) -> Any:
        raise NotImplementedError("Platform adapter must implement send_photo")

    async def send_voice(self, chat_id: str, voice: Union[str, bytes], caption: Optional[str] = None, **kwargs: Any) -> Any:
        raise NotImplementedError("Platform adapter must implement send_voice")

    async def send_chat_action(self, chat_id: str, action: str = "typing") -> Any:
        return True

    async def delete_message(self, chat_id: str, message_id: str) -> Any:
        return True

    def run(self) -> None:
        """Run the bot in standard polling or event loop mode."""
        raise NotImplementedError("Platform adapter must implement run")

    def run_webhook(self, port: int = 8443, host: str = "0.0.0.0", path: str = "/webhook") -> None:
        """Run the bot using the built-in C++ WebhookServer."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def webhook_handler(method: str, req_path: str, body: str) -> str:
            if method.upper() == "POST":
                future = asyncio.run_coroutine_threadsafe(self.handle_event(body), loop)
                try:
                    future.result(timeout=10.0)
                except Exception as e:
                    logger.error("Webhook processing error: %s", e)
            return json.dumps({"ok": True})

        self.webhook_server.add_route(path, webhook_handler)
        self.webhook_server.set_default_handler(webhook_handler)

        logger.info("Starting WebhookServer on http://%s:%d%s", host, port, path)
        if not self.webhook_server.start(host, port):
            raise RuntimeError(f"Failed to start WebhookServer on {host}:{port}")

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Stopping WebhookServer...")
        finally:
            self.webhook_server.stop()
            loop.close()
