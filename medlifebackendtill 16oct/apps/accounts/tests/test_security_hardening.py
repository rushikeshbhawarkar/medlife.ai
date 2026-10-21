# Purpose: Tests for password-change notification email, TOTP on every password sign-in, and TOTP lockout.
# Run: python manage.py test apps.accounts.tests.test_security_hardening
import pyotp
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.accounts.totp import encrypt_totp_secret
from apps.core.authentication import issue_account_token

PASSWORD = "old-strong-password-42"


class SecurityHardeningTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def make_account(self, email="sec@example.com", google_sub=None, totp=True):
        secret = pyotp.random_base32()
        account = Account.objects.create(
            email=email,
            google_sub=google_sub,
            password=make_password(PASSWORD),
            totp_enabled=totp,
            totp_secret_encrypted=encrypt_totp_secret(secret) if totp else "",
        )
        return account, secret

    def signin(self):
        self.client.credentials()
        return self.client.post("/medlife/signin", {"email": "sec@example.com", "password": PASSWORD}, format="json")

    def verify_login(self, challenge_token, code):
        self.client.credentials()
        return self.client.post(
            "/medlife/totp/verify-login", {"challenge_token": challenge_token, "code": code}, format="json"
        )

    # --- password change sends an email -------------------------------------------------------
    def test_password_change_sends_notification_email(self):
        account, _ = self.make_account()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_account_token(account)}")
        response = self.client.post(
            "/medlife/password/change",
            {"current_password": PASSWORD, "new_password": "new-strong-password-77", "confirm_password": "new-strong-password-77"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, [account.email])
        self.assertIn("changed", message.subject.lower())
        self.assertNotIn("new-strong-password-77", message.body)

    def test_failed_password_change_sends_no_email(self):
        account, _ = self.make_account()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_account_token(account)}")
        response = self.client.post(
            "/medlife/password/change",
            {"current_password": "wrong-password", "new_password": "new-strong-password-77", "confirm_password": "new-strong-password-77"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(mail.outbox), 0)

    # --- TOTP on every password sign-in -------------------------------------------------------
    def test_google_linked_account_with_totp_gets_challenge_on_password_signin(self):
        self.make_account(google_sub="google-subject-1", totp=True)
        response = self.signin()
        self.assertEqual(response.status_code, 200, response.json())
        body = response.json()
        self.assertTrue(body["totp_required"])
        self.assertIn("challenge_token", body)
        self.assertNotIn("access_token", body)

    def test_google_linked_account_without_totp_cannot_password_signin(self):
        self.make_account(google_sub="google-subject-2", totp=False)
        response = self.signin()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["totp_setup_required"])
        self.assertIn("setup_token", response.json())
        self.assertNotIn("access_token", response.json())

    # --- TOTP lockout --------------------------------------------------------------------------
    def test_totp_login_locks_after_five_wrong_codes(self):
        _, secret = self.make_account()
        challenge = self.signin().json()["challenge_token"]
        good = pyotp.TOTP(secret).now()
        wrong = "000000" if good != "000000" else "111111"
        for _ in range(5):
            self.assertEqual(self.verify_login(challenge, wrong).status_code, 401)
        locked = self.verify_login(challenge, good)  # even the right code is refused while locked
        self.assertEqual(locked.status_code, 429)
        self.assertNotIn("access_token", locked.json())

    def test_successful_totp_login_clears_failure_count(self):
        _, secret = self.make_account()
        challenge = self.signin().json()["challenge_token"]
        good = pyotp.TOTP(secret).now()
        wrong = "000000" if good != "000000" else "111111"
        for _ in range(4):
            self.assertEqual(self.verify_login(challenge, wrong).status_code, 401)
        ok = self.verify_login(challenge, good)
        self.assertEqual(ok.status_code, 200, ok.json())
        self.assertIn("access_token", ok.json())
