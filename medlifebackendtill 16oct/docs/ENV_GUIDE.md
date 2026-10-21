<!-- # The `.env` file: how it works and how to copy it safely

## What it is (plain English)

`.env` is a sticky note next to the code holding the settings that differ per computer or are secret (database password, secret key). The code never contains those values; it asks for them by name. The loader is one line in `config/settings/base.py`:

```python
load_dotenv(BASE_DIR / ".env")   # BASE_DIR = the backend/ folder (where manage.py is)
```

So the file **must** be at `backend/.env`, next to `manage.py`. Anywhere else, Django cannot see it.

## Variables

| Variable | Needed? | What it does | Default if missing |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | yes in real use | Signs sessions and admin cookies; keep secret | an unsafe dev key |
| `DJANGO_DEBUG` | no | `true` shows detailed errors (dev only; use `false` in production) | `false` |
| `DJANGO_ALLOWED_HOSTS` | no | Comma-separated hostnames Django will answer | `localhost,127.0.0.1` |
| `POSTGRES_DB` / `POSTGRES_USER` | no | Database name and user | `medlife` / `medlife_user` |
| `POSTGRES_PASSWORD` | **yes** (unless `DATABASE_URL` set) | Database password; Django stops with an error if empty | none |
| `POSTGRES_HOST` / `POSTGRES_PORT` | no | Where PostgreSQL runs | `127.0.0.1` / `5433` |
| `DATABASE_URL` | no | One-line alternative to the `POSTGRES_*` values. **If filled in, it wins** and `POSTGRES_*` are ignored | empty |
| `CORS_ALLOWED_ORIGINS` | no | Frontend addresses allowed to call the API | `http://localhost:5173,http://127.0.0.1:5173` |
| `AI_PROVIDER` | no | `mock`, `ollama`, `openai`, or `openai_compatible` | `mock` |
| `AI_API_KEY` | only for `openai` | Server-side AI key | empty |
| `AI_MODEL`, `AI_TIMEOUT_SECONDS`, `AI_RATE_LIMIT_PER_MINUTE` | no | Model name, request timeout (1–300 sec), and request limit | `llama3.1:8b`, `120`, `10` |
| `OLLAMA_BASE_URL` | no | Ollama server base URL, no `/api/chat` suffix | `http://127.0.0.1:11434` |
| `AI_BASE_URL` | no | Full OpenAI-compatible chat-completions endpoint | `https://api.openai.com/v1/chat/completions` |

### Optional variables added for production (older `.env` files keep working without them)

| Variable | What it does | Default |
|---|---|---|
| `AUTH_RATE_LIMIT` | Max `/signup` + `/signin` calls per IP, e.g. `10/min` | `10/min` |
| `NUM_PROXIES` | Reverse proxies in front of Django (needed for correct client IP) | `0` |
| `REDIS_URL` | Shared cache for rate limits across workers | empty (per-process memory) |
| `BEHIND_PROXY` | `true` if a proxy terminates HTTPS and sets `X-Forwarded-Proto` (prod only) | `false` |
| `CSRF_TRUSTED_ORIGINS` | https origins allowed to POST to `/admin/` | empty |
| `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS` | HTTPS redirect / HSTS (prod only) | `true`, `0` |

In production (`config.settings.prod`) `DJANGO_SECRET_KEY` becomes mandatory: 50+ characters and not a placeholder, or Django refuses to start.

Only **one** variable is truly mandatory in development (`POSTGRES_PASSWORD`, or `DATABASE_URL`). Everything else has a safe default, so a copied `.env` cannot break the app by omitting something.

## Copying the same `.env` to another machine or a new backend folder

Do this and nothing will break:

1. Copy the file **as is** (byte for byte) into the new `backend/` folder, next to `manage.py`. File name is exactly `.env` (not `.env.txt`; Windows Explorer can hide extensions).
2. Make sure PostgreSQL there matches the file: same user, password, database name, and **port** (`POSTGRES_PORT`).
3. `python manage.py migrate`, then `python manage.py runserver`.

