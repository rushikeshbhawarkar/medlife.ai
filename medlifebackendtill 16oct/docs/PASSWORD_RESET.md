# Forgot password / reset password

## How it works (one minute)

1. User clicks **Forgot Password?** on the login page and enters their email.
2. `POST /medlife/password/forgot` always answers with the same message. If the account exists, an email with a link is sent.
3. The link opens the frontend reset page: `FRONTEND_PASSWORD_RESET_URL#token=<token>`.
4. The page sends the token and the new password to `POST /medlife/password/reset`. Django checks everything and changes the password.

**Token design (no database change, no migration).** The token is a Django-signed value (the same mechanism the project already uses for TOTP and access tokens) containing the account id and a short keyed fingerprint of the *current password hash*.

| Requirement | How it is met |
|---|---|
| Expires after 300 s | Server-side `signing.loads(max_age=PASSWORD_RESET_TIMEOUT)` |
| Account-specific, tamper-proof | HMAC signature over the payload with `SECRET_KEY` + a dedicated salt |
| Single use | The fingerprint changes when the password changes, so the used token no longer matches |
| Revoked by any other password change | Same fingerprint check |
| No raw token stored | Nothing is stored; the signature is the proof |
| Concurrent requests | `SELECT ... FOR UPDATE` on the account row inside a transaction; the second request waits, sees the new hash and is rejected |
| Token not in logs/URLs sent to servers | It sits after `#` (never sent by browsers); the app never logs it |

**TOTP is untouched.** Reset changes only `Account.password`. After a reset the user still needs password **and** authenticator code to sign in.

**Old sessions are signed out.** Access tokens now carry the same password fingerprint, so after a reset every earlier access token gets 401. Tokens issued *before this update* have no fingerprint; they keep working until their normal 7-day expiry (so deploying does not log anybody out). To make that strict later, change `if "pv" in payload and ...` to `if not hmac.compare_digest(str(payload.get("pv", "")), ...)` in `apps/core/authentication.py`.

## Files

| File | Change |
|---|---|
| `apps/accounts/tokens.py` | + salt and `password_fingerprint()` |
| `apps/accounts/services.py` | + token creation/validation, email sending, `request_password_reset`, `reset_password` |
| `apps/accounts/serializers.py` | + `PasswordResetConfirmSerializer` |
| `apps/accounts/views.py` / `urls.py` | + two public endpoints |
| `apps/core/throttling.py` | + `PasswordResetRateThrottle` |
| `apps/core/authentication.py` | access token carries/checks password fingerprint |
| `config/settings/base.py` | + email, reset URL, timeout, rate settings (all from `.env`, all with defaults) |
| `config/settings/prod.py` | refuses to start if `FRONTEND_PASSWORD_RESET_URL` is not https |
| `.env.example`, `docs/ENV_GUIDE.md` | new variables |
| `apps/accounts/tests/test_password_reset.py` | 25 new tests |
| `docs/frontend-password-reset/*.jsx` | reference UI (see below) |

No new Django app, no new dependency, **no migration** (`makemigrations --check` reports "No changes detected").

## `.env` variables

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_HOST_USER=no-reply@yourcompany.com
EMAIL_HOST_PASSWORD=<app password / SMTP credential>
DEFAULT_FROM_EMAIL=MedLife <no-reply@yourcompany.com>
FRONTEND_PASSWORD_RESET_URL=https://your-site.com/reset-password
PASSWORD_RESET_TIMEOUT=300
PASSWORD_RESET_RATE_LIMIT=5/hour
PASSWORD_RESET_EMAIL_COOLDOWN_SECONDS=60
```

The last two are optional extras (defaults shown). Your existing `.env` keeps working without them, but no email can be sent until `EMAIL_HOST*` are set.

## Configuring the company email account

Only the `.env` changes; no code. When the company changes provider, change these and restart:

| Variable | Change it when |
|---|---|
| `EMAIL_HOST`, `EMAIL_PORT` | provider changes (Gmail/Google Workspace `smtp.gmail.com:587`, Microsoft 365 `smtp.office365.com:587`, Zoho `smtp.zoho.com:587`, SendGrid `smtp.sendgrid.net:587`, Amazon SES `email-smtp.<region>.amazonaws.com:587`) |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | port 587 -> TLS `true`, SSL `false`; port 465 -> SSL `true`, TLS `false` (never both) |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | account or credential changes |
| `DEFAULT_FROM_EMAIL` | the visible sender; must be an address the provider lets you send as |

A normal mailbox password usually does **not** work for SMTP:
- **Google Workspace / Gmail:** turn on 2-Step Verification, then create an *App password* and use that (16 characters, no spaces).
- **Microsoft 365:** SMTP AUTH must be enabled for the mailbox (admin setting), and tenants with Security Defaults/MFA need an app password or an alternative relay; Microsoft is phasing out basic SMTP auth, so ask IT about the supported option.
- **SendGrid / SES / Mailgun:** user is a fixed name (`apikey` for SendGrid) or SMTP username; password is the API key/SMTP credential; the From domain must be verified.

Local development without a mail account: set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`. The email, including the link, is printed in the terminal running `runserver`. Never use this in production (it would write live reset links to logs).

