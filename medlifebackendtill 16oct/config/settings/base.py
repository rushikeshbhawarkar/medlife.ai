# # # # # # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # # # # # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# # # # # import os
# # # # # from pathlib import Path
# # # # # from dotenv import load_dotenv

# # # # # BASE_DIR = Path(__file__).resolve().parents[2]
# # # # # load_dotenv(BASE_DIR / ".env")

# # # # # SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
# # # # # DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# # # # # ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# # # # # INSTALLED_APPS = [
# # # # #     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
# # # # #     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# # # # #     "corsheaders", "rest_framework",
# # # # #     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai",
# # # # # ]
# # # # # MIDDLEWARE = [
# # # # #     "django.middleware.security.SecurityMiddleware",
# # # # #     "corsheaders.middleware.CorsMiddleware",
# # # # #     "django.contrib.sessions.middleware.SessionMiddleware",
# # # # #     "django.middleware.common.CommonMiddleware",
# # # # #     "django.middleware.csrf.CsrfViewMiddleware",
# # # # #     "django.contrib.auth.middleware.AuthenticationMiddleware",
# # # # #     "django.contrib.messages.middleware.MessageMiddleware",
# # # # #     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# # # # # ]
# # # # # ROOT_URLCONF = "config.urls"
# # # # # TEMPLATES = [{
# # # # #     "BACKEND": "django.template.backends.django.DjangoTemplates",
# # # # #     "DIRS": [],
# # # # #     "APP_DIRS": True,
# # # # #     "OPTIONS": {"context_processors": [
# # # # #         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
# # # # #         "django.contrib.messages.context_processors.messages",
# # # # #     ]},
# # # # # }]
# # # # # WSGI_APPLICATION = "config.wsgi.application"
# # # # # ASGI_APPLICATION = "config.asgi.application"


# # # # # # PostgreSQL is intentionally the only configured database engine.

# # # # # DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# # # # # if DATABASE_URL:
# # # # #     from urllib.parse import urlparse, unquote

# # # # #     parsed = urlparse(DATABASE_URL)

# # # # #     if parsed.scheme not in ("postgres", "postgresql"):
# # # # #         raise RuntimeError(
# # # # #             "DATABASE_URL must use PostgreSQL (postgresql://...)."
# # # # #         )

# # # # #     DATABASES = {
# # # # #         "default": {
# # # # #             "ENGINE": "django.db.backends.postgresql",
# # # # #             "NAME": unquote(parsed.path.lstrip("/")),
# # # # #             "USER": unquote(parsed.username or ""),
# # # # #             "PASSWORD": unquote(parsed.password or ""),
# # # # #             "HOST": parsed.hostname or "127.0.0.1",
# # # # #             "PORT": parsed.port or 5432,
# # # # #             "CONN_MAX_AGE": 60,
# # # # #             "CONN_HEALTH_CHECKS": True,
# # # # #         }
# # # # #     }

# # # # # else:
# # # # #     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
# # # # #     if not POSTGRES_PASSWORD:
# # # # #         raise RuntimeError(
# # # # #             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
# # # # #             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
# # # # #         )

# # # # #     DATABASES = {
# # # # #         "default": {
# # # # #             "ENGINE": "django.db.backends.postgresql",
# # # # #             "NAME": os.getenv("POSTGRES_DB", "medlife"),
# # # # #             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
# # # # #             "PASSWORD": POSTGRES_PASSWORD,
# # # # #             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
# # # # #             "PORT": os.getenv("POSTGRES_PORT", "5433"),
# # # # #             "CONN_MAX_AGE": 60,
# # # # #             "CONN_HEALTH_CHECKS": True,
# # # # #         }
# # # # #     }


# # # # # # --- Cache (used by rate limiting) ------------------------------------------
# # # # # # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # # # # # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# # # # # REDIS_URL = os.getenv("REDIS_URL", "").strip()
# # # # # if REDIS_URL:
# # # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# # # # # else:
# # # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# # # # # AUTH_PASSWORD_VALIDATORS = []
# # # # # LANGUAGE_CODE = "en-us"
# # # # # TIME_ZONE = "UTC"
# # # # # USE_I18N = True
# # # # # USE_TZ = True
# # # # # STATIC_URL = "static/"
# # # # # STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# # # # # DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # # # # CORS_ALLOWED_ORIGINS = [
# # # # #     x.strip() for x in os.getenv(
# # # # #         "CORS_ALLOWED_ORIGINS",
# # # # #         "http://localhost:5173,http://127.0.0.1:5173"
# # # # #     ).split(",") if x.strip()
# # # # # ]
# # # # # CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# # # # # APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.
# # # # # DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # # # # FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # # # # REST_FRAMEWORK = {
# # # # #     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
# # # # #     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
# # # # #     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
# # # # #     # (health, signup and signin do). The token is issued by /signin.
# # # # #     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
# # # # #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
# # # # #     "UNAUTHENTICATED_USER": None,
# # # # #     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
# # # # #     "DEFAULT_THROTTLE_RATES": {"auth": os.getenv("AUTH_RATE_LIMIT", "10/min")},
# # # # #     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
# # # # #     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
# # # # #     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# # # # # }

# # # # # MAX_MEMBERS = 4
# # # # # TOKEN_LIMIT = 100
# # # # # AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# # # # # AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
# # # # # AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
# # # # # AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "20")), 1), 90)
# # # # # AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # # # # # Avoid emitting request bodies or health information in application logs.
# # # # # LOGGING = {
# # # # #     "version": 1, "disable_existing_loggers": False,
# # # # #     "handlers": {"console": {"class": "logging.StreamHandler"}},
# # # # #     "root": {"handlers": ["console"], "level": "WARNING"},
# # # # # }




























# # # # # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # # # # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# # # # import os
# # # # from pathlib import Path
# # # # from dotenv import load_dotenv

# # # # BASE_DIR = Path(__file__).resolve().parents[2]
# # # # load_dotenv(BASE_DIR / ".env")

# # # # SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
# # # # # Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
# # # # TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
# # # # DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# # # # ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# # # # INSTALLED_APPS = [
# # # #     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
# # # #     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# # # #     "corsheaders", "rest_framework",
# # # #     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai","apps.documents",
# # # # ]
# # # # MIDDLEWARE = [
# # # #     "django.middleware.security.SecurityMiddleware",
# # # #     "corsheaders.middleware.CorsMiddleware",
# # # #     "django.contrib.sessions.middleware.SessionMiddleware",
# # # #     "django.middleware.common.CommonMiddleware",
# # # #     "django.middleware.csrf.CsrfViewMiddleware",
# # # #     "django.contrib.auth.middleware.AuthenticationMiddleware",
# # # #     "django.contrib.messages.middleware.MessageMiddleware",
# # # #     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# # # # ]
# # # # ROOT_URLCONF = "config.urls"
# # # # TEMPLATES = [{
# # # #     "BACKEND": "django.template.backends.django.DjangoTemplates",
# # # #     "DIRS": [],
# # # #     "APP_DIRS": True,
# # # #     "OPTIONS": {"context_processors": [
# # # #         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
# # # #         "django.contrib.messages.context_processors.messages",
# # # #     ]},
# # # # }]
# # # # WSGI_APPLICATION = "config.wsgi.application"
# # # # ASGI_APPLICATION = "config.asgi.application"


# # # # # PostgreSQL is intentionally the only configured database engine.

# # # # DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# # # # if DATABASE_URL:
# # # #     from urllib.parse import urlparse, unquote

# # # #     parsed = urlparse(DATABASE_URL)

# # # #     if parsed.scheme not in ("postgres", "postgresql"):
# # # #         raise RuntimeError(
# # # #             "DATABASE_URL must use PostgreSQL (postgresql://...)."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": unquote(parsed.path.lstrip("/")),
# # # #             "USER": unquote(parsed.username or ""),
# # # #             "PASSWORD": unquote(parsed.password or ""),
# # # #             "HOST": parsed.hostname or "127.0.0.1",
# # # #             "PORT": parsed.port or 5432,
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }

# # # # else:
# # # #     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
# # # #     if not POSTGRES_PASSWORD:
# # # #         raise RuntimeError(
# # # #             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
# # # #             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": os.getenv("POSTGRES_DB", "medlife"),
# # # #             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
# # # #             "PASSWORD": POSTGRES_PASSWORD,
# # # #             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
# # # #             "PORT": os.getenv("POSTGRES_PORT", "5433"),
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }


# # # # # --- Cache (used by rate limiting) ------------------------------------------
# # # # # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # # # # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# # # # REDIS_URL = os.getenv("REDIS_URL", "").strip()
# # # # if REDIS_URL:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# # # # else:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# # # # AUTH_PASSWORD_VALIDATORS = []
# # # # LANGUAGE_CODE = "en-us"
# # # # TIME_ZONE = "UTC"
# # # # USE_I18N = True
# # # # USE_TZ = True
# # # # STATIC_URL = "static/"
# # # # STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# # # # DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # # # CORS_ALLOWED_ORIGINS = [
# # # #     x.strip() for x in os.getenv(
# # # #         "CORS_ALLOWED_ORIGINS",
# # # #         "http://localhost:5173,http://127.0.0.1:5173"
# # # #     ).split(",") if x.strip()
# # # # ]
# # # # CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# # # # APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

# # # # #new ocr code
# # # # # OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# # # # # Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
# # # # OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
# # # # OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
# # # # OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
# # # # OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
# # # # OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
# # # # OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
# # # # TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()



# # # # DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
# # # # FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # # # REST_FRAMEWORK = {
# # # #     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
# # # #     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
# # # #     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
# # # #     # (health, signup and signin do). The token is issued by /signin.
# # # #     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
# # # #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
# # # #     "UNAUTHENTICATED_USER": None,
# # # #     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
# # # #     "DEFAULT_THROTTLE_RATES": {"auth": os.getenv("AUTH_RATE_LIMIT", "10/min")},
# # # #     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
# # # #     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
# # # #     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# # # # }

# # # # MAX_MEMBERS = 4
# # # # TOKEN_LIMIT = 100
# # # # AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# # # # AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
# # # # AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
# # # # # For OpenAI-compatible providers this is the full chat-completions URL.
# # # # AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
# # # # # Ollama's local server base URL; provider appends /api/chat.
# # # # OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
# # # # # Local models may take longer than hosted APIs, so allow up to five minutes.
# # # # AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
# # # # AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # # # # Avoid emitting request bodies or health information in application logs.
# # # # LOGGING = {
# # # #     "version": 1, "disable_existing_loggers": False,
# # # #     "handlers": {"console": {"class": "logging.StreamHandler"}},
# # # #     "root": {"handlers": ["console"], "level": "WARNING"},
# # # # }


















# # # # # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # # # # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# # # # import os
# # # # from pathlib import Path
# # # # from dotenv import load_dotenv

# # # # BASE_DIR = Path(__file__).resolve().parents[2]
# # # # load_dotenv(BASE_DIR / ".env")

# # # # SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
# # # # # Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
# # # # TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
# # # # DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# # # # ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# # # # INSTALLED_APPS = [
# # # #     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
# # # #     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# # # #     "corsheaders", "rest_framework",
# # # #     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai","apps.documents",
# # # # ]
# # # # MIDDLEWARE = [
# # # #     "django.middleware.security.SecurityMiddleware",
# # # #     "corsheaders.middleware.CorsMiddleware",
# # # #     "django.contrib.sessions.middleware.SessionMiddleware",
# # # #     "django.middleware.common.CommonMiddleware",
# # # #     "django.middleware.csrf.CsrfViewMiddleware",
# # # #     "django.contrib.auth.middleware.AuthenticationMiddleware",
# # # #     "django.contrib.messages.middleware.MessageMiddleware",
# # # #     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# # # # ]
# # # # ROOT_URLCONF = "config.urls"
# # # # TEMPLATES = [{
# # # #     "BACKEND": "django.template.backends.django.DjangoTemplates",
# # # #     "DIRS": [],
# # # #     "APP_DIRS": True,
# # # #     "OPTIONS": {"context_processors": [
# # # #         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
# # # #         "django.contrib.messages.context_processors.messages",
# # # #     ]},
# # # # }]
# # # # WSGI_APPLICATION = "config.wsgi.application"
# # # # ASGI_APPLICATION = "config.asgi.application"


# # # # # PostgreSQL is intentionally the only configured database engine.

# # # # DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# # # # if DATABASE_URL:
# # # #     from urllib.parse import urlparse, unquote

# # # #     parsed = urlparse(DATABASE_URL)

# # # #     if parsed.scheme not in ("postgres", "postgresql"):
# # # #         raise RuntimeError(
# # # #             "DATABASE_URL must use PostgreSQL (postgresql://...)."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": unquote(parsed.path.lstrip("/")),
# # # #             "USER": unquote(parsed.username or ""),
# # # #             "PASSWORD": unquote(parsed.password or ""),
# # # #             "HOST": parsed.hostname or "127.0.0.1",
# # # #             "PORT": parsed.port or 5432,
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }

# # # # else:
# # # #     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
# # # #     if not POSTGRES_PASSWORD:
# # # #         raise RuntimeError(
# # # #             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
# # # #             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": os.getenv("POSTGRES_DB", "medlife"),
# # # #             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
# # # #             "PASSWORD": POSTGRES_PASSWORD,
# # # #             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
# # # #             "PORT": os.getenv("POSTGRES_PORT", "5433"),
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }


# # # # # --- Cache (used by rate limiting) ------------------------------------------
# # # # # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # # # # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# # # # REDIS_URL = os.getenv("REDIS_URL", "").strip()
# # # # if REDIS_URL:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# # # # else:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# # # # AUTH_PASSWORD_VALIDATORS = []
# # # # LANGUAGE_CODE = "en-us"
# # # # TIME_ZONE = "UTC"
# # # # USE_I18N = True
# # # # USE_TZ = True
# # # # STATIC_URL = "static/"
# # # # STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# # # # DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # # # CORS_ALLOWED_ORIGINS = [
# # # #     x.strip() for x in os.getenv(
# # # #         "CORS_ALLOWED_ORIGINS",
# # # #         "http://localhost:5173,http://127.0.0.1:5173"
# # # #     ).split(",") if x.strip()
# # # # ]
# # # # CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# # # # APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

# # # # #new ocr code
# # # # # OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# # # # # Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
# # # # OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
# # # # OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
# # # # OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
# # # # OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
# # # # OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
# # # # OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
# # # # TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()



# # # # DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
# # # # FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # # # REST_FRAMEWORK = {
# # # #     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
# # # #     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
# # # #     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
# # # #     # (health, signup and signin do). The token is issued by /signin.
# # # #     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
# # # #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
# # # #     "UNAUTHENTICATED_USER": None,
# # # #     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
# # # #     "DEFAULT_THROTTLE_RATES": {
# # # #         "auth": os.getenv("AUTH_RATE_LIMIT", "10/min"),
# # # #         "password_reset": os.getenv("PASSWORD_RESET_RATE_LIMIT", "5/hour"),
# # # #     },
# # # #     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
# # # #     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
# # # #     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# # # # }

# # # # MAX_MEMBERS = 4
# # # # TOKEN_LIMIT = 100
# # # # AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# # # # AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
# # # # AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
# # # # # For OpenAI-compatible providers this is the full chat-completions URL.
# # # # AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
# # # # # Ollama's local server base URL; provider appends /api/chat.
# # # # OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
# # # # # Local models may take longer than hosted APIs, so allow up to five minutes.
# # # # AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
# # # # AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # # # # Avoid emitting request bodies or health information in application logs.
# # # # # ---- Forgot password / email (all values come from .env; see docs/PASSWORD_RESET.md) ----
# # # # def _env_bool(name, default="false"):
# # # #     return os.getenv(name, default).strip().lower() == "true"

# # # # EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend").strip()
# # # # EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
# # # # EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
# # # # EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "false")
# # # # EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "false" if EMAIL_USE_SSL else "true")  # Django forbids both
# # # # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
# # # # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
# # # # EMAIL_TIMEOUT = 10  # seconds; a slow mail server must not hang the request
# # # # DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "").strip() or EMAIL_HOST_USER or "no-reply@localhost"
# # # # # Frontend page that shows the "new password / confirm password" form. The token is appended after "#".
# # # # FRONTEND_PASSWORD_RESET_URL = os.getenv("FRONTEND_PASSWORD_RESET_URL", "http://localhost:5173/reset-password").strip()
# # # # PASSWORD_RESET_TIMEOUT = max(int(os.getenv("PASSWORD_RESET_TIMEOUT", "300")), 1)  # seconds the link stays valid
# # # # # Minimum gap between two reset emails for the same address (extra to the per-IP limit above).
# # # # PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS = max(int(os.getenv("PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS", "60")), 0)

# # # # LOGGING = {
# # # #     "version": 1, "disable_existing_loggers": False,
# # # #     "handlers": {"console": {"class": "logging.StreamHandler"}},
# # # #     "root": {"handlers": ["console"], "level": "WARNING"},
# # # # }









# # # # # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # # # # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# # # # import os
# # # # from pathlib import Path
# # # # from dotenv import load_dotenv

# # # # BASE_DIR = Path(__file__).resolve().parents[2]
# # # # load_dotenv(BASE_DIR / ".env")

# # # # SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
# # # # # Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
# # # # TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
# # # # DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# # # # ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# # # # INSTALLED_APPS = [
# # # #     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
# # # #     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# # # #     "corsheaders", "rest_framework",
# # # #     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai","apps.documents",
# # # # ]
# # # # MIDDLEWARE = [
# # # #     "django.middleware.security.SecurityMiddleware",
# # # #     "corsheaders.middleware.CorsMiddleware",
# # # #     "django.contrib.sessions.middleware.SessionMiddleware",
# # # #     "django.middleware.common.CommonMiddleware",
# # # #     "django.middleware.csrf.CsrfViewMiddleware",
# # # #     "django.contrib.auth.middleware.AuthenticationMiddleware",
# # # #     "django.contrib.messages.middleware.MessageMiddleware",
# # # #     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# # # # ]
# # # # ROOT_URLCONF = "config.urls"
# # # # TEMPLATES = [{
# # # #     "BACKEND": "django.template.backends.django.DjangoTemplates",
# # # #     "DIRS": [],
# # # #     "APP_DIRS": True,
# # # #     "OPTIONS": {"context_processors": [
# # # #         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
# # # #         "django.contrib.messages.context_processors.messages",
# # # #     ]},
# # # # }]
# # # # WSGI_APPLICATION = "config.wsgi.application"
# # # # ASGI_APPLICATION = "config.asgi.application"


# # # # # PostgreSQL is intentionally the only configured database engine.

# # # # DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# # # # if DATABASE_URL:
# # # #     from urllib.parse import urlparse, unquote

# # # #     parsed = urlparse(DATABASE_URL)