No code edit is needed. The code only reads variables by name and never hardcodes values.

## Things that cause confusing problems

| Problem | Why | Fix |
|---|---|---|
| Changed `.env` but nothing changed | Django reads it only at startup | Stop and restart `runserver` |
| `.env` value ignored | A real environment variable with the same name already exists in your terminal; **it beats `.env`** | Remove it (`Remove-Item Env:POSTGRES_PASSWORD` in PowerShell) or close the terminal |
| Cannot connect to PostgreSQL | Port mismatch: (fixed in this version) `docker-compose.yml` now publishes PostgreSQL on `POSTGRES_PORT` | If you still have an old container from before, run `docker compose down` then `docker compose up -d db` (the data volume is kept) |
| `DJANGO_DEBUG` seems ignored | It is compared to the exact text `true` | Write `DJANGO_DEBUG=true` (no quotes or spaces) |
| Password with `#`, `$` or spaces breaks | `#` starts a comment in `.env` | Put the value in quotes, or use a URL-encoded `DATABASE_URL` |
| Odd characters at the start of the first line | Editor saved a BOM | Save as UTF-8 **without** BOM |
| Secrets pushed to Git | `.env` must stay ignored | `.gitignore` already lists `.env`; share `.env.example` instead (placeholders only) |

## Adding a new setting later (keeps copies safe)

1. In `config/settings/base.py`: `MY_SETTING = os.getenv("MY_SETTING", "safe-default")`. Always provide a default so older `.env` files keep working.
2. Add the name with a placeholder value to `.env.example`.
3. Add a row to the table above.
4. Never put real secrets in `.env.example`, code, or docs. -->









# The `.env` file: how it works and how to copy it safely

## What it is (plain English)

`.env` is a sticky note next to the code holding the settings that differ per computer or are secret (database password, secret key). The code never contains those values; it asks for them by name. The loader is one line in `config/settings/base.py`:

```python
load_dotenv(BASE_DIR / ".env")   # BASE_DIR = the backend/ folder (where manage.py is)
```

So the file **must** be at `backend/.env`, next to `manage.py`. Anywhere else, Django cannot see it.

## Variables

| Variable | Needed? | What it does | Default if missing |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | yes in real use | Signs sessions and admin cookies; keep secret | an unsafe dev key |
| `TOTP_ENCRYPTION_KEY` | yes in production | Dedicated Fernet key used to encrypt TOTP secrets; generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`; keep stable and backed up | empty in `.env.example`; development derives a fallback from `DJANGO_SECRET_KEY` |
| `DJANGO_DEBUG` | no | `true` shows detailed errors (dev only; use `false` in production) | `false` |
| `DJANGO_ALLOWED_HOSTS` | no | Comma-separated hostnames Django will answer | `localhost,127.0.0.1` |
| `POSTGRES_DB` / `POSTGRES_USER` | no | Database name and user | `medlife` / `medlife_user` |
| `POSTGRES_PASSWORD` | **yes** (unless `DATABASE_URL` set) | Database password; Django stops with an error if empty | none |
| `POSTGRES_HOST` / `POSTGRES_PORT` | no | Where PostgreSQL runs | `127.0.0.1` / `5433` |
| `DATABASE_URL` | no | One-line alternative to the `POSTGRES_*` values. **If filled in, it wins** and `POSTGRES_*` are ignored | empty |
| `CORS_ALLOWED_ORIGINS` | no | Frontend addresses allowed to call the API | `http://localhost:5173,http://127.0.0.1:5173` |
| `AI_PROVIDER` | no | `mock`, `ollama`, `openai`, or `openai_compatible` | `mock` |
| `AI_API_KEY` | only for `openai` | Server-side AI key | empty |
| `AI_MODEL`, `AI_TIMEOUT_SECONDS`, `AI_RATE_LIMIT_PER_MINUTE` | no | Model name, request timeout (1–300 sec), and request limit | `llama3.1:8b`, `120`, `10` |
| `OLLAMA_BASE_URL` | no | Ollama server base URL, no `/api/chat` suffix | `http://127.0.0.1:11434` |
| `AI_BASE_URL` | no | Full OpenAI-compatible chat-completions endpoint | `https://api.openai.com/v1/chat/completions` |

