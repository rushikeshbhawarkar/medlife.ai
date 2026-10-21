<!-- # API contract

All endpoints are mounted under `/medlife/`. **Authentication:** all endpoints except `/health/`, `/signup` and `/signin` need `Authorization: Bearer <access_token>` (from `/signin`). Missing/invalid/expired token: `401 {"detail":...}`. The `email` query/body field is optional now; if sent it must equal the token's email, else `403`. Accounts are never created implicitly by data endpoints.

Send and receive JSON except that the AI answer is a JSON-encoded string for compatibility with the existing client. Error responses use `{"detail":"..."}`.

## Accounts

### `POST /medlife/signup`
Body: `{"email":"person@example.com","password":"secret1"}` (password 6–128 characters). Creates the account, stores only a salted PBKDF2 hash of the password, and returns `201 {"ok":true,"email":"person@example.com"}`. Email is trimmed and lowercased. If the email already has a password: `409 {"detail":"An account with this email already exists. Please sign in."}`. An older email-only account (made before passwords existed) cannot be claimed by sign-up alone: `403 {"detail":"Email verification is required before setting a password."}` (this prevents account takeover). `/signup` and `/signin` are limited to `AUTH_RATE_LIMIT` (default 10/min per IP); beyond that: `429`.

### `POST /medlife/signin`
Same body. Returns `200 {"ok":true,"email":"...","access_token":"...","token_type":"Bearer","expires_in":604800}` when email and password match, otherwise `401 {"detail":"Incorrect email or password."}` (same message for unknown email and wrong password).

**Note:** these two routes have no trailing slash because the frontend calls `/signup` and `/signin` exactly.

## Members

### `GET /medlife/getmember?email=person@example.com`
Returns an object keyed by `member1` through `member4`. Empty accounts return `{}`.

### `POST /medlife/addmember`
Body: `{"email":"person@example.com","firstName":"Asha","lastName":"Patel","dob":"2000-01-01","gender":"Female","race":"","height":"5.5ft","weight":"60kg","a1c":"5.6","bloodPressure":"120/80","medicine":"Vitamin D","tokens":0}`. Returns `201 {"key":"member1"}`. Client-supplied `tokens` is ignored. A fifth profile returns 400 `Maximum of 4 members allowed per email.`

### `POST /medlife/editmember?email=person@example.com&member_name=member1`
Body uses the same profile fields and may include `email`; returns `{"ok":true}`. Token values are ignored.

### `POST /medlife/removemember?email=person@example.com&member_name=member1`
Returns `{"ok":true}` and cascades the member's chat history.

### `GET /medlife/tokens/?email=person@example.com&member_name=member1`
Increments the count atomically and returns `{"message":"1"}`. At 100, returns 400 `{"detail":"Question limit exceeded."}`.

## Chat

### `GET /medlife/fetchChat/?email=person@example.com&member_name=member1`
Returns `{"chat":[{"role":"user","text":"Hello","ts":1720000000123}]}`. `role` must be `user` or `ai`; `ts` is stored as the exact integer sent.

### `POST /medlife/saveChat/?email=person@example.com&member_name=member1`
Body: `{"chat":[{"role":"user","text":"Hello","ts":1720000000123}]}`. Atomically replaces all messages in list order.

## AI

### `GET /medlife/prompt/?query=...`
Accepts up to 4,000 characters and returns an answer string. Uses `AI_PROVIDER=mock` by default; `AI_PROVIDER=openai` requires a server-side `AI_API_KEY`. The endpoint needs a token and has an atomic per-account, per-minute counter (`AI_RATE_LIMIT_PER_MINUTE`, `429` when exceeded) and a provider timeout shorter than the frontend's 120 seconds.

## Shared

`GET /medlife/health/` returns `{"status":"ok"}`. `/admin/` is Django admin.

## Examples (PowerShell)

```powershell
curl.exe -X POST "http://localhost:8000/medlife/signup" -H "Content-Type: application/json" -d "{\"email\":\"person@example.com\",\"password\":\"secret1\"}"
curl.exe -X POST "http://localhost:8000/medlife/signin" -H "Content-Type: application/json" -d "{\"email\":\"person@example.com\",\"password\":\"secret1\"}"
# copy access_token from the reply, then:
curl.exe "http://localhost:8000/medlife/getmember" -H "Authorization: Bearer <access_token>"
curl.exe "http://localhost:8000/medlife/prompt/?query=What%20is%20A1C" -H "Authorization: Bearer <access_token>"
```

