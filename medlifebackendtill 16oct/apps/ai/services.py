# # # Purpose: Applies AI request limits and calls the selected provider.
# # # Edit this file when request-size, rate-limit, or provider orchestration rules change.
# # import logging
# # from django.conf import settings
# # from django.core.cache import cache
# # from rest_framework.exceptions import Throttled, ValidationError
# # from .providers.factory import get_provider

# # logger = logging.getLogger(__name__)

# # def answer_query(request, query):
# #     if not query or not query.strip():
# #         raise ValidationError({"detail": "The query parameter is required."})
# #     if len(query) > 4000:
# #         raise ValidationError({"detail": "The query must be 4,000 characters or fewer."})
# #     # One counter per signed-in account (not per IP: behind a proxy every user shares one IP).
# #     # cache.add + cache.incr is atomic, so parallel requests cannot slip past the limit.
# #     key = f"ai-rate:{request.user.pk}"
# #     cache.add(key, 0, timeout=60)
# #     try:
# #         count = cache.incr(key)
# #     except ValueError:  # the key expired between add() and incr()
# #         cache.set(key, 1, timeout=60)
# #         count = 1
# #     if count > settings.AI_RATE_LIMIT_PER_MINUTE:
# #         raise Throttled(detail="Too many questions. Please wait a minute and try again.")
# #     try:
# #         return get_provider().answer(query)
# #     except Exception as exc:
# #         # Log only the error TYPE (never the prompt, answer or API key) so operators can see failures.
# #         logger.warning("AI provider call failed: %s", type(exc).__name__)
# #         raise RuntimeError("The health assistant is temporarily unavailable. Please try again later.") from None






# # Purpose: Applies AI request limits, retrieves authorized member context, and calls the selected provider.
# import hashlib

# from django.conf import settings
# from django.core.cache import cache
# from rest_framework.exceptions import NotFound, Throttled, ValidationError

# from apps.members.models import FamilyMember
# from .providers.factory import get_provider


# def _profile_context(member):
#     """Return only existing, user-entered profile fields useful for health context."""
#     values = [
#         ("Name", " ".join(part for part in [member.first_name, member.last_name] if part).strip()),
#         ("Date of birth", member.dob),
#         ("Gender", member.gender),
#         ("Height", member.height),
#         ("Weight", member.weight),
#         ("A1C", "" if member.a1c is None else str(member.a1c).rstrip("0").rstrip(".")),
#         ("Blood pressure", member.blood_pressure),
#         ("Medicines reported in profile", member.medicine),
#         ("Medical description", member.medical_description),
#     ]
#     populated = [(label, value) for label, value in values if str(value).strip()]
#     if not populated:
#         return "No health profile values have been provided for this family member."
#     return "\n".join(f"{label}: {value}" for label, value in populated)


# def _check_query(query):
#     if not query or not query.strip():
#         raise ValidationError({"detail": "The query parameter is required."})
#     if len(query) > 4000:
#         raise ValidationError({"detail": "The query must be 4,000 characters or fewer."})


# def _check_rate_limit(request):
#     # Hash the IP before using it as a cache key; no prompt or health data is stored in cache.
#     # Per account when authenticated (behind a proxy every client shares one REMOTE_ADDR), else per IP.
#     user = getattr(request, "user", None)
#     ident = f"user:{user.pk}" if getattr(user, "pk", None) is not None else request.META.get("REMOTE_ADDR", "unknown")
#     key = "ai-rate:" + hashlib.sha256(ident.encode()).hexdigest()
#     count = cache.get(key, 0)
#     if count >= settings.AI_RATE_LIMIT_PER_MINUTE:
#         raise Throttled(detail="Too many questions. Please wait a minute and try again.")
#     cache.set(key, count + 1, timeout=60)


# def _call_provider(request, query, context=""):
#     _check_query(query)
#     _check_rate_limit(request)
#     try:
#         return get_provider().answer(query, context=context)
#     except Exception:
#         # Do not log provider payloads or prompts; return a friendly generic error.
#         raise RuntimeError("The health assistant is temporarily unavailable. Please try again later.") from None


# def answer_query(request, query):
#     """Legacy general-health endpoint; intentionally receives no member profile."""
#     return _call_provider(request, query)


# def answer_member_query(request, account, member_name, query):
#     """Answer using only the selected family member belonging to the authenticated account."""
#     _check_query(query)
#     slot = int(member_name[6:])
#     try:
#         member = FamilyMember.objects.get(account=account, slot=slot)
#     except FamilyMember.DoesNotExist:
#         raise NotFound("The selected family member was not found.")

