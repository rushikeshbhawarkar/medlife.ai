# Purpose: Django command-line entry point. Use it for migrations, tests, and the development server.
# Edit only if you need to customize how Django commands start.
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)













