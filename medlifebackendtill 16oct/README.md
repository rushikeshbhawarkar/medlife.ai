<!-- <!-- # medlife.ai Django backend

This folder is the API backend for the existing React + Vite frontend. It uses Django REST Framework and PostgreSQL only. The frontend contract is intentionally kept compatible with its existing endpoint names, HTTP methods, query parameters, camelCase member fields, and chat message format.

## Windows setup (PowerShell or Command Prompt)

**Prerequisites:** Python 3.12 – 3.14, PostgreSQL 15+ (or Docker Desktop), and Node.js for the frontend.

### 1. Create a virtual environment and install packages

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
```

If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`, or use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current PowerShell window.

### 2. Start PostgreSQL

**Option A — Docker (easy local setup):**

Copy `.env.example` to `.env` first (or use your existing `.env`). The container is published on `POSTGRES_PORT` from `.env` (5433 in the supplied `.env`), bound to 127.0.0.1 only. From `backend` run:

```powershell
docker compose up -d db
```

**Option B — PostgreSQL installed locally:**

Open `psql` as a PostgreSQL administrator and run these commands (change the example password):

```sql
CREATE USER medlife_user WITH PASSWORD 'change-this-password' CREATEDB;  -- CREATEDB lets `manage.py test` build its temporary test database
CREATE DATABASE medlife OWNER medlife_user;
GRANT ALL PRIVILEGES ON DATABASE medlife TO medlife_user;
```

The backend never falls back to SQLite. If PostgreSQL is not reachable, Django commands that access the database will fail rather than silently create a different database.

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set a unique `DJANGO_SECRET_KEY` and the PostgreSQL credentials. For local development, configure PostgreSQL and the security keys in `.env`. To run local Llama 3.1 8B, install Ollama, run `ollama pull llama3.1:8b`, and set `AI_PROVIDER=ollama`, `AI_MODEL=llama3.1:8b`, and `OLLAMA_BASE_URL=http://127.0.0.1:11434`. To use OpenAI or another OpenAI-compatible API, see `docs/LLM_AND_OCR_SETUP.md`.

### 4. Apply migrations, create an admin, and run Django

```powershell
python manage.py migrate        # see docs/MIGRATIONS.md
python manage.py createsuperuser
python manage.py runserver 8000
```

API base: `http://localhost:8000/medlife`. Health check: `http://localhost:8000/medlife/health/`. Admin: `http://localhost:8000/admin/`.

### 5. Run the frontend

In the existing frontend folder, copy `.env.example` to `.env` and use:

```dotenv
VITE_API_BASE=http://localhost:8000/medlife
# VITE_DEMO=true
```

