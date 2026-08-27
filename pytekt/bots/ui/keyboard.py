"""
Cross-platform Button and Keyboard components compiling to Telegram Inline Keyboards
and Discord ActionRow Button components.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .components import UIComponent


# Discord Button Style mappings (1: Primary, 2: Secondary, 3: Success, 4: Danger, 5: Link)
DISCORD_BUTTON_STYLES: Dict[str, int] = {
    "primary": 1,
    "blurple": 1,
    "secondary": 2,
    "grey": 2,
    "gray": 2,
    "success": 3,
    "green": 3,
    "danger": 4,
    "red": 4,
    "link": 5,
}


class Button:
    """
    A single clickable button inside a Keyboard row.

    Parameters
    ----------
    label : str
        The user-visible text on the button.
    callback_id : str, optional
        Unique ID returned when the button is clicked. Handled via `@bot.on_button(callback_id)`.
    url : str, optional
        External URL to open in a web browser when clicked.
    web_app_url : str, optional
        URL of a mini-app to open inside the chat client (Telegram WebApp / Discord Activity).
    style : str, optional
        Visual style: 'primary' (default), 'secondary', 'success', 'danger', or 'link'.
    """

    def __init__(
        self,
        label: str,
        callback_id: Optional[str] = None,
        *,
        url: Optional[str] = None,
        web_app_url: Optional[str] = None,
        style: str = "primary",
    ) -> None:
        self.label = label
        self.callback_id = callback_id or (label.lower().replace(" ", "_") if not url and not web_app_url else "")
        self.url = url
        self.web_app_url = web_app_url
        self.style = style.lower().strip()

    @classmethod
    def from_item(cls, item: Union[Button, Tuple[str, str], str]) -> Button:
        """Convert a tuple (label, callback_id) or Button instance into a Button."""
        if isinstance(item, Button):
            return item
        if isinstance(item, tuple):
            if len(item) == 2:
                return cls(label=item[0], callback_id=item[1])
            elif len(item) == 3:
                return cls(label=item[0], callback_id=item[1], style=item[2])
        if isinstance(item, str):
            return cls(label=item, callback_id=item.lower().replace(" ", "_"))
        raise ValueError(f"Cannot convert item {item!r} to Button")

    def to_telegram(self) -> Dict[str, Any]:
        """Compile into Telegram inline keyboard button dict."""
        btn: Dict[str, Any] = {"text": self.label}
        if self.web_app_url:
            btn["web_app"] = {"url": self.web_app_url}
        elif self.url:
            btn["url"] = self.url
        else:
            btn["callback_data"] = self.callback_id
        return btn

    def to_discord(self) -> Dict[str, Any]:
        """Compile into Discord component button dict."""
        btn: Dict[str, Any] = {
            "type": 2,  # Button component
            "label": self.label,
        }
        if self.web_app_url or self.url:
            btn["style"] = 5  # Link style
            btn["url"] = self.web_app_url or self.url
        else:
            btn["style"] = DISCORD_BUTTON_STYLES.get(self.style, 1)
            btn["custom_id"] = self.callback_id
        return btn

    def __repr__(self) -> str:
        return f"Button(label='{self.label}', callback_id='{self.callback_id}', style='{self.style}')"


class Keyboard(UIComponent):
    """
    Cross-platform Keyboard container for interactive buttons.
    Compiles to Telegram Inline Keyboard markup or Discord ActionRow components.

    Parameters
    ----------
    rows : Sequence[Sequence[Union[Button, Tuple[str, str]]]], optional
        2D grid of buttons.

    Examples
    --------
    >>> kb = Keyboard([
    ...     [("Option 1", "opt_1"), ("Option 2", "opt_2")],
    ...     [Button("Visit Docs", url="https://aqwelai.xyz")]
    ... ])
    """

    def __init__(
        self,
        rows: Optional[Sequence[Sequence[Union[Button, Tuple[str, str], str]]]] = None,
    ) -> None:
        self.rows: List[List[Button]] = []
        if rows:
            for row in rows:
                self.rows.append([Button.from_item(b) for b in row])

    @classmethod
    def web_app_button(cls, label: str, url: str) -> Button:
        """Helper to create an in-chat WebApp button."""
        return Button(label=label, web_app_url=url)

    def add_row(self, *buttons: Union[Button, Tuple[str, str], str]) -> Keyboard:
        """Append a new row of buttons."""
        row = [Button.from_item(b) for b in buttons]
        self.rows.append(row)
        return self

    def add_button(
        self,
        label: str,
        callback_id: Optional[str] = None,
        *,
        url: Optional[str] = None,
        web_app_url: Optional[str] = None,
        style: str = "primary",
        row: Optional[int] = None,
    ) -> Keyboard:
        """Add a single button to a specific row (or the last row)."""
        btn = Button(label=label, callback_id=callback_id, url=url, web_app_url=web_app_url, style=style)
        if row is not None and 0 <= row < len(self.rows):
            self.rows[row].append(btn)
        elif self.rows:
            self.rows[-1].append(btn)
        else:
            self.rows.append([btn])
        return self

    def to_telegram(self) -> Dict[str, Any]:
        """Compile to Telegram InlineKeyboardMarkup payload."""
        return {
            "inline_keyboard": [
                [btn.to_telegram() for btn in row]
                for row in self.rows
                if row
            ]
        }

    def to_discord(self) -> List[Dict[str, Any]]:
        """Compile to Discord components (ActionRows of buttons)."""
        components: List[Dict[str, Any]] = []
        for row in self.rows:
            if not row:
                continue
            # Discord limits max 5 buttons per ActionRow
            for chunk_start in range(0, len(row), 5):
                chunk = row[chunk_start : chunk_start + 5]
                components.append({
                    "type": 1,  # ActionRow
                    "components": [btn.to_discord() for btn in chunk],
                })
        return components

    def __repr__(self) -> str:
        return f"Keyboard(rows={len(self.rows)})"
