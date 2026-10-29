# # # Purpose: Selects the configured AI provider without coupling views to a vendor.
# # # Edit this factory when adding a provider, and choose it through AI_PROVIDER.
# # from django.conf import settings
# # from .mock import MockProvider

# # def get_provider():
# #     if settings.AI_PROVIDER in ("", "mock"):
# #         return MockProvider()
# #     if settings.AI_PROVIDER == "openai":
# #         from .openai_provider import OpenAIProvider
# #         return OpenAIProvider()
# #     raise RuntimeError("Unsupported AI_PROVIDER. Choose 'mock' or 'openai'.")




# # """Selects an AI provider from configuration; API views do not depend on a vendor."""
# # from django.conf import settings
# # from .mock import MockProvider


# # def get_provider():
# #     provider = settings.AI_PROVIDER
# #     if provider in ("", "mock"):
# #         return MockProvider()
# #     if provider == "ollama":
# #         from .ollama_provider import OllamaProvider
# #         return OllamaProvider()
# #     if provider in ("openai", "openai_compatible"):
# #         from .openai_provider import OpenAIProvider
# #         return OpenAIProvider()
# #     raise RuntimeError(
# #         "Unsupported AI_PROVIDER. Choose 'mock', 'ollama', 'openai', or 'openai_compatible'."
# #     )







# """Select an explicitly requested AI provider using server-side credentials."""
# from django.conf import settings
# from rest_framework.exceptions import ValidationError
# from .mock import MockProvider

# PROVIDER_LABELS = {
#     "gemini": "Google Gemini",
#     "claude": "Anthropic Claude",
#     "openai": "ChatGPT (OpenAI)",
#     "local": "Local model (Ollama)",
#     "ollama": "Local model (Ollama)",
#     "mock": "Offline demo model",
# }


# def configured_local_models():
#     configured = getattr(settings, "OLLAMA_MODELS", "")
#     models = [item.strip() for item in configured.split(",") if item.strip()]
#     return models


# def available_providers():
#     """Safe provider metadata for the frontend; never return credentials."""
#     items = []
#     if settings.GEMINI_API_KEY:
#         items.append({"id": "gemini", "label": PROVIDER_LABELS["gemini"]})
#     if settings.ANTHROPIC_API_KEY:
#         items.append({"id": "claude", "label": PROVIDER_LABELS["claude"]})
#     if (getattr(settings, "OPENAI_API_KEY", "") or settings.AI_API_KEY):
#         items.append({"id": "openai", "label": PROVIDER_LABELS["openai"]})
#     if configured_local_models():
#         items.append({
#             "id": "local",
#             "label": PROVIDER_LABELS["local"],
#             "models": configured_local_models(),
#         })
#     # Mock is intentionally available for development/test only.
#     if settings.DEBUG or settings.AI_PROVIDER == "mock":
#         items.append({"id": "mock", "label": PROVIDER_LABELS["mock"]})
#     return {"providers": items}


# def get_provider(provider_name=None, local_model=None):
#     """Build the requested provider; browser input never controls URL or API keys."""
#     provider = (provider_name or settings.AI_PROVIDER or "mock").strip().lower()
#     if provider == "mock":
#         if not (settings.DEBUG or settings.AI_PROVIDER == "mock"):
#             raise ValidationError({"provider": "The offline demo provider is disabled in production."})
#         return MockProvider()
#     if provider == "gemini":
#         if not settings.GEMINI_API_KEY:
#             raise ValidationError({"provider": "Gemini is not configured on the server."})
#         from .gemini_provider import GeminiProvider
#         return GeminiProvider()
#     if provider == "claude":
#         if not settings.ANTHROPIC_API_KEY:
#             raise ValidationError({"provider": "Claude is not configured on the server."})
#         from .claude_provider import ClaudeProvider
#         return ClaudeProvider()
#     if provider in ("openai", "chatgpt", "openai_compatible"):
#         if not (getattr(settings, "OPENAI_API_KEY", "") or settings.AI_API_KEY):
#             raise ValidationError({"provider": "ChatGPT (OpenAI) is not configured on the server."})
#         from .openai_provider import OpenAIProvider
#         return OpenAIProvider()
#     if provider in ("local", "ollama"):
#         models = configured_local_models()
#         selected = (local_model or (models[0] if models else settings.AI_MODEL)).strip()
#         if not models or selected not in models:
#             raise ValidationError({"local_model": "Select a local model configured by the MedLife server."})
#         from .ollama_provider import OllamaProvider
#         return OllamaProvider(model=selected)
#     raise ValidationError({"provider": "Choose gemini, claude, openai, or local."})





