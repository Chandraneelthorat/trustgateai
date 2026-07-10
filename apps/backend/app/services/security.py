"""API key generation and hashing.

Keys are random tokens prefixed with ``tgk_``. Only the SHA-256 hash is persisted;
the plaintext is returned to the caller exactly once at creation time.
"""

from __future__ import annotations

import hashlib
import secrets

KEY_PREFIX = "tgk_"


def generate_api_key() -> str:
    return KEY_PREFIX + secrets.token_urlsafe(32)


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def key_display_prefix(key: str) -> str:
    """Short, non-secret identifier shown in listings (e.g. ``tgk_a1b2c3``)."""
    return key[:12]
