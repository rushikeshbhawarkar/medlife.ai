"""Tests for setting a password after Google sign-in and changing an existing password."""
from django.contrib.auth.hashers import make_password, check_password
from django.test import TestCase
from rest_framework.test import APIClient
import pyotp

from apps.accounts.models import Account
from apps.accounts.totp import encrypt_totp_secret
from apps.core.authentication import issue_account_token


class PasswordChangeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def authenticate(self, account):
        token = issue_account_token(account)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return token

    def change_password(self, **overrides):
        payload = {
            "new_password": "new-strong-password-42",
            "confirm_password": "new-strong-password-42",
        }
        payload.update(overrides)
        return self.client.post("/medlife/password/change", payload, format="json")

    def test_google_account_can_set_first_password_without_current_password(self):
        account = Account.objects.create(
            email="google@example.com",
            google_sub="google-subject",
            password="",
        )
        self.authenticate(account)

        response = self.change_password()
        self.assertEqual(response.status_code, 200, response.json())
        account.refresh_from_db()
        self.assertTrue(check_password("new-strong-password-42", account.password))
        self.assertTrue(response.json()["password_set"])

        # The returned token remains usable after the password fingerprint changes.
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access_token']}")
        me = self.client.get("/medlife/account/")
        self.assertEqual((me.status_code, me.json()["email"]), (200, account.email))

        # Password sign-in always needs TOTP. A Google-linked account that has not enrolled TOTP yet
        # must enrol (/medlife/totp/setup) before it can sign in with its new password.
        self.client.credentials()
        login = self.client.post(
            "/medlife/signin",
            {"email": account.email, "password": "new-strong-password-42"},
            format="json",
        )
        self.assertEqual(login.status_code, 403, login.json())
        self.assertNotIn("access_token", login.json())

    def test_password_account_can_change_password_without_current_password(self):
        account = Account.objects.create(
            email="normal@example.com",
            password=make_password("old-strong-password-42"),
            totp_enabled=True,
            totp_secret_encrypted=encrypt_totp_secret(pyotp.random_base32()),
        )
        self.authenticate(account)

        # 1. Changing password without supplying current_password key
        changed = self.change_password()
        self.assertEqual(changed.status_code, 200, changed.json())
        account.refresh_from_db()
        self.assertTrue(check_password("new-strong-password-42", account.password))

        # Refresh client credentials with the new token issued after the first change
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {changed.json()['access_token']}")

        # 2. Changing password with empty string current_password (matching frontend submission)
        changed_frontend_style = self.change_password(
            current_password="",
            new_password="another-strong-password-42",
            confirm_password="another-strong-password-42",
        )
        self.assertEqual(changed_frontend_style.status_code, 200, changed_frontend_style.json())
        account.refresh_from_db()
        self.assertTrue(check_password("another-strong-password-42", account.password))

        # 3. Explicitly providing an incorrect current_password is still rejected with 401
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {changed_frontend_style.json()['access_token']}")
        wrong = self.change_password(current_password="wrong-password")
        self.assertEqual(wrong.status_code, 401)

    def test_password_change_requires_authentication(self):
        response = self.change_password()
        self.assertEqual(response.status_code, 401)

    def test_cannot_change_another_user_password(self):
        victim = Account.objects.create(
            email="victim@example.com",
            password=make_password("victim-password-123"),
            totp_enabled=True,
            totp_secret_encrypted=encrypt_totp_secret(pyotp.random_base32()),
        )
        attacker = Account.objects.create(
            email="attacker@example.com",
            password=make_password("attacker-password-123"),
            totp_enabled=True,
            totp_secret_encrypted=encrypt_totp_secret(pyotp.random_base32()),
        )
        self.authenticate(attacker)

        # Attacker cannot alter victim's password by supplying victim's email or account_id
        resp = self.change_password(
            email="victim@example.com",
            account_id=victim.pk,
            new_password="hacked-password-123",
            confirm_password="hacked-password-123",
        )
        self.assertEqual(resp.status_code, 200)
        victim.refresh_from_db()
        attacker.refresh_from_db()
        self.assertTrue(check_password("victim-password-123", victim.password))
        self.assertTrue(check_password("hacked-password-123", attacker.password))

    def test_password_change_rejects_mismatched_confirmation(self):
        account = Account.objects.create(
            email="google@example.com",
            google_sub="google-subject",
            password="",
        )
        self.authenticate(account)
        response = self.change_password(confirm_password="different-password-42")
        self.assertEqual(response.status_code, 400)
        account.refresh_from_db()
        self.assertEqual(account.password, "")

    def test_password_change_rejects_short_password(self):
        account = Account.objects.create(
            email="short@example.com",
            password=make_password("existing-password-42"),
            totp_enabled=True,
            totp_secret_encrypted=encrypt_totp_secret(pyotp.random_base32()),
        )
        self.authenticate(account)
        response = self.change_password(new_password="123", confirm_password="123")
        self.assertEqual(response.status_code, 400)
        account.refresh_from_db()
        self.assertTrue(check_password("existing-password-42", account.password))