Then run:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173`. Leave `VITE_DEMO` unset to use the real API by default. If the backend cannot be reached, the existing network-error fallback switches the app to its local demo store. HTTP 4xx/5xx API errors are shown to the user and do not silently fall back to demo data.

### 6. Run automated tests

Ensure PostgreSQL is running and the `.env` database settings work, then:

```powershell
python manage.py test
```

Tests use the configured PostgreSQL database; no SQLite test database is configured. The concurrent token test uses separate connections to verify the 100-question cap.

## WHERE TO EDIT WHAT

| Change | Where |
|---|---|
| Shared settings, CORS, PostgreSQL, member/token limits | `config/settings/base.py` |
| Add a route for a feature | `apps/<feature>/urls.py`, then one include in `config/urls.py` |
| Change member profile fields | `apps/members/models.py`, `serializers.py`, then `python manage.py makemigrations` |
| Change the four-member cap or lowest-free ID | `apps/members/services.py` and `MAX_MEMBERS` in settings |
| Change the 100-question cap | `apps/members/services.py` and `TOKEN_LIMIT` in settings |
| Change sign-up / sign-in rules (password length, messages) | `apps/accounts/serializers.py`, `services.py` |
| Change email-only identity / later replace with login | `apps/core/identity.py` |
| Change chat persistence | `apps/chat/services.py` and `apps/chat/models.py` |
| Change AI health-safety instructions | `apps/ai/providers/system_prompt.py` |
| Change mock answers | `apps/ai/providers/mock.py` |
| Change AI model/provider | `apps/ai/providers/`, `AI_PROVIDER`, `AI_MODEL`; see `docs/LLM_AND_OCR_SETUP.md` |
| Inspect accounts, members, chat | Django admin at `/admin/` |
| Run API/database documentation | `docs/API.md`, `docs/DATABASE.md` |
| How to add features / change the database / env variables | `docs/FUTURE_UPDATES.md`, `docs/ENV_GUIDE.md` |

## Architecture

`React + Vite -> Django REST API -> feature services -> Django ORM -> PostgreSQL`

Views are thin HTTP adapters. Serializers validate incoming data, services own business rules and transactions, models define persisted data, and migrations track schema changes. AI calls are isolated behind a provider interface.

## Authentication (important for the frontend)

`POST /medlife/signin` returns `access_token`. **Every other endpoint except `/health/`, `/signup` and `/signin` now requires** the header `Authorization: Bearer <access_token>`; without it the API answers `401`. The caller is the account inside the token. A frontend-supplied `email` is no longer trusted: if it is sent it must match the token, otherwise `403`. See `docs/API.md`.

## Production checklist

| Item | Where |
|---|---|
| Real `DJANGO_SECRET_KEY` (50+ chars; it also signs login tokens). Production refuses to start with a placeholder | `.env` / server environment |
| `DJANGO_DEBUG=false`, real `DJANGO_ALLOWED_HOSTS`, real `CORS_ALLOWED_ORIGINS` | `.env` |
| Run with production settings: `DJANGO_SETTINGS_MODULE=config.settings.prod` (wsgi/asgi default to it) | server |
| `pip install -r requirements/prod.txt`, then `python manage.py collectstatic` | server |
| Behind nginx / a load balancer: `BEHIND_PROXY=true`, `NUM_PROXIES=1`, `CSRF_TRUSTED_ORIGINS=https://your-domain` | `.env` |
| Several workers: set `REDIS_URL` so rate limits are shared | `.env` |
| Run `python manage.py check --deploy` | server |

## Privacy and remaining production work

Health profiles and chat can contain sensitive data. Before real users: use HTTPS, a secret manager, encryption at rest, restricted database access, tested backups/restore, retention/deletion policies, monitoring without health payloads, and an explicit privacy/legal review. Known limits of the current design: login tokens are stateless 7-day tokens (no server-side revocation or refresh), the minimum password length is the frontend's 6 characters, `/signup` reveals whether an email is registered (409), and the AI question travels in the URL query string (`GET /prompt/?query=`), which can end up in proxy logs. -->









# medlife.ai Django backend

This folder is the API backend for the existing React + Vite frontend. It uses Django REST Framework and PostgreSQL only. The frontend contract is intentionally kept compatible with its existing endpoint names, HTTP methods, query parameters, camelCase member fields, and chat message format.

## Windows setup (PowerShell or Command Prompt)

**Prerequisites:** Python 3.12 – 3.14, PostgreSQL 15+ (or Docker Desktop), and Node.js for the frontend.

### 1. Create a virtual environment and install packages

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
```

If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`, or use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current PowerShell window.

### 2. Start PostgreSQL

**Option A — Docker (easy local setup):**

Copy `.env.example` to `.env` first (or use your existing `.env`). The container is published on `POSTGRES_PORT` from `.env` (5433 in the supplied `.env`), bound to 127.0.0.1 only. From `backend` run:

```powershell
docker compose up -d db
```

**Option B — PostgreSQL installed locally:**

Open `psql` as a PostgreSQL administrator and run these commands (change the example password):

```sql
CREATE USER medlife_user WITH PASSWORD 'change-this-password' CREATEDB;  -- CREATEDB lets `manage.py test` build its temporary test database
CREATE DATABASE medlife OWNER medlife_user;
GRANT ALL PRIVILEGES ON DATABASE medlife TO medlife_user;
```

The backend never falls back to SQLite. If PostgreSQL is not reachable, Django commands that access the database will fail rather than silently create a different database.

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set a unique `DJANGO_SECRET_KEY` and the PostgreSQL credentials. For local development, configure PostgreSQL and the security keys in `.env`. To run local Llama 3.1 8B, install Ollama, run `ollama pull llama3.1:8b`, and set `AI_PROVIDER=ollama`, `AI_MODEL=llama3.1:8b`, and `OLLAMA_BASE_URL=http://127.0.0.1:11434`. To use OpenAI or another OpenAI-compatible API, see `docs/LLM_AND_OCR_SETUP.md`.

