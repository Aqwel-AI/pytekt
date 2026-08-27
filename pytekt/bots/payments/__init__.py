"""
Native Payments Integration for PyTekt Bots.
Provides cross-platform types and Telegram native in-chat Payments API integration,
raising clear NotSupportedError on non-supported platforms (e.g. Discord).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class NotSupportedError(Exception):
    """
    Raised when a feature (such as native in-chat payments) is invoked on a platform
    that does not support it.
    """
    pass


@dataclass
class LabeledPrice:
    """
    Represents a portion of the price for goods or services.

    Parameters
    ----------
    label : str
        Portion label (e.g. 'Product Price', 'Shipping', 'Tax').
    amount : int
        Price in the smallest units of the currency (e.g. 500 cents for $5.00 USD, or 1000 for 10.00 EUR).
    """
    label: str
    amount: int

    def to_dict(self) -> Dict[str, Any]:
        return {"label": self.label, "amount": int(self.amount)}


@dataclass
class Invoice:
    """
    Detailed parameters for sending a payment invoice to a user or chat.
    """
    title: str
    description: str
    payload: str
    provider_token: str
    currency: str
    prices: List[LabeledPrice]
    photo_url: Optional[str] = None
    photo_size: Optional[int] = None
    photo_width: Optional[int] = None
    photo_height: Optional[int] = None
    need_name: bool = False
    need_phone_number: bool = False
    need_email: bool = False
    need_shipping_address: bool = False
    send_phone_number_to_provider: bool = False
    send_email_to_provider: bool = False
    is_flexible: bool = False

    def to_payload(self, chat_id: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "chat_id": chat_id,
            "title": self.title,
            "description": self.description,
            "payload": self.payload,
            "provider_token": self.provider_token,
            "currency": self.currency.upper(),
            "prices": [p.to_dict() for p in self.prices],
            "need_name": self.need_name,
            "need_phone_number": self.need_phone_number,
            "need_email": self.need_email,
            "need_shipping_address": self.need_shipping_address,
            "is_flexible": self.is_flexible,
        }
        if self.photo_url:
            data["photo_url"] = self.photo_url
        if self.photo_size:
            data["photo_size"] = self.photo_size
        if self.photo_width:
            data["photo_width"] = self.photo_width
        if self.photo_height:
            data["photo_height"] = self.photo_height
        return data


@dataclass
class PreCheckoutQuery:
    """Information about an incoming pre-checkout payment confirmation query."""
    id: str
    user_id: str
    currency: str
    total_amount: int
    invoice_payload: str
    raw_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SuccessfulPayment:
    """Information about a confirmed successful payment."""
    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    raw_payload: Dict[str, Any] = field(default_factory=dict)
