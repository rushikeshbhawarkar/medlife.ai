# Purpose: Django registration for the scanned-document (image-to-text) feature app.
# Edit this only if Django app initialization needs customization.
from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.documents"
