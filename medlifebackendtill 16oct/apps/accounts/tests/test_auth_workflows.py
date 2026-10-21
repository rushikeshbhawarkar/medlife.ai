"""Regression tests for mandatory Google password setup and emailed TOTP recovery."""
import re
from urllib.parse import unquote

import pyotp
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.accounts.totp import decrypt_totp_secret, encrypt_totp_secret

GOOGLE_CLAIMS = {
    "sub": "google-subject-new-user",
    "email": "new-user@example.com",
}


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="MedLife <no-reply@medlife.test>",
    FRONTEND_TOTP_RECOVERY_URL="https://app.medlife.test/recover-totp",
    TOTP_RECOVERY_TIMEOUT=900,
)
class AuthWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_password_login_with_no_totp_returns_enrollment_qr_not_access_token(self):
        Account.objects.create(email="first-login@example.com", password=make_password("Strong#Pass987"))
        response = self.client.post("/medlife/signin", {
            "email": "first-login@example.com", "password": "Strong#Pass987"
        }, format="json")
        self.assertEqual(response.status_code, 200, response.json())
        self.assertTrue(response.json()["totp_setup_required"])
        self.assertIn("setup_token", response.json())
        self.assertNotIn("access_token", response.json())

        code = pyotp.TOTP(response.json()["manual_key"]).now()
        verified = self.client.post("/medlife/totp/verify-setup", {
            "setup_token": response.json()["setup_token"], "code": code
        }, format="json")
        self.assertEqual(verified.status_code, 200, verified.json())
        self.assertIn("access_token", verified.json())

    def test_recovery_email_link_can_replace_totp_and_old_link_cannot_be_reused(self):
        old_secret = pyotp.random_base32()
        account = Account.objects.create(
            email="recover@example.com",
            password=make_password("Strong#Pass987"),
            totp_enabled=True,
            totp_secret_encrypted=encrypt_totp_secret(old_secret),
        )
        response = self.client.post("/medlife/totp/recovery/request", {
            "email": "recover@example.com"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("https://app.medlife.test/recover-totp#token=", mail.outbox[0].body)
        match = re.search(r"#token=(\\S+)", mail.outbox[0].body)
        self.assertIsNotNone(match)
        token = unquote(match.group(1))

        setup = self.client.post("/medlife/totp/recovery/setup", {
            "recovery_token": token
        }, format="json")
        self.assertEqual(setup.status_code, 200, setup.json())
        new_secret = setup.json()["manual_key"]
        self.assertNotEqual(new_secret, old_secret)

        code = pyotp.TOTP(new_secret).now()
        verified = self.client.post("/medlife/totp/recovery/verify", {
            "recovery_token": token, "code": code
        }, format="json")
        self.assertEqual(verified.status_code, 200, verified.json())
        account.refresh_from_db()
        self.assertEqual(decrypt_totp_secret(account.totp_secret_encrypted), new_secret)
        self.assertFalse(account.totp_pending_secret_encrypted)

        replay = self.client.post("/medlife/totp/recovery/setup", {
            "recovery_token": token
        }, format="json")
        self.assertEqual(replay.status_code, 401)

    def test_recovery_response_does_not_disclose_unknown_email(self):
        response = self.client.post("/medlife/totp/recovery/request", {
            "email": "not-registered@example.com"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn("If the address belongs", response.json()["detail"])
