# Purpose: Normalizes account identity, stores password hashes, and verifies credentials.
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException
from .models import Account
from .totp import encrypt_totp_secret, make_totp_setup


class AccountExists(APIException):
    status_code = 409
    default_detail = "An account with this email already exists. Please sign in."


class InvalidCredentials(APIException):
    status_code = 401
    default_detail = "Incorrect email or password."


def normalize_email(email):
    return email.strip().lower()




def get_or_create_account(email):
    """Return the account for a normalized email, preserving existing data-service imports."""
    email = normalize_email(email)
    try:
        return Account.objects.get_or_create(email=email)[0]
    except IntegrityError:
        # Handles two first requests racing to create the same unique email.
        return Account.objects.get(email=email)


def create_pending_account(email, password):
    """Create a password-hashed account and an encrypted, unverified TOTP secret."""
    email = normalize_email(email)
    secret, provisioning_uri, qr_data_url = make_totp_setup(email)
    try:
        with transaction.atomic():
            account = Account.objects.create(
                email=email,
                password=make_password(password),
                totp_enabled=False,
                totp_pending_secret_encrypted=encrypt_totp_secret(secret),
            )
    except IntegrityError:
        # Unique email constraint handles simultaneous signup attempts safely.
        if Account.objects.filter(email=email).exists():
            raise AccountExists()
        raise
    return account, secret, provisioning_uri, qr_data_url


def verify_credentials(email, password):
    """Return the account when email and password match, otherwise raise InvalidCredentials."""
    email = normalize_email(email)
    account = Account.objects.filter(email=email).first()
    if account is None or not account.password:
        # Keep unknown-email and wrong-password responses indistinguishable.
        check_password(password, make_password("not-a-real-password"))
        raise InvalidCredentials()
    if not check_password(password, account.password):
        raise InvalidCredentials()
    return account



# ---------------------------------------------------------------------------
# Forgot password / reset password
# ---------------------------------------------------------------------------
import hashlib
import hmac
import logging
from urllib.parse import quote

from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.contrib.auth.password_validation import CommonPasswordValidator, NumericPasswordValidator
from rest_framework.exceptions import ValidationError

from .tokens import PASSWORD_RESET_SALT, password_fingerprint

logger = logging.getLogger(__name__)

RESET_REQUEST_MESSAGE = "If an account with that email exists, a password reset link has been sent."
INVALID_RESET_LINK = "This password reset link is invalid or has already been used. Please request a new one."
EXPIRED_RESET_LINK = "This password reset link has expired. Please request a new one."


class InvalidResetToken(APIException):
    """HTTP 400 with the project's {"detail": "..."} body."""
    status_code = 400
    default_detail = INVALID_RESET_LINK


def make_reset_token(account):
    """Signed, account-specific token. It carries the account id and a fingerprint of the current password hash."""
    return signing.dumps(
        {"account_id": account.pk, "purpose": "password_reset", "fp": password_fingerprint(account.password)},
        salt=PASSWORD_RESET_SALT,
        compress=True,
    )


def _read_reset_token(token):
    """Return the token payload, or raise InvalidResetToken (bad signature / wrong purpose / expired)."""
    try:
        payload = signing.loads(token, salt=PASSWORD_RESET_SALT, max_age=settings.PASSWORD_RESET_TIMEOUT)
        if payload.get("purpose") != "password_reset":
            raise ValueError("wrong purpose")
        payload["account_id"], payload["fp"]  # noqa: B018 - both must exist
        return payload
    except signing.SignatureExpired:
        raise InvalidResetToken(EXPIRED_RESET_LINK)
    except (signing.BadSignature, UnicodeError, KeyError, TypeError, ValueError, AttributeError):
        raise InvalidResetToken(INVALID_RESET_LINK)


def build_reset_url(token):
    # The token goes after "#": browsers never send the fragment to servers, so it stays out of
    # access logs, proxies and Referer headers. The frontend reads it from location.hash.
    return f"{settings.FRONTEND_PASSWORD_RESET_URL}#token={quote(token, safe='')}"


