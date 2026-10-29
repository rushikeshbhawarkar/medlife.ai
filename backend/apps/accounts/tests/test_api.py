# # Purpose: PostgreSQL-backed tests for sign-up/sign-in contracts, password hashing and legacy accounts.
# # Add a test here whenever account API behavior changes.
# from django.test import TestCase
# from rest_framework.test import APIClient
# from django.core.cache import cache
# from apps.accounts.models import Account
# from apps.members.models import FamilyMember

# class AccountAuthTests(TestCase):
#     def setUp(self):
#         cache.clear()  # rate-limit counters must not leak between tests
#         self.client = APIClient()

#     def signup(self, email="User@Example.com", password="secret1"):
#         return self.client.post("/medlife/signup", {"email": email, "password": password}, format="json")

#     def signin(self, email="user@example.com", password="secret1"):
#         return self.client.post("/medlife/signin", {"email": email, "password": password}, format="json")

#     def test_signup_stores_hash_not_plain_password(self):
#         r = self.signup()
#         self.assertEqual(r.status_code, 201)
#         account = Account.objects.get(email="user@example.com")  # email normalized to lowercase
#         self.assertTrue(account.password.startswith("pbkdf2_sha256$"))
#         self.assertNotIn("secret1", account.password)

#     def test_duplicate_signup_returns_detail_error(self):
#         self.signup()
#         r = self.signup(password="another1")
#         self.assertEqual(r.status_code, 409)
#         self.assertEqual(r.json(), {"detail": "An account with this email already exists. Please sign in."})
#         # The original password still works; the duplicate attempt changed nothing.
#         self.assertEqual(self.signin().status_code, 200)

#     def test_signin_success_and_failures(self):
#         self.signup()
#         self.assertEqual(self.signin(email="USER@example.com").status_code, 200)
#         wrong = self.signin(password="wrong-pass")
#         self.assertEqual(wrong.status_code, 401)
#         self.assertEqual(wrong.json(), {"detail": "Incorrect email or password."})
#         unknown = self.signin(email="nobody@example.com")
#         self.assertEqual(unknown.status_code, 401)
#         self.assertEqual(unknown.json(), wrong.json())  # same message: no account-existence leak

#     def test_validation_errors_use_detail_shape(self):
#         r = self.signup(password="123")
#         self.assertEqual(r.status_code, 400)
#         self.assertIn("detail", r.json())
#         r = self.signup(email="not-an-email")
#         self.assertEqual(r.status_code, 400)
#         self.assertIn("detail", r.json())

#     def test_legacy_email_only_account_cannot_be_claimed_without_verification(self):
#         """An old email-only account must not be taken over by whoever signs up first; its data stays intact."""
#         legacy = Account.objects.create(email="user@example.com")  # no password, like pre-password accounts
#         FamilyMember.objects.create(account=legacy, slot=1, first_name="Asha")
#         self.assertEqual(self.signin().status_code, 401)   # no password yet
#         r = self.signup()
#         self.assertEqual(r.status_code, 403)
#         self.assertIn("detail", r.json())
#         legacy.refresh_from_db()
#         self.assertEqual(legacy.password, "")               # not claimed
#         self.assertTrue(FamilyMember.objects.filter(account=legacy, first_name="Asha").exists())

#     def test_signin_token_unlocks_api_and_garbage_token_does_not(self):
#         self.signup()
#         token = self.signin().json()["access_token"]
#         self.assertEqual(self.client.get("/medlife/account/").status_code, 401)
#         self.assertEqual(self.client.get("/medlife/account/", HTTP_AUTHORIZATION="Bearer not.a.token").status_code, 401)
#         r = self.client.get("/medlife/account/", HTTP_AUTHORIZATION=f"Bearer {token}")
#         self.assertEqual((r.status_code, r.json()["email"]), (200, "user@example.com"))
#         self.assertEqual(self.client.get("/medlife/health/").status_code, 200)  # health stays public

#     def test_account_endpoint_never_creates_accounts(self):
#         self.client.get("/medlife/account/", {"email": "ghost@example.com"})
#         self.assertFalse(Account.objects.filter(email="ghost@example.com").exists())

#     def test_signin_is_rate_limited(self):
#         codes = [self.signin(password="wrong-pass").status_code for _ in range(12)]
#         self.assertEqual(codes[0], 401)
#         self.assertIn(429, codes)

















# Purpose: Tests for mandatory TOTP signup, login, token access, and password validation.
from django.test import TestCase
from rest_framework.test import APIClient
from django.core.cache import cache
import pyotp

from apps.accounts.models import Account
from apps.accounts.totp import decrypt_totp_secret


class AccountAuthTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def signup(self, email="User@Example.com", password="secret1"):
        return self.client.post("/medlife/signup", {"email": email, "password": password}, format="json")

    def signin(self, email="user@example.com", password="secret1"):
        return self.client.post("/medlife/signin", {"email": email, "password": password}, format="json")

    def finish_setup(self, signup_response):
        body = signup_response.json()
        code = pyotp.TOTP(body["manual_key"]).now()
        return self.client.post(
            "/medlife/totp/verify-setup",
            {"setup_token": body["setup_token"], "code": code},
            format="json",
        )

    def finish_login(self, signin_response, code=None):
        body = signin_response.json()
        account = Account.objects.get(email=body["email"])
        secret = decrypt_totp_secret(account.totp_secret_encrypted)
        code = code or pyotp.TOTP(secret).now()
        return self.client.post(
            "/medlife/totp/verify-login",
            {"challenge_token": body["challenge_token"], "code": code},
            format="json",
        )

    def test_signup_stores_hash_and_returns_totp_setup_not_access_token(self):
        response = self.signup()
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertTrue(body["totp_setup_required"])
        self.assertTrue(body["qr_code"].startswith("data:image/png;base64,"))
        self.assertIn("manual_key", body)
        self.assertIn("setup_token", body)
        self.assertNotIn("access_token", body)
        account = Account.objects.get(email="user@example.com")
        self.assertTrue(account.password.startswith("pbkdf2_sha256$"))
        self.assertNotIn("secret1", account.password)
        self.assertFalse(account.totp_enabled)
        self.assertTrue(account.totp_pending_secret_encrypted)
        self.assertFalse(account.totp_secret_encrypted)

    def test_duplicate_signup_returns_conflict(self):
        self.signup()
        response = self.signup(password="another1")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": "An account with this email already exists. Please sign in."})

    def test_setup_verification_activates_account_and_issues_access_token(self):
        response = self.signup()
        verified = self.finish_setup(response)
        self.assertEqual(verified.status_code, 200, verified.json())
        body = verified.json()
        self.assertTrue(body["totp_enabled"])
        self.assertIn("access_token", body)
        account = Account.objects.get(email="user@example.com")
        self.assertTrue(account.totp_enabled)
        self.assertTrue(account.totp_secret_encrypted)
        self.assertEqual(account.totp_pending_secret_encrypted, "")

    def test_signin_requires_totp_challenge_then_issues_access_token(self):
        signup_response = self.signup(email="second@example.com")
        self.assertEqual(self.finish_setup(signup_response).status_code, 200)

        signin_response = self.signin(email="second@example.com")
        self.assertEqual(signin_response.status_code, 200)
        self.assertTrue(signin_response.json()["totp_required"])
        self.assertIn("challenge_token", signin_response.json())
        self.assertNotIn("access_token", signin_response.json())
        challenge_token = signin_response.json()["challenge_token"]
        self.assertEqual(
            self.client.get("/medlife/account/", HTTP_AUTHORIZATION=f"Bearer {challenge_token}").status_code,
            401,
        )
        login_verified = self.finish_login(signin_response)
        self.assertEqual(login_verified.status_code, 200, login_verified.json())
        self.assertIn("access_token", login_verified.json())
        token = login_verified.json()["access_token"]
        me = self.client.get("/medlife/account/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual((me.status_code, me.json()["email"]), (200, "second@example.com"))

    def test_same_totp_step_cannot_be_reused_for_login(self):
        signup_response = self.signup()
        self.assertEqual(self.finish_setup(signup_response).status_code, 200)
        challenge = self.signin()
        self.assertEqual(challenge.status_code, 200)
        body = challenge.json()
        account = Account.objects.get(email="user@example.com")
        code = pyotp.TOTP(decrypt_totp_secret(account.totp_secret_encrypted)).now()
        first = self.client.post("/medlife/totp/verify-login", {"challenge_token": body["challenge_token"], "code": code}, format="json")
        self.assertEqual(first.status_code, 200, first.json())
        second = self.client.post("/medlife/totp/verify-login", {"challenge_token": body["challenge_token"], "code": code}, format="json")
        self.assertEqual(second.status_code, 401)

    def test_signin_failures_use_generic_credentials_error(self):
        wrong = self.signin(password="wrong-pass")
        self.assertEqual(wrong.status_code, 401)
        self.assertEqual(wrong.json(), {"detail": "Incorrect email or password."})
        unknown = self.signin(email="nobody@example.com")
        self.assertEqual(unknown.status_code, 401)
        self.assertEqual(unknown.json(), wrong.json())

    def test_validation_errors_use_detail_shape(self):
        response = self.signup(password="123")
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
        response = self.signup(email="not-an-email")
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_pending_account_cannot_access_protected_endpoint(self):
        response = self.signup()
        account = Account.objects.get(email="user@example.com")
        self.assertFalse(account.totp_enabled)
        self.assertEqual(self.client.get("/medlife/account/").status_code, 401)
        self.assertNotIn("access_token", response.json())
        setup_token = response.json()["setup_token"]
        self.assertEqual(
            self.client.get("/medlife/account/", HTTP_AUTHORIZATION=f"Bearer {setup_token}").status_code,
            401,
        )

    def test_setup_can_be_restarted_for_pending_account(self):
        self.signup()
        restarted = self.client.post("/medlife/totp/setup", {"email": "user@example.com", "password": "secret1"}, format="json")
        self.assertEqual(restarted.status_code, 200, restarted.json())
        self.assertTrue(restarted.json()["qr_code"].startswith("data:image/png;base64,"))

    def test_signin_is_rate_limited(self):
        codes = [self.signin(password="wrong-pass").status_code for _ in range(12)]
        self.assertEqual(codes[0], 401)
        self.assertIn(429, codes)

    def test_health_stays_public(self):
        self.assertEqual(self.client.get("/medlife/health/").status_code, 200)
