# Purpose: WSGI entry point used by traditional production servers.
# Edit only if the deployment platform requires a custom WSGI setup.
# Defaults to PRODUCTION settings; local work goes through manage.py, which defaults to dev settings.
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
application = get_wsgi_application()
