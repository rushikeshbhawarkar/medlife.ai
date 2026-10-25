# Purpose: Account feature routes. Keep signup/signin without trailing slashes for frontend compatibility.
from django.urls import path
from .views import (
    account_me, google_signin, google_password_setup, password_change, password_forgot, password_reset,
    signin, signup, totp_setup, verify_totp_login, verify_totp_setup,
    totp_recovery_request, totp_recovery_setup, totp_recovery_verify,
)

urlpatterns = [
    path("account/", account_me, name="account-me"),
    path("signup", signup, name="signup"),
    path("signin", signin, name="signin"),
    path("google/signin", google_signin, name="google-signin"),
    path("google/password-setup", google_password_setup, name="google-password-setup"),
    path("totp/setup", totp_setup, name="totp-setup"),
    path("totp/verify-setup", verify_totp_setup, name="totp-verify-setup"),
    path("totp/verify-login", verify_totp_login, name="totp-verify-login"),
    path("password/forgot", password_forgot, name="password-forgot"),
    path("password/reset", password_reset, name="password-reset"),
    path("password/change", password_change, name="password-change"),
    path("totp/recovery/request", totp_recovery_request, name="totp-recovery-request"),
    path("totp/recovery/setup", totp_recovery_setup, name="totp-recovery-setup"),
    path("totp/recovery/verify", totp_recovery_verify, name="totp-recovery-verify"),
]

