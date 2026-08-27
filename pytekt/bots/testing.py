"""
In-memory Testing Client for PyTekt Bots.
Allows developers to send synthetic messages and assert on bot replies without network connections.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union

from ._core import UniversalEvent

if TYPE_CHECKING:
    from .base import Bot


@dataclass
class TestResponse:
    """A captured outgoing response from the bot."""
    method: str
    chat_id: str
    text: str = ""
    caption: str = ""
    ui: Optional[Any] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[Dict[str, Any]] = None
    embeds: Optional[List[Dict[str, Any]]] = None
    components: Optional[List[Dict[str, Any]]] = None
    photo: Optional[Union[str, bytes]] = None
    voice: Optional[Union[str, bytes]] = None
    message_id: str = "1"
    raw_payload: Dict[str, Any] = field(default_factory=dict)

    def has_button(self, label_or_callback: str) -> bool:
        """Check if response contains a button with given label or callback ID."""
        if self.reply_markup and "inline_keyboard" in self.reply_markup:
            for row in self.reply_markup["inline_keyboard"]:
                for b in row:
                    text = b.get("text", "")
                    cb = b.get("callback_data", "")
                    if label_or_callback == text or label_or_callback in text or label_or_callback == cb:
                        return True
        if self.components:
            for row in self.components:
                for c in row.get("components", []):
                    lbl = c.get("label", "")
                    cid = c.get("custom_id", "")
                    if label_or_callback == lbl or label_or_callback in lbl or label_or_callback == cid:
                        return True
        return False

    def has_text(self, substring: str) -> bool:
        """Check if substring appears in message text, caption, embeds, or payload."""
        if substring in self.text or substring in self.caption:
            return True
        if self.embeds:
            for emb in self.embeds:
                if substring in str(emb.get("title", "")) or substring in str(emb.get("description", "")):
                    return True
                for f in emb.get("fields", []):
                    if substring in str(f.get("name", "")) or substring in str(f.get("value", "")):
                        return True
        return False


class BotTestClient:
    """
    In-memory test harness for PyTekt Bot instances.

    Parameters
    ----------
    bot : Bot
        The bot instance under test.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.responses: List[TestResponse] = []
        self._msg_counter = 1000

        # Intercept outgoing bot messaging methods
        self._orig_send_message = bot.send_message
        self._orig_edit_message_text = bot.edit_message_text
        self._orig_send_photo = bot.send_photo
        self._orig_send_voice = bot.send_voice

        bot.send_message = self._mock_send_message  # type: ignore[assignment]
        bot.edit_message_text = self._mock_edit_message_text  # type: ignore[assignment]
        bot.send_photo = self._mock_send_photo  # type: ignore[assignment]
        bot.send_voice = self._mock_send_voice  # type: ignore[assignment]

    def _next_msg_id(self) -> str:
        self._msg_counter += 1
        return str(self._msg_counter)

    async def _mock_send_message(self, chat_id: str, text: str = "", **kwargs: Any) -> Dict[str, Any]:
        msg_id = self._next_msg_id()
        resp = TestResponse(
            method="sendMessage",
            chat_id=str(chat_id),
            text=str(text),
            reply_markup=kwargs.get("reply_markup"),
            embeds=kwargs.get("embeds"),
            components=kwargs.get("components"),
            parse_mode=kwargs.get("parse_mode"),
            message_id=msg_id,
            raw_payload=kwargs,
        )
        self.responses.append(resp)
        return {"id": msg_id, "message_id": int(msg_id) if msg_id.isdigit() else msg_id, "text": text}

    async def _mock_edit_message_text(self, chat_id: str, message_id: str, text: str = "", **kwargs: Any) -> Dict[str, Any]:
        resp = TestResponse(
            method="editMessageText",
            chat_id=str(chat_id),
            message_id=str(message_id),
            text=str(text),
            reply_markup=kwargs.get("reply_markup"),
            embeds=kwargs.get("embeds"),
            components=kwargs.get("components"),
            parse_mode=kwargs.get("parse_mode"),
            raw_payload=kwargs,
        )
        self.responses.append(resp)
        return {"id": str(message_id), "message_id": message_id, "text": text}

    async def _mock_send_photo(self, chat_id: str, photo: Union[str, bytes], caption: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        msg_id = self._next_msg_id()
        resp = TestResponse(
            method="sendPhoto",
            chat_id=str(chat_id),
            photo=photo,
            caption=caption or "",
            text=caption or "",
            reply_markup=kwargs.get("reply_markup"),
            parse_mode=kwargs.get("parse_mode"),
            message_id=msg_id,
            raw_payload=kwargs,
        )
        self.responses.append(resp)
        return {"id": msg_id, "message_id": int(msg_id) if msg_id.isdigit() else msg_id, "caption": caption}

    async def _mock_send_voice(self, chat_id: str, voice: Union[str, bytes], caption: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        msg_id = self._next_msg_id()
        resp = TestResponse(
            method="sendVoice",
            chat_id=str(chat_id),
            voice=voice,
            caption=caption or "",
            text=caption or "",
            message_id=msg_id,
            raw_payload=kwargs,
        )
        self.responses.append(resp)
        return {"id": msg_id, "message_id": int(msg_id) if msg_id.isdigit() else msg_id}

    @property
    def last_reply(self) -> Optional[TestResponse]:
        """Return the most recent outgoing response from the bot."""
        return self.responses[-1] if self.responses else None

    @property
    def replies(self) -> List[TestResponse]:
        """Return all recorded responses."""
        return self.responses

    def clear(self) -> None:
        """Clear recorded responses."""
        self.responses.clear()

    async def send_message(
        self,
        text: str,
        chat_id: str = "test_chat",
        user_id: str = "test_user",
        metadata: Optional[Dict[str, str]] = None,
    ) -> List[TestResponse]:
        """Send a plain text message to the bot and return new responses."""
        start_idx = len(self.responses)
        ev = UniversalEvent(
            id=self._next_msg_id(),
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            platform=self.bot.platform,
            event_type="message",
            metadata=metadata or {},
        )
        await self.bot.handle_event(ev)
        return self.responses[start_idx:]

    async def send_command(
        self,
        command: str,
        args: Optional[Sequence[str]] = None,
        chat_id: str = "test_chat",
        user_id: str = "test_user",
        metadata: Optional[Dict[str, str]] = None,
    ) -> List[TestResponse]:
        """Send a slash/exclamation command to the bot and return new responses."""
        start_idx = len(self.responses)
        clean_cmd = command.lstrip("/!")
        arg_list = list(args or [])
        text = f"/{clean_cmd} " + " ".join(arg_list) if arg_list else f"/{clean_cmd}"
        ev = UniversalEvent(
            id=self._next_msg_id(),
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            command=clean_cmd,
            args=arg_list,
            platform=self.bot.platform,
            event_type="command",
            metadata=metadata or {},
        )
        await self.bot.handle_event(ev)
        return self.responses[start_idx:]

    async def click_button(
        self,
        callback_id: str,
        chat_id: str = "test_chat",
        user_id: str = "test_user",
        message_id: str = "1001",
        metadata: Optional[Dict[str, str]] = None,
    ) -> List[TestResponse]:
        """Simulate an inline button click or component interaction."""
        start_idx = len(self.responses)
        meta = {"message_id": message_id}
        if metadata:
            meta.update(metadata)

        ev = UniversalEvent(
            id=self._next_msg_id(),
            chat_id=chat_id,
            user_id=user_id,
            text=callback_id,
            platform=self.bot.platform,
            event_type="callback" if self.bot.platform == "telegram" else "interaction",
            metadata=meta,
        )
        await self.bot.handle_event(ev)
        return self.responses[start_idx:]

    send_button = click_button

    async def submit_modal(
        self,
        custom_id: str,
        fields: Dict[str, str],
        chat_id: str = "test_chat",
        user_id: str = "test_user",
    ) -> List[TestResponse]:
        """Simulate a modal form submission."""
        start_idx = len(self.responses)
        ev = UniversalEvent(
            id=self._next_msg_id(),
            chat_id=chat_id,
            user_id=user_id,
            text=custom_id,
            platform=self.bot.platform,
            event_type="modal_submit",
            metadata=fields,
        )
        await self.bot.handle_event(ev)
        return self.responses[start_idx:]
