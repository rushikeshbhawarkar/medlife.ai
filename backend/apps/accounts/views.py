# Purpose: Account endpoints for mandatory TOTP enrollment and two-step login.
from django.core import signing
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, Throttled
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.authentication import issue_account_token, TOKEN_MAX_AGE_SECONDS
from apps.core.identity import caller_email
from apps.core.throttling import AuthRateThrottle
from .models import Account
from .serializers import (
    CredentialsSerializer, SetupVerificationSerializer, LoginVerificationSerializer,
    GoogleSignInSerializer, PasswordChangeSerializer, GooglePasswordSetupSerializer,
    TotpRecoveryEmailSerializer, TotpRecoverySetupSerializer, TotpRecoveryVerifySerializer,
)
from .services import create_pending_account, verify_credentials, _check_new_password, send_password_changed_email
from .tokens import (
    LOGIN_CHALLENGE_MAX_AGE_SECONDS,
    LOGIN_CHALLENGE_SALT,
    SETUP_TOKEN_MAX_AGE_SECONDS,
    SETUP_TOKEN_SALT, GOOGLE_PASSWORD_SETUP_SALT, GOOGLE_PASSWORD_SETUP_MAX_AGE_SECONDS,
    TOTP_RECOVERY_SALT, TOTP_RECOVERY_MAX_AGE_SECONDS,
)
from .totp import (
    create_login_challenge,
    create_setup_token,
    decrypt_totp_secret,
    encrypt_totp_secret,
    make_totp_setup,
    matching_totp_step,
)


def _setup_response(account, secret, provisioning_uri, qr_data_url):
    return {
        "ok": True,
        "email": account.email,
        "totp_setup_required": True,
        "setup_token": create_setup_token(account),
        "setup_expires_in": SETUP_TOKEN_MAX_AGE_SECONDS,
        "qr_code": qr_data_url,
        # The manual key is shown only during setup so the user can add the account without scanning.
        "manual_key": secret,
        "issuer": "Medlife AI",
    }


TOTP_MAX_FAILURES = 5          # wrong codes allowed per account ...
TOTP_LOCKOUT_SECONDS = 15 * 60  # ... within this window, then HTTP 429


@api_view(["GET"])
def account_me(request):
    # Requires a full access token. Never creates an account from a bare email.
    caller_email(request)
    account = request.user
    dashboard = {
        Account.Role.SUPER_ADMIN: "admin",
        Account.Role.DOCTOR: "doctor",
        Account.Role.PATIENT: "patient",
    }.get(account.role, "patient")
    payload = {
        "email": account.email,
        "created_at": account.created_at.isoformat(),
        "role": account.role,
        "dashboard": dashboard,
    }
    # Doctor application state is informational; it never grants doctor permissions.
    from apps.doctors.models import DoctorApplication, DoctorProfile
    profile = DoctorProfile.objects.filter(account=account).first()
    application = DoctorApplication.objects.filter(account=account).order_by("-created_at", "-id").first()
    if profile:
        payload["doctor_status"] = profile.status
    elif application:
        payload["doctor_status"] = application.status
    else:
        payload["doctor_status"] = None
    payload["doctor_application_status"] = application.status if application else None
    # A role/profile mismatch must not direct the UI into a privileged dashboard.
    if account.role == Account.Role.DOCTOR and (not profile or profile.status != DoctorProfile.Status.APPROVED):
        payload["dashboard"] = "patient"
    return Response(payload)


