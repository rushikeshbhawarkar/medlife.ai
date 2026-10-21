# Google Sign-In (backend)

MedLife accepts a Google OpenID Connect ID token at `POST /medlife/google/signin`. The frontend is not included in this backend change; it must obtain the ID token using Google's Identity Services client and post it to this endpoint.

## Google Cloud setup

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project and configure the Google Auth Platform / OAuth consent screen.
3. Create an OAuth client ID with application type **Web application**.
4. Add your frontend origins under **Authorized JavaScript origins** (for local development, typically `http://localhost:5173` and `http://127.0.0.1:5173`; use the actual deployed HTTPS origin in production).
5. Copy the **Client ID** into the backend environment as `GOOGLE_CLIENT_ID`.
6. Do not put a Google client secret in frontend code. This backend flow verifies a Google ID token, so it needs the Web client ID, not a client secret.

The backend's Google client ID must match the client ID used by the frontend to obtain the ID token.

## Environment and dependency

Add this to `.env`:

```dotenv
GOOGLE_CLIENT_ID=your-web-client-id.apps.googleusercontent.com
```

Install the updated dependencies:

```bash
pip install -r requirements.txt
```

Apply the migration:

```bash
python manage.py migrate
```

Restart the backend after changing `.env`. If `GOOGLE_CLIENT_ID` is empty, the endpoint returns HTTP 503 rather than accepting an unverified token.

## API contract

### `POST /medlife/google/signin`

Request JSON:

```json
{
  "id_token": "<Google ID token returned by Google Identity Services>"
}
```

The backend validates the token signature, expiry, issuer, and audience using Google's `google-auth` library. It also requires a Google subject (`sub`) and a verified email. Do not send a Google access token or a client secret in place of the ID token.

### Responses

- **New Google account or account needing TOTP setup:** HTTP 200 with `totp_setup_required: true`, `setup_token`, `qr_code`, and `manual_key`. The user must scan the QR code and call the existing `POST /medlife/totp/verify-setup` endpoint. No MedLife access token is issued until setup is verified.
- **Existing account with TOTP enabled:** HTTP 200 with `totp_required: true` and `challenge_token`. Submit the challenge and the current six-digit code to `POST /medlife/totp/verify-login`. Only that endpoint issues the normal MedLife access token.
- **Invalid ID token:** HTTP 401.
- **Missing server-side Google configuration or inability to retrieve Google's verification keys:** HTTP 503.
- **Missing or malformed `id_token`:** HTTP 400.

A Google-only account is created with an empty password; no Google password is ever collected by MedLife. Users can continue using Google and MedLife TOTP. Existing password hashes are not changed when a verified Google identity is linked to the same email.

## Account linking and safety

- The account's stable Google `sub` is stored in `Account.google_sub`, not the email address. Email must be verified by Google before it is used to find/link an account.
- If a different Google subject is already linked to the MedLife account, the endpoint rejects the login rather than silently replacing the link.
- If the stored Google subject is found but the verified email no longer matches the MedLife account email, sign-in is rejected. Resolve the account/email change through a deliberate support/account-linking flow rather than silently moving data.
- The existing mandatory MedLife TOTP policy is preserved. Google authentication does not directly issue an access token for a TOTP-enabled account.
- Serve the frontend and backend over HTTPS in production. Never log or persist the raw Google ID token.
- Configure the same `GOOGLE_CLIENT_ID` value across environments only where the same Google OAuth client is intended. Restrict OAuth origins to your real frontend origins.