#     context = _profile_context(member)
#     return _call_provider(request, query, context=context)










# # Purpose: Applies AI request limits, retrieves authorized member context, and calls the selected provider.
# import hashlib

# from django.conf import settings
# from django.core.cache import cache
# from rest_framework.exceptions import APIException, NotFound, Throttled, ValidationError

# from apps.members.models import FamilyMember
# from .providers.factory import get_provider


# def _profile_context(member):
#     """Return only existing, user-entered profile fields useful for health context."""
#     values = [
#         ("Name", " ".join(part for part in [member.first_name, member.last_name] if part).strip()),
#         ("Date of birth", member.dob),
#         ("Gender", member.gender),
#         ("Height", member.height),
#         ("Weight", member.weight),
#         ("A1C", "" if member.a1c is None else str(member.a1c).rstrip("0").rstrip(".")),
#         ("Blood pressure", member.blood_pressure),
#         ("Medicines reported in profile", member.medicine),
#         ("Medical description", member.medical_description),
#     ]
#     populated = [(label, value) for label, value in values if str(value).strip()]
#     if not populated:
#         return "No health profile values have been provided for this family member."
#     return "\n".join(f"{label}: {value}" for label, value in populated)


# def _check_query(query):
#     if not query or not query.strip():
#         raise ValidationError({"detail": "The query parameter is required."})
#     if len(query) > 4000:
#         raise ValidationError({"detail": "The query must be 4,000 characters or fewer."})


# def _check_rate_limit(request):
#     # Hash the IP before using it as a cache key; no prompt or health data is stored in cache.
#     # Per account when authenticated (behind a proxy every client shares one REMOTE_ADDR), else per IP.
#     user = getattr(request, "user", None)
#     ident = f"user:{user.pk}" if getattr(user, "pk", None) is not None else request.META.get("REMOTE_ADDR", "unknown")
#     key = "ai-rate:" + hashlib.sha256(ident.encode()).hexdigest()
#     # cache.add initializes once; cache.incr is atomic on supported shared caches.
#     cache.add(key, 0, timeout=60)
#     try:
#         count = cache.incr(key)
#     except ValueError:  # key expired between add and incr
#         cache.set(key, 1, timeout=60)
#         count = 1
#     if count > settings.AI_RATE_LIMIT_PER_MINUTE:
#         raise Throttled(detail="Too many questions. Please wait a minute and try again.")


# def _call_provider(request, query, context="", provider_name=None, local_model=None):
#     _check_query(query)
#     _check_rate_limit(request)
#     try:
#         return get_provider(provider_name=provider_name, local_model=local_model).answer(query, context=context)
#     except APIException:
#         raise
#     except Exception:
#         # Do not log provider payloads or prompts; return a friendly generic error.
#         raise RuntimeError("The health assistant is temporarily unavailable. Please try again later.") from None


# def answer_query(request, query, provider_name=None, local_model=None):
#     """General-health endpoint; intentionally receives no member profile."""
#     return _call_provider(request, query, provider_name=provider_name, local_model=local_model)


# def answer_member_query(request, account, member_name, query, provider_name=None, local_model=None):
#     """Answer using only the selected family member belonging to the authenticated account."""
#     _check_query(query)
#     slot = int(member_name[6:])
#     try:
#         member = FamilyMember.objects.get(account=account, slot=slot)
#     except FamilyMember.DoesNotExist:
#         raise NotFound("The selected family member was not found.")

#     context = _profile_context(member)
#     return _call_provider(request, query, context=context, provider_name=provider_name, local_model=local_model)








# Purpose: Applies AI request limits, retrieves authorized member context, and calls the selected provider.
import hashlib

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException, NotFound, Throttled, ValidationError

from apps.members.models import FamilyMember
from .providers.factory import get_provider


def _profile_context(member):
    """Return only existing, user-entered profile fields useful for health context."""
    values = [
        ("Name", " ".join(part for part in [member.first_name, member.last_name] if part).strip()),
        ("Date of birth", member.dob),
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


def _call_provider(request, query, context="", provider_name=None, local_model=None, model=None):
    _check_query(query)
    _check_rate_limit(request)
    try:
        return get_provider(provider_name=provider_name, local_model=local_model, model=model).answer(query, context=context)
    except APIException:
        raise
    except Exception:
        # Do not log provider payloads or prompts; return a friendly generic error.
        raise RuntimeError("The health assistant is temporarily unavailable. Please try again later.") from None


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
