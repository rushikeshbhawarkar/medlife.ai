# Purpose: PostgreSQL-backed tests for member endpoint contracts, validation, limits, IDs, and tokens.
# Add a test here whenever member API behavior or service rules change.
from concurrent.futures import ThreadPoolExecutor
from django.db import close_old_connections, connections
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from apps.accounts.models import Account
from apps.members.models import FamilyMember
from apps.core.tests.helpers import auth_client

EMAIL = "  TEST@example.com "
PROFILE = {"firstName": "Asha", "lastName": "Patel", "dob": "2000-01-01",
           "gender": "Female", "race": "", "height": "5.5ft", "weight": "60kg",
           "a1c": "5.6", "bloodPressure": "120/80", "medicine": "Vitamin D"}

class MemberAPITests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client, self.account = auth_client("test@example.com")

    def add(self, email="test@example.com", profile=None):
        return self.client.post("/medlife/addmember", {**(profile or PROFILE), "email": email, "tokens": 99}, format="json")

    def test_endpoints_require_a_token(self):
        anon = APIClient()
        self.assertEqual(anon.get("/medlife/getmember", {"email": "test@example.com"}).status_code, 401)
        self.assertEqual(anon.post("/medlife/addmember", {**PROFILE, "email": "test@example.com"}, format="json").status_code, 401)
        self.assertEqual(anon.get("/medlife/tokens/", {"email": "test@example.com", "member_name": "member1"}).status_code, 401)

    def test_cannot_act_on_another_accounts_email(self):
        other, _ = auth_client("other@example.com")
        other.post("/medlife/addmember", PROFILE, format="json")
        r = self.client.get("/medlife/getmember", {"email": "other@example.com"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.get("/medlife/getmember").json(), {})  # no email needed; token decides
        self.assertEqual(self.client.get("/medlife/getmember").status_code, 200)

    def test_edit_does_not_reset_token_count(self):
        self.add()
        FamilyMember.objects.filter(account=self.account).update(tokens_used=7)
        self.client.post("/medlife/editmember?member_name=member1", {**PROFILE, "firstName": "Mira"}, format="json")
        member = FamilyMember.objects.get(account=self.account, slot=1)
        self.assertEqual((member.first_name, member.tokens_used), ("Mira", 7))

    def test_add_list_edit_remove_and_email_normalization(self):
        r = self.add()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json(), {"key": "member1"})
        listed = self.client.get("/medlife/getmember", {"email": EMAIL})
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()["member1"]["firstName"], "Asha")
        self.assertEqual(listed.json()["member1"]["tokens"], 0)  # client token count ignored
        edit = self.client.post("/medlife/editmember?email=test%40example.com&member_name=member1",
                                {**PROFILE, "firstName": "Mira", "email": EMAIL}, format="json")
        self.assertEqual(edit.status_code, 200)
        self.assertEqual(self.client.get("/medlife/getmember", {"email": "test@example.com"}).json()["member1"]["firstName"], "Mira")
        self.assertEqual(self.client.post("/medlife/removemember?email=test%40example.com&member_name=member1", {}, format="json").status_code, 200)
        self.assertEqual(self.client.get("/medlife/getmember", {"email": "test@example.com"}).json(), {})

    def test_four_member_limit_and_lowest_free_slot(self):
        for _ in range(4):
            self.assertEqual(self.add().status_code, 201)
        response = self.add()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Maximum of 4 members allowed per email.", response.json()["detail"])
        self.client.post("/medlife/removemember?email=test%40example.com&member_name=member2", {}, format="json")
        response = self.add()
        self.assertEqual(response.json()["key"], "member2")

    def test_unknown_member_and_validation_errors_are_detail_objects(self):
        r = self.client.get("/medlife/tokens/", {"email": "test@example.com", "member_name": "member1"})
        self.assertEqual(r.status_code, 404)
        self.assertIn("detail", r.json())
        invalid = {**PROFILE, "a1c": "not-a-number", "email": "test@example.com"}
        r = self.client.post("/medlife/addmember", invalid, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("detail", r.json())
        r = self.client.get("/medlife/getmember", {"email": "not-an-email"})
        self.assertEqual(r.status_code, 403)
        self.assertIn("detail", r.json())

    def test_token_limit(self):
        response = self.add()
        member = FamilyMember.objects.get(account__email="test@example.com", slot=1)
        member.tokens_used = 99
        member.save()
        response = self.client.get("/medlife/tokens/", {"email": "test@example.com", "member_name": "member1"})
        self.assertEqual(response.json(), {"message": "100"})
        response = self.client.get("/medlife/tokens/", {"email": "test@example.com", "member_name": "member1"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Question limit exceeded.")

    def test_concurrent_token_requests_do_not_exceed_100(self):
        self.add()
        FamilyMember.objects.filter(account__email="test@example.com").update(tokens_used=95)
        def consume(_):
            close_old_connections()
            try:
                return auth_client("test@example.com")[0].get("/medlife/tokens/", {"email": "test@example.com", "member_name": "member1"}).status_code
            finally:
                connections.close_all()  # CONN_MAX_AGE=60 keeps thread connections open otherwise, blocking test-DB teardown
        with ThreadPoolExecutor(max_workers=8) as pool:
            statuses = list(pool.map(consume, range(10)))
        member = FamilyMember.objects.get(account__email="test@example.com", slot=1)
        self.assertEqual(member.tokens_used, 100)
        self.assertEqual(statuses.count(200), 5)
        self.assertEqual(statuses.count(400), 5)
