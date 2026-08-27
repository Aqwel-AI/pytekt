"""
Telegram Bot Adapter for PyTekt Bots.
Delegates event parsing and rate limiting to C++ _core with Telegram Bot API integration.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Union

from .base import Bot, Context, UniversalEvent

import os
import re

logger = logging.getLogger("pytekt.bots.telegram")


class TelegramBot(Bot):
    """
    Telegram Bot adapter extending the core Bot class.

    Parameters
    ----------
    token : str, optional
        Telegram Bot API token from @BotFather. If omitted, loaded from TELEGRAM_BOT_TOKEN env var.
    base_url : str, optional
        API URL root (default 'https://api.telegram.org').
    """

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.telegram.org",
    ) -> None:
        super().__init__(platform="telegram")
        resolved_token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not resolved_token:
            raise ValueError(
                "TelegramBot requires a bot token. Pass it directly (token='...') "
                "or set the TELEGRAM_BOT_TOKEN environment variable."
            )
        self.token = resolved_token.strip()
        self.base_url = base_url.rstrip("/")
        self._api_prefix = f"{self.base_url}/bot{self.token}"
        self._running = False
        self._last_update_id = 0

    def __repr__(self) -> str:
        masked = (self.token[:6] + ":***") if self.token and ":" in self.token else "***"
        return f"TelegramBot(token='{masked}', platform='telegram')"

    # ------------------------------------------------------------------
    # HTTP API Client with Auto-Backoff
    # ------------------------------------------------------------------

    async def _api_call(
        self,
        method: str,
        payload: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Execute a Telegram Bot API method with automatic 429 flood-control backoff.
        """
        url = f"{self._api_prefix}/{method}"
        data = json.dumps(payload or {}).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        for attempt in range(max_retries):
            # Check rate limiter for backoff
            retry_after = self.rate_limiter.get_retry_after("telegram_api")
            if retry_after > 0:
                logger.info("Telegram API in backoff, sleeping for %.2fs", retry_after)
                await asyncio.sleep(retry_after)

            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            try:
                loop = asyncio.get_event_loop()
                response_bytes = await loop.run_in_executor(
                    None,
                    lambda: urllib.request.urlopen(req, timeout=35).read(),
                )
                res = json.loads(response_bytes.decode("utf-8"))
                if res.get("ok"):
                    return res.get("result", {})
                else:
                    err_code = res.get("error_code")
                    if err_code == 429:
                        retry_sec = float(res.get("parameters", {}).get("retry_after", 1.0))
                        self.rate_limiter.record_429("telegram_api", retry_sec)
                        await asyncio.sleep(retry_sec)
                        continue
                    raise RuntimeError(f"Telegram API error {err_code}: {res.get('description')}")

            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8")
                try:
                    err_json = json.loads(body)
                    if err_json.get("error_code") == 429 or e.code == 429:
                        retry_sec = float(err_json.get("parameters", {}).get("retry_after", 1.0))
                        self.rate_limiter.record_429("telegram_api", retry_sec)
                        await asyncio.sleep(retry_sec)
                        continue
                except Exception:
                    pass

                if attempt == max_retries - 1:
                    raise RuntimeError(f"Telegram API HTTP {e.code}: {body}") from e
                await asyncio.sleep(0.5 * (attempt + 1))

            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))

        return {}

    # ------------------------------------------------------------------
    # Bot API Methods
    # ------------------------------------------------------------------

    async def send_message(
        self,
        chat_id: Union[str, int],
        text: str,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[Union[str, int]] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send a text message."""
        payload: Dict[str, Any] = {
            "chat_id": str(chat_id),
            "text": str(text),
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_to_message_id:
            try:
                payload["reply_to_message_id"] = int(reply_to_message_id)
            except (ValueError, TypeError):
                pass
        if reply_markup:
            payload["reply_markup"] = reply_markup
        payload.update(kwargs)
        return await self._api_call("sendMessage", payload)

    async def edit_message_text(
        self,
        chat_id: Union[str, int],
        message_id: Union[str, int],
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Edit an existing message."""
        payload: Dict[str, Any] = {
            "chat_id": str(chat_id),
            "message_id": int(message_id),
            "text": str(text),
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = reply_markup
        payload.update(kwargs)
        return await self._api_call("editMessageText", payload)

    async def send_photo(
        self,
        chat_id: Union[str, int],
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[Union[str, int]] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send a photo by URL, file_id, or multipart."""
        payload: Dict[str, Any] = {
            "chat_id": str(chat_id),
            "photo": photo if isinstance(photo, str) else "",
        }
        if caption:
            payload["caption"] = caption
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_to_message_id:
            try:
                payload["reply_to_message_id"] = int(reply_to_message_id)
            except (ValueError, TypeError):
                pass
        if reply_markup:
            payload["reply_markup"] = reply_markup
        payload.update(kwargs)
        return await self._api_call("sendPhoto", payload)

    async def send_voice(
        self,
        chat_id: Union[str, int],
        voice: Union[str, bytes],
        caption: Optional[str] = None,
        duration: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send a voice audio note."""
        payload: Dict[str, Any] = {
            "chat_id": str(chat_id),
            "voice": voice if isinstance(voice, str) else "",
        }
        if caption:
            payload["caption"] = caption
        if duration:
            payload["duration"] = duration
        payload.update(kwargs)
        return await self._api_call("sendVoice", payload)

    async def send_chat_action(
        self,
        chat_id: Union[str, int],
        action: str = "typing",
    ) -> Dict[str, Any]:
        """Send chat action status (typing, upload_photo, record_voice, etc.)."""
        payload = {
            "chat_id": str(chat_id),
            "action": action,
        }
        return await self._api_call("sendChatAction", payload)

    async def delete_message(
        self,
        chat_id: Union[str, int],
        message_id: Union[str, int],
    ) -> Dict[str, Any]:
        """Delete a message."""
        payload = {
            "chat_id": str(chat_id),
            "message_id": int(message_id),
        }
        return await self._api_call("deleteMessage", payload)

    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 30,
    ) -> List[Dict[str, Any]]:
        """Fetch updates from Telegram using long polling."""
        payload: Dict[str, Any] = {"limit": limit, "timeout": timeout}
        if offset is not None:
            payload["offset"] = offset
        res = await self._api_call("getUpdates", payload)
        return res if isinstance(res, list) else []

    async def set_webhook(
        self,
        url: str,
        certificate: Optional[str] = None,
        max_connections: int = 40,
        drop_pending_updates: bool = False,
    ) -> Dict[str, Any]:
        """Set Telegram webhook URL."""
        payload: Dict[str, Any] = {
            "url": url,
            "max_connections": max_connections,
            "drop_pending_updates": drop_pending_updates,
        }
        if certificate:
            payload["certificate"] = certificate
        return await self._api_call("setWebhook", payload)

    async def delete_webhook(self, drop_pending_updates: bool = False) -> Dict[str, Any]:
        """Delete Telegram webhook."""
        return await self._api_call("deleteWebhook", {"drop_pending_updates": drop_pending_updates})

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
    ) -> Dict[str, Any]:
        """Send a native Telegram payment invoice."""
        price_objs = [
            p.to_dict() if hasattr(p, "to_dict") else {"label": p.get("label", ""), "amount": int(p.get("amount", 0))}
            for p in prices
        ]
        body: Dict[str, Any] = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "currency": currency.upper(),
            "prices": price_objs,
            **kwargs,
        }
        return await self._api_call("sendInvoice", body)

    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool = True,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Confirm or reject a Telegram pre-checkout payment query."""
        body: Dict[str, Any] = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok,
        }
        if error_message:
            body["error_message"] = error_message
        return await self._api_call("answerPreCheckoutQuery", body)

    # ------------------------------------------------------------------
    # Polling & Execution
    # ------------------------------------------------------------------

    async def start_polling(self, poll_interval: float = 0.1, timeout: int = 30) -> None:
        """Start long-polling loop."""
        self._running = True
        logger.info("TelegramBot started polling...")

        # Clear any existing webhook to enable getUpdates
        try:
            await self.delete_webhook()
        except Exception:
            pass

        while self._running:
            try:
                updates = await self.get_updates(
                    offset=self._last_update_id + 1 if self._last_update_id > 0 else None,
                    timeout=timeout,
                )
                for update in updates:
                    up_id = update.get("update_id", 0)
                    if up_id > self._last_update_id:
                        self._last_update_id = up_id

                    # Zero-copy parse in C++ dispatcher and process asynchronously
                    asyncio.create_task(self.handle_event(json.dumps(update)))

                if poll_interval > 0:
                    await asyncio.sleep(poll_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Polling error: %s", e)
                await asyncio.sleep(2.0)

    def run(self) -> None:
        """Run the bot with long polling until interrupted."""
        try:
            asyncio.run(self.start_polling())
        except KeyboardInterrupt:
            logger.info("TelegramBot stopped.")
        finally:
            self._running = False
