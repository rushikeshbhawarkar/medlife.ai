# # # # Purpose: Production-safe overrides. Configure HTTPS and secrets in the deployment environment.
# # # # Edit this file when preparing a real deployment.
# # # from django.core.exceptions import ImproperlyConfigured
# # # from .base import *

# # # DEBUG = False

# # # # --- Refuse to start with a missing/placeholder secret -------------------------------------
# # # # SECRET_KEY also signs the login tokens, so a guessable key lets anyone forge a login.
# # # _BAD_KEY_PREFIXES = ("unsafe-", "replace-this", "change-me")
# # # if len(SECRET_KEY) < 50 or SECRET_KEY.lower().startswith(_BAD_KEY_PREFIXES):
# # #     raise ImproperlyConfigured(
# # #         "DJANGO_SECRET_KEY is missing, too short (<50 chars) or still a placeholder. Generate one with: "
# # #         'python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"'
# # #     )

# # # # --- HTTPS ---------------------------------------------------------------------------------
# # # SECURE_CONTENT_TYPE_NOSNIFF = True
# # # SESSION_COOKIE_SECURE = True
# # # CSRF_COOKIE_SECURE = True
# # # SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
# # # SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
# # # SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
# # # SECURE_HSTS_PRELOAD = False
# # # SECURE_REFERRER_POLICY = "same-origin"
# # # X_FRAME_OPTIONS = "DENY"

# # # # Behind nginx / a cloud load balancer that terminates HTTPS, Django only sees plain HTTP and
# # # # SECURE_SSL_REDIRECT would loop forever. Set BEHIND_PROXY=true ONLY if a proxy you control sets
# # # # X-Forwarded-Proto (never when Django is exposed directly: clients could fake the header).
# # # if os.getenv("BEHIND_PROXY", "false").lower() == "true":
# # #     SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # # # --- Static files for /admin/ (served by WhiteNoise after `python manage.py collectstatic`) --
# # # MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
# # # STORAGES = {
# # #     "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
# # #     "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
# # # }





















# # # Purpose: Production-safe overrides. Configure HTTPS and secrets in the deployment environment.
# # # Edit this file when preparing a real deployment.
# # from django.core.exceptions import ImproperlyConfigured
# # from .base import *

# # DEBUG = False

# # # --- Refuse to start with a missing/placeholder secret -------------------------------------
# # # SECRET_KEY also signs the login tokens, so a guessable key lets anyone forge a login.
# # _BAD_KEY_PREFIXES = ("unsafe-", "replace-this", "change-me")
# # if len(SECRET_KEY) < 50 or SECRET_KEY.lower().startswith(_BAD_KEY_PREFIXES):
# #     raise ImproperlyConfigured(
# #         "DJANGO_SECRET_KEY is missing, too short (<50 chars) or still a placeholder. Generate one with: "
# #         'python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"'
# #     )

# # if not TOTP_ENCRYPTION_KEY:
# #     raise ImproperlyConfigured(
# #         "TOTP_ENCRYPTION_KEY is required in production. Generate one with: "
# #         'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
# #     )
# # try:
# #     from cryptography.fernet import Fernet
# #     Fernet(TOTP_ENCRYPTION_KEY.encode("ascii"))
# # except (ValueError, UnicodeEncodeError):
# #     raise ImproperlyConfigured("TOTP_ENCRYPTION_KEY must be a valid Fernet key.")

# # # --- HTTPS ---------------------------------------------------------------------------------
# # SECURE_CONTENT_TYPE_NOSNIFF = True
# # SESSION_COOKIE_SECURE = True
# # CSRF_COOKIE_SECURE = True
# # SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
# # SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
# # SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
# # SECURE_HSTS_PRELOAD = False
# # SECURE_REFERRER_POLICY = "same-origin"
# # X_FRAME_OPTIONS = "DENY"

# # # Behind nginx / a cloud load balancer that terminates HTTPS, Django only sees plain HTTP and
# # # SECURE_SSL_REDIRECT would loop forever. Set BEHIND_PROXY=true ONLY if a proxy you control sets
# # # X-Forwarded-Proto (never when Django is exposed directly: clients could fake the header).
# # if os.getenv("BEHIND_PROXY", "false").lower() == "true":
# #     SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # # --- Static files for /admin/ (served by WhiteNoise after `python manage.py collectstatic`) --
# # MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
# # STORAGES = {
# #     "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
# #     "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
# # }



















