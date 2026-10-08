"""
Slack Bot Adapter for PyTekt Bots.
Normalizes Slack Events API, Slash Commands, and Interactive Block Actions
into UniversalEvent and delegates hot-path routing and rate limiting to the core engine.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Sequence, Union

from .base import Bot, Context, UniversalEvent

logger = logging.getLogger("pytekt.bots.slack")


class SlackBot(Bot):
    """
    Slack Bot adapter normalizing Events API, Slash Commands, and Block Actions into UniversalEvents.

    Parameters
    ----------
    token : str, optional
        Slack Bot OAuth Token (xoxb-...). If omitted, read from SLACK_BOT_TOKEN environment variable.
    signing_secret : str, optional
        Slack Signing Secret for request verification. If omitted, read from SLACK_SIGNING_SECRET.
    base_url : str, default="https://slack.com/api"
        Slack Web API base endpoint.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        signing_secret: Optional[str] = None,
        base_url: str = "https://slack.com/api",
    ) -> None:
        super().__init__(platform="slack")
        resolved_token = token or os.environ.get("SLACK_BOT_TOKEN", "")
        if not resolved_token:
            raise ValueError(
                "SlackBot requires a bot token. Pass token='xoxb-...' or set "
                "the SLACK_BOT_TOKEN environment variable."
            )
        self.token = resolved_token.strip()
        self.signing_secret = signing_secret or os.environ.get("SLACK_SIGNING_SECRET", "")
        self.base_url = base_url.rstrip("/")

    def __repr__(self) -> str:
        masked = (self.token[:6] + "***") if self.token and len(self.token) > 6 else "***"
        return f"SlackBot(token='{masked}', platform='slack')"

    def verify_signature(
        self,
        timestamp: Union[str, int],
        body_bytes: bytes,
        signature: str,
    ) -> bool:
        """
        Verify incoming request signature from Slack using HMAC-SHA256.

        Parameters
        ----------
        timestamp : str or int
            Value from 'X-Slack-Request-Timestamp' header.
        body_bytes : bytes
            Raw HTTP request body.
        signature : str
            Value from 'X-Slack-Signature' header (starts with 'v0=').
        """
        if not self.signing_secret:
            return True  # If no signing secret provided, skip validation

        # Anti-replay: request should not be older than 5 minutes
        try:
            ts_int = int(timestamp)
            if abs(time.time() - ts_int) > 300:
                logger.warning("Slack signature verification failed: timestamp drift > 300s")
                return False
        except (ValueError, TypeError):
            return False

        sig_basestring = f"v0:{timestamp}:".encode("utf-8") + body_bytes
        computed = "v0=" + hmac.new(
            self.signing_secret.encode("utf-8"),
            sig_basestring,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(computed, signature)

    async def _api_call(
        self,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Execute a Slack Web API call with token authorization and flood-control handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        data = json.dumps(payload or {}).encode("utf-8") if payload is not None else None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "PyTekt-Bots (https://github.com/Aqwel-AI/pytekt, 0.2.1)",
        }

        for attempt in range(max_retries):
            retry_after = self.rate_limiter.get_retry_after("slack_api")
            if retry_after > 0:
                await asyncio.sleep(retry_after)

            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            try:
                loop = asyncio.get_event_loop()
                response_bytes = await loop.run_in_executor(
                    None,
                    lambda: urllib.request.urlopen(req, timeout=30).read(),
                )
                if response_bytes:
                    res_json = json.loads(response_bytes.decode("utf-8"))
                    if not res_json.get("ok", False):
                        err = res_json.get("error", "unknown_error")
                        if err == "ratelimited":
                            self.rate_limiter.record_429("slack_api", 1.0)
                            await asyncio.sleep(1.0)
                            continue
                        logger.warning("Slack API returned error: %s", err)
                    return res_json
                return {}

            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8")
                retry_sec = e.headers.get("Retry-After")
                if retry_sec:
                    try:
                        wait = float(retry_sec)
                        self.rate_limiter.record_429("slack_api", wait)
                        await asyncio.sleep(wait)
                        continue
                    except Exception:
                        pass

                if attempt == max_retries - 1:
                    raise RuntimeError(f"Slack API HTTP {e.code}: {body}") from e
                await asyncio.sleep(0.5 * (attempt + 1))

            except Exception:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))

        return {}

    async def send_message(
        self,
        chat_id: Union[str, int],
        text: str = "",
        blocks: Optional[List[Dict[str, Any]]] = None,
        thread_ts: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel or DM (chat_id = channel ID).
        """
        payload: Dict[str, Any] = {
            "channel": str(chat_id),
            "text": str(text) if text else "",
        }
        if blocks:
            payload["blocks"] = blocks
        if thread_ts:
            payload["thread_ts"] = str(thread_ts)
        payload.update(kwargs)
        return await self._api_call("chat.postMessage", payload)

    async def edit_message_text(
        self,
        chat_id: Union[str, int],
        message_id: Union[str, int],
        text: str = "",
        blocks: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Edit an existing message in a Slack channel (message_id = message 'ts' timestamp).
        """
        payload: Dict[str, Any] = {
            "channel": str(chat_id),
            "ts": str(message_id),
            "text": str(text) if text else "",
        }
        if blocks is not None:
            payload["blocks"] = blocks
        payload.update(kwargs)
        return await self._api_call("chat.update", payload)

    async def delete_message(
        self,
        chat_id: Union[str, int],
        message_id: Union[str, int],
    ) -> Dict[str, Any]:
        """Delete a message from a Slack channel (message_id = message 'ts' timestamp)."""
        payload = {
            "channel": str(chat_id),
            "ts": str(message_id),
        }
        return await self._api_call("chat.delete", payload)

    async def send_chat_action(
        self,
        chat_id: Union[str, int],
        action: str = "typing",
    ) -> Dict[str, Any]:
        """No-op on standard Slack Web API (typing indicators are supported via RTM/WebSocket)."""
        return {"ok": True}

    def parse_webhook_payload(self, raw_data: Union[str, bytes, Dict[str, Any]]) -> Optional[UniversalEvent]:
        """
        Normalize a raw Slack payload (Events API, Slash Commands, or Interactive Actions)
        into a UniversalEvent.
        """
        if isinstance(raw_data, (str, bytes)):
            try:
                data = json.loads(raw_data)
            except Exception:
                # May be application/x-www-form-urlencoded (Slash commands or interactive actions)
                parsed = urllib.parse.parse_qs(
                    raw_data.decode("utf-8") if isinstance(raw_data, bytes) else raw_data
                )
                if "command" in parsed:
                    cmd_name = parsed["command"][0]
                    text = parsed.get("text", [""])[0]
                    full_text = f"{cmd_name} {text}".strip()
                    user_id = parsed.get("user_id", [""])[0]
                    channel_id = parsed.get("channel_id", [""])[0]
                    meta = {k: str(v[0]) for k, v in parsed.items()}
                    return UniversalEvent(
                        id=f"cmd_{int(time.time()*1000)}",
                        platform="slack",
                        event_type="command",
                        user_id=user_id,
                        chat_id=channel_id,
                        text=full_text,
                        command=cmd_name.lstrip("/"),
                        metadata=meta,
                    )
                if "payload" in parsed:
                    try:
                        data = json.loads(parsed["payload"][0])
                    except Exception:
                        return None
                else:
                    return None
        else:
            data = raw_data

        if not isinstance(data, dict):
            return None

        # 1. URL Verification challenge
        if data.get("type") == "url_verification":
            ch = str(data.get("challenge", ""))
            return UniversalEvent(
                id="url_verification",
                platform="slack",
                event_type="system",
                user_id="",
                chat_id="",
                text=ch,
                metadata={"challenge": ch},
            )

        # 2. Events API event_callback
        if data.get("type") == "event_callback":
            ev = data.get("event", {})
            ev_type = ev.get("type", "message")
            user_id = str(ev.get("user", ""))
            channel_id = str(ev.get("channel", ""))
            text = str(ev.get("text", ""))
            msg_ts = str(ev.get("ts", ""))

            # Avoid processing bot's own messages
            if ev.get("bot_id") or ev.get("subtype") == "bot_message":
                return None

            # Detect command
            command = ""
            if text.startswith("/"):
                command = text.split()[0].lstrip("/")

            meta = {
                "message_id": msg_ts,
                "thread_ts": str(ev.get("thread_ts") or ""),
            }

            return UniversalEvent(
                id=msg_ts or str(int(time.time() * 1000)),
                platform="slack",
                event_type="command" if command else "message",
                user_id=user_id,
                chat_id=channel_id,
                text=text,
                command=command,
                metadata=meta,
            )

        # 3. Interactive Block Actions
        if data.get("type") == "block_actions":
            user_id = str(data.get("user", {}).get("id", ""))
            channel_id = str(data.get("channel", {}).get("id", ""))
            actions = data.get("actions", [])
            action_id = str(actions[0].get("action_id", "")) if actions else ""
            action_value = str(actions[0].get("value", "")) if actions else ""
            msg_ts = str(data.get("message", {}).get("ts", ""))

            meta = {
                "callback_id": action_id,
                "action_id": action_id,
                "message_id": msg_ts,
            }

            return UniversalEvent(
                id=str(int(time.time() * 1000)),
                platform="slack",
                event_type="callback",
                user_id=user_id,
                chat_id=channel_id,
                text=action_value or action_id,
                command="",
                metadata=meta,
            )

        return None

    async def handle_webhook_payload(
        self,
        raw_body: Union[str, bytes],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Process an incoming Slack webhook request.
        Handles URL verification challenge automatically or dispatches event.
        """
        body_bytes = raw_body.encode("utf-8") if isinstance(raw_body, str) else raw_body

        if headers and self.signing_secret:
            timestamp = headers.get("X-Slack-Request-Timestamp") or headers.get("x-slack-request-timestamp", "")
            signature = headers.get("X-Slack-Signature") or headers.get("x-slack-signature", "")
            if not self.verify_signature(timestamp, body_bytes, signature):
                return {"error": "invalid_signature", "status_code": 401}

        event = self.parse_webhook_payload(body_bytes)
        if event is None:
            return {"ok": True}

        # Respond to URL verification immediately
        if event.id == "url_verification":
            return {"challenge": event.text}

        await self.handle_event(event)
        return {"ok": True}

    def run(self) -> None:
        """Run Slack bot via Webhook listener."""
        logger.info("SlackBot running in webhook mode. Use bot.run_webhook(...) for custom host/port.")
        self.run_webhook(port=8443, host="0.0.0.0", path="/slack/events")
