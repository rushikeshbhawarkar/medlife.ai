# # Purpose: Makes accounts inspectable in Django admin.
# # Edit when changing the fields shown to staff.
# from django.contrib import admin
# from .models import Account

# @admin.register(Account)
# class AccountAdmin(admin.ModelAdmin):
#     list_display = ("id", "email", "created_at")
#     search_fields = ("email",)
#     readonly_fields = ("created_at",)
#     exclude = ("password",)  # the hash must never be shown or hand-edited in admin






# Purpose: Makes accounts inspectable in Django admin.
# Edit when changing the fields shown to staff.
from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "role", "created_at")
    search_fields = ("email",)
    readonly_fields = ("created_at", "role")
    exclude = ("password",)  # the hash must never be shown or hand-edited in admin
