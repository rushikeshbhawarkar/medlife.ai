# Purpose: ASGI entry point for asynchronous-capable servers.
# Edit only if the deployment platform requires a custom ASGI setup.
# Defaults to PRODUCTION settings; local work goes through manage.py, which defaults to dev settings.
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
application = get_asgi_application()