### 4. Apply migrations, create an admin, and run Django

```powershell
python manage.py migrate        # see docs/MIGRATIONS.md
python manage.py createsuperuser
python manage.py runserver 8000
```

API base: `http://localhost:8000/medlife`. Health check: `http://localhost:8000/medlife/health/`. Admin: `http://localhost:8000/admin/`.

### 5. Run the frontend

In the existing frontend folder, copy `.env.example` to `.env` and use:

```dotenv
VITE_API_BASE=http://localhost:8000/medlife
# VITE_DEMO=true
```

Then run:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173`. Leave `VITE_DEMO` unset to use the real API by default. If the backend cannot be reached, the existing network-error fallback switches the app to its local demo store. HTTP 4xx/5xx API errors are shown to the user and do not silently fall back to demo data.

### 6. Run automated tests

Ensure PostgreSQL is running and the `.env` database settings work, then:

```powershell
python manage.py test
```

Tests use the configured PostgreSQL database; no SQLite test database is configured. The concurrent token test uses separate connections to verify the 100-question cap.

## WHERE TO EDIT WHAT

| Change | Where |
|---|---|
| Shared settings, CORS, PostgreSQL, member/token limits | `config/settings/base.py` |
| Add a route for a feature | `apps/<feature>/urls.py`, then one include in `config/urls.py` |
| Change member profile fields | `apps/members/models.py`, `serializers.py`, then `python manage.py makemigrations` |
| Change the four-member cap or lowest-free ID | `apps/members/services.py` and `MAX_MEMBERS` in settings |
| Change the 100-question cap | `apps/members/services.py` and `TOKEN_LIMIT` in settings |
| Change sign-up / sign-in rules (password length, messages) | `apps/accounts/serializers.py`, `services.py` |
| Change email-only identity / later replace with login | `apps/core/identity.py` |
| Change chat persistence | `apps/chat/services.py` and `apps/chat/models.py` |
| Change AI health-safety instructions | `apps/ai/providers/system_prompt.py` |
| Change mock answers | `apps/ai/providers/mock.py` |
| Change AI model/provider | `apps/ai/providers/`, `AI_PROVIDER`, `AI_MODEL`; see `docs/LLM_AND_OCR_SETUP.md` |
| Inspect accounts, members, chat | Django admin at `/admin/` |
| Run API/database documentation | `docs/API.md`, `docs/DATABASE.md` |
| How to add features / change the database / env variables | `docs/FUTURE_UPDATES.md`, `docs/ENV_GUIDE.md` |

## Architecture

`React + Vite -> Django REST API -> feature services -> Django ORM -> PostgreSQL`

Views are thin HTTP adapters. Serializers validate incoming data, services own business rules and transactions, models define persisted data, and migrations track schema changes. AI calls are isolated behind a provider interface.

## Authentication (important for the frontend)

Signup now requires TOTP enrollment before a normal access token is issued. `POST /medlife/signup` returns a QR code, a short-lived setup token, and a manual authenticator key; submit the first six-digit code to `/medlife/totp/verify-setup`. Later, `/medlife/signin` returns a restricted challenge token, and `/medlife/totp/verify-login` returns the normal `access_token` only after TOTP verification. Setup and challenge tokens must never be used as normal bearer tokens. Protected endpoints require `Authorization: Bearer <access_token>`. The caller is the account inside the token. A frontend-supplied `email` is no longer trusted: if it is sent it must match the token, otherwise `403`. See `docs/API.md`.

For production, configure a dedicated `TOTP_ENCRYPTION_KEY` in the environment (generate it with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`). Keep this key backed up securely; losing or changing it without re-encrypting the database secrets prevents users from generating valid TOTP codes.

## Production checklist

| Item | Where |
|---|---|
| Real `DJANGO_SECRET_KEY` (50+ chars; it also signs login tokens). Production refuses to start with a placeholder | `.env` / server environment |
| `DJANGO_DEBUG=false`, real `DJANGO_ALLOWED_HOSTS`, real `CORS_ALLOWED_ORIGINS` | `.env` |
| Run with production settings: `DJANGO_SETTINGS_MODULE=config.settings.prod` (wsgi/asgi default to it) | server |
| `pip install -r requirements/prod.txt`, then `python manage.py collectstatic` | server |
| Behind nginx / a load balancer: `BEHIND_PROXY=true`, `NUM_PROXIES=1`, `CSRF_TRUSTED_ORIGINS=https://your-domain` | `.env` |
| Several workers: set `REDIS_URL` so rate limits are shared | `.env` |
| Run `python manage.py check --deploy` | server |