### Optional variables added for production (older `.env` files keep working without them)

| Variable | What it does | Default |
|---|---|---|
| `AUTH_RATE_LIMIT` | Max `/signup` + `/signin` calls per IP, e.g. `10/min` | `10/min` |
| `NUM_PROXIES` | Reverse proxies in front of Django (needed for correct client IP) | `0` |
| `REDIS_URL` | Shared cache for rate limits across workers | empty (per-process memory) |
| `BEHIND_PROXY` | `true` if a proxy terminates HTTPS and sets `X-Forwarded-Proto` (prod only) | `false` |
| `CSRF_TRUSTED_ORIGINS` | https origins allowed to POST to `/admin/` | empty |
| `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS` | HTTPS redirect / HSTS (prod only) | `true`, `0` |

In production (`config.settings.prod`) `DJANGO_SECRET_KEY` must be 50+ characters and not a placeholder, and `TOTP_ENCRYPTION_KEY` must be set; otherwise Django refuses to start. Do not rotate the TOTP encryption key without re-encrypting existing account secrets.

Only **one** variable is truly mandatory in development (`POSTGRES_PASSWORD`, or `DATABASE_URL`). Everything else has a safe default, so a copied `.env` cannot break the app by omitting something.

## Copying the same `.env` to another machine or a new backend folder

Do this and nothing will break:

1. Copy the file **as is** (byte for byte) into the new `backend/` folder, next to `manage.py`. File name is exactly `.env` (not `.env.txt`; Windows Explorer can hide extensions).
2. Make sure PostgreSQL there matches the file: same user, password, database name, and **port** (`POSTGRES_PORT`).
3. `python manage.py migrate`, then `python manage.py runserver`.

No code edit is needed. The code only reads variables by name and never hardcodes values.

## Things that cause confusing problems

| Problem | Why | Fix |
|---|---|---|
| Changed `.env` but nothing changed | Django reads it only at startup | Stop and restart `runserver` |
| `.env` value ignored | A real environment variable with the same name already exists in your terminal; **it beats `.env`** | Remove it (`Remove-Item Env:POSTGRES_PASSWORD` in PowerShell) or close the terminal |
| Cannot connect to PostgreSQL | Port mismatch: (fixed in this version) `docker-compose.yml` now publishes PostgreSQL on `POSTGRES_PORT` | If you still have an old container from before, run `docker compose down` then `docker compose up -d db` (the data volume is kept) |
| `DJANGO_DEBUG` seems ignored | It is compared to the exact text `true` | Write `DJANGO_DEBUG=true` (no quotes or spaces) |
| Password with `#`, `$` or spaces breaks | `#` starts a comment in `.env` | Put the value in quotes, or use a URL-encoded `DATABASE_URL` |
| Odd characters at the start of the first line | Editor saved a BOM | Save as UTF-8 **without** BOM |
| Secrets pushed to Git | `.env` must stay ignored | `.gitignore` already lists `.env`; share `.env.example` instead (placeholders only) |

## Adding a new setting later (keeps copies safe)

1. In `config/settings/base.py`: `MY_SETTING = os.getenv("MY_SETTING", "safe-default")`. Always provide a default so older `.env` files keep working.
2. Add the name with a placeholder value to `.env.example`.
3. Add a row to the table above.
4. Never put real secrets in `.env.example`, code, or docs.











# The `.env` file: how it works and how to copy it safely

## What it is (plain English)

