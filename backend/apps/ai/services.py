# Purpose: Applies AI request limits, retrieves authorized member context, and calls the selected provider.
import hashlib

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException, NotFound, Throttled, ValidationError

from apps.members.models import FamilyMember
from .providers.factory import get_provider


def _profile_context(member):
    """Return only existing, user-entered profile fields useful for health context."""
    # Do not send direct identifiers (name or date of birth) to AI providers.
    values = [
        ("Gender", member.gender),
        ("Height", member.height),
        ("Weight", member.weight),
        ("A1C", "" if member.a1c is None else str(member.a1c).rstrip("0").rstrip(".")),
        ("Blood pressure", member.blood_pressure),
        ("Medicines reported in profile", member.medicine),
        ("Medical description", member.medical_description),
    ]
    populated = [(label, value) for label, value in values if str(value).strip()]
    if not populated:
        return "No health profile values have been provided for this family member."
    return "\n".join(f"{label}: {value}" for label, value in populated)


def _check_query(query):
    if not query or not query.strip():
        raise ValidationError({"detail": "The query parameter is required."})
    if len(query) > 4000:
        raise ValidationError({"detail": "The query must be 4,000 characters or fewer."})


def _check_rate_limit(request):
    # Hash the IP before using it as a cache key; no prompt or health data is stored in cache.
    # Per account when authenticated (behind a proxy every client shares one REMOTE_ADDR), else per IP.
    user = getattr(request, "user", None)
    ident = f"user:{user.pk}" if getattr(user, "pk", None) is not None else request.META.get("REMOTE_ADDR", "unknown")
    key = "ai-rate:" + hashlib.sha256(ident.encode()).hexdigest()
    # cache.add initializes once; cache.incr is atomic on supported shared caches.
    cache.add(key, 0, timeout=60)
    try:
        count = cache.incr(key)
    except ValueError:  # key expired between add and incr
        cache.set(key, 1, timeout=60)
        count = 1
    if count > settings.AI_RATE_LIMIT_PER_MINUTE:
        raise Throttled(detail="Too many questions. Please wait a minute and try again.")


def _provider_key(provider_name=None):
    """Normalize provider aliases to decide whether data leaves the MedLife server."""
    provider = (provider_name or settings.AI_PROVIDER or "ollama").strip().lower()
    if provider in ("local", "ollama"):
        return "local"
    if provider in ("openai", "chatgpt", "openai_compatible"):
        return "openai"
    return provider


def _provider_model(provider_key, model=None, local_model=None):
    """Return a model label for audit metadata; never record prompts or profile values."""
    requested = model or local_model
    if requested:
        return requested[:120]
    setting_name = {
        "gemini": "GEMINI_MODEL",
        "claude": "CLAUDE_MODEL",
        "openai": "OPENAI_MODEL",
        "local": "AI_MODEL",
        "mock": "AI_MODEL",
    }.get(provider_key)
    return str(getattr(settings, setting_name, "") or "")[:120]


def _write_provider_audit(account, provider_key, model_name, outcome):
    """Record provider metadata only; never store prompts, answers, or clinical details."""
    from .models import AIProviderAudit
    AIProviderAudit.objects.create(
        account=account if getattr(account, "pk", None) is not None else None,
        provider=provider_key[:24],
        model=model_name[:120],
        outcome=outcome,
    )


def _call_provider(request, query, context="", provider_name=None, local_model=None, model=None):
    _check_query(query)
    _check_rate_limit(request)
    provider_key = _provider_key(provider_name)
    account = getattr(request, "user", None)
    cloud_provider = provider_key in {"gemini", "claude", "openai"}
    model_name = _provider_model(provider_key, model=model, local_model=local_model)

    # Consent is checked on the server for every cloud AI call, including general questions.
    if cloud_provider:
        if not getattr(account, "pk", None):
            raise APIException("Sign in is required before using a cloud AI provider.")
        if not account.cloud_ai_consent:
            _write_provider_audit(account, provider_key, model_name, "blocked_no_consent")
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied({
                "code": "cloud_ai_consent_required",
                "detail": "Please provide consent to send your question to a cloud AI provider before continuing.",
            })

    try:
        answer = get_provider(
            provider_name=provider_name, local_model=local_model, model=model
        ).answer(query, context=context)
    except APIException:
        if cloud_provider:
            _write_provider_audit(account, provider_key, model_name, "failed")
        raise
    except Exception:
        if cloud_provider:
            _write_provider_audit(account, provider_key, model_name, "failed")
        # Do not log provider payloads or prompts; return a friendly generic error.
        raise RuntimeError("The health assistant is temporarily unavailable. Please try again later.") from None
    if cloud_provider:
        _write_provider_audit(account, provider_key, model_name, "succeeded")
    return answer


def answer_query(request, query, provider_name=None, local_model=None, model=None):
    """General-health endpoint; intentionally receives no member profile."""
    return _call_provider(request, query, provider_name=provider_name, local_model=local_model, model=model)


def answer_member_query(request, account, member_name, query, provider_name=None, local_model=None, model=None):
    """Answer using only the selected family member belonging to the authenticated account."""
    _check_query(query)
    slot = int(member_name[6:])
    try:
        member = FamilyMember.objects.get(account=account, slot=slot)
    except FamilyMember.DoesNotExist:
        raise NotFound("The selected family member was not found.")

    context = _profile_context(member)
    return _call_provider(request, query, context=context, provider_name=provider_name, local_model=local_model, model=model)