# # Purpose: Production-safe overrides. Configure HTTPS and secrets in the deployment environment.
# # Edit this file when preparing a real deployment.
# from django.core.exceptions import ImproperlyConfigured
# from .base import *

# DEBUG = False

# # --- Refuse to start with a missing/placeholder secret -------------------------------------
# # SECRET_KEY also signs the login tokens, so a guessable key lets anyone forge a login.
# _BAD_KEY_PREFIXES = ("unsafe-", "replace-this", "change-me")
# if len(SECRET_KEY) < 50 or SECRET_KEY.lower().startswith(_BAD_KEY_PREFIXES):
#     raise ImproperlyConfigured(
#         "DJANGO_SECRET_KEY is missing, too short (<50 chars) or still a placeholder. Generate one with: "
#         'python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"'
#     )

# if not TOTP_ENCRYPTION_KEY:
#     raise ImproperlyConfigured(
#         "TOTP_ENCRYPTION_KEY is required in production. Generate one with: "
#         'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
#     )
# try:
#     from cryptography.fernet import Fernet
#     Fernet(TOTP_ENCRYPTION_KEY.encode("ascii"))
# except (ValueError, UnicodeEncodeError):
#     raise ImproperlyConfigured("TOTP_ENCRYPTION_KEY must be a valid Fernet key.")

# # --- HTTPS ---------------------------------------------------------------------------------
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
# SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
# SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
# SECURE_HSTS_PRELOAD = False
# SECURE_REFERRER_POLICY = "same-origin"
# X_FRAME_OPTIONS = "DENY"

# # Behind nginx / a cloud load balancer that terminates HTTPS, Django only sees plain HTTP and
# # SECURE_SSL_REDIRECT would loop forever. Set BEHIND_PROXY=true ONLY if a proxy you control sets
# # X-Forwarded-Proto (never when Django is exposed directly: clients could fake the header).
# if os.getenv("BEHIND_PROXY", "false").lower() == "true":
#     SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # --- Static files for /admin/ (served by WhiteNoise after `python manage.py collectstatic`) --
# MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
# STORAGES = {
#     "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
#     "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
# }


# # Forgot-password links must be https in production (the reset token travels in the link).
# if not FRONTEND_PASSWORD_RESET_URL.lower().startswith("https://"):
#     raise ImproperlyConfigured(
#         "FRONTEND_PASSWORD_RESET_URL must start with https:// in production "
#         "(the public address of your frontend's reset-password page)."
#     )


# # --- Email: password-reset / password-change emails must be able to leave the server ---------
# # Without this check a wrong SMTP setup only shows up as silent "link sent" messages with no email.
# if EMAIL_BACKEND.endswith("smtp.EmailBackend"):
#     if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
#         raise ImproperlyConfigured(
#             "EMAIL_HOST, EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are required in production "
#             "(password reset and password change emails). Test with: python manage.py sendtestemail you@example.com"
#         )
#     if EMAIL_USE_SSL and EMAIL_USE_TLS:
#         raise ImproperlyConfigured("Set only one of EMAIL_USE_SSL / EMAIL_USE_TLS to true.")
#     if DEFAULT_FROM_EMAIL.lower().endswith("@localhost"):
#         raise ImproperlyConfigured("Set DEFAULT_FROM_EMAIL to a real sender address your SMTP provider allows.")

# # --- Rate limits behind a proxy ---------------------------------------------------------------
# # With a proxy in front and NUM_PROXIES=0 every visitor shares the proxy's IP, so the per-IP limits
# # (sign-in, forgot-password) would apply to all users together.
# if os.getenv("BEHIND_PROXY", "false").lower() == "true" and REST_FRAMEWORK["NUM_PROXIES"] < 1:
#     raise ImproperlyConfigured("BEHIND_PROXY=true requires NUM_PROXIES to be at least 1 (number of proxies in front of Django).")

# if not REDIS_URL:
#     import logging
#     logging.getLogger(__name__).warning(
#         "REDIS_URL is not set: rate limits, TOTP lockout and the reset-email cooldown are per worker process. "
#         "Set REDIS_URL when running more than one worker."
#     )