`.env` is a sticky note next to the code holding the settings that differ per computer or are secret (database password, secret key). The code never contains those values; it asks for them by name. The loader is one line in `config/settings/base.py`:

```python
load_dotenv(BASE_DIR / ".env")   # BASE_DIR = the backend/ folder (where manage.py is)
```

So the file **must** be at `backend/.env`, next to `manage.py`. Anywhere else, Django cannot see it.

## Variables

| Variable | Needed? | What it does | Default if missing |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | yes in real use | Signs sessions and admin cookies; keep secret | an unsafe dev key |
| `TOTP_ENCRYPTION_KEY` | yes in production | Dedicated Fernet key used to encrypt TOTP secrets; generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`; keep stable and backed up | empty in `.env.example`; development derives a fallback from `DJANGO_SECRET_KEY` |
| `DJANGO_DEBUG` | no | `true` shows detailed errors (dev only; use `false` in production) | `false` |
| `DJANGO_ALLOWED_HOSTS` | no | Comma-separated hostnames Django will answer | `localhost,127.0.0.1` |
| `POSTGRES_DB` / `POSTGRES_USER` | no | Database name and user | `medlife` / `medlife_user` |
| `POSTGRES_PASSWORD` | **yes** (unless `DATABASE_URL` set) | Database password; Django stops with an error if empty | none |
| `POSTGRES_HOST` / `POSTGRES_PORT` | no | Where PostgreSQL runs | `127.0.0.1` / `5433` |
| `DATABASE_URL` | no | One-line alternative to the `POSTGRES_*` values. **If filled in, it wins** and `POSTGRES_*` are ignored | empty |
| `CORS_ALLOWED_ORIGINS` | no | Frontend addresses allowed to call the API | `http://localhost:5173,http://127.0.0.1:5173` |
| `AI_PROVIDER` | no | `mock`, `ollama`, `openai`, or `openai_compatible` | `mock` |
| `AI_API_KEY` | only for `openai` | Server-side AI key | empty |
| `AI_MODEL`, `AI_TIMEOUT_SECONDS`, `AI_RATE_LIMIT_PER_MINUTE` | no | Model name, request timeout (1–300 sec), and request limit | `llama3.1:8b`, `120`, `10` |
| `OLLAMA_BASE_URL` | no | Ollama server base URL, no `/api/chat` suffix | `http://127.0.0.1:11434` |
| `AI_BASE_URL` | no | Full OpenAI-compatible chat-completions endpoint | `https://api.openai.com/v1/chat/completions` |
| `TESSERACT_CMD` | no, unless Tesseract is not on PATH | Full path to the Tesseract executable | empty (uses PATH) |
| `OCR_LANGUAGES` | no | Tesseract language code(s), e.g. `eng` or `eng+hin` if language data is installed | `eng` |
| `OCR_MAX_UPLOAD_MB` | no | Maximum uploaded image size, clamped to 1–20 MB | `5` |
| `OCR_MAX_IMAGE_PIXELS` | no | Maximum decoded image pixel count, clamped to 1–50 million | `25000000` |
| `OCR_MIN_CONFIDENCE` | no | Mean OCR confidence below which a warning is returned | `65` |
| `OCR_TIMEOUT_SECONDS` | no | Per-image OCR time limit, clamped to 1–90 seconds | `30` |

### Optional variables added for production (older `.env` files keep working without them)

| Variable | What it does | Default |
|---|---|---|
| `AUTH_RATE_LIMIT` | Max `/signup` + `/signin` calls per IP, e.g. `10/min` | `10/min` |
| `NUM_PROXIES` | Reverse proxies in front of Django (needed for correct client IP) | `0` |
| `REDIS_URL` | Shared cache for rate limits across workers | empty (per-process memory) |
| `BEHIND_PROXY` | `true` if a proxy terminates HTTPS and sets `X-Forwarded-Proto` (prod only) | `false` |
| `CSRF_TRUSTED_ORIGINS` | https origins allowed to POST to `/admin/` | empty |
| `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS` | HTTPS redirect / HSTS (prod only) | `true`, `0` |

