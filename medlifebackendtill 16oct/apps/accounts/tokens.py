"""Signing purposes and lifetimes for restricted TOTP setup/login challenges."""
SETUP_TOKEN_SALT = "medlife.totp-setup.v1"
SETUP_TOKEN_MAX_AGE_SECONDS = 10 * 60
LOGIN_CHALLENGE_SALT = "medlife.totp-login-challenge.v1"
LOGIN_CHALLENGE_MAX_AGE_SECONDS = 5 * 60

# --- Password reset (forgot password) ---
# The reset token is a Django-signed value; its lifetime is settings.PASSWORD_RESET_TIMEOUT (300 s by default).
PASSWORD_RESET_SALT = "medlife.password-reset.v1"


def password_fingerprint(password_hash):
    """Short keyed fingerprint of the stored password hash.

    A reset token embeds it, so the token stops working the moment the password changes (single use, and
    any other password change also revokes it). Access tokens embed it too, so a reset signs out old sessions.
    The hash itself is never placed in a token.
    """
    from django.utils.crypto import salted_hmac
    return salted_hmac("medlife.password-fingerprint.v1", password_hash or "").hexdigest()[:20]


# Short-lived, purpose-specific tokens for first Google password setup and TOTP recovery.
GOOGLE_PASSWORD_SETUP_SALT = "medlife.google-password-setup.v1"
GOOGLE_PASSWORD_SETUP_MAX_AGE_SECONDS = 10 * 60
TOTP_RECOVERY_SALT = "medlife.totp-recovery.v1"
TOTP_RECOVERY_MAX_AGE_SECONDS = 15 * 60
