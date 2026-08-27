"""
Cross-platform Card component compiling to native Discord Embeds or Telegram rich formatted text and photos.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .components import UIComponent, parse_color
from .keyboard import Keyboard


class Card(UIComponent):
    """
    Cross-platform rich media card.
    Compiles to a native Discord Embed, or formatted text + photo on Telegram.

    Parameters
    ----------
    title : str, optional
        Header title of the card.
    description : str, optional
        Main body description text.
    image : str, optional
        URL or file path of an image to display.
    fields : Dict[str, str] or Sequence[Tuple[str, str, bool]], optional
        Key-value field pairs (or tuples of (name, value, is_inline)).
    color : int or str, optional
        Accent color (e.g. 0x3498DB, '#3498db', 'gold', 'success').
    footer : str, optional
        Footer text at the bottom of the card.
    url : str, optional
        Hyperlink URL attached to the title.
    thumbnail : str, optional
        Small thumbnail image URL (displayed on the side on Discord).
    keyboard : Keyboard, optional
        Interactive button keyboard attached to the card.
    """

    def __init__(
        self,
        title: str = "",
        description: str = "",
        *,
        image: Optional[str] = None,
        fields: Optional[Union[Dict[str, str], Sequence[Union[Tuple[str, str], Tuple[str, str, bool]]]]] = None,
        color: Union[int, str] = "primary",
        footer: Optional[str] = None,
        url: Optional[str] = None,
        thumbnail: Optional[str] = None,
        keyboard: Optional[Keyboard] = None,
    ) -> None:
        self.title = title
        self.description = description
        self.image = image
        self.color = parse_color(color)
        self.footer = footer
        self.url = url
        self.thumbnail = thumbnail
        self.keyboard = keyboard

        self._fields: List[Dict[str, Any]] = []
        if fields:
            if isinstance(fields, dict):
                for k, v in fields.items():
                    self.add_field(str(k), str(v), inline=True)
            else:
                for item in fields:
                    if len(item) == 2:
                        self.add_field(str(item[0]), str(item[1]), inline=True)
                    elif len(item) == 3:
                        self.add_field(str(item[0]), str(item[1]), inline=bool(item[2]))

    def add_field(self, name: str, value: str, inline: bool = True) -> Card:
        """Add a field to the card."""
        self._fields.append({
            "name": name,
            "value": value,
            "inline": inline,
        })
        return self

    def to_discord(self) -> Dict[str, Any]:
        """Compile to native Discord Embed payload."""
        embed: Dict[str, Any] = {
            "title": self.title,
            "description": self.description,
            "color": self.color,
        }
        if self.url:
            embed["url"] = self.url
        if self.image:
            embed["image"] = {"url": self.image}
        if self.thumbnail:
            embed["thumbnail"] = {"url": self.thumbnail}
        if self.footer:
            embed["footer"] = {"text": self.footer}
        if self._fields:
            embed["fields"] = self._fields

        payload: Dict[str, Any] = {"embed": embed}
        if self.keyboard:
            payload["components"] = self.keyboard.to_discord()
        return payload

    def to_telegram(self) -> Dict[str, Any]:
        """
        Compile to Telegram payload (formatted HTML text + photo if available).
        Silently degrades Discord embeds into clean, formatted Telegram HTML.
        """
        lines: List[str] = []

        if self.title:
            if self.url:
                lines.append(f'<b><a href="{self.url}">{self.title}</a></b>')
            else:
                lines.append(f"<b>{self.title}</b>")
            lines.append("")

        if self.description:
            lines.append(self.description)
            lines.append("")

        if self._fields:
            for f in self._fields:
                lines.append(f"• <b>{f['name']}</b>: {f['value']}")
            lines.append("")

        if self.footer:
            lines.append(f"<i>{self.footer}</i>")

        formatted_text = "\n".join(lines).strip()

        payload: Dict[str, Any] = {
            "parse_mode": "HTML",
        }

        if self.image:
            payload["photo"] = self.image
            payload["caption"] = formatted_text
            payload["text"] = formatted_text
        else:
            payload["text"] = formatted_text

        if self.keyboard:
            payload["reply_markup"] = self.keyboard.to_telegram()

        return payload

    def __repr__(self) -> str:
        return f"Card(title='{self.title}', fields={len(self._fields)}, image={bool(self.image)})"
