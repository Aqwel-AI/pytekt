"""
Platform-agnostic Bot and Context base classes.
High-performance core dispatching delegating to C++ _core with Python decorators.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import json
import logging
import time
from typing import Any, Callable, Coroutine, Dict, List, Optional, Sequence, Union

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

logger = logging.getLogger("pytekt.bots")

HandlerFunc = Callable[..., Any]
MiddlewareFunc = Callable[..., Any]


class Context:
    """
    Context wrapping a normalized UniversalEvent and providing convenience methods
    for replying, sending media, managing FSM state, and streaming AI responses.
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

    def _fsm_key(self) -> str:
        return f"{self.chat_id}:{self.user_id}" if self.user_id else self.chat_id

    # ------------------------------------------------------------------
    # FSM State & Session helpers
    # ------------------------------------------------------------------

    async def get_state(self) -> str:
        return self.bot.fsm.get_state(self._fsm_key())

    async def set_state(self, state: str, ttl: float = 0.0) -> None:
        self.bot.fsm.set_state(self._fsm_key(), state, ttl)

    async def clear_state(self) -> None:
        self.bot.fsm.clear_state(self._fsm_key())

    async def get_data(self, key: str) -> str:
        return self.bot.fsm.get_data(self._fsm_key(), key)

    async def set_data(self, key: str, value: str, ttl: float = 0.0) -> None:
        self.bot.fsm.set_data(self._fsm_key(), key, value, ttl)

    async def get_all_data(self) -> Dict[str, str]:
        return self.bot.fsm.get_all_data(self._fsm_key())

    async def clear_data(self) -> None:
        self.bot.fsm.clear_data(self._fsm_key())

    # ------------------------------------------------------------------
    # Messaging & Action helpers
    # ------------------------------------------------------------------

    async def reply(self, text: str, **kwargs: Any) -> Any:
        """Send a reply to the originating chat."""
        return await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_to_message_id=self.id or None,
            **kwargs,
        )

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
                    msg_id = getattr(first_msg, "id", None) or getattr(first_msg, "message_id", None) or str(first_msg)
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
                msg_id = getattr(first_msg, "id", None) or getattr(first_msg, "message_id", None) or str(first_msg)
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
    Dispatcher, RateLimiter, FSM, in-process Cache, WebhookServer, AntiSpam, Metrics.
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

        self._handlers: Dict[str, HandlerFunc] = {}
        self._middlewares: List[MiddlewareFunc] = []
        self._handler_counter = 0

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
        if not handler_ids:
            return []

        results: List[Any] = []

        # 4. Execute matched handlers through middleware chain
        for hid in handler_ids:
            handler = self._handlers.get(hid)
            if not handler:
                continue

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
                logger.error("Error running handler %s: %s", hid, e, exc_info=True)

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