Keep `APPEND_SLASH=False`: the frontend intentionally calls some routes with slashes and some without, and Django's automatic redirect can lose POST bodies. -->








# API contract

All endpoints are mounted under `/medlife/`. Protected endpoints require `Authorization: Bearer <access_token>`. The normal access token is issued only after successful TOTP verification. `/health/`, `/signup`, `/signin`, and the TOTP enrollment/login verification endpoints are public but rate-limited. Missing/invalid/expired access token: `401 {"detail":"..."}`. The `email` query/body field is optional now; if sent it must equal the token's email, else `403`. Accounts are never created implicitly by data endpoints.

Send and receive JSON except that the AI answer is a JSON-encoded string for compatibility with the existing client. Error responses use `{"detail":"..."}`.

## Accounts and mandatory TOTP

### `POST /medlife/signup`
Body: `{"email":"person@example.com","password":"secret1"}` (password 6–128 characters). Creates an account with a salted Django password hash and an encrypted pending TOTP secret. Returns `201` with `totp_setup_required`, a short-lived `setup_token`, `setup_expires_in`, a `qr_code` PNG data URL, and `manual_key`. It does **not** return a normal access token. Email is trimmed and lowercased. A duplicate email returns `409 {"detail":"An account with this email already exists. Please sign in."}`.

### `POST /medlife/totp/verify-setup`
Body: `{"setup_token":"...","code":"123456"}`. Validates the first authenticator code, enables TOTP, moves the encrypted pending secret to the active-secret field, and returns the normal `access_token`. Setup tokens expire after 10 minutes.

### `POST /medlife/totp/setup`
Body: `{"email":"person@example.com","password":"secret1"}`. Restarts QR enrollment for an account whose TOTP setup is still incomplete. It requires the account password and rotates the pending secret. It refuses to reset TOTP for an already-enabled account.

### `POST /medlife/signin`
Body: `{"email":"person@example.com","password":"secret1"}`. Validates the password and returns a short-lived `challenge_token`, `totp_required: true`, and `challenge_expires_in`; it does **not** return an access token yet. Wrong/unknown credentials return `401 {"detail":"Incorrect email or password."}`. Accounts that have not completed TOTP setup must resume setup before signing in.

### `POST /medlife/totp/verify-login`
Body: `{"challenge_token":"...","code":"123456"}`. Validates the TOTP code and returns the normal bearer access token, valid for 7 days. Login challenges expire after 5 minutes. Setup and login tokens use signing salts distinct from normal access tokens and cannot authorize protected API requests. The same TOTP time-step is rejected for repeated login verification.

The `/signup` and `/signin` routes have no trailing slash because the frontend calls those exact paths. TOTP routes are `/totp/setup`, `/totp/verify-setup`, and `/totp/verify-login`. Public authentication/TOTP routes use `AUTH_RATE_LIMIT` (default `10/min` per IP); beyond that they return `429`.

**Frontend integration:** after signup, render the returned `qr_code` as an image and submit `setup_token` plus the user's six-digit code to `/totp/verify-setup`. On later login, store the `challenge_token` temporarily and submit it with the six-digit code to `/totp/verify-login`; only then store/use `access_token`. Never use the setup or challenge token as the application's bearer token.

**Key configuration:** production must set `TOTP_ENCRYPTION_KEY` to a dedicated Fernet key. Generate one with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Keep it secret and back it up securely; changing it without re-encrypting existing TOTP secrets makes those secrets unreadable. Development can derive a fallback from `DJANGO_SECRET_KEY`.

**Not included yet:** account recovery codes, a user-facing TOTP disable flow, and email verification are not implemented in this change.

## Members

### `GET /medlife/getmember?email=person@example.com`
Returns an object keyed by `member1` through `member4`. Empty accounts return `{}`.

### `POST /medlife/addmember`
Body: `{"email":"person@example.com","firstName":"Asha","lastName":"Patel","dob":"2000-01-01","gender":"Female","race":"","height":"5.5ft","weight":"60kg","a1c":"5.6","bloodPressure":"120/80","medicine":"Vitamin D","tokens":0}`. Returns `201 {"key":"member1"}`. Client-supplied `tokens` is ignored. A fifth profile returns 400 `Maximum of 4 members allowed per email.`

### `POST /medlife/editmember?email=person@example.com&member_name=member1`
Body uses the same profile fields and may include `email`; returns `{"ok":true}`. Token values are ignored.

