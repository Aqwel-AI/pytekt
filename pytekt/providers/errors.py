"""Errors raised by LLM provider clients."""

from __future__ import annotations

import json
import re
from typing import List, Optional


class ProviderError(Exception):
    """HTTP or API error from a remote LLM provider."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        body: Optional[str] = None,
    ):
        super().__init__(message)
        self.status = status
        self.body = body

    def __str__(self) -> str:
        return self.friendly_message()

    def friendly_message(self) -> str:
        """Plain-language explanation for CLI users (no raw HTTP dumps)."""
        raw = str(self.args[0]) if self.args else ""
        lower = raw.lower()
        if "certificate verify failed" in lower or "ssl: certificate" in lower:
            return (
                "Could not verify the provider's HTTPS certificate.\n\n"
                "On macOS this usually means Python is missing CA certificates.\n"
                "Fix: pip install certifi\n"
                "Then restart the agent and try /connect nvidia again."
            )
        if "timed out" in lower:
            return (
                "The model took too long to respond.\n\n"
                "Try a faster model: /connect nvidia and pick one from the top "
                "(e.g. meta/llama-3.1-8b-instruct or nvidia/nemotron-mini-4b-instruct)."
            )
        detail = self._api_detail_message()
        if self.status == 429:
            return self._friendly_rate_limit(detail)
        if self.status == 401:
            return (
                "Your API key was rejected.\n\n"
                "Check that the key is correct and active, then set it again "
                "(environment variable or `aion api add <provider> <key>`)."
            )
        if self.status == 403:
            return (
                "Access was denied for this API key.\n\n"
                "The key may lack permission for this model or API. "
                "Check your provider dashboard and billing status."
            )
        if self.status == 404:
            return (
                "The model or endpoint was not found.\n\n"
                "Try `/connect <provider>` again and pick a different model, "
                "or update `agent.model` in ~/.pytekt.yaml."
            )
        if self.status and self.status >= 500:
            return (
                "The provider's servers returned an error.\n\n"
                "This is usually temporary — wait a moment and try again."
                + (f"\n\nDetail: {detail}" if detail else "")
            )
        if detail:
            return self._clean_detail(detail)
        if self.status:
            return f"The request failed (HTTP {self.status}). Please try again."
        return raw or "The request failed. Please try again."

    def _friendly_rate_limit(self, detail: str) -> str:
        lines: List[str] = [
            "The AI provider could not answer because you hit a usage limit.",
            "",
        ]
        lower = detail.lower()
        if "quota" in lower or "limit: 0" in lower:
            lines.append(
                "Your free-tier quota for this model looks exhausted "
                "(no requests left right now)."
            )
        else:
            lines.append("You are sending requests too quickly for your current plan.")

        retry = self._retry_seconds(detail)
        if retry is not None:
            lines.append(f"Try again in about {retry} seconds.")

        model = self._mentioned_model(detail)
        if model:
            lines.append(f"Model: {model}")

        lines.extend(
            [
                "",
                "What you can do:",
                "  • Wait, then send your message again",
                "  • Check usage: https://ai.dev/rate-limit",
                "  • Enable billing on your Google AI / provider account",
                "  • Switch provider in Aion: /connect ollama or /connect deepseek",
            ]
        )
        return "\n".join(lines)

    def _api_detail_message(self) -> str:
        if not self.body:
            return ""
        try:
            data = json.loads(self.body)
        except (json.JSONDecodeError, TypeError):
            return self._clean_detail(self.body)

        err = data.get("error")
        if isinstance(err, dict):
            msg = err.get("message")
            if msg:
                return self._clean_detail(str(msg))
        if isinstance(err, str):
            return self._clean_detail(err)
        msg = data.get("message")
        if msg:
            return self._clean_detail(str(msg))
        return self._clean_detail(self.body)

    @staticmethod
    def _clean_detail(text: str) -> str:
        text = text.strip()
        text = re.sub(r"^HTTP \d+:\s*", "", text)
        return text

    @staticmethod
    def _retry_seconds(text: str) -> Optional[int]:
        match = re.search(r"retry in (\d+(?:\.\d+)?)\s*s", text, re.IGNORECASE)
        if match:
            return max(1, int(float(match.group(1))))
        return None

    @staticmethod
    def _mentioned_model(text: str) -> Optional[str]:
        match = re.search(r"model:\s*([^\s,*]+)", text, re.IGNORECASE)
        return match.group(1) if match else None
