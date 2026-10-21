<!-- # What changed in this version (and what deliberately did not)

**Not touched (so migrations stay safe):** every `models.py`, every `migrations/` folder, `urls.py` files, serializers, `.env` variable names. `makemigrations --check` reports "No changes detected" and `migrate` on an already-migrated database reports "No migrations to apply".

## Flaws found and fixed
| # | Severity | Flaw in the original | Fix | Files |
|---|---|---|---|---|
| 1 | Critical | Login tokens were issued but **never checked**. `/getmember`, `/addmember`, `/saveChat`, `/tokens/` etc. trusted a bare `?email=`: anyone knowing an email could read/edit that person's health profiles and chats. Any email also auto-created an account | DRF now authenticates every request with the bearer token and requires login by default (`/health/`, `/signup`, `/signin` stay public). The caller is the token's account; a sent `email` must match or gets 403; reads never create accounts | `config/settings/base.py`, `apps/core/identity.py`, `apps/accounts/views.py` |
| 2 | Critical | `/prompt/` was open to the internet: anyone could spend your OpenAI quota | Requires login (same default) | `config/settings/base.py` |
| 3 | High | Placeholder/default `DJANGO_SECRET_KEY` accepted everywhere. The key signs login tokens, so a guessable key = forgeable logins | `config.settings.prod` refuses to start with a missing/short/placeholder key. Dev is unchanged | `config/settings/prod.py` |
| 4 | High | `wsgi.py`/`asgi.py` defaulted to **dev** settings (DEBUG true by default): a server that forgot the setting ran in debug mode | They default to `config.settings.prod`. `manage.py` still defaults to dev | `config/wsgi.py`, `config/asgi.py` |
| 5 | High | No brute-force protection on `/signin` and `/signup` | Per-IP limit `AUTH_RATE_LIMIT` (default 10/min) -> 429 | `apps/core/throttling.py`, `apps/accounts/views.py` |
| 6 | Medium | AI rate limit was per IP (all users behind one proxy share an IP), non-atomic (parallel requests slip through), and per-process | Per account, atomic `add`+`incr`; optional shared Redis via `REDIS_URL`. Provider failures now logged by error type only (never prompts/keys) | `apps/ai/services.py`, `config/settings/base.py` |
| 7 | Medium | `editmember` saved the whole row from a stale read, which could overwrite `tokens_used` incremented a moment earlier (bypassing the 100-question cap) | Row-locked and writes only the profile columns | `apps/members/services.py` |
| 8 | Medium | Two simultaneous `saveChat` calls for one member could collide on the unique (member, position) key -> HTTP 500 | Member row is locked during the replace | `apps/chat/services.py` |
| 9 | Medium | DRF trusted the client's `X-Forwarded-For` header, so rate limits could be dodged by faking it | `NUM_PROXIES` (default 0 = use the real socket address) | `config/settings/base.py` |
| 10 | Medium | Production HTTPS settings incomplete: SSL redirect loops behind a proxy, admin has no CSS (no `STATIC_ROOT`), no CSRF trusted origins | `BEHIND_PROXY`, `CSRF_TRUSTED_ORIGINS`, WhiteNoise + `STATIC_ROOT`, referrer/frame headers | `config/settings/prod.py`, `base.py`, `requirements/prod.txt` |
| 11 | Medium | `docker-compose.yml` published PostgreSQL on **5432** while your `.env` uses **5433** (a common cause of "can't connect / migrate fails"); DB exposed on all interfaces; weak default password | Host port follows `POSTGRES_PORT` (5433), bound to 127.0.0.1, password required | `docker-compose.yml` |
| 12 | Low | `DATABASE_URL` without a port silently used 5433; no connection health check for persistent connections | Default 5432 (PostgreSQL standard); `CONN_HEALTH_CHECKS=True` | `config/settings/base.py` |
| 13 | Low | Test suite had a stale failing test (legacy account claim contradicted the code, which correctly blocks takeover) and no coverage of auth | Fixed; tests now 24 (were 15) covering auth, ownership, throttling, token reset bug | `apps/*/tests/`, `apps/core/tests/helpers.py` |
| 14 | Low | Zip shipped a Windows `venv/` (Python 3.14), `__pycache__`, and requirement ranges that could drift | Package excludes them; requirements state tested versions; `requirements.txt` convenience file | `requirements/*`, `.gitignore` |