@api_view(["GET", "POST"])
def cloud_ai_consent(request):
    """Read or update the signed-in account's consent for sending questions to cloud AI."""
    account = request.user
    if request.method == "GET":
        return Response({
            "cloud_ai_consent": account.cloud_ai_consent,
            "cloud_ai_consent_at": account.cloud_ai_consent_at.isoformat() if account.cloud_ai_consent_at else None,
        })

    consent = request.data.get("consent")
    if not isinstance(consent, bool):
        from rest_framework.exceptions import ValidationError
        raise ValidationError({"consent": "Provide true or false."})

    account.cloud_ai_consent = consent
    account.cloud_ai_consent_at = timezone.now() if consent else None
    account.save(update_fields=["cloud_ai_consent", "cloud_ai_consent_at"])
    return Response({
        "cloud_ai_consent": account.cloud_ai_consent,
        "cloud_ai_consent_at": account.cloud_ai_consent_at.isoformat() if account.cloud_ai_consent_at else None,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def signup(request):
    serializer = CredentialsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    account, secret, provisioning_uri, qr_data_url = create_pending_account(
        serializer.validated_data["email"], serializer.validated_data["password"]
    )
    return Response(_setup_response(account, secret, provisioning_uri, qr_data_url), status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def totp_setup(request):
    """Restart enrollment for a password-verified account whose TOTP setup is incomplete."""
    serializer = CredentialsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    account = verify_credentials(
        serializer.validated_data["email"], serializer.validated_data["password"]
    )
    if account.totp_enabled:
        raise PermissionDenied("TOTP is already enabled. Please sign in instead.")
    secret, provisioning_uri, qr_data_url = make_totp_setup(account.email)
    account.totp_pending_secret_encrypted = encrypt_totp_secret(secret)
    account.totp_last_verified_step = None
    account.save(update_fields=["totp_pending_secret_encrypted", "totp_last_verified_step"])
    return Response(_setup_response(account, secret, provisioning_uri, qr_data_url))


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def verify_totp_setup(request):
    serializer = SetupVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        payload = signing.loads(
            serializer.validated_data["setup_token"],
            salt=SETUP_TOKEN_SALT,
            max_age=SETUP_TOKEN_MAX_AGE_SECONDS,
        )
        if payload.get("purpose") != "totp_setup":
            raise ValueError("Wrong token purpose")
        account_id = payload["account_id"]
    except (UnicodeError, signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError):
        raise AuthenticationFailed("Invalid or expired TOTP setup token.")

    with transaction.atomic():
        try:
            account = Account.objects.select_for_update().get(pk=account_id)
        except Account.DoesNotExist:
            raise AuthenticationFailed("Invalid or expired TOTP setup token.")
        if account.totp_enabled:
            raise PermissionDenied("TOTP setup has already been completed. Please sign in.")
        if not account.totp_pending_secret_encrypted:
            raise AuthenticationFailed("TOTP setup is unavailable. Start setup again.")
        try:
            secret = decrypt_totp_secret(account.totp_pending_secret_encrypted)
        except ValueError:
            raise AuthenticationFailed("TOTP setup is unavailable. Start setup again.")
        matched_step = matching_totp_step(secret, serializer.validated_data["code"])
        if matched_step is None:
            raise AuthenticationFailed("Invalid authenticator code. Check your device time and try again.")
        account.totp_secret_encrypted = account.totp_pending_secret_encrypted
        account.totp_pending_secret_encrypted = ""
        account.totp_enabled = True
        # Setup verifies ownership of the authenticator; replay tracking begins at login.
        # This lets a user finish setup and sign in without waiting for the next 30-second code.
        account.totp_last_verified_step = None
        account.save(update_fields=[
            "totp_secret_encrypted", "totp_pending_secret_encrypted", "totp_enabled",
            "totp_last_verified_step",
        ])

    return Response({
        "ok": True,
        "email": account.email,
        "totp_enabled": True,
        "access_token": issue_account_token(account),
        "token_type": "Bearer",
        "expires_in": TOKEN_MAX_AGE_SECONDS,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def signin(request):
    serializer = CredentialsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    account = verify_credentials(serializer.validated_data["email"], serializer.validated_data["password"])
    # Password sign-in always requires TOTP, including for Google-linked accounts (Google sign-in itself
    # does not). A Google-linked account that set a password but never enrolled TOTP must enrol first.
    if not account.totp_enabled or not account.totp_secret_encrypted:
        # Password was verified, so allow first-time TOTP enrollment without issuing an access token.
        secret, provisioning_uri, qr_data_url = make_totp_setup(account.email)
        account.totp_pending_secret_encrypted = encrypt_totp_secret(secret)
        account.totp_last_verified_step = None
        account.save(update_fields=["totp_pending_secret_encrypted", "totp_last_verified_step"])
        return Response({
            **_setup_response(account, secret, provisioning_uri, qr_data_url),
            "access_token": None,
            "totp_setup_required": True,
            "detail": "Verify the QR code to finish sign-in.",
        })
    return Response({
        "ok": True,
        "email": account.email,
        "totp_required": True,
        "challenge_token": create_login_challenge(account),
        "challenge_expires_in": LOGIN_CHALLENGE_MAX_AGE_SECONDS,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def verify_totp_login(request):
    serializer = LoginVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        payload = signing.loads(
            serializer.validated_data["challenge_token"],
            salt=LOGIN_CHALLENGE_SALT,
            max_age=LOGIN_CHALLENGE_MAX_AGE_SECONDS,
        )
        if payload.get("purpose") != "totp_login":
            raise ValueError("Wrong token purpose")
        account_id = payload["account_id"]
    except (UnicodeError, signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError):
        raise AuthenticationFailed("Invalid or expired TOTP login challenge.")

    # Per-account lockout: the per-IP throttle alone does not stop a distributed guess of the 6-digit code.
    fail_key = f"totp-fail:{account_id}"
    if cache.get(fail_key, 0) >= TOTP_MAX_FAILURES:
        raise Throttled(detail="Too many incorrect authenticator codes. Please try again in 15 minutes.")

    with transaction.atomic():
        try:
            account = Account.objects.select_for_update().get(pk=account_id)
        except Account.DoesNotExist:
            raise AuthenticationFailed("Invalid or expired TOTP login challenge.")
        if not account.totp_enabled or not account.totp_secret_encrypted:
            raise AuthenticationFailed("TOTP is not enabled for this account.")
        try:
            secret = decrypt_totp_secret(account.totp_secret_encrypted)
        except ValueError:
            raise AuthenticationFailed("TOTP verification is unavailable. Contact support.")
        matched_step = matching_totp_step(secret, serializer.validated_data["code"])
        if matched_step is None or (
            account.totp_last_verified_step is not None
            and matched_step <= account.totp_last_verified_step
        ):
            cache.add(fail_key, 0, TOTP_LOCKOUT_SECONDS)
            try:
                cache.incr(fail_key)
            except ValueError:  # key expired between add and incr
                cache.set(fail_key, 1, TOTP_LOCKOUT_SECONDS)
            raise AuthenticationFailed("Invalid or already-used authenticator code.")
        account.totp_last_verified_step = matched_step
        account.save(update_fields=["totp_last_verified_step"])
    cache.delete(fail_key)

    return Response({
        "ok": True,
        "email": account.email,
        "access_token": issue_account_token(account),
        "token_type": "Bearer",
        "expires_in": TOKEN_MAX_AGE_SECONDS,
    })



# ---------------------------------------------------------------------------
# Forgot password / reset password (public endpoints; no access token needed)
# ---------------------------------------------------------------------------
from apps.core.throttling import PasswordResetRateThrottle
from .serializers import EmailSerializer, PasswordResetConfirmSerializer
from .services import RESET_REQUEST_MESSAGE, request_password_reset, reset_password


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRateThrottle])
def password_forgot(request):
    """Always answers 200 with the same message for a well-formed email, whether or not it is registered."""
    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    request_password_reset(serializer.validated_data["email"])
    return Response({"ok": True, "detail": RESET_REQUEST_MESSAGE})


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def password_reset(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    reset_password(serializer.validated_data["token"], serializer.validated_data["new_password"])
    return Response({"ok": True, "detail": "Your password has been changed. Please sign in with your new password."})


# ---------------------------------------------------------------------------
# Google Sign-In (Google OpenID Connect ID token -> MedLife account + access token)
# ---------------------------------------------------------------------------
from django.conf import settings
from django.core.mail import send_mail
from urllib.parse import quote
import hmac
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.exceptions import APIException
from . import google_auth


class GoogleSignInUnavailable(APIException):
    status_code = 503
    default_detail = "Google Sign-In is temporarily unavailable. Please use email and password or try again later."


def _get_or_link_google_account(subject, email):
    """Resolve a verified Google identity without allowing one Google identity to replace another."""
    with transaction.atomic():
        account = Account.objects.select_for_update().filter(google_sub=subject).first()
        if account is not None:
            if account.email.lower() != email:
                raise AuthenticationFailed("This Google account is not linked to the matching MedLife email.")
            return account

        account = Account.objects.select_for_update().filter(email=email).first()
        if account is not None:
            if account.google_sub and account.google_sub != subject:
                raise AuthenticationFailed("A different Google account is already linked to this MedLife account.")
            if not account.google_sub:
                account.google_sub = subject
                account.save(update_fields=["google_sub"])
            return account

        # The nested atomic block creates a savepoint so a concurrent unique-email / unique-sub race
        # can be recovered without leaving the outer transaction broken.
        try:
            with transaction.atomic():
                return Account.objects.create(email=email, password="", google_sub=subject)
        except IntegrityError:
            account = Account.objects.select_for_update().filter(google_sub=subject).first()
            if account is None:
                account = Account.objects.select_for_update().filter(email=email).first()
            if account is None or (account.google_sub and account.google_sub != subject):
                raise AuthenticationFailed("Unable to link this Google account to MedLife.")
            if account.email.lower() != email:
                raise AuthenticationFailed("This Google account is not linked to the matching MedLife email.")
            if not account.google_sub:
                account.google_sub = subject
                account.save(update_fields=["google_sub"])
            return account


def _google_account_response(account):
    """Return normal application access token upon Google sign-in."""
    return {
        "ok": True,
        "email": account.email,
        "auth_method": "google",
        "access_token": issue_account_token(account),
        "token_type": "Bearer",
        "expires_in": TOKEN_MAX_AGE_SECONDS,
        "password_set": bool(account.password),
        "password_setup_required": False,
    }


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def google_signin(request):
    """Verify a Google ID token and sign the user in without a TOTP challenge."""
    serializer = GoogleSignInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        claims = google_auth.verify_google_id_token(serializer.validated_data["id_token"])
    except google_auth.GoogleSignInNotConfigured:
        raise GoogleSignInUnavailable()
    except google_auth.GoogleVerificationUnavailable:
        raise GoogleSignInUnavailable()
    except google_auth.InvalidGoogleIDToken:
        raise AuthenticationFailed("Invalid Google ID token. Please try signing in again.")

    account = _get_or_link_google_account(claims["sub"], claims["email"])
    return Response(_google_account_response(account))


# ---------------------------------------------------------------------------
# Change password (authenticated dashboard endpoint)
# ---------------------------------------------------------------------------
@api_view(["POST"])
def password_change(request):
    """Set a password for Google-only accounts or change it for password accounts."""
    serializer = PasswordChangeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    with transaction.atomic():
        account = Account.objects.select_for_update().get(pk=request.user.pk)

        # Do not require current_password for authenticated password updates.
        # If a non-empty current password is provided, verify it matches.
        if account.password and data.get("current_password"):
            if not check_password(data["current_password"], account.password):
                raise AuthenticationFailed("Current password is incorrect.")

        _check_new_password(data["new_password"], account)
        account.password = make_password(data["new_password"])
        account.save(update_fields=["password"])

        # Password fingerprints revoke old tokens. Return a fresh token so this session
        # remains signed in after changing the password.
        access_token = issue_account_token(account)

    # Notify the owner after the change is committed; an email failure never undoes the change.
    send_password_changed_email(account)

    return Response({
        "ok": True,
        "detail": "Password updated successfully.",
        "email": account.email,
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": TOKEN_MAX_AGE_SECONDS,
        "password_set": True,
    })


# ---------------------------------------------------------------------------
# First Google sign-in: mandatory password setup before issuing an access token
# ---------------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def google_password_setup(request):
    serializer = GooglePasswordSetupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        payload = signing.loads(
            serializer.validated_data["setup_token"],
            salt=GOOGLE_PASSWORD_SETUP_SALT,
            max_age=GOOGLE_PASSWORD_SETUP_MAX_AGE_SECONDS,
        )
        if payload.get("purpose") != "google_password_setup":
            raise ValueError("Wrong token purpose")
        account_id = payload["account_id"]
    except (UnicodeError, signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError):
        raise AuthenticationFailed("Invalid or expired password setup link. Please sign in with Google again.")

    with transaction.atomic():
        account = Account.objects.select_for_update().filter(pk=account_id).first()
        if account is None or account.password:
            raise AuthenticationFailed("Password setup is no longer available. Please sign in again.")
        _check_new_password(serializer.validated_data["new_password"], account)
        account.password = make_password(serializer.validated_data["new_password"])
        account.save(update_fields=["password"])
        token = issue_account_token(account)

    send_password_changed_email(account)
    return Response({
        "ok": True, "detail": "Password set successfully.", "email": account.email,
        "password_set": True, "access_token": token, "token_type": "Bearer",
        "expires_in": TOKEN_MAX_AGE_SECONDS,
    })


# ---------------------------------------------------------------------------
# Lost authenticator recovery through a short-lived, email-verified link
# ---------------------------------------------------------------------------
def _totp_secret_fingerprint(account):
    import hashlib
    return hashlib.sha256((account.totp_secret_encrypted or "").encode("utf-8")).hexdigest()


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def totp_recovery_request(request):
    """Send a recovery link only to the account's registered email; response is non-enumerating."""
    serializer = TotpRecoveryEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"].strip().lower()
    account = Account.objects.filter(email__iexact=email, totp_enabled=True).first()
    if account and account.totp_secret_encrypted:
        token = signing.dumps({
            "account_id": account.pk,
            "purpose": "totp_recovery",
            "secret_fp": _totp_secret_fingerprint(account),
        }, salt=TOTP_RECOVERY_SALT, compress=True)
        frontend_url = getattr(settings, "FRONTEND_TOTP_RECOVERY_URL", "http://localhost:5173/recover-totp")
        link = f"{frontend_url}#token={quote(token, safe='')}"
        try:
            send_mail(
                subject="Recover your MedLife authenticator",
                message=(
                    "Hello,\n\nA request was made to replace the authenticator for your MedLife account. "
                    f"Open this link within {TOTP_RECOVERY_MAX_AGE_SECONDS // 60} minutes to set up a new authenticator:\n\n"
                    f"{link}\n\nIf you did not request this, ignore this email. Your current authenticator remains active.\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[account.email],
                fail_silently=False,
            )
        except Exception:
            # Avoid exposing account existence or mail-server details in the public response.
            pass
    return Response({
        "ok": True,
        "detail": "If the address belongs to an account with authenticator enabled, a recovery link has been sent."
    })


def _read_totp_recovery_token(token):
    try:
        payload = signing.loads(token, salt=TOTP_RECOVERY_SALT, max_age=TOTP_RECOVERY_MAX_AGE_SECONDS)
        if payload.get("purpose") != "totp_recovery":
            raise ValueError("Wrong token purpose")
        payload["account_id"], payload["secret_fp"]
        return payload
    except signing.SignatureExpired:
        raise AuthenticationFailed("The authenticator recovery link has expired. Request a new one.")
    except (UnicodeError, signing.BadSignature, KeyError, TypeError, ValueError, AttributeError):
        raise AuthenticationFailed("Invalid authenticator recovery link.")


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def totp_recovery_setup(request):
    """Validate the emailed link and return a QR code for a pending replacement secret."""
    serializer = TotpRecoverySetupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    payload = _read_totp_recovery_token(serializer.validated_data["recovery_token"])
    with transaction.atomic():
        account = Account.objects.select_for_update().filter(pk=payload["account_id"]).first()
        if (account is None or not account.totp_enabled or not account.totp_secret_encrypted
                or not hmac.compare_digest(_totp_secret_fingerprint(account), str(payload["secret_fp"]))):
            raise AuthenticationFailed("This authenticator recovery link is no longer valid.")
        secret, provisioning_uri, qr_data_url = make_totp_setup(account.email)
        account.totp_pending_secret_encrypted = encrypt_totp_secret(secret)
        account.save(update_fields=["totp_pending_secret_encrypted"])
    return Response({
        "ok": True, "email": account.email, "totp_setup_required": True,
        "qr_code": qr_data_url, "manual_key": secret, "issuer": "Medlife AI",
        "recovery_token": serializer.validated_data["recovery_token"],
        "setup_expires_in": TOTP_RECOVERY_MAX_AGE_SECONDS,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def totp_recovery_verify(request):
    """Activate the replacement authenticator only after a valid code and re-checking the emailed token."""
    serializer = TotpRecoveryVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    payload = _read_totp_recovery_token(serializer.validated_data["recovery_token"])
    with transaction.atomic():
        account = Account.objects.select_for_update().filter(pk=payload["account_id"]).first()
        if (account is None or not account.totp_enabled or not account.totp_secret_encrypted
                or not hmac.compare_digest(_totp_secret_fingerprint(account), str(payload["secret_fp"]))):
            raise AuthenticationFailed("This authenticator recovery link is no longer valid.")
        if not account.totp_pending_secret_encrypted:
            raise AuthenticationFailed("Start authenticator recovery again to generate a new QR code.")
        try:
            new_secret = decrypt_totp_secret(account.totp_pending_secret_encrypted)
        except ValueError:
            raise AuthenticationFailed("Authenticator recovery is unavailable. Request a new link.")
        matched_step = matching_totp_step(new_secret, serializer.validated_data["code"])
        if matched_step is None:
            raise AuthenticationFailed("Invalid authenticator code. Please try again.")
        account.totp_secret_encrypted = account.totp_pending_secret_encrypted
        account.totp_pending_secret_encrypted = ""
        account.totp_last_verified_step = matched_step
        account.save(update_fields=[
            "totp_secret_encrypted", "totp_pending_secret_encrypted", "totp_last_verified_step"
        ])
    return Response({
        "ok": True, "detail": "Authenticator updated successfully. Sign in using your new code.",
        "email": account.email, "totp_enabled": True,
    })
