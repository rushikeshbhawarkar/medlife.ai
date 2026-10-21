# MedLife Spatial UI Redesign: Changelog

Restyle of the whole visual layer into a Spatial UI (depth, glass materials, specular edges). Behaviour, API integration, state, routing, the theming mechanism and the folder structure were **not** changed.

**No files were deleted, renamed or added.** 42 files were modified (37 CSS, 2 JSX, 3 static HTML): +599 / −105 lines. Almost all changes are *appended* CSS blocks, so the existing minified files are not reformatted.

## A. Read this first: what is and is not verified

| Check | Status |
|---|---|
| `src/services/*`, `src/router/*`, `src/utils/*`, `src/data/*`, `main.jsx`, `index.html`, `package.json`, `package-lock.json`, `vite.config.js`, `.env`, `certs/*` byte-identical | **Verified**: `sha256sum -c`, 26 of 26 OK (manifest taken before any edit) |
| No file deleted/renamed/added | **Verified**: file lists of original ZIP and result are identical (excluding `dist/`, `node_modules/`) |
| JSX diffs contain only className / static-`style` changes | **Verified**: token-level diff (see §D) |
| `npm ci` | **Not run successfully**: the authoring sandbox has no npm registry access (`ENOTFOUND registry.npmjs.org`) |
| `npm run build` (Vite) and "no new warnings" | **Unverified**: could not run. Run `npm ci && npm run build` and expect the same pre-existing >500 kB chunk warning |
| Visual / responsive / contrast checks | **Verified, with a substitute for the build**: the *original compiled JS* from the ZIP's `dist/` was served with the *new CSS* (concatenated in the original bundle's cascade order) in headless Chromium. This exercises the real React app, but it is **not** a Vite build of the new source |
| Reset-password page | Rendered from its exact markup (the ZIP's `dist/` is stale and predates this page, so it was not available in the bundle). **Not run inside the app** |
| Backend flows (sign-in/TOTP, members CRUD, chat, scan, password reset) | **Not tested**: no backend. For visual checks only, the dashboard was fed canned responses by a test-time network stub in the test harness; nothing like that is in the delivered code. |
| `dist/` in this ZIP | **Omitted**: I could not rebuild it, and the shipped one is stale (no reset page, old CSS). Run `npm run build` to regenerate |

There is no lint script and no test suite in this project, so none was run.

## B. Frozen-file checksum evidence

```
$ sha256sum -c /tmp/frozen.sha256 | awk -F': ' '{print $2}' | sort | uniq -c
     26 OK
```
`src/services/*` (`api.js`, `buildQuery.js`, `demoReplies.js`, `demoStore.js`) was **not touched**. Backend contract (`VITE_API_BASE`, Bearer token key, all endpoints) is unchanged.

## C. File-by-file table

| File path | Action | Reason | Specific changes | Functionality impact | Backend impact | Verification |
|---|---|---|---|---|---|---|
| `public/about-us.html` | Modified (+48/−26) | Match spatial system (static page) | `<style>` replaced with tokens copied from `tokens.css`, floating glass header, near-opaque content panel, `prefers-color-scheme` fallback when `data-theme` is unset; one added script line applies the saved `medlife_palette`. Page content/markup untouched. | None (presentation only) | None | Rendered in browser (static page), 4 theme×palette, 375/1280, contrast audited |
| `public/privacy-policy.html` | Modified (+48/−26) | Same as About Us | Identical style block + palette script line. Content untouched. | None (presentation only) | None | Rendered in browser (static page), 4 theme×palette, 375/1280, contrast audited |
| `public/terms-of-use.html` | Modified (+48/−26) | Same as About Us | Identical style block + palette script line. Content untouched. | None (presentation only) | None | Rendered in browser (static page), 4 theme×palette, 375/1280, contrast audited |
| `src/components/Avatar/Avatar.css` | Modified (+2/−0) | Specular ring | Added inset highlight + ring + shadow. Inline size/gradient left untouched. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/components/Banner/Banner.css` | Modified (+6/−0) | Floating pill banner | Larger radius, edge/shadow, tinted fill; error text uses AA danger token. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/components/Button/Button.css` | Modified (+18/−0) | Pill buttons, specular edge, press compression | Pulled forward from Batch 2: glass ghost/outline, token-driven primary gradient (white text ≥4.5:1), hover lift under `@media(hover:hover)`, `:active` scale, 44 px min height on mobile, AA accent text on outline, darker `danger-solid`. All variants kept. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/components/Logo/Logo.css` | Modified (+7/−0) | Spatial logo mark, palette-following accent | Token-driven gradient + specular highlight; `.ai` uses AA accent text; `.logo-light span` (sidebar) now follows the palette instead of fixed pink. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/components/Modal/Modal.css` | Modified (+9/−0) | Floating dialog over dimmed, blurred scrim | Scrim `backdrop-filter` on the fixed backdrop itself; near-opaque dialog card (no blur-on-blur), edge light, deep shadow, ease-out scale-in, 44 px close target on mobile. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/components/Reveal/Reveal.css` | Modified (+2/−0) | Softer easing | Transition timing only; existing reduced-motion rule untouched. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/components/SectionHeader/SectionHeader.css` | Modified (+3/−0) | Glass eyebrow pill | Eyebrow becomes a glass pill with AA accent text; sentence case instead of all-caps. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/components/Spinner/Spinner.css` | Modified (+4/−0) | Palette-following glow, reduced-motion handling | Border/glow from accent tokens (was hard-coded red glow); slow the spin under `prefers-reduced-motion` instead of 0.01 ms jitter. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/auth/ResetPasswordPage.jsx` | Modified (+8/−7) | Replace static inline styles with classes; accessible success/danger colours | `<main>`→`reset-page`; inputs→`reset-input`; message `green`→`.reset-success` (`--sp-ok-text`), error `red`→`.reset-error` (`--sp-danger-text`); buttons get existing `btn` classes. CRLF line endings preserved. | None: className/`style` props only; handlers, bindings, attributes untouched | None | Diff-checked (class/style tokens only); rendered via reset-page markup harness |
| `src/features/auth/SignInModal/SignInModal.css` | Modified (+25/−0) | Glass inputs, focus glow, reset-password page styles | Inputs with ≥3:1 borders and accent focus halo; pill submit (`.button-primary` had no base styling before); QR on light plate (`.qr-plate`); `.signin-links`; new `.reset-*` classes for ResetPasswordPage (no CSS file of its own). | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/auth/SignInModal/SignInModal.jsx` | Modified (+3/−3) | Replace 3 static inline styles with classes (§2.3c) | QR image → `className="qr-plate"`; submit button gets `signin-submit`, `style` removed; links row → `className="signin-links"`. | None: className/`style` props only; handlers, bindings, attributes untouched | None | Diff-checked (class/style tokens only); sign-in modal rendered in real app bundle |
| `src/features/chat/Chat/Chat.css` | Modified (+5/−0) | Chat as its own floating pane | Near-opaque, **no blur** (long chats stay light on phones). | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/chat/ChatHeader/ChatHeader.css` | Modified (+9/−0) | Header + wrapping | Glass-tinted header; header now wraps so the download button is not clipped in the narrower dashboard pane. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/chat/Composer/Composer.css` | Modified (+10/−0) | Floating composer pill | Raised glass pill, accent focus halo, press compression, 44 px send on mobile. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/chat/EmptyChat/EmptyChat.css` | Modified (+7/−0) | Suggestion chips | Glass chips, hover lift on hover devices only, 44 px. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/chat/MessageBubble/MessageBubble.css` | Modified (+7/−0) | Distinct user/AI tint | Tinted fills + edge light, no per-bubble blur; user bubble gradient AA with white text. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/chat/MessageList/MessageList.css` | Modified (+2/−0) | Scroll container | Only `scrollbar-gutter:stable` (nothing else to restyle). | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/chat/QuestionMeter/QuestionMeter.css` | Modified (+5/−0) | Meter | Danger state (≥90) now also uses a striped fill, not tint alone; numeric label unchanged. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/chat/TypingIndicator/TypingIndicator.css` | Modified (+6/−0) | Typing bubble | Tinted bubble; dots static under reduced motion. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/dashboard/HealthTile/HealthTile.css` | Modified (+9/−0) | Dense data tiles, AA status badges | Near-opaque, no lift (not interactive). Badges keep their text labels and tones; text now AA in all combos. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/dashboard/MedicinesList/MedicinesList.css` | Modified (+5/−0) | Surface + AA chips | Chips use AA accent text. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/dashboard/MemberForm/MemberForm.css` | Modified (+6/−0) | Glass inputs, visible focus ring | ≥3:1 borders, 44 px fields, accent halo + outline on `:focus-visible` (old `:focus{outline:0}` removed focus ring). | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/dashboard/OnboardingEmpty/OnboardingEmpty.css` | Modified (+5/−0) | Floating empty-state slab | Glass slab with glow. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/dashboard/ProfileHeader/ProfileHeader.css` | Modified (+4/−0) | Floating pane | Near-opaque pane. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/dashboard/Sidebar/Sidebar.css` | Modified (+20/−0) | Floating dock | Detached dock with edge light (stays black via `--side-bg`), palette-following selected state and accents, mobile drawer keeps `.sidebar-open/.scrim-visible`, blurred scrim, 44 px targets. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/faq/FaqItem/FaqItem.css` | Modified (+7/−0) | Glass accordion | Open-state tint/edge, 44 px question target. `.faq-open` height animation untouched. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/features/FeatureCard/FeatureCard.css` | Modified (+6/−0) | Surface card with hover physics | Near-opaque surface; `translateY(-3px) scale(1.01)` only under `hover:hover`, on the inner card (not `.reveal`). | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/home/ChatPreview/ChatPreview.css` | Modified (+26/−0) | Suspended 3D workspace | Perspective-tilted glass card, ground shadow, floating chips (transform-only animation), blobs now palette-driven (blob B was fixed red), reduced-motion handling for new + existing pulse. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/home/CtaBanner/CtaBanner.css` | Modified (+4/−0) | Glowing glass slab | Accent-tinted dark slab with edge light and aura; white text ≥4.5:1 on every stop. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/home/Hero/Hero.css` | Modified (+9/−0) | Spatial hero typography | Glass eyebrow, accent glow on emphasised words, AA accent text, trust list contrast. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/howItWorks/StepCard/StepCard.css` | Modified (+6/−0) | Numbered glass | Same hover rule; token-driven numbered orb with halo ring. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/features/plans/PlanCard/PlanCard.css` | Modified (+9/−0) | Featured tier elevation + aura | Featured plan: higher elevation, accent ring/aura; `.popular-badge` kept; hover physics only on hover devices. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/layout/Footer/Footer.css` | Modified (+14/−0) | Floating glass footer panel | Panel on `.site-footer>.container`, 44 px social targets, link text 11.2→13 px, AA accent hover. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/layout/Navbar/Navbar.css` | Modified (+31/−0) | Detached floating glass bar with pill nav | Rules appended after the live copy (commented legacy block untouched): glass `.nav-row` pill, header background removed so `.navbar-scrolled` logic still works, inset nav pill with accent active-route pill, solid-glass mobile dropdown anchored to the pill (no nested blur), 44 px targets, compact ≤480 px rule. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/pages/DashboardPage/DashboardPage.css` | Modified (+48/−0) | Multi-pane spatial workspace + scanner restyle | Appended last (file has duplicated/commented blocks, left alone): floating glass top bar, 2-column pane grid ≥1280 px (profile/tiles full width, medicines+scanner left, chat right, sticky), 16–24 px gaps. Scanner: defines the `--surface/--text/--muted/--border/--accent` variables the old rules relied on, pill buttons, accent submit, 44 px targets. No transform/filter on `.dashboard-layout/main/content` (fixed modals and drawer depend on it). | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/pages/FaqPage/FaqPage.css` | Modified (+3/−0) | Dense answers on near-opaque pane | `.faq-list` surface restyle. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/styles/base.css` | Modified (+23/−0) | Ambient canvas, glass utilities, surface card | Appended: body canvas gradient (`--sp-canvas`), `.soft-hero` grid kept over ambient glow, `.card` near-opaque surface, `.sp-glass`/`.sp-glass-raised`/`.sp-solid` utilities with `@supports` and `prefers-reduced-transparency` fallbacks, `.theme-toggle` glass, text-wrap, selection, scrollbar thumb. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/styles/palette-overrides.css` | Modified (+17/−15) | Keep green palette in sync with restyled components | Edited existing green rules for `.btn-primary`, `.logo-mark/.preview-avatar/.account-initial/.step-number`, `.signin-form .button-primary`, `.cta-banner`, `.dashboard-sidebar`, `.member-selected`, composer/bubble button and `.scanner-error` so they use the same token-driven gradients as the base styles (no more hard-coded green gradients diverging from the new look). `.scanner-error` now uses the danger token instead of green. | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |
| `src/styles/tokens.css` | Modified (+65/−2) | Spatial design tokens | Appended `--sp-*` tokens (dark + light values) and AA-safe text tokens. Changed two existing values: `--text-muted` dark `#64748b`→`#8493aa`, light `#6b7280`→`#5b6472` (measured below 4.5:1 on canvas/glass). | None (presentation only) | None | Rendered in real app bundle with this CSS (see §E) |

### Files inspected and intentionally not modified
`HomePage.css`, `FeaturesPage.css`, `HowItWorksPage.css`, `PlansPage.css` (3-line stubs; page look comes from `base.css` and feature CSS); `RichText.css`, `HealthTiles.css` (grid only, nothing to restyle); `ConfirmRemoveModal.css` (stub; it renders through `Modal` + `Button`, both restyled; its inline `<style>` tag in the JSX was left alone); `PublicLayout.css` (min-height rule must stay); `styles/index.css`. Commented-out legacy blocks in `Navbar.css`, `DashboardPage.css`, `App.jsx`, `main.jsx`, `DashboardPage.jsx`, `TextScanner.jsx` were left alone.

**New files:** none. **Deleted files:** none.

## D. JSX edits (before / after)

`src/features/auth/SignInModal/SignInModal.jsx`
```diff
- <img src={challenge.qr} alt="Authenticator setup QR code" style={{display:'block',maxWidth:220,width:'100%',margin:'12px auto'}}/>
+ <img src={challenge.qr} alt="Authenticator setup QR code" className="qr-plate"/>
- <button className="button button-primary" disabled={busy} type="submit" style={{width:'100%',justifyContent:'center'}}>
+ <button className="button button-primary signin-submit" disabled={busy} type="submit">
- {!verify&&<p style={{display:'flex',gap:12,flexWrap:'wrap',justifyContent:'center'}}>
+ {!verify&&<p className="signin-links">
```
`src/features/auth/ResetPasswordPage.jsx` (CRLF preserved)
```diff
- <main style={{ maxWidth: 480, margin: '60px auto', padding: 24 }}>
+ <main className="reset-page">
- <p role="status" style={{ color: 'green' }}>{message}</p>
+ <p role="status" className="reset-success">{message}</p>
+ className="btn btn-primary"                (Return to MedLife button)
- style={{ display: 'block', width: '100%', padding: 12, margin: '8px 0 16px' }}   (x2)
+ className="reset-input"
- {error && <p role="alert" style={{ color: 'red' }}>{error}</p>}
+ {error && <p role="alert" className="reset-error">{error}</p>}
- <button type="submit" disabled={busy}>
+ <button type="submit" disabled={busy} className="btn btn-primary btn-lg btn-block">
```
Dynamic inline styles (`Avatar`, `Reveal`, `QuestionMeter`) were left untouched.

## E. Test results (executed vs not executed)

**Executed** (headless Chromium via Playwright, real app bundle + new CSS, see §A caveat):
- 5 public routes × 375 / 768 / 1280 px × {dark,light} × {red,green} + dashboard shell: **no horizontal overflow, no JS errors** (72 page loads in the final pass). 375 and 360 px verified for the navbar; **320 px still overflows by ~8–31 px** (see §G).
- Fixed-position integrity: sign-in modal, member form modal and sidebar scrim cover the full viewport at 375 and 1280 px (the "no transform/filter on a fixed element's ancestor" rule holds).
- Automated contrast audit: text colour vs the *actual rendered pixels behind it* (text hidden, backdrop sampled) for every visible text node, on 5 public routes, dashboard, sign-in modal and member form, 4 theme×palette combos, 375 and 1280 px. Real misses found and fixed during the audit: muted text, accent text on dark green, chip/nav label text, outline-button text, danger "Remove" button, sidebar avatar initial. **Remaining flagged items are exempt or artifacts**: the *disabled* "Coming soon" and "Scan and save document" buttons (WCAG exempts disabled controls) and page text behind an open modal's scrim.
- Reset page (both states) and the 3 static pages: no overflow, no contrast failures, 4 combos × 375/1280.
- Dashboard with API unreachable (requests aborted): shell renders, error banner shown, no mock data.

**Not executed / unverified:** Vite build and warnings; `npm ci`; keyboard focus-ring walkthrough (rings are styled but were not tabbed through, except that `:focus-visible` rules exist on all new controls); real-device checks (iOS/Android camera capture, Safari `backdrop-filter`); screen-reader behaviour; every backend flow listed in §A; dark/light × red/green screenshots were taken for all routes but only a subset was visually inspected by the author.

## F. Tokens introduced (`src/styles/tokens.css`)
`--sp-glass`, `--sp-glass-raised`, `--sp-glass-solid`, `--sp-blur`, `--sp-blur-heavy`, `--sp-edge`, `--sp-edge-top`, `--sp-shadow-1/2/3`, `--sp-radius-sm/md/lg/pill`, `--sp-ease`, `--sp-glow`, plus additions: `--sp-canvas` (ambient background), `--sp-accent-fill` (darkened accent so white text passes AA), `--sp-accent-text`, `--sp-danger-text`, `--sp-ok-text` (AA-safe text colours on glass). All colours derive from `--red-primary`/existing tokens via `color-mix()`, so `data-palette="green"` tints everything green. No existing token was renamed. **Two existing values changed**: `--text-muted` (dark + light), for contrast.

## G. Known limitations and decisions
- **Not built here.** Please run `npm ci && npm run build` and smoke-test before shipping.
- `color-mix()` and `backdrop-filter` are used heavily. Browsers without `color-mix()` (pre-2023) will lose glass tints. `backdrop-filter` has `@supports` and `prefers-reduced-transparency` fallbacks to opaque surfaces.
- Blurred layers are limited (navbar, hero card, footer, dashboard top bar, empty-state slab; none in chat bubbles/list). Modal dialog is near-opaque by design because it sits inside the blurred scrim.
- 320 px width: the dashboard and the navbar are tight; a few px of horizontal overflow remains there (the original also overflowed at 375 px in the navbar before the compact rule was added).
- Existing `prefers-reduced-motion` rule in `base.css` was left as is; it sets `animation-duration:.01ms` without limiting iterations. New animations are individually disabled under reduce, and the spinner is slowed instead.
- Member avatar colours are dynamic inline gradients (`Avatar`), so they stay red in the green palette, as before.
- Visual decisions you may want to revisit: eyebrow labels changed from all-caps to sentence case; footer link text enlarged 11.2→13 px; `.scanner-error` is now danger-coloured (it was green under the green palette); the previously unstyled `.button-primary` sign-in submit now looks like the primary button; `--text-muted` is lighter in dark mode.
- The three static pages: the theme script still defaults to dark (unchanged); `prefers-color-scheme` applies only when `data-theme` is unset (no-JS). One script line was added so the saved palette is honoured.
- The README mentions `.env.example`, which the ZIP does not ship (unchanged).

## H. How to run
```
npm ci
# set VITE_API_BASE in the existing .env (default http://localhost:8000/medlife)
npm run dev       # development
npm run build     # production build (regenerates dist/)
```