"""Select an AI provider using server-side credentials and server-controlled model allowlists."""
from django.conf import settings
from rest_framework.exceptions import ValidationError
from .mock import MockProvider

PROVIDER_LABELS = {
    "gemini": "Google Gemini",
    "claude": "Anthropic Claude",
    "openai": "OpenAI",
    "local": "Local model (Ollama)",
    "ollama": "Local model (Ollama)",
    "mock": "Offline demo model",
}


def _models(setting_name, default):
    """Return a de-duplicated list of models configured by the server."""
    raw = getattr(settings, setting_name, "") or default
    return list(dict.fromkeys(item.strip() for item in raw.split(",") if item.strip()))


def configured_local_models():
    return _models("OLLAMA_MODELS", getattr(settings, "AI_MODEL", "llama3.1:8b"))


def _configured_model(setting_name, default_setting, requested, provider_label):
    default = getattr(settings, default_setting)
    choices = _models(setting_name, default)
    selected = (requested or default).strip()
    if selected not in choices:
        raise ValidationError({
            "model": f"Choose a {provider_label} model configured by the MedLife server."
        })
    return selected


def available_providers():
    """Return safe configuration metadata; never expose credentials or claim live connectivity."""
    items = []
    if settings.GEMINI_API_KEY:
        items.append({
            "id": "gemini", "label": PROVIDER_LABELS["gemini"],
            "configured": True, "models": _models("GEMINI_MODELS", settings.GEMINI_MODEL),
        })
    if settings.ANTHROPIC_API_KEY:
        items.append({
            "id": "claude", "label": PROVIDER_LABELS["claude"],
            "configured": True, "models": _models("CLAUDE_MODELS", settings.CLAUDE_MODEL),
        })
    if getattr(settings, "OPENAI_API_KEY", "") or settings.AI_API_KEY:
        items.append({
            "id": "openai", "label": PROVIDER_LABELS["openai"],
            "configured": True, "models": _models("OPENAI_MODELS", settings.OPENAI_MODEL),
        })
    local_models = configured_local_models()
    if local_models:
        items.append({
            "id": "local", "label": PROVIDER_LABELS["local"],
            "configured": True, "models": local_models,
        })
    if settings.DEBUG or settings.AI_PROVIDER == "mock":
        items.append({
            "id": "mock", "label": PROVIDER_LABELS["mock"],
            "configured": True, "models": ["mock"],
        })
    return {
        "default_provider": "local" if settings.AI_PROVIDER == "ollama" else settings.AI_PROVIDER,
        "providers": items,
    }


def get_provider(provider_name=None, local_model=None, model=None):
    """Build the requested provider; browser input never controls URLs or API keys."""
    provider = (provider_name or settings.AI_PROVIDER or "ollama").strip().lower()
    if provider == "mock":
        if not (settings.DEBUG or settings.AI_PROVIDER == "mock"):
            raise ValidationError({"provider": "The offline demo provider is disabled in production."})
        if model not in (None, "", "mock"):
            raise ValidationError({"model": "The offline demo provider only supports the mock model."})
        return MockProvider()
    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValidationError({"provider": "Gemini is not configured on the server. Ask an administrator to configure GEMINI_API_KEY."})
        selected = _configured_model("GEMINI_MODELS", "GEMINI_MODEL", model, "Gemini")
        from .gemini_provider import GeminiProvider
        return GeminiProvider(model=selected)
    if provider == "claude":
        if not settings.ANTHROPIC_API_KEY:
            raise ValidationError({"provider": "Claude is not configured on the server. Ask an administrator to configure ANTHROPIC_API_KEY."})
        selected = _configured_model("CLAUDE_MODELS", "CLAUDE_MODEL", model, "Claude")
        from .claude_provider import ClaudeProvider
        return ClaudeProvider(model=selected)
    if provider in ("openai", "chatgpt", "openai_compatible"):
        if not (getattr(settings, "OPENAI_API_KEY", "") or settings.AI_API_KEY):
            raise ValidationError({"provider": "OpenAI is not configured on the server. Ask an administrator to configure OPENAI_API_KEY."})
        selected = _configured_model("OPENAI_MODELS", "OPENAI_MODEL", model, "OpenAI")
        from .openai_provider import OpenAIProvider
        return OpenAIProvider(model=selected)
    if provider in ("local", "ollama"):
        models = configured_local_models()
        selected = (model or local_model or (models[0] if models else "")).strip()
        if not models or selected not in models:
            raise ValidationError({"model": "Select a local model configured by the MedLife server."})
        from .ollama_provider import OllamaProvider
        return OllamaProvider(model=selected)
    raise ValidationError({"provider": "Choose gemini, claude, openai, or local."})
