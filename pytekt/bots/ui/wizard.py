"""
Cross-platform Multi-step Wizard Flow primitive.
Behaves identically across Telegram and Discord using message edits and in-process state tracking.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from .card import Card
from .components import UIComponent
from .keyboard import Button, Keyboard


class WizardStep:
    """
    A single step inside a multi-step Wizard flow.

    Parameters
    ----------
    id : str
        Unique step identifier.
    title : str
        Title displayed at the top of this step.
    description : str, optional
        Informational content or instructions for the step.
    fields : Dict[str, str], optional
        Key-value field summary to display in the step.
    keyboard : Keyboard, optional
        Custom step-specific options / action buttons.
    image : str, optional
        Illustration or diagram image URL.
    color : int or str, optional
        Step card accent color.
    """

    def __init__(
        self,
        id: str,
        title: str,
        *,
        description: str = "",
        fields: Optional[Dict[str, str]] = None,
        keyboard: Optional[Keyboard] = None,
        image: Optional[str] = None,
        color: Union[int, str] = "primary",
    ) -> None:
        self.id = id
        self.title = title
        self.description = description
        self.fields = fields or {}
        self.keyboard = keyboard
        self.image = image
        self.color = color

    def __repr__(self) -> str:
        return f"WizardStep(id='{self.id}', title='{self.title}')"


class Wizard(UIComponent):
    """
    A declarative multi-step wizard flow.
    Tracks the active step index and automatically manages back/next/finish navigation
    by editing messages in place across Telegram and Discord.

    Parameters
    ----------
    id : str
        Unique wizard flow identifier.
    steps : List[WizardStep]
        Ordered list of steps in the wizard.
    on_finish : Callable, optional
        Callback invoked when the user finishes the wizard (`async fn(ctx, wizard_data)`).
    on_cancel : Callable, optional
        Callback invoked if the user cancels the wizard.
    show_nav : bool, optional
        Whether to automatically append Next/Back/Cancel navigation buttons (default True).
    """

    def __init__(
        self,
        id: str,
        steps: Optional[Sequence[WizardStep]] = None,
        *,
        on_finish: Optional[Callable[..., Any]] = None,
        on_cancel: Optional[Callable[..., Any]] = None,
        show_nav: bool = True,
        next_label: str = "Next ➡️",
        back_label: str = "⬅️ Back",
        cancel_label: str = "❌ Cancel",
        finish_label: str = "✅ Done",
    ) -> None:
        self.id = id
        self.steps: List[WizardStep] = list(steps or [])
        self.on_finish = on_finish
        self.on_cancel = on_cancel
        self.show_nav = show_nav
        self.next_label = next_label
        self.back_label = back_label
        self.cancel_label = cancel_label
        self.finish_label = finish_label

    def add_step(
        self,
        id: str,
        title: str,
        *,
        description: str = "",
        fields: Optional[Dict[str, str]] = None,
        keyboard: Optional[Keyboard] = None,
        image: Optional[str] = None,
        color: Union[int, str] = "primary",
    ) -> Wizard:
        """Add a step to the wizard sequence."""
        self.steps.append(
            WizardStep(
                id=id,
                title=title,
                description=description,
                fields=fields,
                keyboard=keyboard,
                image=image,
                color=color,
            )
        )
        return self

    def render_step(self, step_index: int, platform: str) -> Dict[str, Any]:
        """Render a specific step as a Card + Keyboard compiled for the target platform."""
        total = len(self.steps)
        if total == 0:
            card = Card(title=f"Wizard: {self.id}", description="No steps configured.")
            return card.compile(platform)

        idx = max(0, min(step_index, total - 1))
        step = self.steps[idx]

        # Combine step-specific keyboard with navigation buttons
        kb = Keyboard()
        if step.keyboard:
            for row in step.keyboard.rows:
                kb.rows.append(list(row))

        if self.show_nav:
            nav_row: List[Button] = []
            if idx > 0:
                nav_row.append(Button(self.back_label, callback_id=f"wiz:{self.id}:back:{idx}", style="secondary"))
            if idx < total - 1:
                nav_row.append(Button(self.next_label, callback_id=f"wiz:{self.id}:next:{idx}", style="primary"))
            else:
                nav_row.append(Button(self.finish_label, callback_id=f"wiz:{self.id}:finish:{idx}", style="success"))

            nav_row.append(Button(self.cancel_label, callback_id=f"wiz:{self.id}:cancel:{idx}", style="danger"))
            kb.rows.append(nav_row)

        step_title = f"Step {idx + 1} of {total}: {step.title}"
        card = Card(
            title=step_title,
            description=step.description,
            fields=step.fields,
            image=step.image,
            color=step.color,
            footer=f"Flow ID: {self.id}",
            keyboard=kb,
        )

        return card.compile(platform)

    def to_telegram(self) -> Dict[str, Any]:
        """Compile initial step to Telegram payload."""
        return self.render_step(0, "telegram")

    def to_discord(self) -> Dict[str, Any]:
        """Compile initial step to Discord payload."""
        return self.render_step(0, "discord")

    def __repr__(self) -> str:
        return f"Wizard(id='{self.id}', steps={len(self.steps)})"
