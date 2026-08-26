"""
Discord Bot Adapter for PyTekt Bots.
Normalizes Discord Gateway / Webhook / Interaction events into UniversalEvent
and delegates hot-path routing and rate limiting to the C++ _core.
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

logger = logging.getLogger("pytekt.bots.discord")


class DiscordBot(Bot):
    """
    Discord Bot adapter extending the core Bot class.

    Parameters
    ----------
    token : str
        Discord Bot Token (e.g. from Discord Developer Portal).
    base_url : str, optional
        API URL root (default 'https://discord.com/api/v10').
    """

    def __init__(
        self,
        token: str,
        base_url: str = "https://discord.com/api/v10",
    ) -> None:
        super().__init__(platform="discord")
        self.token = token.strip()
        self.base_url = base_url.rstrip("/")
        self._running = False

    async def _api_call(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Execute a Discord REST API call with flood-control handling."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        data = json.dumps(payload or {}).encode("utf-8") if payload is not None else None
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "PyTekt-Bots (https://github.com/Aqwel-AI/pytekt, 0.2.1)",
        }

        for attempt in range(max_retries):
            retry_after = self.rate_limiter.get_retry_after("discord_api")
            if retry_after > 0:
                await asyncio.sleep(retry_after)

            req = urllib.request.Request(url, data=data, headers=headers, method=method)

            try:
                loop = asyncio.get_event_loop()
                response_bytes = await loop.run_in_executor(
                    None,
                    lambda: urllib.request.urlopen(req, timeout=30).read(),
                )
                if response_bytes:
                    return json.loads(response_bytes.decode("utf-8"))
                return {}

            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8")
                try:
                    err_json = json.loads(body)
                    if e.code == 429 or "retry_after" in err_json:
                        retry_sec = float(err_json.get("retry_after", 1.0))
                        self.rate_limiter.record_429("discord_api", retry_sec)
                        await asyncio.sleep(retry_sec)
                        continue
                except Exception:
                    pass

                if attempt == max_retries - 1:
                    raise RuntimeError(f"Discord API HTTP {e.code}: {body}") from e
                await asyncio.sleep(0.5 * (attempt + 1))

            except Exception:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))

        return {}

    async def send_message(
        self,
        chat_id: Union[str, int],
        text: str,
        reply_to_message_id: Optional[Union[str, int]] = None,
        embeds: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send a message to a Discord channel (chat_id = channel_id)."""
        payload: Dict[str, Any] = {
            "content": str(text),
        }
        if reply_to_message_id:
            payload["message_reference"] = {"message_id": str(reply_to_message_id)}
        if embeds:
            payload["embeds"] = embeds
        payload.update(kwargs)
        return await self._api_call("POST", f"/channels/{chat_id}/messages", payload)

    async def edit_message_text(
        self,
        chat_id: Union[str, int],
        message_id: Union[str, int],
        text: str,
        embeds: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Edit an existing Discord message."""
        payload: Dict[str, Any] = {
            "content": str(text),
        }
        if embeds is not None:
            payload["embeds"] = embeds
        payload.update(kwargs)
        return await self._api_call("PATCH", f"/channels/{chat_id}/messages/{message_id}", payload)

    async def send_chat_action(
        self,
        chat_id: Union[str, int],
        action: str = "typing",
    ) -> Dict[str, Any]:
        """Trigger typing indicator in channel."""
        return await self._api_call("POST", f"/channels/{chat_id}/typing", {})

    async def delete_message(
        self,
        chat_id: Union[str, int],
        message_id: Union[str, int],
    ) -> Dict[str, Any]:
        """Delete a message in a channel."""
        return await self._api_call("DELETE", f"/channels/{chat_id}/messages/{message_id}")

    def run(self) -> None:
        """Run Discord bot via Webhook listener or mock Gateway."""
        logger.info("DiscordBot running in webhook/gateway mode. Use bot.run_webhook(...) for webhooks.")
        self.run_webhook(port=8443, host="0.0.0.0", path="/discord")
