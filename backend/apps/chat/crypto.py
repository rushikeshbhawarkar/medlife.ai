"""Encryption helpers for stored chat text (Fernet, same key management as the TOTP secrets).

Key choice: CHAT_ENCRYPTION_KEY if set, otherwise TOTP_ENCRYPTION_KEY, so existing deployments need no new
environment variable. Outside DEBUG a key is mandatory. Losing the key makes stored chats unreadable.
"""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

TOKEN_PREFIX = "gAAAAA"  # every Fernet token starts with this (version byte + timestamp), used to spot ciphertext


def _fernet():
    key = (getattr(settings, "CHAT_ENCRYPTION_KEY", "") or getattr(settings, "TOTP_ENCRYPTION_KEY", "") or "").strip()
    if not key:
        if not settings.DEBUG:
            raise RuntimeError("TOTP_ENCRYPTION_KEY (or CHAT_ENCRYPTION_KEY) must be configured outside DEBUG mode.")
        key = base64.urlsafe_b64encode(
            hashlib.sha256((settings.SECRET_KEY + ":medlife-chat-v1").encode("utf-8")).digest()
        ).decode("ascii")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError("The chat encryption key must be a valid Fernet key.") from exc


def encrypt_text(plaintext):
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt_text(stored):
    """Return plaintext for a stored value.

    Rows written before encryption was added are plain text and are returned unchanged, so the migration can
    run at any time. A value that looks like ciphertext but cannot be decrypted means the key is wrong; that is
    raised loudly rather than shown to the user as if it were their message.
    """
    if not stored.startswith(TOKEN_PREFIX):
        return stored
    try:
        return _fernet().decrypt(stored.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("A stored chat message could not be decrypted. Check TOTP_ENCRYPTION_KEY / CHAT_ENCRYPTION_KEY.") from exc
    except UnicodeEncodeError:
        return stored


def is_encrypted(stored):
    return isinstance(stored, str) and stored.startswith(TOKEN_PREFIX)
