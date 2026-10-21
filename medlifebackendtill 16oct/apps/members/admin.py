# Purpose: Makes family profiles inspectable in Django admin without exposing health details in logs.
# Edit when changing the columns or filters staff need.
from django.contrib import admin
from .models import FamilyMember

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "slot", "first_name", "last_name", "tokens_used", "updated_at")
    list_filter = ("gender",)
    search_fields = ("account__email", "first_name", "last_name")
    readonly_fields = ("created_at", "updated_at")