# # # #     if parsed.scheme not in ("postgres", "postgresql"):
# # # #         raise RuntimeError(
# # # #             "DATABASE_URL must use PostgreSQL (postgresql://...)."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": unquote(parsed.path.lstrip("/")),
# # # #             "USER": unquote(parsed.username or ""),
# # # #             "PASSWORD": unquote(parsed.password or ""),
# # # #             "HOST": parsed.hostname or "127.0.0.1",
# # # #             "PORT": parsed.port or 5432,
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }

# # # # else:
# # # #     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
# # # #     if not POSTGRES_PASSWORD:
# # # #         raise RuntimeError(
# # # #             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
# # # #             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": os.getenv("POSTGRES_DB", "medlife"),
# # # #             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
# # # #             "PASSWORD": POSTGRES_PASSWORD,
# # # #             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
# # # #             "PORT": os.getenv("POSTGRES_PORT", "5433"),
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }


# # # # # --- Cache (used by rate limiting) ------------------------------------------
# # # # # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # # # # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# # # # REDIS_URL = os.getenv("REDIS_URL", "").strip()
# # # # if REDIS_URL:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# # # # else:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# # # # AUTH_PASSWORD_VALIDATORS = []
# # # # LANGUAGE_CODE = "en-us"
# # # # TIME_ZONE = "UTC"
# # # # USE_I18N = True
# # # # USE_TZ = True
# # # # STATIC_URL = "static/"
# # # # STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# # # # DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # # # CORS_ALLOWED_ORIGINS = [
# # # #     x.strip() for x in os.getenv(
# # # #         "CORS_ALLOWED_ORIGINS",
# # # #         "http://localhost:5173,http://127.0.0.1:5173"
# # # #     ).split(",") if x.strip()
# # # # ]
# # # # CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# # # # APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

# # # # #new ocr code
# # # # # OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# # # # # Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
# # # # OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
# # # # OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
# # # # OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
# # # # OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
# # # # OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
# # # # OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
# # # # TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()

# # # # # Prescription OCR pipeline. "trocr" is the default; "tesseract" selects the preserved legacy engine.
# # # # OCR_ENGINE = os.getenv("OCR_ENGINE", "trocr").strip().lower()
# # # # PADDLEOCR_DET_MODEL_DIR = os.getenv("PADDLEOCR_DET_MODEL_DIR", "").strip()
# # # # TROCR_MODEL_DIR = os.getenv("TROCR_MODEL_DIR", "").strip()
# # # # TROCR_MAX_NEW_TOKENS = min(max(int(os.getenv("TROCR_MAX_NEW_TOKENS", "128")), 16), 512)
# # # # TROCR_NUM_BEAMS = min(max(int(os.getenv("TROCR_NUM_BEAMS", "1")), 1), 4)
# # # # PRESCRIPTION_DRUGS_FILE = os.getenv("PRESCRIPTION_DRUGS_FILE", str(BASE_DIR / "apps" / "documents" / "data" / "drugs.txt")).strip()



# # # # DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
# # # # FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # # # REST_FRAMEWORK = {
# # # #     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
# # # #     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
# # # #     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
# # # #     # (health, signup and signin do). The token is issued by /signin.
# # # #     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
# # # #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
# # # #     "UNAUTHENTICATED_USER": None,
# # # #     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
# # # #     "DEFAULT_THROTTLE_RATES": {
# # # #         "auth": os.getenv("AUTH_RATE_LIMIT", "10/min"),
# # # #         "password_reset": os.getenv("PASSWORD_RESET_RATE_LIMIT", "5/hour"),
# # # #     },
# # # #     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
# # # #     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
# # # #     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# # # # }

# # # # MAX_MEMBERS = 4
# # # # TOKEN_LIMIT = 100
# # # # AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# # # # AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
# # # # AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
# # # # # For OpenAI-compatible providers this is the full chat-completions URL.
# # # # AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
# # # # # Ollama's local server base URL; provider appends /api/chat.
# # # # OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
# # # # # Local models may take longer than hosted APIs, so allow up to five minutes.
# # # # AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
# # # # AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # # # # Avoid emitting request bodies or health information in application logs.
# # # # # ---- Forgot password / email (all values come from .env; see docs/PASSWORD_RESET.md) ----
# # # # def _env_bool(name, default="false"):
# # # #     return os.getenv(name, default).strip().lower() == "true"

# # # # EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend").strip()
# # # # EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
# # # # EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
# # # # EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "false")
# # # # EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "false" if EMAIL_USE_SSL else "true")  # Django forbids both
# # # # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
# # # # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
# # # # EMAIL_TIMEOUT = 10  # seconds; a slow mail server must not hang the request
# # # # DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "").strip() or EMAIL_HOST_USER or "no-reply@localhost"
# # # # # Frontend page that shows the "new password / confirm password" form. The token is appended after "#".
# # # # FRONTEND_PASSWORD_RESET_URL = os.getenv("FRONTEND_PASSWORD_RESET_URL", "http://localhost:5173/reset-password").strip()
# # # # PASSWORD_RESET_TIMEOUT = max(int(os.getenv("PASSWORD_RESET_TIMEOUT", "300")), 1)  # seconds the link stays valid
# # # # # Minimum gap between two reset emails for the same address (extra to the per-IP limit above).
# # # # PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS = max(int(os.getenv("PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS", "60")), 0)

# # # # LOGGING = {
# # # #     "version": 1, "disable_existing_loggers": False,
# # # #     "handlers": {"console": {"class": "logging.StreamHandler"}},
# # # #     "root": {"handlers": ["console"], "level": "WARNING"},
# # # # }





















# # # # # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # # # # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# # # # import os
# # # # from pathlib import Path
# # # # from dotenv import load_dotenv

# # # # BASE_DIR = Path(__file__).resolve().parents[2]
# # # # load_dotenv(BASE_DIR / ".env")

# # # # SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
# # # # # Google OAuth 2.0 Web client ID used to verify incoming OpenID Connect ID tokens.
# # # # GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
# # # # # Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
# # # # TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
# # # # DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# # # # ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# # # # INSTALLED_APPS = [
# # # #     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
# # # #     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# # # #     "corsheaders", "rest_framework",
# # # #     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai","apps.documents",
# # # # ]
# # # # MIDDLEWARE = [
# # # #     "django.middleware.security.SecurityMiddleware",
# # # #     "corsheaders.middleware.CorsMiddleware",
# # # #     "django.contrib.sessions.middleware.SessionMiddleware",
# # # #     "django.middleware.common.CommonMiddleware",
# # # #     "django.middleware.csrf.CsrfViewMiddleware",
# # # #     "django.contrib.auth.middleware.AuthenticationMiddleware",
# # # #     "django.contrib.messages.middleware.MessageMiddleware",
# # # #     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# # # # ]
# # # # ROOT_URLCONF = "config.urls"
# # # # TEMPLATES = [{
# # # #     "BACKEND": "django.template.backends.django.DjangoTemplates",
# # # #     "DIRS": [],
# # # #     "APP_DIRS": True,
# # # #     "OPTIONS": {"context_processors": [
# # # #         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
# # # #         "django.contrib.messages.context_processors.messages",
# # # #     ]},
# # # # }]
# # # # WSGI_APPLICATION = "config.wsgi.application"
# # # # ASGI_APPLICATION = "config.asgi.application"


# # # # # PostgreSQL is intentionally the only configured database engine.

# # # # DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# # # # if DATABASE_URL:
# # # #     from urllib.parse import urlparse, unquote

# # # #     parsed = urlparse(DATABASE_URL)

# # # #     if parsed.scheme not in ("postgres", "postgresql"):
# # # #         raise RuntimeError(
# # # #             "DATABASE_URL must use PostgreSQL (postgresql://...)."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": unquote(parsed.path.lstrip("/")),
# # # #             "USER": unquote(parsed.username or ""),
# # # #             "PASSWORD": unquote(parsed.password or ""),
# # # #             "HOST": parsed.hostname or "127.0.0.1",
# # # #             "PORT": parsed.port or 5432,
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }

# # # # else:
# # # #     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
# # # #     if not POSTGRES_PASSWORD:
# # # #         raise RuntimeError(
# # # #             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
# # # #             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": os.getenv("POSTGRES_DB", "medlife"),
# # # #             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
# # # #             "PASSWORD": POSTGRES_PASSWORD,
# # # #             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
# # # #             "PORT": os.getenv("POSTGRES_PORT", "5433"),
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }


# # # # # --- Cache (used by rate limiting) ------------------------------------------
# # # # # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # # # # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# # # # REDIS_URL = os.getenv("REDIS_URL", "").strip()
# # # # if REDIS_URL:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# # # # else:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# # # # AUTH_PASSWORD_VALIDATORS = []
# # # # LANGUAGE_CODE = "en-us"
# # # # TIME_ZONE = "UTC"
# # # # USE_I18N = True
# # # # USE_TZ = True
# # # # STATIC_URL = "static/"
# # # # STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# # # # DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # # # CORS_ALLOWED_ORIGINS = [
# # # #     x.strip() for x in os.getenv(
# # # #         "CORS_ALLOWED_ORIGINS",
# # # #         "http://localhost:5173,http://127.0.0.1:5173"
# # # #     ).split(",") if x.strip()
# # # # ]
# # # # CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# # # # APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

# # # # #new ocr code
# # # # # OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# # # # # Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
# # # # OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
# # # # OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
# # # # OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
# # # # OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
# # # # OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
# # # # OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
# # # # TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
# # # # OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract").strip().lower()
# # # # PRESCRIPTION_DRUGS_FILE = os.getenv("PRESCRIPTION_DRUGS_FILE", "").strip()



# # # # DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
# # # # FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # # # REST_FRAMEWORK = {
# # # #     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
# # # #     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
# # # #     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
# # # #     # (health, signup and signin do). The token is issued by /signin.
# # # #     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
# # # #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
# # # #     "UNAUTHENTICATED_USER": None,
# # # #     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
# # # #     "DEFAULT_THROTTLE_RATES": {
# # # #         "auth": os.getenv("AUTH_RATE_LIMIT", "10/min"),
# # # #         "password_reset": os.getenv("PASSWORD_RESET_RATE_LIMIT", "5/hour"),
# # # #     },
# # # #     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
# # # #     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
# # # #     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# # # # }

# # # # MAX_MEMBERS = 4
# # # # TOKEN_LIMIT = 100
# # # # AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# # # # AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
# # # # AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
# # # # # For OpenAI-compatible providers this is the full chat-completions URL.
# # # # AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
# # # # # Ollama's local server base URL; provider appends /api/chat.
# # # # OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
# # # # # Local models may take longer than hosted APIs, so allow up to five minutes.
# # # # AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
# # # # AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # # # # Avoid emitting request bodies or health information in application logs.
# # # # # ---- Forgot password / email (all values come from .env; see docs/PASSWORD_RESET.md) ----
# # # # def _env_bool(name, default="false"):
# # # #     return os.getenv(name, default).strip().lower() == "true"

# # # # EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend").strip()
# # # # EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
# # # # EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
# # # # EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "false")
# # # # EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "false" if EMAIL_USE_SSL else "true")  # Django forbids both
# # # # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
# # # # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
# # # # EMAIL_TIMEOUT = 10  # seconds; a slow mail server must not hang the request
# # # # DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "").strip() or EMAIL_HOST_USER or "no-reply@localhost"
# # # # # Frontend page that shows the "new password / confirm password" form. The token is appended after "#".
# # # # FRONTEND_PASSWORD_RESET_URL = os.getenv("FRONTEND_PASSWORD_RESET_URL", "http://localhost:5173/reset-password").strip()
# # # # PASSWORD_RESET_TIMEOUT = max(int(os.getenv("PASSWORD_RESET_TIMEOUT", "300")), 1)  # seconds the link stays valid
# # # # # Minimum gap between two reset emails for the same address (extra to the per-IP limit above).
# # # # PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS = max(int(os.getenv("PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS", "60")), 0)

# # # # LOGGING = {
# # # #     "version": 1, "disable_existing_loggers": False,
# # # #     "handlers": {"console": {"class": "logging.StreamHandler"}},
# # # #     "root": {"handlers": ["console"], "level": "WARNING"},
# # # # }














# # # # # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # # # # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# # # # import os
# # # # from pathlib import Path
# # # # from dotenv import load_dotenv

# # # # BASE_DIR = Path(__file__).resolve().parents[2]
# # # # load_dotenv(BASE_DIR / ".env")

# # # # SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
# # # # # Google OAuth 2.0 Web client ID used to verify incoming OpenID Connect ID tokens.
# # # # GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
# # # # # Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
# # # # TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
# # # # DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# # # # ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# # # # INSTALLED_APPS = [
# # # #     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
# # # #     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# # # #     "corsheaders", "rest_framework",
# # # #     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai","apps.documents",
# # # # ]
# # # # MIDDLEWARE = [
# # # #     "django.middleware.security.SecurityMiddleware",
# # # #     "corsheaders.middleware.CorsMiddleware",
# # # #     "django.contrib.sessions.middleware.SessionMiddleware",
# # # #     "django.middleware.common.CommonMiddleware",
# # # #     "django.middleware.csrf.CsrfViewMiddleware",
# # # #     "django.contrib.auth.middleware.AuthenticationMiddleware",
# # # #     "django.contrib.messages.middleware.MessageMiddleware",
# # # #     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# # # # ]
# # # # ROOT_URLCONF = "config.urls"
# # # # TEMPLATES = [{
# # # #     "BACKEND": "django.template.backends.django.DjangoTemplates",
# # # #     "DIRS": [],
# # # #     "APP_DIRS": True,
# # # #     "OPTIONS": {"context_processors": [
# # # #         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
# # # #         "django.contrib.messages.context_processors.messages",
# # # #     ]},
# # # # }]
# # # # WSGI_APPLICATION = "config.wsgi.application"
# # # # ASGI_APPLICATION = "config.asgi.application"


# # # # # PostgreSQL is intentionally the only configured database engine.

# # # # DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# # # # if DATABASE_URL:
# # # #     from urllib.parse import urlparse, unquote

# # # #     parsed = urlparse(DATABASE_URL)

# # # #     if parsed.scheme not in ("postgres", "postgresql"):
# # # #         raise RuntimeError(
# # # #             "DATABASE_URL must use PostgreSQL (postgresql://...)."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": unquote(parsed.path.lstrip("/")),
# # # #             "USER": unquote(parsed.username or ""),
# # # #             "PASSWORD": unquote(parsed.password or ""),
# # # #             "HOST": parsed.hostname or "127.0.0.1",
# # # #             "PORT": parsed.port or 5432,
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }

# # # # else:
# # # #     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
# # # #     if not POSTGRES_PASSWORD:
# # # #         raise RuntimeError(
# # # #             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
# # # #             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": os.getenv("POSTGRES_DB", "medlife"),
# # # #             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
# # # #             "PASSWORD": POSTGRES_PASSWORD,
# # # #             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
# # # #             "PORT": os.getenv("POSTGRES_PORT", "5433"),
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }


# # # # # --- Cache (used by rate limiting) ------------------------------------------
# # # # # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # # # # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# # # # REDIS_URL = os.getenv("REDIS_URL", "").strip()
# # # # if REDIS_URL:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# # # # else:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# # # # AUTH_PASSWORD_VALIDATORS = []
# # # # LANGUAGE_CODE = "en-us"
# # # # TIME_ZONE = "UTC"
# # # # USE_I18N = True
# # # # USE_TZ = True
# # # # STATIC_URL = "static/"
# # # # STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# # # # DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # # # CORS_ALLOWED_ORIGINS = [
# # # #     x.strip() for x in os.getenv(
# # # #         "CORS_ALLOWED_ORIGINS",
# # # #         "http://localhost:5173,http://127.0.0.1:5173"
# # # #     ).split(",") if x.strip()
# # # # ]
# # # # CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# # # # APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

# # # # #new ocr code
# # # # # OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# # # # # Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
# # # # OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
# # # # OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
# # # # OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
# # # # OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
# # # # OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
# # # # OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
# # # # TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
# # # # OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract").strip().lower()
# # # # PRESCRIPTION_DRUGS_FILE = os.getenv("PRESCRIPTION_DRUGS_FILE", "").strip()



# # # # DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
# # # # FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # # # REST_FRAMEWORK = {
# # # #     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
# # # #     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
# # # #     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
# # # #     # (health, signup and signin do). The token is issued by /signin.
# # # #     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
# # # #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
# # # #     "UNAUTHENTICATED_USER": None,
# # # #     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
# # # #     "DEFAULT_THROTTLE_RATES": {
# # # #         "auth": os.getenv("AUTH_RATE_LIMIT", "10/min"),
# # # #         "password_reset": os.getenv("PASSWORD_RESET_RATE_LIMIT", "5/hour"),
# # # #     },
# # # #     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
# # # #     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
# # # #     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# # # # }

# # # # MAX_MEMBERS = 4
# # # # TOKEN_LIMIT = 100
# # # # AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# # # # AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
# # # # AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
# # # # # For OpenAI-compatible providers this is the full chat-completions URL.
# # # # AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
# # # # # Ollama's local server base URL; provider appends /api/chat.
# # # # OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
# # # # # Local models may take longer than hosted APIs, so allow up to five minutes.
# # # # AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
# # # # AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # # # # Avoid emitting request bodies or health information in application logs.
# # # # # ---- Forgot password / email (all values come from .env; see docs/PASSWORD_RESET.md) ----
# # # # def _env_bool(name, default="false"):
# # # #     return os.getenv(name, default).strip().lower() == "true"

# # # # EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend").strip()
# # # # EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
# # # # EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
# # # # EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "false")
# # # # EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "false" if EMAIL_USE_SSL else "true")  # Django forbids both
# # # # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
# # # # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
# # # # EMAIL_TIMEOUT = 10  # seconds; a slow mail server must not hang the request
# # # # DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "").strip() or EMAIL_HOST_USER or "no-reply@localhost"
# # # # # Frontend page that shows the "new password / confirm password" form. The token is appended after "#".
# # # # FRONTEND_PASSWORD_RESET_URL = os.getenv("FRONTEND_PASSWORD_RESET_URL", "http://localhost:5173/reset-password").strip()
# # # # PASSWORD_RESET_TIMEOUT = max(int(os.getenv("PASSWORD_RESET_TIMEOUT", "300")), 1)  # seconds the link stays valid
# # # # # Minimum gap between two reset emails for the same address (extra to the per-IP limit above).
# # # # PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS = max(int(os.getenv("PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS", "60")), 0)

# # # # LOGGING = {
# # # #     "version": 1, "disable_existing_loggers": False,
# # # #     "handlers": {"console": {"class": "logging.StreamHandler"}},
# # # #     "root": {"handlers": ["console"], "level": "WARNING"},
# # # # }


# # # # # Frontend page that reads the emailed TOTP recovery token from the URL fragment.
# # # # FRONTEND_TOTP_RECOVERY_URL = os.getenv("FRONTEND_TOTP_RECOVERY_URL", "http://localhost:5173/recover-totp").strip()




















# # # # # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # # # # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# # # # import os
# # # # from pathlib import Path
# # # # from dotenv import load_dotenv