If email delivery fails, the user still sees the generic success message (so attackers learn nothing) and the server console logs one line such as `Password reset email could not be sent (account id=3, SMTPAuthenticationError). Check the EMAIL_* settings.` Look there when emails do not arrive.

## Frontend

The ZIP contains only the Django backend, so no website pages could be changed. Two small React (Vite) reference components are provided in `docs/frontend-password-reset/`; copy them into your frontend and match your styling and login route:

- `ForgotPasswordModal.jsx`: opened by a **Forgot Password?** button on the login page; validates the email and calls `/password/forgot`.
- `ResetPasswordPage.jsx`: route `/reset-password`; reads `#token=...`, removes it from the address bar, has *Enter New Password*, *Confirm New Password*, **Reset Password**, shows a success message with a link to login.

The reset URL in `.env` must be the public address of that route. Add the frontend origin to `CORS_ALLOWED_ORIGINS` (already required for the rest of the app).

## API

### `POST /medlife/password/forgot`
```json
{ "email": "person@example.com" }
```
- `200` `{"ok": true, "detail": "If an account with that email exists, a password reset link has been sent."}`: same for known and unknown emails
- `400` `{"detail": "Enter a valid email address."}`: malformed or missing email
- `429` `{"detail": "Request was throttled. Expected available in N seconds."}`: more than `PASSWORD_RESET_RATE_LIMIT` per IP

### `POST /medlife/password/reset`
```json
{ "token": "<from the email link>", "new_password": "Brand-New#Pass9", "confirm_password": "Brand-New#Pass9" }
```
- `200` `{"ok": true, "detail": "Your password has been changed. Please sign in with your new password."}`
- `400` `{"detail": "..."}` for: expired link, invalid/tampered/already-used link, mismatch (`Passwords do not match.`), too short (< 6), too common, entirely numeric, same as email, same as current password, missing fields
- `429` after 10 requests/minute/IP (the existing `AUTH_RATE_LIMIT`)

A failed password check (mismatch, weak) does **not** use up the link; a successful reset does.

Password rules: at least 6 characters (same floor as sign-up), at most 128, not on Django's common-password list, not all digits, not equal to the email, not equal to the current password.

## Test with Postman

1. Set `.env` to the console email backend (or real SMTP), run `python manage.py runserver`.
2. `POST http://127.0.0.1:8000/medlife/password/forgot`, Body -> raw -> JSON `{"email":"<a registered email>"}`. Expect 200.
3. Copy the link from the terminal (or your inbox). The token is everything after `#token=` (URL-decode it if it contains `%` codes).
4. `POST http://127.0.0.1:8000/medlife/password/reset` with the JSON above. Expect 200.
5. Send step 4 again: expect 400 "invalid or has already been used".
6. `POST /medlife/signin` with the new password: expect 200 with `totp_required: true`; the old password gives 401.
7. Expiry: wait more than 5 minutes (or set `PASSWORD_RESET_TIMEOUT=20`) before step 4: expect 400 "has expired".

## Test the whole flow on the website

1. Login page -> **Forgot Password?** -> enter a registered email -> see the generic message.
2. Open the email, click the link; the reset page opens with the token already removed from the address bar.
3. Enter two different passwords -> "Passwords do not match". Enter a weak one (`123456`) -> error. Enter a good one -> success message with a login link.
4. Sign in with the new password, then the authenticator code as usual. Reopen the old email link: it is rejected.

## Run the tests

```
python manage.py test apps.accounts.tests.test_password_reset      # new tests
python manage.py test                                              # everything
```
Tests need PostgreSQL (the only configured database), a `TOTP_ENCRYPTION_KEY` in the environment (Django forces `DEBUG=False` while testing), and use Django's in-memory mail backend, so no real emails are sent.

## Known limitations

- Per-address cooldown and the per-IP limit use Django's cache; with several server workers set `REDIS_URL` so counters are shared (same advice as the existing rate limits).
- Emails are sent during the request, so a known address answers slightly slower than an unknown one. Moving sending to a background worker would remove that timing difference.
- A TOTP login challenge issued just before a reset stays valid for its own 5-minute life.
- Anyone who controls the user's mailbox can reset the password, but still needs the authenticator code to sign in.
