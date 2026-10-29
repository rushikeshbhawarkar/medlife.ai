"""Tests for Google OIDC sign-in, account linking, and MedLife's mandatory TOTP policy."""
from unittest import mock

# pyrefly: ignore[missing-import]
import pyotp
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.accounts.totp import decrypt_totp_secret, encrypt_totp_secret


CLIENT_ID = "medlife-test-web-client.apps.googleusercontent.com"
GOOGLE_CLAIMS = {
    "sub": "google-subject-123",
    "email": "user@example.com",
}


@override_settings(GOOGLE_CLIENT_ID=CLIENT_ID)
class GoogleSignInApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def google_signin(self, claims=None, token="valid-google-id-token"):
        claims = claims or GOOGLE_CLAIMS
        with mock.patch("apps.accounts.google_auth.verify_google_id_token", return_value=claims) as verifier:
            response = self.client.post(
                "/medlife/google/signin", {"id_token": token}, format="json"
            )
        verifier.assert_called_once_with(token)
        return response

    def finish_setup(self, response):
        body = response.json()
        code = pyotp.TOTP(body["manual_key"]).now()
        return self.client.post(
            "/medlife/totp/verify-setup",
            {"setup_token": body["setup_token"], "code": code},
            format="json",
        )

    def finish_login(self, response):
        body = response.json()
        account = Account.objects.get(email=body["email"])
        secret = decrypt_totp_secret(account.totp_secret_encrypted)
        code = pyotp.TOTP(secret).now()
        return self.client.post(
            "/medlife/totp/verify-login",
            {"challenge_token": body["challenge_token"], "code": code},
            format="json",
        )

    def test_new_google_user_receives_access_token_directly_without_mandatory_password(self):
        response = self.google_signin()
        self.assertEqual(response.status_code, 200, response.json())
        body = response.json()
        self.assertEqual(body["auth_method"], "google")
        self.assertFalse(body["password_setup_required"])
        self.assertFalse(body["password_set"])
        self.assertIn("access_token", body)

        account = Account.objects.get(email="user@example.com")
        self.assertEqual(account.google_sub, GOOGLE_CLAIMS["sub"])
        self.assertEqual(account.role, Account.Role.PATIENT)
        self.assertEqual(account.password, "")
        self.assertFalse(account.totp_enabled)

        # Access token allows direct access to protected endpoints
        me = self.client.get(
            "/medlife/account/", HTTP_AUTHORIZATION=f"Bearer {body['access_token']}"
        )
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], account.email)

    def test_existing_google_user_without_password_receives_access_token(self):
        Account.objects.create(
            email="user@example.com",
            google_sub=GOOGLE_CLAIMS["sub"],
            password="",
        )
        response = self.google_signin()
        self.assertEqual(response.status_code, 200, response.json())
        self.assertFalse(response.json()["password_setup_required"])
        self.assertFalse(response.json()["password_set"])
        self.assertIn("access_token", response.json())

    def test_verified_google_email_links_existing_password_account_without_changing_password(self):
        original_hash = make_password("existing-password")
        account = Account.objects.create(
            email="user@example.com",
            password=original_hash,
            totp_enabled=True,
            totp_secret_encrypted=encrypt_totp_secret(pyotp.random_base32()),
        )
        response = self.google_signin()
        self.assertEqual(response.status_code, 200, response.json())
        account.refresh_from_db()
        self.assertEqual(account.google_sub, GOOGLE_CLAIMS["sub"])
        self.assertEqual(account.password, original_hash)
        self.assertIn("access_token", response.json())
        self.assertNotIn("totp_required", response.json())

    def test_different_google_subject_cannot_replace_existing_link(self):
        Account.objects.create(
            email="user@example.com",
            google_sub="some-other-google-subject",
            password="",
            totp_enabled=True,
            totp_secret_encrypted=encrypt_totp_secret(pyotp.random_base32()),
        )
        response = self.google_signin()
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

    def test_invalid_google_token_is_rejected(self):
        from apps.accounts.google_auth import InvalidGoogleIDToken

        with mock.patch(
            "apps.accounts.google_auth.verify_google_id_token",
            side_effect=InvalidGoogleIDToken(),
        ):
            response = self.client.post(
                "/medlife/google/signin", {"id_token": "invalid"}, format="json"
            )
        self.assertEqual(response.status_code, 401)
        self.assertFalse(Account.objects.exists())

    def test_google_signin_requires_id_token(self):
        response = self.client.post("/medlife/google/signin", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    @override_settings(GOOGLE_CLIENT_ID="")
    def test_missing_google_configuration_returns_service_unavailable(self):
        response = self.client.post(
            "/medlife/google/signin", {"id_token": "valid-google-id-token"}, format="json"
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn("detail", response.json())
        self.assertFalse(Account.objects.exists())


@override_settings(GOOGLE_CLIENT_ID=CLIENT_ID)
class GoogleIDTokenValidationTests(TestCase):
    def test_verifier_requires_google_verified_email_and_expected_audience(self):
        from apps.accounts.google_auth import InvalidGoogleIDToken, verify_google_id_token

        claims = {
            "iss": "https://accounts.google.com",
            "sub": "subject",
            "email": "USER@example.com",
            "email_verified": True,
        }
        with mock.patch("apps.accounts.google_auth.id_token.verify_oauth2_token", return_value=claims) as verify:
            result = verify_google_id_token("raw-token")
        self.assertEqual(result, {"sub": "subject", "email": "user@example.com"})
        self.assertEqual(verify.call_args.args[0], "raw-token")
        self.assertEqual(verify.call_args.kwargs["audience"], CLIENT_ID)

        for invalid_claims in (
            {**claims, "email_verified": False},
            {**claims, "iss": "https://attacker.example"},
            {**claims, "sub": ""},
            {**claims, "email": "not-an-email"},
        ):
            with mock.patch(
                "apps.accounts.google_auth.id_token.verify_oauth2_token",
                return_value=invalid_claims,
            ):
                with self.assertRaises(InvalidGoogleIDToken):
                    verify_google_id_token("raw-token")
