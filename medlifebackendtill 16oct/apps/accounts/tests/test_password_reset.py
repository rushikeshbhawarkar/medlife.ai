# Purpose: Tests for "forgot password" / "reset password": email contents, token life and reuse, password rules,
# rate limits, mail failure, and proof that TOTP and the existing sign-in services are untouched.
# Run: python manage.py test apps.accounts.tests.test_password_reset
import re
import threading
import time
from unittest import mock
from urllib.parse import unquote

import pyotp
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.core.cache import cache
from django.db import connection
from django.test import TestCase, TransactionTestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.accounts.services import (
    EXPIRED_RESET_LINK, INVALID_RESET_LINK, RESET_REQUEST_MESSAGE, InvalidCredentials,
    make_reset_token, reset_password, verify_credentials,
)
from apps.accounts.totp import encrypt_totp_secret
from apps.core.authentication import TOKEN_SALT, issue_account_token

OLD = "OldPass#2024"
NEW = "Brand-New#Pass9"
RESET_URL = "https://app.medlife.test/reset-password"


def make_account(email="user@example.com", password=OLD):
    return Account.objects.create(
        email=email,
        password=make_password(password),
        totp_enabled=True,
        totp_secret_encrypted=encrypt_totp_secret(pyotp.random_base32()),
    )


def token_from_outbox(index=-1):
    body = mail.outbox[index].body
    match = re.search(r"#token=(\S+)", body)
    assert match, body
    return unquote(match.group(1))


@override_settings(FRONTEND_PASSWORD_RESET_URL=RESET_URL, PASSWORD_RESET_TIMEOUT=300,
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
                   DEFAULT_FROM_EMAIL="MedLife <no-reply@medlife.test>")
class ForgotPasswordTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.account = make_account()

    def forgot(self, email="user@example.com"):
        return self.client.post("/medlife/password/forgot", {"email": email}, format="json")

    def reset(self, token, new=NEW, confirm=None):
        return self.client.post(
            "/medlife/password/reset",
            {"token": token, "new_password": new, "confirm_password": new if confirm is None else confirm},
            format="json",
        )

    def request_token(self):
        self.assertEqual(self.forgot().status_code, 200)
        return token_from_outbox()

    # 1, 2, 3 ------------------------------------------------------------------------------------------
    def test_registered_email_gets_one_email_and_generic_reply(self):
        r = self.forgot("User@Example.com")  # case-insensitive
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"ok": True, "detail": RESET_REQUEST_MESSAGE})
        self.assertEqual(len(mail.outbox), 1)

    def test_unknown_email_gets_identical_reply_and_no_email(self):
        known = self.forgot()
        unknown = self.forgot("nobody@example.com")
        self.assertEqual(unknown.status_code, 200)
        self.assertEqual(unknown.json(), known.json())
        self.assertEqual(len(mail.outbox), 1)  # only the registered address was mailed

    def test_email_contents_and_reset_url(self):
        self.forgot()
        message = mail.outbox[0]
        self.assertEqual(message.to, ["user@example.com"])
        self.assertEqual(message.from_email, "MedLife <no-reply@medlife.test>")
        self.assertEqual(message.subject, "Reset your MedLife password")
        self.assertIn("5 minutes", message.body)
        self.assertIn(RESET_URL + "#token=", message.body)
        self.assertNotIn("?token=", message.body)  # fragment, not query string: stays out of server logs
        self.assertNotIn(OLD, message.body)
        self.assertNotIn(self.account.password, message.body)

    def test_malformed_missing_and_blank_email_are_rejected(self):
        for body in ({"email": "not-an-email"}, {}, {"email": ""}):
            r = self.client.post("/medlife/password/forgot", body, format="json")
            self.assertEqual(r.status_code, 400, body)
            self.assertIn("detail", r.json())
        self.assertEqual(len(mail.outbox), 0)

    # 14 -----------------------------------------------------------------------------------------------
    def test_forgot_is_rate_limited_per_ip(self):
        statuses = [self.forgot(f"nobody{i}@example.com").status_code for i in range(6)]
        self.assertEqual(statuses, [200] * 5 + [429])

    def test_same_address_cannot_be_mailed_twice_within_cooldown(self):
        self.assertEqual(self.forgot().status_code, 200)
        self.assertEqual(self.forgot().status_code, 200)  # same generic answer ...
        self.assertEqual(len(mail.outbox), 1)             # ... but only one email

    # 4, 5 ---------------------------------------------------------------------------------------------
    def test_token_valid_just_before_expiry(self):
        token = self.request_token()
        with mock.patch("django.core.signing.time.time", return_value=time.time() + 295):
            r = self.reset(token)
        self.assertEqual(r.status_code, 200, r.content)

    def test_token_rejected_after_300_seconds(self):
        token = self.request_token()
        with mock.patch("django.core.signing.time.time", return_value=time.time() + 305):
            r = self.reset(token)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), {"detail": EXPIRED_RESET_LINK})
        self.account.refresh_from_db()
        self.assertTrue(verify_credentials("user@example.com", OLD))  # unchanged

    def test_timeout_follows_setting(self):
        token = self.request_token()
        with override_settings(PASSWORD_RESET_TIMEOUT=10):
            with mock.patch("django.core.signing.time.time", return_value=time.time() + 30):
                r = self.reset(token)
        self.assertEqual(r.status_code, 400)

    # 6 ------------------------------------------------------------------------------------------------
    def test_invalid_and_tampered_tokens_rejected(self):
        token = self.request_token()
        tampered = token[:-2] + ("AA" if not token.endswith("AA") else "BB")
        wrong_purpose = issue_account_token(self.account)  # a real signed token, but for another purpose
        for bad in ("garbage", "a:b:c", tampered, wrong_purpose, token[: len(token) // 2]):
            r = self.reset(bad)
            self.assertEqual(r.status_code, 400, bad)
            self.assertEqual(r.json(), {"detail": INVALID_RESET_LINK}, bad)
        self.assertTrue(verify_credentials("user@example.com", OLD))

    def test_token_is_bound_to_its_own_account(self):
        other = make_account("other@example.com", "Other#Pass77")
        token_for_user = self.request_token()
        self.assertEqual(self.reset(token_for_user).status_code, 200)
        other.refresh_from_db()
        self.assertTrue(verify_credentials("other@example.com", "Other#Pass77"))  # untouched

    def test_missing_fields_rejected(self):
        for body in ({}, {"token": "x"}, {"token": "x", "new_password": NEW}, {"new_password": NEW, "confirm_password": NEW}):
            r = self.client.post("/medlife/password/reset", body, format="json")
            self.assertEqual(r.status_code, 400, body)
            self.assertIn("detail", r.json())

    def test_deleted_account_token_rejected(self):
        token = self.request_token()
        self.account.delete()
        r = self.reset(token)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), {"detail": INVALID_RESET_LINK})

    # 7 ------------------------------------------------------------------------------------------------
    def test_token_cannot_be_reused_after_success(self):
        token = self.request_token()
        self.assertEqual(self.reset(token).status_code, 200)
        again = self.reset(token, new="Another#Pass123")
        self.assertEqual(again.status_code, 400)
        self.assertEqual(again.json(), {"detail": INVALID_RESET_LINK})
        self.assertTrue(verify_credentials("user@example.com", NEW))  # second attempt changed nothing

    def test_newer_password_change_invalidates_older_token(self):
        token = self.request_token()
        self.account.password = make_password("Changed#Elsewhere1")
        self.account.save(update_fields=["password"])
        self.assertEqual(self.reset(token).status_code, 400)

    # 8, 9 ---------------------------------------------------------------------------------------------
    def test_confirmation_mismatch_rejected_and_token_stays_usable(self):
        token = self.request_token()
        r = self.reset(token, confirm="Different#Pass1")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), {"detail": "Passwords do not match."})
        self.assertTrue(verify_credentials("user@example.com", OLD))
        self.assertEqual(self.reset(token).status_code, 200)  # a typo does not burn the link

    def test_weak_passwords_rejected_and_token_stays_usable(self):
        token = self.request_token()
        for weak in ("abc", "123456", "12345678901", "password", "user@example.com", OLD):
            r = self.reset(token, new=weak)
            self.assertEqual(r.status_code, 400, weak)
            self.assertIn("detail", r.json())
        self.assertTrue(verify_credentials("user@example.com", OLD))
        self.assertEqual(self.reset(token).status_code, 200)

    # 10, 11, 12 ---------------------------------------------------------------------------------------
    def test_successful_reset_hashes_password_and_old_one_stops_working(self):
        token = self.request_token()
        r = self.reset(token)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        self.account.refresh_from_db()
        self.assertTrue(self.account.password.startswith("pbkdf2_sha256$"))
        self.assertNotIn(NEW, self.account.password)
        self.assertEqual(verify_credentials("user@example.com", NEW).pk, self.account.pk)  # existing service
        with self.assertRaises(InvalidCredentials):
            verify_credentials("user@example.com", OLD)
        self.assertEqual(self.client.post("/medlife/signin", {"email": "user@example.com", "password": NEW}, format="json").status_code, 200)
        self.assertEqual(self.client.post("/medlife/signin", {"email": "user@example.com", "password": OLD}, format="json").status_code, 401)

    def test_response_does_not_log_in_or_return_a_token(self):
        body = self.reset(self.request_token()).json()
        self.assertEqual(set(body), {"ok", "detail"})

    # 13 -----------------------------------------------------------------------------------------------
    def test_totp_stays_enabled_and_mandatory_after_reset(self):
        before = Account.objects.get(pk=self.account.pk)
        self.assertEqual(self.reset(self.request_token()).status_code, 200)
        after = Account.objects.get(pk=self.account.pk)
        self.assertTrue(after.totp_enabled)
        self.assertEqual(after.totp_secret_encrypted, before.totp_secret_encrypted)
        self.assertEqual(after.totp_pending_secret_encrypted, before.totp_pending_secret_encrypted)
        self.assertEqual(after.totp_last_verified_step, before.totp_last_verified_step)
        signin = self.client.post("/medlife/signin", {"email": "user@example.com", "password": NEW}, format="json").json()
        self.assertTrue(signin["totp_required"])
        self.assertIn("challenge_token", signin)
        self.assertNotIn("access_token", signin)  # password alone still does not log anyone in

    # sessions -----------------------------------------------------------------------------------------
    def test_reset_revokes_older_access_tokens_but_not_new_ones(self):
        old_token = issue_account_token(self.account)
        me = lambda t: self.client.get("/medlife/account/", HTTP_AUTHORIZATION=f"Bearer {t}").status_code  # noqa: E731
        self.assertEqual(me(old_token), 200)
        self.assertEqual(self.reset(self.request_token()).status_code, 200)
        self.assertEqual(me(old_token), 401)
        self.account.refresh_from_db()
        self.assertEqual(me(issue_account_token(self.account)), 200)

    def test_access_tokens_issued_before_this_feature_keep_working(self):
        from django.core import signing
        legacy = signing.dumps({"account_id": self.account.pk, "purpose": "access"}, salt=TOKEN_SALT, compress=True)
        r = self.client.get("/medlife/account/", HTTP_AUTHORIZATION=f"Bearer {legacy}")
        self.assertEqual(r.status_code, 200)

    # 15 -----------------------------------------------------------------------------------------------
    def test_email_failure_is_hidden_from_caller_logged_safely_and_retryable(self):
        import smtplib
        with mock.patch("apps.accounts.services.send_mail", side_effect=smtplib.SMTPAuthenticationError(535, b"bad credentials")):
            with self.assertLogs("apps.accounts.services", level="ERROR") as logs:
                r = self.forgot()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"ok": True, "detail": RESET_REQUEST_MESSAGE})  # no hint of failure
        logged = "\n".join(logs.output)
        self.assertIn("SMTPAuthenticationError", logged)
        self.assertNotIn("user@example.com", logged)
        self.assertNotIn("token", logged.lower().replace("check the email_* settings", ""))
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(self.forgot().status_code, 200)  # cooldown was released, so a retry sends
        self.assertEqual(len(mail.outbox), 1)

    def test_tokens_are_never_logged_on_the_success_path(self):
        with self.assertNoLogs("apps.accounts", level="DEBUG"):
            self.forgot()
            self.reset(token_from_outbox())


@override_settings(FRONTEND_PASSWORD_RESET_URL=RESET_URL, PASSWORD_RESET_TIMEOUT=300)
class ResetConcurrencyTests(TransactionTestCase):
    def test_two_simultaneous_resets_with_one_token_only_one_wins(self):
        account = make_account()
        token = make_reset_token(account)
        barrier = threading.Barrier(2)
        results = []

        def attempt(password):
            try:
                barrier.wait(timeout=10)
                reset_password(token, password)
                results.append(("ok", password))
            except Exception as exc:  # InvalidResetToken for the loser
                results.append(("fail", type(exc).__name__))
            finally:
                connection.close()

        threads = [threading.Thread(target=attempt, args=(p,)) for p in ("First#Winner11", "Second#Winner22")]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
        winners = [r for r in results if r[0] == "ok"]
        self.assertEqual(len(winners), 1, results)
        self.assertEqual(len(results), 2, results)
        self.assertTrue(verify_credentials("user@example.com", winners[0][1]))
