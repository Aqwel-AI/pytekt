"""
Cross-platform Modal popup form component compiling to Discord Native Modals
and degrading gracefully to Telegram ForceReply conversational prompts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .components import UIComponent


class ModalField:
    """
    A single input field in a Modal popup form.

    Parameters
    ----------
    id : str
        Unique identifier for this input field.
    label : str
        Display label explaining what the user should enter.
    placeholder : str, optional
        Hint or placeholder text.
    default : str, optional
        Pre-filled default value.
    required : bool, optional
        Whether this input is mandatory (default True).
    style : str, optional
        'short' for single-line text, 'paragraph' for multi-line text.
    min_length : int, optional
        Minimum character length.
    max_length : int, optional
        Maximum character length.
    """

    def __init__(
        self,
        id: str,
        label: str,
        *,
        placeholder: str = "",
        default: str = "",
        required: bool = True,
        style: str = "short",
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> None:
        self.id = id
        self.label = label
        self.placeholder = placeholder
        self.default = default
        self.required = required
        self.style = style.lower().strip()
        self.min_length = min_length
        self.max_length = max_length

    def to_discord(self) -> Dict[str, Any]:
        """Compile to Discord TextInput component."""
        comp: Dict[str, Any] = {
            "type": 4,  # TextInput
            "custom_id": self.id,
            "label": self.label,
            "style": 1 if self.style == "short" else 2,  # 1 = Short, 2 = Paragraph
            "required": self.required,
        }
        if self.placeholder:
            comp["placeholder"] = self.placeholder
        if self.default:
            comp["value"] = self.default
        if self.min_length is not None:
            comp["min_length"] = self.min_length
        if self.max_length is not None:
            comp["max_length"] = self.max_length
        return comp

    def __repr__(self) -> str:
        return f"ModalField(id='{self.id}', label='{self.label}', style='{self.style}')"


class Modal(UIComponent):
    """
    Cross-platform interactive modal form.
    Compiles to a native Discord Modal popup, and degrades gracefully to a Telegram ForceReply prompt.

    Parameters
    ----------
    title : str
        Popup modal title.
    custom_id : str
        Unique identifier for the modal, handled via `@bot.on_modal_submit(custom_id)`.
    fields : List[ModalField]
        List of input fields inside the modal.
    """

    def __init__(
        self,
        title: str,
        custom_id: str,
        fields: Optional[List[ModalField]] = None,
    ) -> None:
        self.title = title
        self.custom_id = custom_id
        self.fields: List[ModalField] = list(fields or [])

    def add_field(
        self,
        id: str,
        label: str,
        *,
        placeholder: str = "",
        default: str = "",
        required: bool = True,
        style: str = "short",
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> Modal:
        """Add an input field to the modal."""
        self.fields.append(
            ModalField(
                id=id,
                label=label,
                placeholder=placeholder,
                default=default,
                required=required,
                style=style,
                min_length=min_length,
                max_length=max_length,
            )
        )
        return self

    def to_discord(self) -> Dict[str, Any]:
        """Compile to native Discord Modal Interaction response payload."""
        return {
            "type": 9,  # MODAL response type
            "data": {
                "title": self.title,
                "custom_id": self.custom_id,
                "components": [
                    {
                        "type": 1,  # ActionRow wrapper required per input
                        "components": [field.to_discord()],
                    }
                    for field in self.fields
                ],
            },
        }

    def to_telegram(self) -> Dict[str, Any]:
        """
        Degrade gracefully on Telegram to a ForceReply prompt.
        Allows users to reply to the bot with their input directly in chat.
        """
        lines: List[str] = [
            f"📋 <b>{self.title}</b>",
            "",
            "Please provide your input for the following fields:",
        ]
        for f in self.fields:
            req_tag = "<i>(Required)</i>" if f.required else "<i>(Optional)</i>"
            hint = f" — {f.placeholder}" if f.placeholder else ""
            lines.append(f"• <b>{f.label}</b> {req_tag}{hint}")

        lines.append("")
        lines.append("<i>Reply to this message with your response.</i>")

        return {
            "text": "\n".join(lines),
            "reply_markup": {
                "force_reply": True,
                "selective": True,
            },
            "parse_mode": "HTML",
            "custom_id": self.custom_id,
            "is_fallback": True,
        }

    def __repr__(self) -> str:
        return f"Modal(title='{self.title}', custom_id='{self.custom_id}', fields={len(self.fields)})"