## Privacy and remaining production work

Health profiles and chat can contain sensitive data. Before real users: use HTTPS, a secret manager, encryption at rest, restricted database access, tested backups/restore, retention/deletion policies, monitoring without health payloads, and an explicit privacy/legal review. Known limits of the current design: login tokens are stateless 7-day tokens (no server-side revocation or refresh), the minimum password length is the frontend's 6 characters, `/signup` reveals whether an email is registered (409), and the AI question travels in the URL query string (`GET /prompt/?query=`), which can end up in proxy logs.

----------------------------







# medlife.ai Django backend

This folder is the API backend for the existing React + Vite frontend. It uses Django REST Framework and PostgreSQL only. The frontend contract is intentionally kept compatible with its existing endpoint names, HTTP methods, query parameters, camelCase member fields, and chat message format.

## Windows setup (PowerShell or Command Prompt)

**Prerequisites:** Python 3.12 – 3.14, PostgreSQL 15+ (or Docker Desktop), and Node.js for the frontend.

### 1. Create a virtual environment and install packages

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
```

If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`, or use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current PowerShell window.

### 2. Start PostgreSQL

**Option A — Docker (easy local setup):**

Copy `.env.example` to `.env` first (or use your existing `.env`). The container is published on `POSTGRES_PORT` from `.env` (5433 in the supplied `.env`), bound to 127.0.0.1 only. From `backend` run:

```powershell
docker compose up -d db
```

**Option B — PostgreSQL installed locally:**

Open `psql` as a PostgreSQL administrator and run these commands (change the example password):

```sql
CREATE USER medlife_user WITH PASSWORD 'change-this-password' CREATEDB;  -- CREATEDB lets `manage.py test` build its temporary test database
CREATE DATABASE medlife OWNER medlife_user;
GRANT ALL PRIVILEGES ON DATABASE medlife TO medlife_user;
```

The backend never falls back to SQLite. If PostgreSQL is not reachable, Django commands that access the database will fail rather than silently create a different database.

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set a unique `DJANGO_SECRET_KEY` and the PostgreSQL credentials. For local development, configure PostgreSQL and the security keys in `.env`. To run local Llama 3.1 8B, install Ollama, run `ollama pull llama3.1:8b`, and set `AI_PROVIDER=ollama`, `AI_MODEL=llama3.1:8b`, and `OLLAMA_BASE_URL=http://127.0.0.1:11434`. To use OpenAI or another OpenAI-compatible API, see `docs/LLM_AND_OCR_SETUP.md`.

### 4. Apply migrations, create an admin, and run Django

```powershell
python manage.py migrate        # see docs/MIGRATIONS.md
python manage.py createsuperuser
python manage.py runserver 8000
```

API base: `http://localhost:8000/medlife`. Health check: `http://localhost:8000/medlife/health/`. Admin: `http://localhost:8000/admin/`.

### 5. Run the frontend

In the existing frontend folder, copy `.env.example` to `.env` and use:

```dotenv
VITE_API_BASE=http://localhost:8000/medlife
# VITE_DEMO=true
```

