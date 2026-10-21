# Purpose: Lets staff inspect scanned-document metadata in Django admin.
# The extracted text is sensitive medical data, so it is not shown in the list view or searchable.
from django.contrib import admin
from .models import ScannedDocument


@admin.register(ScannedDocument)
class ScannedDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "member", "document_type", "is_confirmed", "created_at")
    list_filter = ("document_type", "is_confirmed")
    search_fields = ("account__email",)
    readonly_fields = ("created_at", "updated_at", "ocr_text", "ocr_confidence", "warnings")