## New optional `.env` variables (old `.env` works unchanged)
`AUTH_RATE_LIMIT`, `NUM_PROXIES`, `REDIS_URL`, `BEHIND_PROXY`, `CSRF_TRUSTED_ORIGINS` (see `docs/ENV_GUIDE.md`).

## Behavior change your frontend must handle
After `/signin`, store `access_token` and send `Authorization: Bearer <token>` on every other call (including `/prompt/`). On HTTP 401 send the user to the sign-in screen. Example:
```js
const token = localStorage.getItem("access_token");
fetch(`${import.meta.env.VITE_API_BASE}/getmember`, { headers: { Authorization: `Bearer ${token}` } });
```

## Known limits left as-is (need a product decision, not a code patch)
Stateless 7-day tokens without revocation/refresh; 6-character minimum password (matches the frontend form); 409 on `/signup` reveals registered emails; AI question is in the URL (`GET /prompt/?query=`); health data is stored unencrypted at the application layer; Django admin shows chat text to any staff user. -->






# What changed in this version (and what deliberately did not)

**Not touched (so migrations stay safe):** every `models.py`, every `migrations/` folder, `urls.py` files, serializers, `.env` variable names. `makemigrations --check` reports "No changes detected" and `migrate` on an already-migrated database reports "No migrations to apply".

## Flaws found and fixed
| # | Severity | Flaw in the original | Fix | Files |
|---|---|---|---|---|
| 1 | Critical | Login tokens were issued but **never checked**. `/getmember`, `/addmember`, `/saveChat`, `/tokens/` etc. trusted a bare `?email=`: anyone knowing an email could read/edit that person's health profiles and chats. Any email also auto-created an account | DRF now authenticates every request with the bearer token and requires login by default (`/health/`, `/signup`, `/signin` stay public). The caller is the token's account; a sent `email` must match or gets 403; reads never create accounts | `config/settings/base.py`, `apps/core/identity.py`, `apps/accounts/views.py` |
| 2 | Critical | `/prompt/` was open to the internet: anyone could spend your OpenAI quota | Requires login (same default) | `config/settings/base.py` |
| 3 | High | Placeholder/default `DJANGO_SECRET_KEY` accepted everywhere. The key signs login tokens, so a guessable key = forgeable logins | `config.settings.prod` refuses to start with a missing/short/placeholder key. Dev is unchanged | `config/settings/prod.py` |
| 4 | High | `wsgi.py`/`asgi.py` defaulted to **dev** settings (DEBUG true by default): a server that forgot the setting ran in debug mode | They default to `config.settings.prod`. `manage.py` still defaults to dev | `config/wsgi.py`, `config/asgi.py` |
| 5 | High | No brute-force protection on `/signin` and `/signup` | Per-IP limit `AUTH_RATE_LIMIT` (default 10/min) -> 429 | `apps/core/throttling.py`, `apps/accounts/views.py` |
| 6 | Medium | AI rate limit was per IP (all users behind one proxy share an IP), non-atomic (parallel requests slip through), and per-process | Per account, atomic `add`+`incr`; optional shared Redis via `REDIS_URL`. Provider failures now logged by error type only (never prompts/keys) | `apps/ai/services.py`, `config/settings/base.py` |
| 7 | Medium | `editmember` saved the whole row from a stale read, which could overwrite `tokens_used` incremented a moment earlier (bypassing the 100-question cap) | Row-locked and writes only the profile columns | `apps/members/services.py` |
| 8 | Medium | Two simultaneous `saveChat` calls for one member could collide on the unique (member, position) key -> HTTP 500 | Member row is locked during the replace | `apps/chat/services.py` |
| 9 | Medium | DRF trusted the client's `X-Forwarded-For` header, so rate limits could be dodged by faking it | `NUM_PROXIES` (default 0 = use the real socket address) | `config/settings/base.py` |
| 10 | Medium | Production HTTPS settings incomplete: SSL redirect loops behind a proxy, admin has no CSS (no `STATIC_ROOT`), no CSRF trusted origins | `BEHIND_PROXY`, `CSRF_TRUSTED_ORIGINS`, WhiteNoise + `STATIC_ROOT`, referrer/frame headers | `config/settings/prod.py`, `base.py`, `requirements/prod.txt` |
| 11 | Medium | `docker-compose.yml` published PostgreSQL on **5432** while your `.env` uses **5433** (a common cause of "can't connect / migrate fails"); DB exposed on all interfaces; weak default password | Host port follows `POSTGRES_PORT` (5433), bound to 127.0.0.1, password required | `docker-compose.yml` |
| 12 | Low | `DATABASE_URL` without a port silently used 5433; no connection health check for persistent connections | Default 5432 (PostgreSQL standard); `CONN_HEALTH_CHECKS=True` | `config/settings/base.py` |
| 13 | Low | Test suite had a stale failing test (legacy account claim contradicted the code, which correctly blocks takeover) and no coverage of auth | Fixed; tests now 24 (were 15) covering auth, ownership, throttling, token reset bug | `apps/*/tests/`, `apps/core/tests/helpers.py` |
| 14 | Low | Zip shipped a Windows `venv/` (Python 3.14), `__pycache__`, and requirement ranges that could drift | Package excludes them; requirements state tested versions; `requirements.txt` convenience file | `requirements/*`, `.gitignore` |

