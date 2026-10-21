# Purpose: Reads and atomically replaces a member's complete ordered chat history.
# Edit this file when chat persistence or ordering rules change.
from django.db import transaction
from rest_framework.exceptions import NotFound
from apps.accounts.services import get_or_create_account
from apps.members.services import _member
from .models import ChatMessage

def fetch_chat(email, name):
    account = get_or_create_account(email)
    member = _member(account, name)
    return {"chat": [{"role": m.role, "text": m.text, "ts": m.ts}
                     for m in member.chat_messages.order_by("position")]}

@transaction.atomic
def save_chat(email, name, messages):
    account = get_or_create_account(email)
    member = _member(account, name, lock=True)  # serializes concurrent saves for the same member
    ChatMessage.objects.filter(member=member).delete()
    ChatMessage.objects.bulk_create([
        ChatMessage(member=member, position=i, role=item["role"], text=item["text"], ts=item["ts"])
        for i, item in enumerate(messages)
    ])
    return {"ok": True}
