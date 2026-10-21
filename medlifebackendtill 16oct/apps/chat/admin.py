# Purpose: Allows staff to inspect persisted chat rows in Django admin.
# Be careful with permissions because messages can contain sensitive health information.
from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "position", "role", "ts", "created_at")
    list_filter = ("role",)
    search_fields = ("member__account__email", "text")
    readonly_fields = ("created_at",)
