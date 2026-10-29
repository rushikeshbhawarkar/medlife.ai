"""Fast unit tests for local and API-based LLM provider adapters."""
from unittest.mock import Mock, patch
from django.test import SimpleTestCase, override_settings
from apps.ai.providers.factory import get_provider


class ProviderFactoryTests(SimpleTestCase):
    @override_settings(AI_PROVIDER="ollama")
    def test_factory_selects_ollama(self):
        self.assertEqual(get_provider().__class__.__name__, "OllamaProvider")

    @override_settings(AI_PROVIDER="openai", AI_API_KEY="test-key")
    def test_factory_keeps_openai_provider(self):
        self.assertEqual(get_provider().__class__.__name__, "OpenAIProvider")

    @override_settings(AI_PROVIDER="openai_compatible", AI_API_KEY="test-key")
    def test_factory_selects_openai_compatible_provider(self):
        self.assertEqual(get_provider().__class__.__name__, "OpenAIProvider")


class OllamaProviderTests(SimpleTestCase):
    @override_settings(AI_MODEL="llama3.1:8b", OLLAMA_BASE_URL="http://127.0.0.1:11434", AI_TIMEOUT_SECONDS=120)
    @patch("apps.ai.providers.ollama_provider.requests.post")
    def test_sends_member_context_to_local_ollama(self, post):
        response = Mock()
        response.json.return_value = {"message": {"content": "General information only."}}
        post.return_value = response
        from apps.ai.providers.ollama_provider import OllamaProvider
        answer = OllamaProvider().answer("What does this mean?", context="Medical description: asthma")
        self.assertEqual(answer, "General information only.")
        args, kwargs = post.call_args
        self.assertEqual(args[0], "http://127.0.0.1:11434/api/chat")
        self.assertEqual(kwargs["json"]["model"], "llama3.1:8b")
        self.assertFalse(kwargs["json"]["stream"])
        self.assertIn("Medical description: asthma", kwargs["json"]["messages"][1]["content"])
        self.assertEqual(kwargs["timeout"], 120)
        response.raise_for_status.assert_called_once_with()


class OpenAICompatibleProviderTests(SimpleTestCase):
    @override_settings(OPENAI_API_KEY="test-secret", OPENAI_MODEL="future-model", AI_BASE_URL="https://example.test/v1/chat/completions")
    @patch("apps.ai.providers.openai_provider.requests.post")
    def test_uses_configured_url_key_and_model(self, post):
        response = Mock()
        response.json.return_value = {"choices": [{"message": {"content": "Answer"}}]}
        post.return_value = response
        from apps.ai.providers.openai_provider import OpenAIProvider
        self.assertEqual(OpenAIProvider().answer("Question"), "Answer")
        args, kwargs = post.call_args
        self.assertEqual(args[0], "https://example.test/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-secret")
        self.assertEqual(kwargs["json"]["model"], "future-model")


class UserSelectedProviderTests(SimpleTestCase):
    @override_settings(GEMINI_API_KEY="gemini-test", GEMINI_MODEL="gemini-test-model", AI_TIMEOUT_SECONDS=12)
    @patch("apps.ai.providers.gemini_provider.requests.post")
    def test_gemini_provider_uses_server_key_and_timeout(self, post):
        response = Mock()
        response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "Gemini answer"}]}}]}
        post.return_value = response
        from apps.ai.providers.gemini_provider import GeminiProvider
        self.assertEqual(GeminiProvider().answer("Question", context="Height: 170 cm"), "Gemini answer")
        args, kwargs = post.call_args
        self.assertIn("gemini-test-model", args[0])
        self.assertEqual(kwargs["headers"]["x-goog-api-key"], "gemini-test")
        self.assertEqual(kwargs["timeout"], 12)
        self.assertIn("Height: 170 cm", kwargs["json"]["systemInstruction"]["parts"][0]["text"])

    @override_settings(ANTHROPIC_API_KEY="claude-test", CLAUDE_MODEL="claude-test-model", AI_TIMEOUT_SECONDS=13)
    @patch("apps.ai.providers.claude_provider.requests.post")
    def test_claude_provider_uses_messages_api(self, post):
        response = Mock()
        response.json.return_value = {"content": [{"type": "text", "text": "Claude answer"}]}
        post.return_value = response
        from apps.ai.providers.claude_provider import ClaudeProvider
        self.assertEqual(ClaudeProvider().answer("Question"), "Claude answer")
        args, kwargs = post.call_args
        self.assertEqual(args[0], "https://api.anthropic.com/v1/messages")
        self.assertEqual(kwargs["headers"]["x-api-key"], "claude-test")
        self.assertEqual(kwargs["json"]["model"], "claude-test-model")
        self.assertEqual(kwargs["timeout"], 13)

    @override_settings(OPENAI_API_KEY="openai-test", OPENAI_MODEL="gpt-test", AI_BASE_URL="https://api.openai.com/v1/chat/completions")
    def test_factory_selects_user_chosen_cloud_provider(self):
        self.assertEqual(get_provider("openai").__class__.__name__, "OpenAIProvider")
        self.assertEqual(get_provider("claude").__class__.__name__, "ClaudeProvider")
        self.assertEqual(get_provider("gemini").__class__.__name__, "GeminiProvider")

    @override_settings(AI_MODEL="legacy-model", OLLAMA_MODELS="small-model,large-model")
    def test_local_model_must_be_server_allowlisted(self):
        self.assertEqual(get_provider("local", "small-model").model, "small-model")
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            get_provider("local", "unlisted-model")


class ProviderDiscoveryAndModelSelectionTests(SimpleTestCase):
    @override_settings(
        AI_PROVIDER="ollama",
        AI_MODEL="llama3.1:8b",
        OLLAMA_MODELS="llama3.1:8b,llama3.2:3b",
        GEMINI_API_KEY="",
        ANTHROPIC_API_KEY="",
        OPENAI_API_KEY="",
        AI_API_KEY="",
        DEBUG=False,
    )
    def test_discovery_reports_local_models_and_default_without_secrets(self):
        from apps.ai.providers.factory import available_providers
        result = available_providers()
        self.assertEqual(result["default_provider"], "local")
        local = next(item for item in result["providers"] if item["id"] == "local")
        self.assertEqual(local["models"], ["llama3.1:8b", "llama3.2:3b"])
        self.assertNotIn("api_key", str(result).lower())

    @override_settings(
        GEMINI_API_KEY="test-key",
        GEMINI_MODEL="gemini-default",
        GEMINI_MODELS="gemini-default,gemini-fast",
    )
    def test_factory_accepts_only_allowlisted_gemini_models(self):
        from apps.ai.providers.factory import get_provider
        self.assertEqual(get_provider("gemini", model="gemini-fast").model, "gemini-fast")
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            get_provider("gemini", model="unapproved-model")

    @override_settings(GEMINI_API_KEY="")
    def test_missing_cloud_key_returns_configuration_error(self):
        from apps.ai.providers.factory import get_provider
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError) as error:
            get_provider("gemini")
        self.assertIn("not configured", str(error.exception.detail).lower())
