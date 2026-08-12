#!/usr/bin/env python3
"""
PyTekt - Utilities
=======================

General helpers: data formatting and conversion, string manipulation and
validation, random data and UUIDs, hashing, number processing, and
sanitization. Shared across Aion modules and user code.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import re
import uuid
import hashlib


def format_bytes(size: int) -> str:
    """Format size in bytes as human-readable string (B, KB, MB, GB)."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def format_duration(seconds: int) -> str:
    """Format seconds as 'N min M sec'."""
    minutes, secs = divmod(seconds, 60)
    return f"{minutes} min {secs} sec"


def random_string(length: int = 8) -> str:
    """Return random alphanumeric string of given length."""
    import random
    import string
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def slugify(text: str) -> str:
    """Convert text to lowercase, strip, and replace spaces with hyphens."""
    return text.strip().lower().replace(" ", "-")


def is_valid_email(email: str) -> bool:
    """Return True if string matches local@domain.tld pattern."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def generate_uuid() -> str:
    """Return a new UUID4 string."""
    return str(uuid.uuid4())


def md5_hash(text: str) -> str:
    """Return MD5 hex digest of text (UTF-8)."""
    return hashlib.md5(text.encode()).hexdigest()


def get_even_numbers(numbers: list) -> list:
    """Return list of even numbers from input."""
    return [n for n in numbers if n % 2 == 0]


def get_odd_numbers(numbers: list) -> list:
    """Return list of odd numbers from input."""
    return [n for n in numbers if n % 2 != 0]