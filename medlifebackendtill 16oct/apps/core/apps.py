# Purpose: Django registration for the core feature app.
# Edit this only if Django app initialization needs customization.
from django.apps import AppConfig
class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