# Purpose: Production-safe overrides. Configure HTTPS and secrets in the deployment environment.
# Edit this file when preparing a real deployment.
from django.core.exceptions import ImproperlyConfigured
from .base import *

DEBUG = False

# --- Refuse to start with a missing/placeholder secret -------------------------------------
# SECRET_KEY also signs the login tokens, so a guessable key lets anyone forge a login.
_BAD_KEY_PREFIXES = ("unsafe-", "replace-this", "change-me")
if len(SECRET_KEY) < 50 or SECRET_KEY.lower().startswith(_BAD_KEY_PREFIXES):
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY is missing, too short (<50 chars) or still a placeholder. Generate one with: "
        'python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"'
    )

if not TOTP_ENCRYPTION_KEY:
    raise ImproperlyConfigured(
        "TOTP_ENCRYPTION_KEY is required in production. Generate one with: "
        'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
    )
try:
    from cryptography.fernet import Fernet
    Fernet(TOTP_ENCRYPTION_KEY.encode("ascii"))
except (ValueError, UnicodeEncodeError):
    raise ImproperlyConfigured("TOTP_ENCRYPTION_KEY must be a valid Fernet key.")

# --- HTTPS ---------------------------------------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = False
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# Behind nginx / a cloud load balancer that terminates HTTPS, Django only sees plain HTTP and
# SECURE_SSL_REDIRECT would loop forever. Set BEHIND_PROXY=true ONLY if a proxy you control sets
# X-Forwarded-Proto (never when Django is exposed directly: clients could fake the header).
if os.getenv("BEHIND_PROXY", "false").lower() == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Static files for /admin/ (served by WhiteNoise after `python manage.py collectstatic`) --
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}


# Forgot-password links must be https in production (the reset token travels in the link).
if not FRONTEND_PASSWORD_RESET_URL.lower().startswith("https://"):
    raise ImproperlyConfigured(
        "FRONTEND_PASSWORD_RESET_URL must start with https:// in production "
        "(the public address of your frontend's reset-password page)."
    )


# --- Email: password-reset / password-change emails must be able to leave the server ---------
# Without this check a wrong SMTP setup only shows up as silent "link sent" messages with no email.
if EMAIL_BACKEND.endswith("smtp.EmailBackend"):
    if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
        raise ImproperlyConfigured(
            "EMAIL_HOST, EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are required in production "
            "(password reset and password change emails). Test with: python manage.py sendtestemail you@example.com"
        )
    if EMAIL_USE_SSL and EMAIL_USE_TLS:
        raise ImproperlyConfigured("Set only one of EMAIL_USE_SSL / EMAIL_USE_TLS to true.")
    if DEFAULT_FROM_EMAIL.lower().endswith("@localhost"):
        raise ImproperlyConfigured("Set DEFAULT_FROM_EMAIL to a real sender address your SMTP provider allows.")

# --- Rate limits behind a proxy ---------------------------------------------------------------
# With a proxy in front and NUM_PROXIES=0 every visitor shares the proxy's IP, so the per-IP limits
# (sign-in, forgot-password) would apply to all users together.
if os.getenv("BEHIND_PROXY", "false").lower() == "true" and REST_FRAMEWORK["NUM_PROXIES"] < 1:
    raise ImproperlyConfigured("BEHIND_PROXY=true requires NUM_PROXIES to be at least 1 (number of proxies in front of Django).")

if not REDIS_URL:
    # Rate limits, the TOTP lockout and the reset-email cooldown live in the cache. Without a shared cache every
    # gunicorn worker keeps its own counters (limits become N times looser) and a restart resets them.
    if os.getenv("ALLOW_PER_PROCESS_CACHE", "false").strip().lower() == "true":
        import logging
        logging.getLogger(__name__).warning(
            "ALLOW_PER_PROCESS_CACHE=true: rate limits are per worker process. Only acceptable with a single worker."
        )
    else:
        raise ImproperlyConfigured(
            "REDIS_URL is required in production so rate limits and the TOTP lockout are shared by all workers. "
            "Example: REDIS_URL=redis://127.0.0.1:6379/1. For a single-worker server without Redis, "
            "set ALLOW_PER_PROCESS_CACHE=true to accept per-process limits."
        )
