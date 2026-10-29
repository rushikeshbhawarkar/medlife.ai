"""Google OpenID Connect ID-token verification for MedLife.

The browser sends a Google ID token; this module verifies its signature, issuer,
expiry, and audience using Google's maintained authentication library.
"""
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from google.auth.exceptions import GoogleAuthError, TransportError
from google.auth.transport.requests import Request
from google.oauth2 import id_token


class GoogleSignInNotConfigured(Exception):
    """The deployment has not configured its Google OAuth web client ID."""


class InvalidGoogleIDToken(Exception):
    """Google's ID token is invalid or does not identify a verified email."""


class GoogleVerificationUnavailable(Exception):
    """Google's signing keys could not be retrieved to verify the token."""


def verify_google_id_token(raw_token):
    """Return the verified Google claims needed by MedLife, or raise a typed error."""
    audience = getattr(settings, "GOOGLE_CLIENT_ID", "").strip()
    if not audience:
        raise GoogleSignInNotConfigured()

    try:
        claims = id_token.verify_oauth2_token(raw_token, Request(), audience=audience)
    except TransportError as exc:
        raise GoogleVerificationUnavailable() from exc
    except (ValueError, GoogleAuthError, TypeError, KeyError) as exc:
        raise InvalidGoogleIDToken() from exc

    issuer = claims.get("iss")
    if issuer not in ("accounts.google.com", "https://accounts.google.com"):
        raise InvalidGoogleIDToken()

    subject = claims.get("sub")
    email = claims.get("email")
    email_verified = claims.get("email_verified")
    verified_email = email_verified is True or (
        isinstance(email_verified, str) and email_verified.lower() == "true"
    )
    if not isinstance(subject, str) or not subject or len(subject) > 255:
        raise InvalidGoogleIDToken()
    if not isinstance(email, str) or not email or not verified_email:
        raise InvalidGoogleIDToken()
    email = email.strip().lower()
    if len(email) > 254:
        raise InvalidGoogleIDToken()
    try:
        validate_email(email)
    except DjangoValidationError as exc:
        raise InvalidGoogleIDToken() from exc

    return {"sub": subject, "email": email}