def _send_reset_email(account, token):
    minutes = max(settings.PASSWORD_RESET_TIMEOUT // 60, 1)
    expiry = f"{minutes} minute{'s' if minutes != 1 else ''}" if settings.PASSWORD_RESET_TIMEOUT >= 60 else f"{settings.PASSWORD_RESET_TIMEOUT} seconds"
    body = (
        "Hello,\n\n"
        "We received a request to reset the password for your MedLife account.\n"
        f"Open this link to choose a new password (it expires in {expiry} and works once):\n\n"
        f"{build_reset_url(token)}\n\n"
        "If you did not request this, you can ignore this email; your password will not change.\n"
        "Your authenticator app (two-factor sign-in) is not affected by a password reset.\n"
    )
    send_mail("Reset your MedLife password", body, settings.DEFAULT_FROM_EMAIL, [account.email], fail_silently=False)


def _send_password_reset_success_email(account):
    """Notify the user after their password has been changed successfully."""
    try:
        send_mail(
            subject="Your MedLife password was changed successfully",
            message=(
                "Hello,\n\n"
                "Your MedLife account password has been reset successfully.\n\n"
                "If you made this change, no further action is required.\n"
                "If you did not reset your password, please contact support "
                "immediately to secure your account.\n\n"
                "Your two-factor authentication settings have not been changed.\n\n"
                "Regards,\n"
                "MedLife Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[account.email],
            fail_silently=False,
        )
    except Exception as exc:
        # Email failure must not undo a successful password reset.
        logger.error(
            "Password reset confirmation email could not be sent "
            "(account id=%s, %s).",
            account.pk,
            type(exc).__name__,
        )


def request_password_reset(email):
    """Send a reset email if the account exists. Never reveals whether it does (callers return a generic message)."""
    email = normalize_email(email)
    account = Account.objects.filter(email=email).first()
    if account is None:
        return
    cooldown = settings.PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS
    cache_key = "pwreset:" + hashlib.sha256(email.encode("utf-8")).hexdigest()
    # cache.add is atomic: only one of several simultaneous requests gets to send.
    if cooldown and not cache.add(cache_key, 1, cooldown):
        return
    try:
        _send_reset_email(account, make_reset_token(account))
    except Exception as exc:  # SMTP down, wrong credentials, bad host ... never surface this to the caller
        cache.delete(cache_key)  # let the user try again straight away
        logger.error(
            "Password reset email could not be sent (account id=%s, %s). Check the EMAIL_* settings.",
            account.pk, type(exc).__name__,
        )


def _check_new_password(password, account):
    if password.strip().lower() == account.email.lower():
        raise ValidationError({"new_password": "Your password cannot be the same as your email address."})
    for validator in (CommonPasswordValidator(), NumericPasswordValidator()):
        try:
            validator.validate(password)
        except DjangoValidationError as exc:
            raise ValidationError({"new_password": " ".join(exc.messages)})
    if account.password and check_password(password, account.password):
        raise ValidationError({"new_password": "Choose a password different from your current one."})


def reset_password(token, new_password):
    """Validate the token, then change the password. The password change itself consumes the token."""
    payload = _read_reset_token(token)
    with transaction.atomic():
        # Row lock: of two simultaneous requests with the same token, the second waits, then sees the
        # changed password hash, fails the fingerprint check below, and is rejected.
        account = Account.objects.select_for_update().filter(pk=payload["account_id"]).first()
        if account is None:
            raise InvalidResetToken(INVALID_RESET_LINK)
        if not hmac.compare_digest(str(payload["fp"]), password_fingerprint(account.password)):
            raise InvalidResetToken(INVALID_RESET_LINK)
        _check_new_password(new_password, account)
       
        account.password = make_password(new_password)
        account.save(update_fields=["password"])

    _send_password_reset_success_email(account)
    return account


def send_password_changed_email(account):
    """Notify the user after a dashboard password change (set or change). Failure is logged, never raised."""
    try:
        send_mail(
            subject="Your MedLife password was changed",
            message=(
                "Hello,\n\n"
                "The password for your MedLife account was just changed from your account dashboard.\n\n"
                "If you made this change, no further action is required.\n"
                "If you did not, reset your password with 'Forgot password' right away and contact support.\n\n"
                "Regards,\n"
                "MedLife Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[account.email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error(
            "Password change email could not be sent (account id=%s, %s).",
            account.pk, type(exc).__name__,
        )
