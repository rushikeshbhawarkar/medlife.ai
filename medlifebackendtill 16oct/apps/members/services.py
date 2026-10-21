# Purpose: Owns member limits, lowest-free slot allocation, profile CRUD, and atomic token use.
# Edit this file when changing the rules for member profiles or question counts.
from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError
from apps.accounts.services import get_or_create_account
from .models import FamilyMember
from .serializers import member_to_frontend

def get_members(email):
    account = get_or_create_account(email)
    return {m.key: member_to_frontend(m) for m in account.members.order_by("slot")}

def _member(account, name, lock=False):
    import re
    if not re.fullmatch(r"member[1-4]", str(name or "")):
        raise ValidationError({"detail": "Invalid member_name."})
    try:
        qs = FamilyMember.objects.select_for_update() if lock else FamilyMember.objects
        return qs.get(account=account, slot=int(name[6:]))
    except FamilyMember.DoesNotExist:
        raise NotFound("Member not found")

@transaction.atomic
def add_member(email, values):
    account = get_or_create_account(email)
    # Lock the parent account so simultaneous adds serialize even when no member row exists yet.
    from apps.accounts.models import Account
    account = Account.objects.select_for_update().get(pk=account.pk)
    members = FamilyMember.objects.filter(account=account)
    if members.count() >= settings.MAX_MEMBERS:
        raise ValidationError({"detail": "Maximum of 4 members allowed per email."})
    used = set(members.values_list("slot", flat=True))
    slot = next(n for n in range(1, settings.MAX_MEMBERS + 1) if n not in used)
    member = FamilyMember.objects.create(account=account, slot=slot, **values)
    return {"key": member.key}

@transaction.atomic
def edit_member(email, name, values):
    account = get_or_create_account(email)
    member = _member(account, name, lock=True)
    for key, value in values.items():
        setattr(member, key, value)
    # update_fields: only write the profile columns, so a token use that happened meanwhile is not overwritten.
    member.save(update_fields=[*values.keys(), "updated_at"])
    return {"ok": True}

@transaction.atomic
def remove_member(email, name):
    account = get_or_create_account(email)
    member = _member(account, name)
    member.delete()  # ChatMessage rows cascade through their foreign key.
    return {"ok": True}

@transaction.atomic
def consume_token(email, name):
    account = get_or_create_account(email)
    from apps.accounts.models import Account
    # Serializing token updates per account/member makes the 100-question cap safe under concurrency.
    Account.objects.select_for_update().get(pk=account.pk)
    member = _member(account, name)
    if member.tokens_used >= settings.TOKEN_LIMIT:
        raise ValidationError({"detail": "Question limit exceeded."})
    member.tokens_used += 1
    member.save(update_fields=["tokens_used", "updated_at"])
    return member.tokens_used