# # # # BASE_DIR = Path(__file__).resolve().parents[2]
# # # # load_dotenv(BASE_DIR / ".env")

# # # # SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
# # # # # Google OAuth 2.0 Web client ID used to verify incoming OpenID Connect ID tokens.
# # # # GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
# # # # # Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
# # # # TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
# # # # DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# # # # ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# # # # INSTALLED_APPS = [
# # # #     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
# # # #     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# # # #     "corsheaders", "rest_framework",
# # # #     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai", "apps.documents", "apps.doctors",
# # # # ]
# # # # MIDDLEWARE = [
# # # #     "django.middleware.security.SecurityMiddleware",
# # # #     "corsheaders.middleware.CorsMiddleware",
# # # #     "django.contrib.sessions.middleware.SessionMiddleware",
# # # #     "django.middleware.common.CommonMiddleware",
# # # #     "django.middleware.csrf.CsrfViewMiddleware",
# # # #     "django.contrib.auth.middleware.AuthenticationMiddleware",
# # # #     "django.contrib.messages.middleware.MessageMiddleware",
# # # #     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# # # # ]
# # # # ROOT_URLCONF = "config.urls"
# # # # TEMPLATES = [{
# # # #     "BACKEND": "django.template.backends.django.DjangoTemplates",
# # # #     "DIRS": [],
# # # #     "APP_DIRS": True,
# # # #     "OPTIONS": {"context_processors": [
# # # #         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
# # # #         "django.contrib.messages.context_processors.messages",
# # # #     ]},
# # # # }]
# # # # WSGI_APPLICATION = "config.wsgi.application"
# # # # ASGI_APPLICATION = "config.asgi.application"


# # # # # PostgreSQL is intentionally the only configured database engine.

# # # # DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# # # # if DATABASE_URL:
# # # #     from urllib.parse import urlparse, unquote

# # # #     parsed = urlparse(DATABASE_URL)

# # # #     if parsed.scheme not in ("postgres", "postgresql"):
# # # #         raise RuntimeError(
# # # #             "DATABASE_URL must use PostgreSQL (postgresql://...)."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": unquote(parsed.path.lstrip("/")),
# # # #             "USER": unquote(parsed.username or ""),
# # # #             "PASSWORD": unquote(parsed.password or ""),
# # # #             "HOST": parsed.hostname or "127.0.0.1",
# # # #             "PORT": parsed.port or 5432,
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }

# # # # else:
# # # #     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
# # # #     if not POSTGRES_PASSWORD:
# # # #         raise RuntimeError(
# # # #             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
# # # #             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
# # # #         )

# # # #     DATABASES = {
# # # #         "default": {
# # # #             "ENGINE": "django.db.backends.postgresql",
# # # #             "NAME": os.getenv("POSTGRES_DB", "medlife"),
# # # #             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
# # # #             "PASSWORD": POSTGRES_PASSWORD,
# # # #             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
# # # #             "PORT": os.getenv("POSTGRES_PORT", "5433"),
# # # #             "CONN_MAX_AGE": 60,
# # # #             "CONN_HEALTH_CHECKS": True,
# # # #         }
# # # #     }


# # # # # --- Cache (used by rate limiting) ------------------------------------------
# # # # # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # # # # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# # # # REDIS_URL = os.getenv("REDIS_URL", "").strip()
# # # # if REDIS_URL:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# # # # else:
# # # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# # # # AUTH_PASSWORD_VALIDATORS = []
# # # # LANGUAGE_CODE = "en-us"
# # # # TIME_ZONE = "UTC"
# # # # USE_I18N = True
# # # # USE_TZ = True
# # # # STATIC_URL = "static/"
# # # # STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# # # # DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # # # CORS_ALLOWED_ORIGINS = [
# # # #     x.strip() for x in os.getenv(
# # # #         "CORS_ALLOWED_ORIGINS",
# # # #         "http://localhost:5173,http://127.0.0.1:5173"
# # # #     ).split(",") if x.strip()
# # # # ]
# # # # CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# # # # APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

# # # # #new ocr code
# # # # # OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# # # # # Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
# # # # OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
# # # # OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
# # # # OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
# # # # OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
# # # # OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
# # # # OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
# # # # TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
# # # # OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract").strip().lower()
# # # # PRESCRIPTION_DRUGS_FILE = os.getenv("PRESCRIPTION_DRUGS_FILE", "").strip()



# # # # DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
# # # # FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # # # REST_FRAMEWORK = {
# # # #     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
# # # #     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
# # # #     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
# # # #     # (health, signup and signin do). The token is issued by /signin.
# # # #     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
# # # #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
# # # #     "UNAUTHENTICATED_USER": None,
# # # #     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
# # # #     "DEFAULT_THROTTLE_RATES": {
# # # #         "auth": os.getenv("AUTH_RATE_LIMIT", "10/min"),
# # # #         "password_reset": os.getenv("PASSWORD_RESET_RATE_LIMIT", "5/hour"),
# # # #     },
# # # #     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
# # # #     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
# # # #     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# # # # }

# # # # MAX_MEMBERS = 4
# # # # TOKEN_LIMIT = 100
# # # # AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# # # # AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
# # # # AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
# # # # # For OpenAI-compatible providers this is the full chat-completions URL.
# # # # AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
# # # # # Ollama's local server base URL; provider appends /api/chat.
# # # # OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
# # # # # Local models may take longer than hosted APIs, so allow up to five minutes.
# # # # AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
# # # # AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # # # # Avoid emitting request bodies or health information in application logs.
# # # # # ---- Forgot password / email (all values come from .env; see docs/PASSWORD_RESET.md) ----
# # # # def _env_bool(name, default="false"):
# # # #     return os.getenv(name, default).strip().lower() == "true"

# # # # EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend").strip()
# # # # EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
# # # # EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
# # # # EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "false")
# # # # EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "false" if EMAIL_USE_SSL else "true")  # Django forbids both
# # # # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
# # # # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
# # # # EMAIL_TIMEOUT = 10  # seconds; a slow mail server must not hang the request
# # # # DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "").strip() or EMAIL_HOST_USER or "no-reply@localhost"
# # # # # Frontend page that shows the "new password / confirm password" form. The token is appended after "#".
# # # # FRONTEND_PASSWORD_RESET_URL = os.getenv("FRONTEND_PASSWORD_RESET_URL", "http://localhost:5173/reset-password").strip()
# # # # PASSWORD_RESET_TIMEOUT = max(int(os.getenv("PASSWORD_RESET_TIMEOUT", "300")), 1)  # seconds the link stays valid
# # # # # Minimum gap between two reset emails for the same address (extra to the per-IP limit above).
# # # # PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS = max(int(os.getenv("PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS", "60")), 0)

# # # # LOGGING = {
# # # #     "version": 1, "disable_existing_loggers": False,
# # # #     "handlers": {"console": {"class": "logging.StreamHandler"}},
# # # #     "root": {"handlers": ["console"], "level": "WARNING"},
# # # # }


# # # # # Frontend page that reads the emailed TOTP recovery token from the URL fragment.
# # # # FRONTEND_TOTP_RECOVERY_URL = os.getenv("FRONTEND_TOTP_RECOVERY_URL", "http://localhost:5173/recover-totp").strip()

# # # # # MedLife doctor-system administrator allowlists. Never expose these controls through public signup.
# # # # MEDLIFE_SUPER_ADMIN_EMAILS = [x.strip().lower() for x in os.getenv("MEDLIFE_SUPER_ADMIN_EMAILS", "").split(",") if x.strip()]
# # # # MEDLIFE_DOCTOR_REVIEWER_EMAILS = [x.strip().lower() for x in os.getenv("MEDLIFE_DOCTOR_REVIEWER_EMAILS", "").split(",") if x.strip()]
# # # # FRONTEND_DOCTOR_INVITATION_URL = os.getenv("FRONTEND_DOCTOR_INVITATION_URL", "http://localhost:5173/doctor-invitation").strip()






















# # # # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # # # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# # # import os
# # # from pathlib import Path
# # # from dotenv import load_dotenv

# # # BASE_DIR = Path(__file__).resolve().parents[2]
# # # load_dotenv(BASE_DIR / ".env")

# # # SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
# # # # Google OAuth 2.0 Web client ID used to verify incoming OpenID Connect ID tokens.
# # # GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
# # # # Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
# # # TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
# # # DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# # # ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# # # INSTALLED_APPS = [
# # #     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
# # #     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# # #     "corsheaders", "rest_framework",
# # #     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai", "apps.documents", "apps.doctors",
# # # ]
# # # MIDDLEWARE = [
# # #     "django.middleware.security.SecurityMiddleware",
# # #     "corsheaders.middleware.CorsMiddleware",
# # #     "django.contrib.sessions.middleware.SessionMiddleware",
# # #     "django.middleware.common.CommonMiddleware",
# # #     "django.middleware.csrf.CsrfViewMiddleware",
# # #     "django.contrib.auth.middleware.AuthenticationMiddleware",
# # #     "django.contrib.messages.middleware.MessageMiddleware",
# # #     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# # # ]
# # # ROOT_URLCONF = "config.urls"
# # # TEMPLATES = [{
# # #     "BACKEND": "django.template.backends.django.DjangoTemplates",
# # #     "DIRS": [],
# # #     "APP_DIRS": True,
# # #     "OPTIONS": {"context_processors": [
# # #         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
# # #         "django.contrib.messages.context_processors.messages",
# # #     ]},
# # # }]
# # # WSGI_APPLICATION = "config.wsgi.application"
# # # ASGI_APPLICATION = "config.asgi.application"


# # # # PostgreSQL is intentionally the only configured database engine.

# # # DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# # # if DATABASE_URL:
# # #     from urllib.parse import urlparse, unquote

# # #     parsed = urlparse(DATABASE_URL)

# # #     if parsed.scheme not in ("postgres", "postgresql"):
# # #         raise RuntimeError(
# # #             "DATABASE_URL must use PostgreSQL (postgresql://...)."
# # #         )

# # #     DATABASES = {
# # #         "default": {
# # #             "ENGINE": "django.db.backends.postgresql",
# # #             "NAME": unquote(parsed.path.lstrip("/")),
# # #             "USER": unquote(parsed.username or ""),
# # #             "PASSWORD": unquote(parsed.password or ""),
# # #             "HOST": parsed.hostname or "127.0.0.1",
# # #             "PORT": parsed.port or 5432,
# # #             "CONN_MAX_AGE": 60,
# # #             "CONN_HEALTH_CHECKS": True,
# # #         }
# # #     }

# # # else:
# # #     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
# # #     if not POSTGRES_PASSWORD:
# # #         raise RuntimeError(
# # #             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
# # #             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
# # #         )

# # #     DATABASES = {
# # #         "default": {
# # #             "ENGINE": "django.db.backends.postgresql",
# # #             "NAME": os.getenv("POSTGRES_DB", "medlife"),
# # #             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
# # #             "PASSWORD": POSTGRES_PASSWORD,
# # #             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
# # #             "PORT": os.getenv("POSTGRES_PORT", "5433"),
# # #             "CONN_MAX_AGE": 60,
# # #             "CONN_HEALTH_CHECKS": True,
# # #         }
# # #     }


# # # # --- Cache (used by rate limiting) ------------------------------------------
# # # # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # # # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# # # REDIS_URL = os.getenv("REDIS_URL", "").strip()
# # # if REDIS_URL:
# # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# # # else:
# # #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# # # AUTH_PASSWORD_VALIDATORS = []
# # # LANGUAGE_CODE = "en-us"
# # # TIME_ZONE = "UTC"
# # # USE_I18N = True
# # # USE_TZ = True
# # # STATIC_URL = "static/"
# # # STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# # # DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # # CORS_ALLOWED_ORIGINS = [
# # #     x.strip() for x in os.getenv(
# # #         "CORS_ALLOWED_ORIGINS",
# # #         "http://localhost:5173,http://127.0.0.1:5173"
# # #     ).split(",") if x.strip()
# # # ]
# # # CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# # # APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

# # # #new ocr code
# # # # OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# # # # Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
# # # OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
# # # OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
# # # OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
# # # OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
# # # OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
# # # OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
# # # TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
# # # OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract").strip().lower()
# # # PRESCRIPTION_DRUGS_FILE = os.getenv("PRESCRIPTION_DRUGS_FILE", "").strip()



# # # DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
# # # FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # # REST_FRAMEWORK = {
# # #     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
# # #     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
# # #     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
# # #     # (health, signup and signin do). The token is issued by /signin.
# # #     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
# # #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
# # #     "UNAUTHENTICATED_USER": None,
# # #     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
# # #     "DEFAULT_THROTTLE_RATES": {
# # #         "auth": os.getenv("AUTH_RATE_LIMIT", "10/min"),
# # #         "password_reset": os.getenv("PASSWORD_RESET_RATE_LIMIT", "5/hour"),
# # #     },
# # #     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
# # #     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
# # #     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# # # }

# # # MAX_MEMBERS = 4
# # # TOKEN_LIMIT = 100
# # # AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# # # AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
# # # AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
# # # # For OpenAI-compatible providers this is the full chat-completions URL.
# # # AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
# # # # Ollama's local server base URL; provider appends /api/chat.
# # # OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
# # # # Local models may take longer than hosted APIs, so allow up to five minutes.
# # # AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
# # # AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # # # Avoid emitting request bodies or health information in application logs.
# # # # ---- Forgot password / email (all values come from .env; see docs/PASSWORD_RESET.md) ----
# # # def _env_bool(name, default="false"):
# # #     return os.getenv(name, default).strip().lower() == "true"

# # # EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend").strip()
# # # EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
# # # EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
# # # EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "false")
# # # EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "false" if EMAIL_USE_SSL else "true")  # Django forbids both
# # # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
# # # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
# # # EMAIL_TIMEOUT = 10  # seconds; a slow mail server must not hang the request
# # # DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "").strip() or EMAIL_HOST_USER or "no-reply@localhost"
# # # # Frontend page that shows the "new password / confirm password" form. The token is appended after "#".
# # # FRONTEND_PASSWORD_RESET_URL = os.getenv("FRONTEND_PASSWORD_RESET_URL", "http://localhost:5173/reset-password").strip()
# # # PASSWORD_RESET_TIMEOUT = max(int(os.getenv("PASSWORD_RESET_TIMEOUT", "300")), 1)  # seconds the link stays valid
# # # # Minimum gap between two reset emails for the same address (extra to the per-IP limit above).
# # # PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS = max(int(os.getenv("PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS", "60")), 0)

# # # LOGGING = {
# # #     "version": 1, "disable_existing_loggers": False,
# # #     "handlers": {"console": {"class": "logging.StreamHandler"}},
# # #     "root": {"handlers": ["console"], "level": "WARNING"},
# # # }


# # # # Frontend page that reads the emailed TOTP recovery token from the URL fragment.
# # # FRONTEND_TOTP_RECOVERY_URL = os.getenv("FRONTEND_TOTP_RECOVERY_URL", "http://localhost:5173/recover-totp").strip()

# # # # MedLife doctor-system administrator allowlists. Never expose these controls through public signup.
# # # FRONTEND_DOCTOR_INVITATION_URL = os.getenv("FRONTEND_DOCTOR_INVITATION_URL", "http://localhost:5173/doctor-invitation").strip()



















# # # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# # import os
# # from pathlib import Path
# # from dotenv import load_dotenv

# # BASE_DIR = Path(__file__).resolve().parents[2]
# # load_dotenv(BASE_DIR / ".env")

# # SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
# # # Google OAuth 2.0 Web client ID used to verify incoming OpenID Connect ID tokens.
# # GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
# # # Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
# # TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
# # DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# # ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# # INSTALLED_APPS = [
# #     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
# #     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# #     "corsheaders", "rest_framework",
# #     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai", "apps.documents", "apps.doctors",
# # ]
# # MIDDLEWARE = [
# #     "django.middleware.security.SecurityMiddleware",
# #     "corsheaders.middleware.CorsMiddleware",
# #     "django.contrib.sessions.middleware.SessionMiddleware",
# #     "django.middleware.common.CommonMiddleware",
# #     "django.middleware.csrf.CsrfViewMiddleware",
# #     "django.contrib.auth.middleware.AuthenticationMiddleware",
# #     "django.contrib.messages.middleware.MessageMiddleware",
# #     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# # ]
# # ROOT_URLCONF = "config.urls"
# # TEMPLATES = [{
# #     "BACKEND": "django.template.backends.django.DjangoTemplates",
# #     "DIRS": [],
# #     "APP_DIRS": True,
# #     "OPTIONS": {"context_processors": [
# #         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
# #         "django.contrib.messages.context_processors.messages",
# #     ]},
# # }]
# # WSGI_APPLICATION = "config.wsgi.application"
# # ASGI_APPLICATION = "config.asgi.application"


# # # PostgreSQL is intentionally the only configured database engine.

# # DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# # if DATABASE_URL:
# #     from urllib.parse import urlparse, unquote

# #     parsed = urlparse(DATABASE_URL)

# #     if parsed.scheme not in ("postgres", "postgresql"):
# #         raise RuntimeError(
# #             "DATABASE_URL must use PostgreSQL (postgresql://...)."
# #         )

# #     DATABASES = {
# #         "default": {
# #             "ENGINE": "django.db.backends.postgresql",
# #             "NAME": unquote(parsed.path.lstrip("/")),
# #             "USER": unquote(parsed.username or ""),
# #             "PASSWORD": unquote(parsed.password or ""),
# #             "HOST": parsed.hostname or "127.0.0.1",
# #             "PORT": parsed.port or 5432,
# #             "CONN_MAX_AGE": 60,
# #             "CONN_HEALTH_CHECKS": True,
# #         }
# #     }

# # else:
# #     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
# #     if not POSTGRES_PASSWORD:
# #         raise RuntimeError(
# #             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
# #             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
# #         )

# #     DATABASES = {
# #         "default": {
# #             "ENGINE": "django.db.backends.postgresql",
# #             "NAME": os.getenv("POSTGRES_DB", "medlife"),
# #             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
# #             "PASSWORD": POSTGRES_PASSWORD,
# #             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
# #             "PORT": os.getenv("POSTGRES_PORT", "5433"),
# #             "CONN_MAX_AGE": 60,
# #             "CONN_HEALTH_CHECKS": True,
# #         }
# #     }


# # # --- Cache (used by rate limiting) ------------------------------------------
# # # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# # REDIS_URL = os.getenv("REDIS_URL", "").strip()
# # if REDIS_URL:
# #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# # else:
# #     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# # AUTH_PASSWORD_VALIDATORS = []
# # LANGUAGE_CODE = "en-us"
# # TIME_ZONE = "UTC"
# # USE_I18N = True
# # USE_TZ = True
# # STATIC_URL = "static/"
# # STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# # DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # CORS_ALLOWED_ORIGINS = [
# #     x.strip() for x in os.getenv(
# #         "CORS_ALLOWED_ORIGINS",
# #         "http://localhost:5173,http://127.0.0.1:5173"
# #     ).split(",") if x.strip()
# # ]
# # CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# # APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