### `POST /medlife/removemember?email=person@example.com&member_name=member1`
Returns `{"ok":true}` and cascades the member's chat history.

### `GET /medlife/tokens/?email=person@example.com&member_name=member1`
Increments the count atomically and returns `{"message":"1"}`. At 100, returns 400 `{"detail":"Question limit exceeded."}`.

## Chat

### `GET /medlife/fetchChat/?email=person@example.com&member_name=member1`
Returns `{"chat":[{"role":"user","text":"Hello","ts":1720000000123}]}`. `role` must be `user` or `ai`; `ts` is stored as the exact integer sent.

### `POST /medlife/saveChat/?email=person@example.com&member_name=member1`
Body: `{"chat":[{"role":"user","text":"Hello","ts":1720000000123}]}`. Atomically replaces all messages in list order.

## AI

### `GET /medlife/prompt/?query=...`
Accepts up to 4,000 characters and returns an answer string. Uses `AI_PROVIDER=mock` by default; `AI_PROVIDER=openai` requires a server-side `AI_API_KEY`. The endpoint needs a token and has an atomic per-account, per-minute counter (`AI_RATE_LIMIT_PER_MINUTE`, `429` when exceeded) and a provider timeout shorter than the frontend's 120 seconds.

## Shared

`GET /medlife/health/` returns `{"status":"ok"}`. `/admin/` is Django admin.

## Examples (PowerShell)

```powershell
curl.exe -X POST "http://localhost:8000/medlife/signup" -H "Content-Type: application/json" -d "{\"email\":\"person@example.com\",\"password\":\"secret1\"}"
# Read qr_code from the signup response and scan it with an authenticator app.
# Submit setup_token and the current six-digit code to /medlife/totp/verify-setup.
# On later logins, submit challenge_token and the current code to /medlife/totp/verify-login.
# Only use the access_token returned by a successful TOTP verification:
curl.exe "http://localhost:8000/medlife/getmember" -H "Authorization: Bearer <access_token>"
curl.exe "http://localhost:8000/medlife/prompt/?query=What%20is%20A1C" -H "Authorization: Bearer <access_token>"
```

Keep `APPEND_SLASH=False`: the frontend intentionally calls some routes with slashes and some without, and Django's automatic redirect can lose POST bodies.





























# API contract

All endpoints are mounted under `/medlife/`. Protected endpoints require `Authorization: Bearer <access_token>`. The normal access token is issued only after successful TOTP verification. `/health/`, `/signup`, `/signin`, and the TOTP enrollment/login verification endpoints are public but rate-limited. Missing/invalid/expired access token: `401 {"detail":"..."}`. The `email` query/body field is optional now; if sent it must equal the token's email, else `403`. Accounts are never created implicitly by data endpoints.

Send and receive JSON except that the AI answer is a JSON-encoded string for compatibility with the existing client. Error responses use `{"detail":"..."}`.

## Accounts and mandatory TOTP

### `POST /medlife/signup`
Body: `{"email":"person@example.com","password":"secret1"}` (password 6–128 characters). Creates an account with a salted Django password hash and an encrypted pending TOTP secret. Returns `201` with `totp_setup_required`, a short-lived `setup_token`, `setup_expires_in`, a `qr_code` PNG data URL, and `manual_key`. It does **not** return a normal access token. Email is trimmed and lowercased. A duplicate email returns `409 {"detail":"An account with this email already exists. Please sign in."}`.

### `POST /medlife/totp/verify-setup`
Body: `{"setup_token":"...","code":"123456"}`. Validates the first authenticator code, enables TOTP, moves the encrypted pending secret to the active-secret field, and returns the normal `access_token`. Setup tokens expire after 10 minutes.

### `POST /medlife/totp/setup`
Body: `{"email":"person@example.com","password":"secret1"}`. Restarts QR enrollment for an account whose TOTP setup is still incomplete. It requires the account password and rotates the pending secret. It refuses to reset TOTP for an already-enabled account.

### `POST /medlife/signin`
Body: `{"email":"person@example.com","password":"secret1"}`. Validates the password and returns a short-lived `challenge_token`, `totp_required: true`, and `challenge_expires_in`; it does **not** return an access token yet. Wrong/unknown credentials return `401 {"detail":"Incorrect email or password."}`. Accounts that have not completed TOTP setup must resume setup before signing in.

