# Purpose: Django registration for the chat feature app.
# Edit this only if Django app initialization needs customization.
from django.apps import AppConfig
class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat"
