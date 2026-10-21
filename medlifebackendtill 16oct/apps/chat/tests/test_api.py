# Purpose: Tests chat save/fetch ordering, timestamp round-tripping, and cascade deletion.
# Add tests here when the persisted chat message contract changes.
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from apps.accounts.models import Account
from apps.members.models import FamilyMember
from apps.chat.models import ChatMessage
from apps.core.tests.helpers import auth_client

class ChatAPITests(TransactionTestCase):
    def setUp(self):
        self.client, account = auth_client("chat@example.com")
        self.member = FamilyMember.objects.create(account=account, slot=1, first_name="Sam")
        self.params = {"email": "chat@example.com", "member_name": "member1"}

    def test_replace_all_preserves_order_and_exact_timestamps(self):
        chat = [{"role": "user", "text": "hello", "ts": 1720000000123},
                {"role": "ai", "text": "hi there", "ts": 1720000000456}]
        r = self.client.post("/medlife/saveChat/?email=chat%40example.com&member_name=member1", {"chat": chat}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get("/medlife/fetchChat/", self.params).json(), {"chat": chat})
        replacement = [{"role": "user", "text": "replacement", "ts": 9999999999999}]
        self.client.post("/medlife/saveChat/?email=chat%40example.com&member_name=member1", {"chat": replacement}, format="json")
        self.assertEqual(self.client.get("/medlife/fetchChat/", self.params).json(), {"chat": replacement})

    def test_remove_member_cascades_chat(self):
        ChatMessage.objects.create(member=self.member, position=0, role="user", text="private", ts=123)
        self.client.post("/medlife/removemember?email=chat%40example.com&member_name=member1", {}, format="json")
        self.assertFalse(ChatMessage.objects.filter(member=self.member).exists())

    def test_chat_requires_token_and_is_private_to_owner(self):
        url = "/medlife/fetchChat/"
        self.assertEqual(APIClient().get(url, self.params).status_code, 401)
        intruder, _ = auth_client("intruder@example.com")
        self.assertEqual(intruder.get(url, self.params).status_code, 403)  # email != token's account
        self.assertEqual(intruder.get(url, {"member_name": "member1"}).status_code, 404)  # has no such member