### `POST /medlife/totp/verify-login`
Body: `{"challenge_token":"...","code":"123456"}`. Validates the TOTP code and returns the normal bearer access token, valid for 7 days. Login challenges expire after 5 minutes. Setup and login tokens use signing salts distinct from normal access tokens and cannot authorize protected API requests. The same TOTP time-step is rejected for repeated login verification.

The `/signup` and `/signin` routes have no trailing slash because the frontend calls those exact paths. TOTP routes are `/totp/setup`, `/totp/verify-setup`, and `/totp/verify-login`. Public authentication/TOTP routes use `AUTH_RATE_LIMIT` (default `10/min` per IP); beyond that they return `429`.

**Frontend integration:** after signup, render the returned `qr_code` as an image and submit `setup_token` plus the user's six-digit code to `/totp/verify-setup`. On later login, store the `challenge_token` temporarily and submit it with the six-digit code to `/totp/verify-login`; only then store/use `access_token`. Never use the setup or challenge token as the application's bearer token.

**Key configuration:** production must set `TOTP_ENCRYPTION_KEY` to a dedicated Fernet key. Generate one with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Keep it secret and back it up securely; changing it without re-encrypting existing TOTP secrets makes those secrets unreadable. Development can derive a fallback from `DJANGO_SECRET_KEY`.

**Not included yet:** account recovery codes, a user-facing TOTP disable flow, and email verification are not implemented in this change.

## Members

### `GET /medlife/getmember?email=person@example.com`
Returns an object keyed by `member1` through `member4`. Empty accounts return `{}`.

### `POST /medlife/addmember`
Body: `{"email":"person@example.com","firstName":"Asha","lastName":"Patel","dob":"2000-01-01","gender":"Female","race":"","height":"5.5ft","weight":"60kg","a1c":"5.6","bloodPressure":"120/80","medicine":"Vitamin D","tokens":0}`. Returns `201 {"key":"member1"}`. Client-supplied `tokens` is ignored. A fifth profile returns 400 `Maximum of 4 members allowed per email.`

### `POST /medlife/editmember?email=person@example.com&member_name=member1`
Body uses the same profile fields and may include `email`; returns `{"ok":true}`. Token values are ignored.

### `POST /medlife/removemember?email=person@example.com&member_name=member1`
Returns `{"ok":true}` and cascades the member's chat history.

### `GET /medlife/tokens/?email=person@example.com&member_name=member1`
Increments the count atomically and returns `{"message":"1"}`. At 100, returns 400 `{"detail":"Question limit exceeded."}`.

## Chat

### `GET /medlife/fetchChat/?email=person@example.com&member_name=member1`
Returns `{"chat":[{"role":"user","text":"Hello","ts":1720000000123}]}`. `role` must be `user` or `ai`; `ts` is stored as the exact integer sent.

### `POST /medlife/saveChat/?email=person@example.com&member_name=member1`
Body: `{"chat":[{"role":"user","text":"Hello","ts":1720000000123}]}`. Atomically replaces all messages in list order.

## AI

### `GET /medlife/prompt/?query=...`
Accepts up to 4,000 characters and returns an answer string. Uses `AI_PROVIDER=mock` by default; `AI_PROVIDER=openai` requires a server-side `AI_API_KEY`. The endpoint needs a token and has an atomic per-account, per-minute counter (`AI_RATE_LIMIT_PER_MINUTE`, `429` when exceeded) and a provider timeout shorter than the frontend's 120 seconds.

## Shared

`GET /medlife/health/` returns `{"status":"ok"}`. `/admin/` is Django admin.

## Examples (PowerShell)

```powershell
curl.exe -X POST "http://localhost:8000/medlife/signup" -H "Content-Type: application/json" -d "{\"email\":\"person@example.com\",\"password\":\"secret1\"}"
# Read qr_code from the signup response and scan it with an authenticator app.
# Submit setup_token and the current six-digit code to /medlife/totp/verify-setup.
# On later logins, submit challenge_token and the current code to /medlife/totp/verify-login.
# Only use the access_token returned by a successful TOTP verification:
curl.exe "http://localhost:8000/medlife/getmember" -H "Authorization: Bearer <access_token>"
curl.exe "http://localhost:8000/medlife/prompt/?query=What%20is%20A1C" -H "Authorization: Bearer <access_token>"
```

Keep `APPEND_SLASH=False`: the frontend intentionally calls some routes with slashes and some without, and Django's automatic redirect can lose POST bodies.
