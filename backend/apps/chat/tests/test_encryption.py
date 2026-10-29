from datetime import timedelta
from io import StringIO

from django.contrib import admin
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TransactionTestCase, override_settings
from django.utils import timezone

from apps.chat.crypto import TOKEN_PREFIX, decrypt_text, encrypt_text
from apps.chat.models import ChatMessage
from apps.core.tests.helpers import auth_client
from apps.members.models import FamilyMember


def raw_text(pk):
    with connection.cursor() as cursor:
        cursor.execute("SELECT text FROM chat_chatmessage WHERE id = %s", [pk])
        return cursor.fetchone()[0]


class ChatEncryptionTests(TransactionTestCase):
    def setUp(self):
        self.client, account = auth_client("crypt@example.com")
        self.member = FamilyMember.objects.create(account=account, slot=1, first_name="Sam")

    def test_text_is_ciphertext_in_the_database_and_plain_in_python(self):
        msg = ChatMessage.objects.create(member=self.member, position=0, role="user", text="I take warfarin", ts=1)
        stored = raw_text(msg.pk)
        self.assertTrue(stored.startswith(TOKEN_PREFIX))
        self.assertNotIn("warfarin", stored)
        self.assertEqual(ChatMessage.objects.get(pk=msg.pk).text, "I take warfarin")

    def test_api_round_trip_is_unchanged_for_the_frontend(self):
        chat = [{"role": "user", "text": "chest pain? ünïcode ✓", "ts": 1720000000123},
                {"role": "ai", "text": "please see a doctor", "ts": 1720000000456}]
        url = "/medlife/saveChat/?member_name=member1"
        self.assertEqual(self.client.post(url, {"chat": chat}, format="json").status_code, 200)
        self.assertEqual(self.client.get("/medlife/fetchChat/", {"member_name": "member1"}).json(), {"chat": chat})
        for pk in ChatMessage.objects.values_list("pk", flat=True):
            self.assertTrue(raw_text(pk).startswith(TOKEN_PREFIX))

    def test_saving_an_empty_chat_deletes_everything(self):
        ChatMessage.objects.create(member=self.member, position=0, role="user", text="x", ts=1)
        self.client.post("/medlife/saveChat/?member_name=member1", {"chat": []}, format="json")
        self.assertFalse(ChatMessage.objects.filter(member=self.member).exists())

    def test_legacy_plaintext_rows_are_still_readable(self):
        msg = ChatMessage.objects.create(member=self.member, position=0, role="user", text="placeholder", ts=1)
        with connection.cursor() as cursor:
            cursor.execute("UPDATE chat_chatmessage SET text = %s WHERE id = %s", ["old plaintext", msg.pk])
        self.assertEqual(ChatMessage.objects.get(pk=msg.pk).text, "old plaintext")

    def test_wrong_key_fails_loudly_instead_of_showing_ciphertext(self):
        msg = ChatMessage.objects.create(member=self.member, position=0, role="user", text="secret", ts=1)
        from cryptography.fernet import Fernet
        with override_settings(TOTP_ENCRYPTION_KEY=Fernet.generate_key().decode()):
            with self.assertRaises(RuntimeError):
                ChatMessage.objects.get(pk=msg.pk)

    def test_crypto_helpers(self):
        token = encrypt_text("hello")
        self.assertNotEqual(token, "hello")
        self.assertNotEqual(encrypt_text("hello"), token)  # random IV
        self.assertEqual(decrypt_text(token), "hello")
        self.assertEqual(decrypt_text("plain"), "plain")

    def test_admin_cannot_search_or_see_message_text(self):
        model_admin = admin.site._registry[ChatMessage]
        self.assertNotIn("text", model_admin.search_fields)
        self.assertIn("text", model_admin.exclude)


class PurgeOldChatsTests(TransactionTestCase):
    def setUp(self):
        _, account = auth_client("purge@example.com")
        self.member = FamilyMember.objects.create(account=account, slot=1, first_name="Sam")
        self.old = ChatMessage.objects.create(member=self.member, position=0, role="user", text="old", ts=1)
        self.new = ChatMessage.objects.create(member=self.member, position=1, role="ai", text="new", ts=2)
        ChatMessage.objects.filter(pk=self.old.pk).update(created_at=timezone.now() - timedelta(days=120))

    def test_dry_run_deletes_nothing(self):
        out = StringIO()
        call_command("purge_old_chats", "--days", "90", "--dry-run", stdout=out)
        self.assertIn("1 chat message", out.getvalue())
        self.assertEqual(ChatMessage.objects.count(), 2)

    def test_deletes_only_stale_messages(self):
        call_command("purge_old_chats", "--days", "90", stdout=StringIO())
        self.assertEqual(list(ChatMessage.objects.values_list("pk", flat=True)), [self.new.pk])

    def test_rejects_nonsense_days(self):
        with self.assertRaises(CommandError):
            call_command("purge_old_chats", "--days", "0", stdout=StringIO())
