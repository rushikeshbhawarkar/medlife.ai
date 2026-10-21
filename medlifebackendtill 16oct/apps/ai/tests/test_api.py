# # Purpose: Tests mock AI responses, auth, request validation, per-user rate limits, and graceful provider failures.
# # Add tests here when provider selection or AI endpoint behavior changes.
# from unittest.mock import patch
# from django.test import TestCase, override_settings
# from rest_framework.test import APIClient
# from apps.core.tests.helpers import auth_client

# class AIApiTests(TestCase):
#     def setUp(self):
#         self.client, _ = auth_client("ai@example.com")

#     def test_prompt_requires_login(self):
#         self.assertEqual(APIClient().get("/medlife/prompt/", {"query": "What is A1C?"}).status_code, 401)

#     @override_settings(AI_PROVIDER="mock", AI_RATE_LIMIT_PER_MINUTE=100)
#     def test_mock_provider_success(self):
#         response = self.client.get("/medlife/prompt/", {"query": "What is A1C?"})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("Sample", response.json())

#     def test_query_length_validation(self):
#         response = self.client.get("/medlife/prompt/", {"query": "x" * 4001})
#         self.assertEqual(response.status_code, 400)
#         self.assertIn("detail", response.json())

#     @override_settings(AI_PROVIDER="mock", AI_RATE_LIMIT_PER_MINUTE=2)
#     def test_rate_limit_is_per_user(self):
#         other, _ = auth_client("someone-else@example.com")  # create BOTH users first (helper clears the cache)
#         self.client, _ = auth_client("ai@example.com")
#         # NOTE: auth_client clears the cache, so build `other` before exhausting `self.client`'s allowance.
#         codes = [self.client.get("/medlife/prompt/", {"query": "hello"}).status_code for _ in range(3)]
#         self.assertEqual(codes, [200, 200, 429])
#         self.assertEqual(other.get("/medlife/prompt/", {"query": "hello"}).status_code, 200)  # unaffected

#     @override_settings(AI_PROVIDER="openai", AI_API_KEY="fake-key", AI_RATE_LIMIT_PER_MINUTE=100)
#     def test_provider_failure_is_friendly(self):
#         with patch("apps.ai.providers.openai_provider.requests.post", side_effect=TimeoutError()):
#             response = self.client.get("/medlife/prompt/", {"query": "general health question"})
#         self.assertEqual(response.status_code, 503)
#         self.assertEqual(response.json()["detail"], "The health assistant is temporarily unavailable. Please try again later.")







# Purpose: Tests mock AI responses, request validation, rate limits, and graceful provider failures.
# Add tests here when provider selection or AI endpoint behavior changes.
from unittest.mock import patch
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

class AIApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(AI_PROVIDER="mock", AI_RATE_LIMIT_PER_MINUTE=100)
    def test_mock_provider_success(self):
        response = self.client.get("/medlife/prompt/", {"query": "What is A1C?"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample", response.json())

    def test_query_length_validation(self):
        response = self.client.get("/medlife/prompt/", {"query": "x" * 4001})
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    @override_settings(AI_PROVIDER="openai", AI_API_KEY="fake-key", AI_RATE_LIMIT_PER_MINUTE=100)
    def test_provider_failure_is_friendly(self):
        with patch("apps.ai.providers.openai_provider.requests.post", side_effect=TimeoutError()):
            response = self.client.get("/medlife/prompt/", {"query": "general health question"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "The health assistant is temporarily unavailable. Please try again later.")


    @override_settings(AI_PROVIDER="mock", AI_RATE_LIMIT_PER_MINUTE=100)
    def test_member_chat_requires_bearer_token(self):
        response = self.client.post(
            "/medlife/chat/ask/",
            {"member_name": "member1", "query": "What should I know about my blood pressure?"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    @override_settings(AI_PROVIDER="mock", AI_RATE_LIMIT_PER_MINUTE=100)
    def test_member_chat_passes_only_selected_members_profile_to_provider(self):
        from apps.accounts.models import Account
        from apps.core.authentication import issue_account_token
        from apps.members.models import FamilyMember

        account = Account.objects.create(email="personalized@example.com")
        FamilyMember.objects.create(
            account=account,
            slot=1,
            first_name="Asha",
            height="165 cm",
            weight="62 kg",
            a1c="5.60",
            blood_pressure="120/80",
            medicine="Vitamin D",
            medical_description="Occasional headaches reported by member.",
        )
        # Another account's profile must not be visible through this token.
        other = Account.objects.create(email="other@example.com")
        FamilyMember.objects.create(
            account=other,
            slot=1,
            first_name="Private",
            blood_pressure="190/120",
        )
        token = issue_account_token(account)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        with patch("apps.ai.services.get_provider") as get_provider:
            get_provider.return_value.answer.return_value = "Personalized test answer"
            response = self.client.post(
                "/medlife/chat/ask/",
                {"member_name": "member1", "query": "Can you explain my health readings?"},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"answer": "Personalized test answer"})
        args, kwargs = get_provider.return_value.answer.call_args
        self.assertEqual(args[0], "Can you explain my health readings?")
        self.assertIn("Height: 165 cm", kwargs["context"])
        self.assertIn("Blood pressure: 120/80", kwargs["context"])
        self.assertIn("A1C: 5.6", kwargs["context"])
        self.assertIn("Medical description: Occasional headaches reported by member.", kwargs["context"])
        self.assertNotIn("190/120", kwargs["context"])
        self.assertNotIn("Private", kwargs["context"])

    @override_settings(AI_PROVIDER="mock", AI_RATE_LIMIT_PER_MINUTE=100)
    def test_member_chat_rejects_missing_member(self):
        from apps.accounts.models import Account
        from apps.core.authentication import issue_account_token

        account = Account.objects.create(email="missing-member@example.com")
        token = issue_account_token(account)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post(
            "/medlife/chat/ask/",
            {"member_name": "member1", "query": "What does my A1C mean?"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