In production (`config.settings.prod`) `DJANGO_SECRET_KEY` must be 50+ characters and not a placeholder, and `TOTP_ENCRYPTION_KEY` must be set; otherwise Django refuses to start. Do not rotate the TOTP encryption key without re-encrypting existing account secrets.

Only **one** variable is truly mandatory in development (`POSTGRES_PASSWORD`, or `DATABASE_URL`). Everything else has a safe default, so a copied `.env` cannot break the app by omitting something.

## Copying the same `.env` to another machine or a new backend folder

Do this and nothing will break:

1. Copy the file **as is** (byte for byte) into the new `backend/` folder, next to `manage.py`. File name is exactly `.env` (not `.env.txt`; Windows Explorer can hide extensions).
2. Make sure PostgreSQL there matches the file: same user, password, database name, and **port** (`POSTGRES_PORT`).
3. `python manage.py migrate`, then `python manage.py runserver`.

No code edit is needed. The code only reads variables by name and never hardcodes values.

## Things that cause confusing problems

| Problem | Why | Fix |
|---|---|---|
| Changed `.env` but nothing changed | Django reads it only at startup | Stop and restart `runserver` |
| `.env` value ignored | A real environment variable with the same name already exists in your terminal; **it beats `.env`** | Remove it (`Remove-Item Env:POSTGRES_PASSWORD` in PowerShell) or close the terminal |
| Cannot connect to PostgreSQL | Port mismatch: (fixed in this version) `docker-compose.yml` now publishes PostgreSQL on `POSTGRES_PORT` | If you still have an old container from before, run `docker compose down` then `docker compose up -d db` (the data volume is kept) |
| `DJANGO_DEBUG` seems ignored | It is compared to the exact text `true` | Write `DJANGO_DEBUG=true` (no quotes or spaces) |
| Password with `#`, `$` or spaces breaks | `#` starts a comment in `.env` | Put the value in quotes, or use a URL-encoded `DATABASE_URL` |
| Odd characters at the start of the first line | Editor saved a BOM | Save as UTF-8 **without** BOM |
| Secrets pushed to Git | `.env` must stay ignored | `.gitignore` already lists `.env`; share `.env.example` instead (placeholders only) |

## Adding a new setting later (keeps copies safe)

1. In `config/settings/base.py`: `MY_SETTING = os.getenv("MY_SETTING", "safe-default")`. Always provide a default so older `.env` files keep working.
2. Add the name with a placeholder value to `.env.example`.
3. Add a row to the table above.
4. Never put real secrets in `.env.example`, code, or docs.


For Windows Tesseract installation and image-to-text API usage, see [OCR setup](OCR.md).

## Forgot-password / email variables

All are optional for the server to start, but password-reset emails are only delivered when the `EMAIL_*` values are correct. Full setup and provider notes: [Password reset](PASSWORD_RESET.md).

| Variable | Default | Meaning |
|---|---|---|
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` | Use `...console.EmailBackend` in development to print emails in the terminal |
| `EMAIL_HOST` / `EMAIL_PORT` | *(empty)* / `587` | SMTP server and port |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | `true` / `false` | STARTTLS (587) or implicit SSL (465); only one may be `true` |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | *(empty)* | SMTP login. Often an **app password**, not the mailbox password |
| `DEFAULT_FROM_EMAIL` | `EMAIL_HOST_USER` | Sender shown on the email |
| `FRONTEND_PASSWORD_RESET_URL` | `http://localhost:5173/reset-password` | Frontend reset page; **must be https in production** |
| `PASSWORD_RESET_TIMEOUT` | `300` | Seconds the link is valid |
| `PASSWORD_RESET_RATE_LIMIT` | `5/hour` | Reset requests per client IP |
| `PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS` | `60` | Minimum gap between emails to one address |
