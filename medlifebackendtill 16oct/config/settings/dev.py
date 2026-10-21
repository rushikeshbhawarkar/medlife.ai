# Purpose: Local development settings. Defaults to DEBUG while keeping database configuration in base.py.
# Edit this file only for development-specific conveniences.
from .base import *
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