Then run:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173`. Leave `VITE_DEMO` unset to use the real API by default. If the backend cannot be reached, the existing network-error fallback switches the app to its local demo store. HTTP 4xx/5xx API errors are shown to the user and do not silently fall back to demo data.

### 6. Run automated tests

Ensure PostgreSQL is running and the `.env` database settings work, then:

```powershell
python manage.py test
```

Tests use the configured PostgreSQL database; no SQLite test database is configured. The concurrent token test uses separate connections to verify the 100-question cap.

## WHERE TO EDIT WHAT

| Change | Where |
|---|---|
| Shared settings, CORS, PostgreSQL, member/token limits | `config/settings/base.py` |
| Add a route for a feature | `apps/<feature>/urls.py`, then one include in `config/urls.py` |
| Change member profile fields | `apps/members/models.py`, `serializers.py`, then `python manage.py makemigrations` |
| Change the four-member cap or lowest-free ID | `apps/members/services.py` and `MAX_MEMBERS` in settings |
| Change the 100-question cap | `apps/members/services.py` and `TOKEN_LIMIT` in settings |
| Change sign-up / sign-in rules (password length, messages) | `apps/accounts/serializers.py`, `services.py` |
| Change email-only identity / later replace with login | `apps/core/identity.py` |
| Change chat persistence | `apps/chat/services.py` and `apps/chat/models.py` |
| Change AI health-safety instructions | `apps/ai/providers/system_prompt.py` |
| Change mock answers | `apps/ai/providers/mock.py` |
| Change AI model/provider | `apps/ai/providers/`, `AI_PROVIDER`, `AI_MODEL`; see `docs/LLM_AND_OCR_SETUP.md` |
| Inspect accounts, members, chat | Django admin at `/admin/` |
| Run API/database documentation | `docs/API.md`, `docs/DATABASE.md` |
| How to add features / change the database / env variables | `docs/FUTURE_UPDATES.md`, `docs/ENV_GUIDE.md` |

## Architecture

`React + Vite -> Django REST API -> feature services -> Django ORM -> PostgreSQL`

Views are thin HTTP adapters. Serializers validate incoming data, services own business rules and transactions, models define persisted data, and migrations track schema changes. AI calls are isolated behind a provider interface.

## Authentication (important for the frontend)

Signup now requires TOTP enrollment before a normal access token is issued. `POST /medlife/signup` returns a QR code, a short-lived setup token, and a manual authenticator key; submit the first six-digit code to `/medlife/totp/verify-setup`. Later, `/medlife/signin` returns a restricted challenge token, and `/medlife/totp/verify-login` returns the normal `access_token` only after TOTP verification. Setup and challenge tokens must never be used as normal bearer tokens. Protected endpoints require `Authorization: Bearer <access_token>`. The caller is the account inside the token. A frontend-supplied `email` is no longer trusted: if it is sent it must match the token, otherwise `403`. See `docs/API.md`.

For production, configure a dedicated `TOTP_ENCRYPTION_KEY` in the environment (generate it with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`). Keep this key backed up securely; losing or changing it without re-encrypting the database secrets prevents users from generating valid TOTP codes.

## Production checklist

| Item | Where |
|---|---|
| Real `DJANGO_SECRET_KEY` (50+ chars; it also signs login tokens). Production refuses to start with a placeholder | `.env` / server environment |
| `DJANGO_DEBUG=false`, real `DJANGO_ALLOWED_HOSTS`, real `CORS_ALLOWED_ORIGINS` | `.env` |
| Run with production settings: `DJANGO_SETTINGS_MODULE=config.settings.prod` (wsgi/asgi default to it) | server |
| `pip install -r requirements/prod.txt`, then `python manage.py collectstatic` | server |
| Behind nginx / a load balancer: `BEHIND_PROXY=true`, `NUM_PROXIES=1`, `CSRF_TRUSTED_ORIGINS=https://your-domain` | `.env` |
| Several workers: set `REDIS_URL` so rate limits are shared | `.env` |
| Run `python manage.py check --deploy` | server |

## Privacy and remaining production work

Health profiles and chat can contain sensitive data. Before real users: use HTTPS, a secret manager, encryption at rest, restricted database access, tested backups/restore, retention/deletion policies, monitoring without health payloads, and an explicit privacy/legal review. Known limits of the current design: login tokens are stateless 7-day tokens (no server-side revocation or refresh), the minimum password length is the frontend's 6 characters, `/signup` reveals whether an email is registered (409), and the AI question travels in the URL query string (`GET /prompt/?query=`), which can end up in proxy logs.






## Doctor consultation system

The backend-only doctor onboarding, appointment, patient-consent, chat-request, consultation-note and notification API is documented in [`docs/DOCTOR_SYSTEM.md`](docs/DOCTOR_SYSTEM.md). The three-role account model, Super Admin provisioning, migration/backfill behavior and identity response are documented in [`docs/ACCOUNT_ROLES.md`](docs/ACCOUNT_ROLES.md). Provision the single Super Admin using the existing account and `python manage.py provision_super_admin <existing-account-email>` before using invitation/review endpoints; legacy email allowlists no longer grant privileges.