## New optional `.env` variables (old `.env` works unchanged)
`AUTH_RATE_LIMIT`, `NUM_PROXIES`, `REDIS_URL`, `BEHIND_PROXY`, `CSRF_TRUSTED_ORIGINS` (see `docs/ENV_GUIDE.md`).

## Behavior change your frontend must handle
After `/signin`, store `access_token` and send `Authorization: Bearer <token>` on every other call (including `/prompt/`). On HTTP 401 send the user to the sign-in screen. Example:
```js
const token = localStorage.getItem("access_token");
fetch(`${import.meta.env.VITE_API_BASE}/getmember`, { headers: { Authorization: `Bearer ${token}` } });
```

## Known limits left as-is (need a product decision, not a code patch)
Stateless 7-day tokens without revocation/refresh; 6-character minimum password (matches the frontend form); 409 on `/signup` reveals registered emails; AI question is in the URL (`GET /prompt/?query=`); health data is stored unencrypted at the application layer; Django admin shows chat text to any staff user.


## Image-to-text feature wiring (2026-10-13)

- Registered the existing `apps.documents` app and included its API routes under `/medlife/`.
- Added OCR settings with safe defaults and aligned Django's request-body limit with the configured upload limit.
- Added `Pillow` and `pytesseract` to runtime dependencies; the separate Tesseract executable is documented in `docs/OCR.md`.
- Updated the dependency-free `.env.example`, API documentation, migration guidance, and Windows setup instructions.
- Updated document API test setup to use the project's existing helper for TOTP-enabled authenticated test accounts.
- No new model or migration was required: the existing `ScannedDocument` model and `0001_initial` migration already store both original OCR output and editable description.


## Llama 3.1 and reviewed OCR-to-member integration

- Added `OllamaProvider` and provider-factory support for `AI_PROVIDER=ollama`; default target model is configured with `AI_MODEL=llama3.1:8b`.
- Made the existing OpenAI provider endpoint configurable through `AI_BASE_URL` and added `openai_compatible` as an alias for API services using the OpenAI Chat Completions format. Keys remain server-side.
- Raised the configurable provider timeout ceiling to 300 seconds to accommodate local models; no frontend API contract change is required for the provider switch.
- Connected the existing documents workflow to `FamilyMember.medical_description` only after the user confirms OCR text. Corrections remove the previous generated section until re-confirmed; deleting a scan removes its generated section while preserving other profile notes.
- Added provider adapter unit tests and OCR synchronization regression tests. No database schema change or migration is required.
- The OCR app, model, migration, routes, Pillow/pytesseract dependencies, and app registration were already present in the supplied archive; this change completes the missing data synchronization rather than duplicating the app.

- Added `docs/FRONTEND_INTEGRATION.md` describing the member-specific chat request and OCR upload/review/confirmation calls.


## Auth hardening update (16 Oct)
- `apps/accounts/views.py`: password sign-in now always requires TOTP (Google-linked accounts included); wrong TOTP login codes lock the account for 15 minutes after 5 failures (HTTP 429); `/password/change` emails the owner after success.
- `apps/accounts/services.py`: new `send_password_changed_email`.
- `apps/ai/services.py`: AI rate limit is keyed per account instead of per IP.
- `config/settings/prod.py`: refuses to start with incomplete SMTP settings or `BEHIND_PROXY=true` with `NUM_PROXIES=0`; warns when `REDIS_URL` is missing.
- Tests: `apps/accounts/tests/test_security_hardening.py` (new); `test_password_change.py` updated for the TOTP rule.