# # #new ocr code
# # # OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# # # Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
# # OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
# # OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
# # OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
# # OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
# # OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
# # OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
# # TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
# # OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract").strip().lower()
# # PRESCRIPTION_DRUGS_FILE = os.getenv("PRESCRIPTION_DRUGS_FILE", "").strip()



# # DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
# # FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# # REST_FRAMEWORK = {
# #     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
# #     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
# #     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
# #     # (health, signup and signin do). The token is issued by /signin.
# #     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
# #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
# #     "UNAUTHENTICATED_USER": None,
# #     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
# #     "DEFAULT_THROTTLE_RATES": {
# #         "auth": os.getenv("AUTH_RATE_LIMIT", "10/min"),
# #         "password_reset": os.getenv("PASSWORD_RESET_RATE_LIMIT", "5/hour"),
# #     },
# #     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
# #     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
# #     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# # }

# # MAX_MEMBERS = 4
# # TOKEN_LIMIT = 100
# # AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# # AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
# # AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
# # # For OpenAI-compatible providers this is the full chat-completions URL.
# # AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
# # # Ollama's local server base URL; provider appends /api/chat.
# # OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
# # # Local models may take longer than hosted APIs, so allow up to five minutes.
# # AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
# # AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # # Avoid emitting request bodies or health information in application logs.
# # # ---- Forgot password / email (all values come from .env; see docs/PASSWORD_RESET.md) ----
# # def _env_bool(name, default="false"):
# #     return os.getenv(name, default).strip().lower() == "true"

# # EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend").strip()
# # EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
# # EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
# # EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "false")
# # EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "false" if EMAIL_USE_SSL else "true")  # Django forbids both
# # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
# # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
# # EMAIL_TIMEOUT = 10  # seconds; a slow mail server must not hang the request
# # DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "").strip() or EMAIL_HOST_USER or "no-reply@localhost"
# # # Frontend page that shows the "new password / confirm password" form. The token is appended after "#".
# # FRONTEND_PASSWORD_RESET_URL = os.getenv("FRONTEND_PASSWORD_RESET_URL", "http://localhost:5173/reset-password").strip()
# # FRONTEND_DOCTOR_ACTIVATION_URL = os.getenv("FRONTEND_DOCTOR_ACTIVATION_URL", "http://localhost:5173/doctor-activate").strip()
# # PASSWORD_RESET_TIMEOUT = max(int(os.getenv("PASSWORD_RESET_TIMEOUT", "300")), 1)  # seconds the link stays valid
# # # Minimum gap between two reset emails for the same address (extra to the per-IP limit above).
# # PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS = max(int(os.getenv("PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS", "60")), 0)

# # LOGGING = {
# #     "version": 1, "disable_existing_loggers": False,
# #     "handlers": {"console": {"class": "logging.StreamHandler"}},
# #     "root": {"handlers": ["console"], "level": "WARNING"},
# # }


# # # Frontend page that reads the emailed TOTP recovery token from the URL fragment.
# # FRONTEND_TOTP_RECOVERY_URL = os.getenv("FRONTEND_TOTP_RECOVERY_URL", "http://localhost:5173/recover-totp").strip()

# # # MedLife doctor-system administrator allowlists. Never expose these controls through public signup.
# # FRONTEND_DOCTOR_INVITATION_URL = os.getenv("FRONTEND_DOCTOR_INVITATION_URL", "http://localhost:5173/doctor-invitation").strip()

# # # Private application uploads are stored under the project media directory.
# # MEDIA_URL = os.getenv("MEDIA_URL", "/media/").strip()
# # MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BASE_DIR / "media")))











# # Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# # Edit this file for shared settings and limits; do not put feature-specific business logic here.
# import os
# from pathlib import Path
# from dotenv import load_dotenv

# BASE_DIR = Path(__file__).resolve().parents[2]
# load_dotenv(BASE_DIR / ".env")

# SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()
# DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
# if not SECRET_KEY or (not DEBUG and (
#     len(SECRET_KEY) < 50 or "change-me" in SECRET_KEY.lower() or "unsafe-development" in SECRET_KEY.lower()
# )):
#     if DEBUG and not SECRET_KEY:
#         SECRET_KEY = "unsafe-development-key-change-me"
#     else:
#         raise RuntimeError(
#             "Set DJANGO_SECRET_KEY to a strong, unique value (at least 50 characters) "
#             "when DJANGO_DEBUG is false."
#         )
# # Google OAuth 2.0 Web client ID used to verify incoming OpenID Connect ID tokens.
# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
# # Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
# TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
# ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

# INSTALLED_APPS = [
#     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
#     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
#     "corsheaders", "rest_framework",
#     "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai", "apps.documents", "apps.doctors",
# ]
# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "corsheaders.middleware.CorsMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]
# ROOT_URLCONF = "config.urls"
# TEMPLATES = [{
#     "BACKEND": "django.template.backends.django.DjangoTemplates",
#     "DIRS": [],
#     "APP_DIRS": True,
#     "OPTIONS": {"context_processors": [
#         "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
#         "django.contrib.messages.context_processors.messages",
#     ]},
# }]
# WSGI_APPLICATION = "config.wsgi.application"
# ASGI_APPLICATION = "config.asgi.application"


# # PostgreSQL is intentionally the only configured database engine.

# DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# if DATABASE_URL:
#     from urllib.parse import urlparse, unquote

#     parsed = urlparse(DATABASE_URL)

#     if parsed.scheme not in ("postgres", "postgresql"):
#         raise RuntimeError(
#             "DATABASE_URL must use PostgreSQL (postgresql://...)."
#         )

#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.postgresql",
#             "NAME": unquote(parsed.path.lstrip("/")),
#             "USER": unquote(parsed.username or ""),
#             "PASSWORD": unquote(parsed.password or ""),
#             "HOST": parsed.hostname or "127.0.0.1",
#             "PORT": parsed.port or 5432,
#             "CONN_MAX_AGE": 60,
#             "CONN_HEALTH_CHECKS": True,
#         }
#     }

# else:
#     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
#     if not POSTGRES_PASSWORD:
#         raise RuntimeError(
#             f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
#             f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
#         )

#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.postgresql",
#             "NAME": os.getenv("POSTGRES_DB", "medlife"),
#             "USER": os.getenv("POSTGRES_USER", "medlife_user"),
#             "PASSWORD": POSTGRES_PASSWORD,
#             "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
#             "PORT": os.getenv("POSTGRES_PORT", "5433"),
#             "CONN_MAX_AGE": 60,
#             "CONN_HEALTH_CHECKS": True,
#         }
#     }


# # --- Cache (used by rate limiting) ------------------------------------------
# # Default is per-process memory: fine for one dev process. With several gunicorn workers,
# # set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
# REDIS_URL = os.getenv("REDIS_URL", "").strip()
# if REDIS_URL:
#     CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
# else:
#     CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# AUTH_PASSWORD_VALIDATORS = [
#     {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]
# LANGUAGE_CODE = "en-us"
# TIME_ZONE = "UTC"
# USE_I18N = True
# USE_TZ = True
# STATIC_URL = "static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS_ALLOWED_ORIGINS = [
#     x.strip() for x in os.getenv(
#         "CORS_ALLOWED_ORIGINS",
#         "http://localhost:5173,http://127.0.0.1:5173"
#     ).split(",") if x.strip()
# ]
# CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
# APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

# #new ocr code
# # OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# # Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
# OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
# OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
# OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
# OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
# OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
# OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
# TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
# OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract").strip().lower()
# PRESCRIPTION_DRUGS_FILE = os.getenv("PRESCRIPTION_DRUGS_FILE", "").strip()



# DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
# FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
# REST_FRAMEWORK = {
#     "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
#     "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
#     # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
#     # (health, signup and signin do). The token is issued by /signin.
#     "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
#     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
#     "UNAUTHENTICATED_USER": None,
#     "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
#     "DEFAULT_THROTTLE_RATES": {
#         "auth": os.getenv("AUTH_RATE_LIMIT", "10/min"),
#         "password_reset": os.getenv("PASSWORD_RESET_RATE_LIMIT", "5/hour"),
#     },
#     # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
#     # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
#     "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
# }

# MAX_MEMBERS = 4
# TOKEN_LIMIT = 100
# # AI providers: credentials stay exclusively on the backend.
# AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
# AI_API_KEY = os.getenv("AI_API_KEY", "").strip()  # legacy alias
# OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or os.getenv("AI_API_KEY", "")).strip()
# OPENAI_MODEL = os.getenv("OPENAI_MODEL", os.getenv("AI_MODEL", "gpt-4o-mini")).strip()
# ANTHROPIC_API_KEY = (os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY", "")).strip()
# CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022").strip()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
# GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
# AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()  # legacy default
# OLLAMA_MODELS = os.getenv("OLLAMA_MODELS", "llama3.1:8b").strip()
# # For legacy OpenAI-compatible configurations, the URL is server-controlled.
# AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
# OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
# AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
# AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# # Avoid emitting request bodies or health information in application logs.
# # ---- Forgot password / email (all values come from .env; see docs/PASSWORD_RESET.md) ----
# def _env_bool(name, default="false"):
#     return os.getenv(name, default).strip().lower() == "true"

# EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend").strip()
# EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
# EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
# EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "false")
# EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "false" if EMAIL_USE_SSL else "true")  # Django forbids both
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
# EMAIL_TIMEOUT = 10  # seconds; a slow mail server must not hang the request
# DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "").strip() or EMAIL_HOST_USER or "no-reply@localhost"
# # Frontend page that shows the "new password / confirm password" form. The token is appended after "#".
# FRONTEND_PASSWORD_RESET_URL = os.getenv("FRONTEND_PASSWORD_RESET_URL", "http://localhost:5173/reset-password").strip()
# FRONTEND_DOCTOR_ACTIVATION_URL = os.getenv("FRONTEND_DOCTOR_ACTIVATION_URL", "http://localhost:5173/doctor-activate").strip()
# PASSWORD_RESET_TIMEOUT = max(int(os.getenv("PASSWORD_RESET_TIMEOUT", "300")), 1)  # seconds the link stays valid
# # Minimum gap between two reset emails for the same address (extra to the per-IP limit above).
# PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS = max(int(os.getenv("PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS", "60")), 0)

# LOGGING = {
#     "version": 1, "disable_existing_loggers": False,
#     "handlers": {"console": {"class": "logging.StreamHandler"}},
#     "root": {"handlers": ["console"], "level": "WARNING"},
# }


# # Frontend page that reads the emailed TOTP recovery token from the URL fragment.
# FRONTEND_TOTP_RECOVERY_URL = os.getenv("FRONTEND_TOTP_RECOVERY_URL", "http://localhost:5173/recover-totp").strip()

# # MedLife doctor-system administrator allowlists. Never expose these controls through public signup.
# FRONTEND_DOCTOR_INVITATION_URL = os.getenv("FRONTEND_DOCTOR_INVITATION_URL", "http://localhost:5173/doctor-invitation").strip()

# # Private application uploads are stored under the project media directory.
# MEDIA_URL = os.getenv("MEDIA_URL", "/media/").strip()
# MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BASE_DIR / "media")))
















# Purpose: Shared Django configuration, environment variables, installed apps, middleware, and PostgreSQL.
# Edit this file for shared settings and limits; do not put feature-specific business logic here.
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
if not SECRET_KEY or (not DEBUG and (
    len(SECRET_KEY) < 50 or "change-me" in SECRET_KEY.lower() or "unsafe-development" in SECRET_KEY.lower()
)):
    if DEBUG and not SECRET_KEY:
        SECRET_KEY = "unsafe-development-key-change-me"
    else:
        raise RuntimeError(
            "Set DJANGO_SECRET_KEY to a strong, unique value (at least 50 characters) "
            "when DJANGO_DEBUG is false."
        )
# Google OAuth 2.0 Web client ID used to verify incoming OpenID Connect ID tokens.
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
# Dedicated Fernet key for encrypting TOTP secrets; development can derive a fallback from SECRET_KEY.
TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", "").strip()
ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "corsheaders", "rest_framework",
    "apps.core", "apps.accounts", "apps.members", "apps.chat", "apps.ai", "apps.documents", "apps.doctors",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# PostgreSQL is intentionally the only configured database engine.

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    from urllib.parse import urlparse, unquote

    parsed = urlparse(DATABASE_URL)

    if parsed.scheme not in ("postgres", "postgresql"):
        raise RuntimeError(
            "DATABASE_URL must use PostgreSQL (postgresql://...)."
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(parsed.path.lstrip("/")),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname or "127.0.0.1",
            "PORT": parsed.port or 5432,
            "CONN_MAX_AGE": 60,
            "CONN_HEALTH_CHECKS": True,
        }
    }

else:
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    if not POSTGRES_PASSWORD:
        raise RuntimeError(
            f"POSTGRES_PASSWORD is empty. Check that the .env file exists at "
            f"{BASE_DIR / '.env'} and contains POSTGRES_PASSWORD=..."
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "medlife"),
            "USER": os.getenv("POSTGRES_USER", "medlife_user"),
            "PASSWORD": POSTGRES_PASSWORD,
            "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.getenv("POSTGRES_PORT", "5433"),
            "CONN_MAX_AGE": 60,
            "CONN_HEALTH_CHECKS": True,
        }
    }


# --- Cache (used by rate limiting) ------------------------------------------
# Default is per-process memory: fine for one dev process. With several gunicorn workers,
# set REDIS_URL (e.g. redis://127.0.0.1:6379/1) so the limits are shared by all workers.
REDIS_URL = os.getenv("REDIS_URL", "").strip()
if REDIS_URL:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic` in production (admin CSS/JS)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    x.strip() for x in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",") if x.strip()
]
CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x.strip()]
APPEND_SLASH = False  # Frontend routes intentionally mix trailing and non-trailing slashes.

#new ocr code
# OCR upload limits. The image is processed in memory/temporary upload storage and is not persisted.
# Keep Django's request-body limit slightly above the allowed image size for multipart overhead.
OCR_MAX_UPLOAD_MB = min(max(int(os.getenv("OCR_MAX_UPLOAD_MB", "5")), 1), 20)
OCR_MAX_UPLOAD_BYTES = OCR_MAX_UPLOAD_MB * 1024 * 1024
OCR_MAX_IMAGE_PIXELS = min(max(int(os.getenv("OCR_MAX_IMAGE_PIXELS", "25000000")), 1_000_000), 50_000_000)
OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
OCR_MIN_CONFIDENCE = min(max(float(os.getenv("OCR_MIN_CONFIDENCE", "65")), 0.0), 100.0)
OCR_TIMEOUT_SECONDS = min(max(int(os.getenv("OCR_TIMEOUT_SECONDS", "30")), 1), 90)
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract").strip().lower()
PRESCRIPTION_DRUGS_FILE = os.getenv("PRESCRIPTION_DRUGS_FILE", "").strip()



DATA_UPLOAD_MAX_MEMORY_SIZE = OCR_MAX_UPLOAD_BYTES + 64 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    # Every endpoint requires a valid signed bearer token unless a view opts out with AllowAny
    # (health, signup and signin do). The token is issued by /signin.
    "DEFAULT_AUTHENTICATION_CLASSES": ["apps.core.authentication.AccountTokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "apps.core.errors.detail_exception_handler",
    "DEFAULT_THROTTLE_RATES": {
        "auth": os.getenv("AUTH_RATE_LIMIT", "10/min"),
        "password_reset": os.getenv("PASSWORD_RESET_RATE_LIMIT", "5/hour"),
    },
    # How many reverse proxies sit in front of Django. 0 = use REMOTE_ADDR and ignore the
    # client-controlled X-Forwarded-For header (otherwise anyone can dodge rate limits by faking it).
    "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "0")),
}

MAX_MEMBERS = 4
TOKEN_LIMIT = 100
# AI providers: credentials stay exclusively on the backend.
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").strip().lower()
AI_API_KEY = os.getenv("AI_API_KEY", "").strip()  # legacy alias
OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or os.getenv("AI_API_KEY", "")).strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
ANTHROPIC_API_KEY = (os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY", "")).strip()
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
# Optional comma-separated model allowlists; defaults expose the configured model only.
OPENAI_MODELS = os.getenv("OPENAI_MODELS", OPENAI_MODEL).strip()
CLAUDE_MODELS = os.getenv("CLAUDE_MODELS", CLAUDE_MODEL).strip()
GEMINI_MODELS = os.getenv("GEMINI_MODELS", GEMINI_MODEL).strip()
AI_MODEL = os.getenv("AI_MODEL", "llama3.1:8b").strip()  # legacy/local default
OLLAMA_MODELS = os.getenv("OLLAMA_MODELS", "llama3.1:8b").strip()
# For legacy OpenAI-compatible configurations, the URL is server-controlled.
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip() or "https://api.openai.com/v1/chat/completions"
OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434").rstrip("/")
AI_TIMEOUT_SECONDS = min(max(int(os.getenv("AI_TIMEOUT_SECONDS", "120")), 1), 300)
AI_RATE_LIMIT_PER_MINUTE = max(int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10")), 1)

# Avoid emitting request bodies or health information in application logs.
# ---- Forgot password / email (all values come from .env; see docs/PASSWORD_RESET.md) ----
def _env_bool(name, default="false"):
    return os.getenv(name, default).strip().lower() == "true"

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend").strip()
EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "false")
EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "false" if EMAIL_USE_SSL else "true")  # Django forbids both
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = 10  # seconds; a slow mail server must not hang the request
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "").strip() or EMAIL_HOST_USER or "no-reply@localhost"
# Frontend page that shows the "new password / confirm password" form. The token is appended after "#".
FRONTEND_PASSWORD_RESET_URL = os.getenv("FRONTEND_PASSWORD_RESET_URL", "http://localhost:5173/reset-password").strip()
FRONTEND_DOCTOR_ACTIVATION_URL = os.getenv("FRONTEND_DOCTOR_ACTIVATION_URL", "http://localhost:5173/doctor-activate").strip()
PASSWORD_RESET_TIMEOUT = max(int(os.getenv("PASSWORD_RESET_TIMEOUT", "300")), 1)  # seconds the link stays valid
# Minimum gap between two reset emails for the same address (extra to the per-IP limit above).
PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS = max(int(os.getenv("PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS", "60")), 0)

LOGGING = {
    "version": 1, "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}


# Frontend page that reads the emailed TOTP recovery token from the URL fragment.
FRONTEND_TOTP_RECOVERY_URL = os.getenv("FRONTEND_TOTP_RECOVERY_URL", "http://localhost:5173/recover-totp").strip()

# MedLife doctor-system administrator allowlists. Never expose these controls through public signup.
FRONTEND_DOCTOR_INVITATION_URL = os.getenv("FRONTEND_DOCTOR_INVITATION_URL", "http://localhost:5173/doctor-invitation").strip()

# Private application uploads are stored under the project media directory.
MEDIA_URL = os.getenv("MEDIA_URL", "/media/").strip()
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BASE_DIR / "media")))

