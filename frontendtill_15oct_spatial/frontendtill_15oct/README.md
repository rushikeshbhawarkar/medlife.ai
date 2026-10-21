# Medlife AI frontend

React 18 + Vite frontend using the existing public-page layout and member dashboard. It is wired to the production Django API; there is no demo-data fallback.

## Run locally
1. Install Node.js 18+.
2. Copy `.env.example` to `.env` and set `VITE_API_BASE` to the backend base URL (default `http://localhost:8000/medlife`).
3. Run `npm install`, then `npm run dev`.
4. Open the local URL Vite prints (normally `http://localhost:5173`).
5. Run `npm run build` to verify the production bundle.

The frontend does not configure the backend host, SMTP, CORS, or deployment networking. Those are backend/server settings. SMTP password reset works through the backend's `/password/forgot` endpoint; email delivery requires valid SMTP settings in the backend environment. On mobile, the scanner's **Open camera** input uses `capture="environment"`; camera support depends on browser/device permissions and typically requires HTTPS outside localhost.

## API / security
- Sign-up and sign-in follow the backend's authenticator-based TOTP setup and verification flow.
- Authenticated requests use the backend-issued Bearer token.
- Each member dashboard contains its own AI chat and text scanner. Chat uses `/chat/ask/` with the selected member's profile context; scans use `/documents/scan/` and saved documents are listed/deleted via the backend.
- Do not expose backend secrets in frontend environment variables. `VITE_API_BASE` is a public URL only.

## Useful files
- `src/services/api.js`: API base URL, auth, member, chat, and document endpoints.
- `src/features/auth/SignInModal/SignInModal.jsx`: sign-in, sign-up, authenticator verification, password reset request.
- `src/pages/DashboardPage/DashboardPage.jsx`: dashboard composition and theme controls.
- `src/features/dashboard/TextScanner.jsx`: scanner, mobile camera input, saved scans.
- `src/features/chat/Chat/Chat.jsx`: member-specific chat UI.
- `src/styles/`: global styles and design tokens.
