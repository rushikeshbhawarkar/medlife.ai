
"""TOTP helpers for enrollment, QR generation, encryption, and code validation."""
import base64
import hashlib
import hmac
import io
import time

import pyotp
import qrcode
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

ISSUER_NAME = "Medlife AI"
TOTP_VALID_WINDOW = 1  # Allow a small clock drift: one 30-second step either side.


def _fernet():
    """Use a dedicated key when configured; development can derive one from SECRET_KEY."""
    key = getattr(settings, "TOTP_ENCRYPTION_KEY", "")
    if not key:
        if not settings.DEBUG:
            raise RuntimeError("TOTP_ENCRYPTION_KEY must be configured outside DEBUG mode.")
        # Stable for this development SECRET_KEY, but production must set a dedicated key.
        key = base64.urlsafe_b64encode(
            hashlib.sha256((settings.SECRET_KEY + ":medlife-totp-v1").encode("utf-8")).digest()
        ).decode("ascii")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError("TOTP_ENCRYPTION_KEY must be a valid Fernet key.") from exc


def encrypt_totp_secret(secret):
    return _fernet().encrypt(secret.encode("utf-8")).decode("ascii")


def decrypt_totp_secret(encrypted_secret):
    try:
        return _fernet().decrypt(encrypted_secret.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, UnicodeEncodeError) as exc:
        raise ValueError("The stored TOTP secret could not be decrypted.") from exc


def render_totp_setup(email, secret):
    """Render the provisioning URI and QR code for an existing secret."""
    uri = pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=ISSUER_NAME)
    image = qrcode.make(uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    qr_data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    return uri, qr_data_url


def make_totp_setup(email):
    """Return a new base32 secret, provisioning URI, and PNG QR data URL."""
    secret = pyotp.random_base32()
    uri, qr_data_url = render_totp_setup(email, secret)
    return secret, uri, qr_data_url


def matching_totp_step(secret, code, now=None):
    """Return the matching time-step for a valid code, otherwise None."""
    if not isinstance(code, str) or len(code) != 6 or not code.isdigit():
        return None
    totp = pyotp.TOTP(secret)
    timestamp = time.time() if now is None else now
    current_step = int(timestamp // totp.interval)
    for step in range(current_step - TOTP_VALID_WINDOW, current_step + TOTP_VALID_WINDOW + 1):
        expected = totp.at(step * totp.interval)
        if hmac.compare_digest(expected, code):
            return step
    return None


def create_setup_token(account):
    from django.core import signing
    from .tokens import SETUP_TOKEN_SALT
    return signing.dumps(
        {"account_id": account.pk, "purpose": "totp_setup"},
        salt=SETUP_TOKEN_SALT,
        compress=True,
    )


def create_login_challenge(account):
    from django.core import signing
    from .tokens import LOGIN_CHALLENGE_SALT
    return signing.dumps(
        {"account_id": account.pk, "purpose": "totp_login"},
        salt=LOGIN_CHALLENGE_SALT,
        compress=True,
    )
