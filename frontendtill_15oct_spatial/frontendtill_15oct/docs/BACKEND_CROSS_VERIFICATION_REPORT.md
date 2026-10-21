# MedLife Backend Cross-Verification & API Audit Report

**Date:** October 2026  
**Auditor:** Antigravity Pairing Assistant  
**Backend Directory:** `medlifebackendtill 16oct` (Inspected strictly in read-only mode)  
**Frontend Directory:** `frontendtill_15oct_spatial/frontendtill_15oct`

---

## Executive Summary

A comprehensive source-level audit and cross-verification was conducted across the MedLife Django REST Framework backend and Vite/React frontend. The backend implementation was verified for:
1. Dynamic AI provider discovery and model selection (`apps/ai/`).
2. Doctor invitations and role verification (`apps/doctors/`).
3. Appointment booking, doctor access grants, and family member identification (`apps/doctors/`, `apps/members/`).
4. General security, secret management, session tokens, and caching architecture.

No backend files were modified during this inspection. Frontend adaptations have been strictly limited to matching the actual backend contracts, exposing server-verified AI providers, locking pending submissions, and surfacing error banners directly within modals.

---

## 1. Confirmed Backend Defects & Contract Mismatches

### Finding 1: `caller_email` Identity Assertion in Doctor Invitations Endpoint
- **Severity:** High
- **Verification Status:** Confirmed (Static Code & Logic Analysis)
- **Backend File & Location:** [`apps/doctors/views.py:1884-1886`](file:///c:/Users/rushi/OneDrive/Desktop/claude%20medlife/Oct_16/medlifebackend_updated_16oct/medlifebackendtill%2016oct/apps/doctors/views.py#L1884-L1886)
- **Relevant Function:** `admin_invitations(request)` / `caller_email(request)` in [`apps/core/identity.py:11-21`](file:///c:/Users/rushi/OneDrive/Desktop/claude%20medlife/Oct_16/medlifebackend_updated_16oct/medlifebackendtill%2016oct/apps/core/identity.py#L11-L21)

#### Description & Evidence
When a Super Admin invites a prospective physician, the frontend POSTs `{ "email": "<doctor_email>" }` to `/medlife/doctor/admin/invitations/` with the Super Admin's bearer token.
The view begins with:
```python
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def admin_invitations(request):
    caller_email(request)  # <--- DEFECT
    _require_staff(request.user, super_admin=True)
    ...
```
`caller_email(request)` checks if `request.data.get("email")` matches the authenticated caller's email (`request.user.email`). Because the prospective doctor's email is distinct from the Super Admin's account email, `caller_email` raises:
`PermissionDenied("The email does not match the signed-in account.")` (HTTP 403 Forbidden).

#### Impact
Super Admins cannot send doctor onboarding invitations through the API.

#### Frontend Workaround Status
Cannot be safely bypassed purely on the frontend without sending the admin's own email as the invitation recipient, which would incorrectly send the onboarding token to the admin rather than the prospective doctor. The frontend now displays this exact error inside the modal to make the cause explicit.

#### Recommended Backend Fix
Remove `caller_email(request)` from `admin_invitations()`. The subsequent call to `_require_staff(request.user, super_admin=True)` already guarantees that the caller is an authenticated Super Admin.

---

### Finding 2: Missing Database Primary Key in `/medlife/getmember` & PK Lookup in Appointment Booking
- **Severity:** High
- **Verification Status:** Confirmed (Database & Static Code Analysis)
- **Backend File & Location:** [`apps/doctors/views.py:1590-1593`](file:///c:/Users/rushi/OneDrive/Desktop/claude%20medlife/Oct_16/medlifebackend_updated_16oct/medlifebackendtill%2016oct/apps/doctors/views.py#L1590-L1593) & [`apps/members/serializers.py:117-126`](file:///c:/Users/rushi/OneDrive/Desktop/claude%20medlife/Oct_16/medlifebackend_updated_16oct/medlifebackendtill%2016oct/apps/members/serializers.py#L117-L126)
- **Relevant Functions:** `_member_for_owner(account, member_id)` & `member_to_frontend(member)`

#### Description & Evidence
1. The endpoint `POST /medlife/doctor/appointments/` resolves family members using:
   ```python
   def _member_for_owner(account, member_id):
       if getattr(account, "role", "") != Account.Role.PATIENT:
           raise PermissionDenied("Patient account access is required.")
       return get_object_or_404(FamilyMember, pk=member_id, account=account)
   ```
   It strictly queries by `pk=member_id` (database primary key integer).
2. However, the patient member endpoint `GET /medlife/getmember` serializes members via `member_to_frontend(member)`:
   ```python
   def member_to_frontend(member):
       return {
           "firstName": member.first_name,
           "lastName": member.last_name,
           "dob": member.dob,
           "gender": member.gender,
           ...
           # Primary key "id" / "pk" is omitted!
       }
   ```
3. Because the frontend never receives `id`, it falls back to parsing the account-relative slot index (`1` from `"member1"`).
4. In real databases with multiple users, `FamilyMember.pk` is an auto-incrementing integer across all accounts. For user `bhawarkarrushikesh@gmail.com`, their member is in slot 1 (`member1`), but holds database primary key `pk = 2`.
5. When the client sends `member_id: 1`, the query `FamilyMember.objects.get(pk=1, account="bhawarkarrushikesh@gmail.com")` fails with `Http404` (`"No FamilyMember matches the given query."`).

#### Impact
Patients whose member PK does not happen to match their 1-indexed slot number receive a 404 error when attempting to book an appointment or request online chat.

#### Frontend Workaround Status
The frontend now checks if existing grants (`doctor/access-grants/`) contain the real `member_id` mapped to the selected member name. If not yet resolved, it gracefully surfaces the error inside the modal rather than letting it fail silently behind the backdrop.

#### Recommended Backend Fix
In `apps/doctors/views.py`, update `_member_for_owner` to look up by either `pk` or `slot`:
```python
def _member_for_owner(account, member_id):
    if getattr(account, "role", "") != Account.Role.PATIENT:
        raise PermissionDenied("Patient account access is required.")
    try:
        val = int(member_id)
        qs = FamilyMember.objects.filter(account=account)
        member = qs.filter(pk=val).first() or qs.filter(slot=val).first()
        if member:
            return member
    except (TypeError, ValueError):
        pass
    raise Http404("No FamilyMember matches the given query.")
```
Additionally, include `"id": member.pk` in `apps/members/serializers.py:member_to_frontend`.

---

## 2. Dynamic AI Provider Implementation Cross-Verification

The backend AI subsystem was inspected against the intended multi-provider architecture:

| Verification Item | Backend State | Details / Evidence |
| :--- | :--- | :--- |
| **Provider Discovery Endpoint** | **Implemented** | `GET /medlife/providers/` exists in `apps/ai/urls.py` and returns `{"providers": [...]}`. |
| **Authentication Requirement** | **Implemented** | Protected by `PatientRolePermission`. Requires an authenticated Patient Bearer token. |
| **Supported Provider Identifiers** | **Implemented** | `"gemini"` (Google Gemini), `"claude"` (Anthropic Claude), `"openai"` (ChatGPT), `"local"` (Ollama), `"mock"` (Offline demo). |
| **Local Model Configuration** | **Implemented** | Reads `settings.OLLAMA_MODELS` (comma-separated, default `"llama3.1:8b"`). Exposes models array in `local` provider object. |
| **Chat Request Contract** | **Implemented** | `POST /medlife/chat/ask/` accepts `member_name`, `query`, optional `provider`, and optional `local_model`. |
| **Prompt Request Contract** | **Implemented** | `GET /medlife/prompt/` accepts query params `query`, `provider`, `local_model`. |
| **Credential Safety** | **Confirmed** | All API keys (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) remain strictly server-side in Django settings. |
| **Dynamic Switching** | **Confirmed** | `get_provider(provider_name, local_model)` dynamically instantiates the requested provider class. |
| **Unavailable Providers** | **Confirmed** | Providers without server-side keys are omitted from `GET /medlife/providers/`. Direct requests for unconfigured providers raise `ValidationError`. |

---

## 3. Potential Security & Reliability Risks

### Risk 1: In-Memory Cache in Production Multi-Worker Environments
- **Severity:** Medium
- **Location:** `config/settings/base.py` & `apps/ai/services.py:161-175`
- **Details:** The AI question rate limiter uses `cache.add()` and `cache.incr()`. If deployed with multiple Gunicorn/Uvicorn workers without configuring Redis or Memcached (falling back to Django's default `LocMemCache`), each worker maintains its own isolated rate-limit counter, allowing clients to exceed the configured question limit across workers.
- **Recommendation:** Ensure a shared Redis or Memcached cache is configured in `production.py`.

### Risk 2: Default Development Secret Key Guard
- **Severity:** Low (Mitigated in Production)
- **Location:** `config/settings/base.py:1895-1905`
- **Details:** In `DEBUG=True`, `SECRET_KEY` falls back to `"unsafe-development-key-change-me"`. However, in `DEBUG=False`, `base.py` strictly validates that `len(SECRET_KEY) >= 50` and does not contain placeholder strings, failing startup safely if unconfigured.

---

## 4. Frontend Integration Summary

The following frontend enhancements were made to achieve full compatibility with the backend:
1. **API Client (`src/services/api.js`):**
   - Added `getAIProviders()` mapping to `GET /medlife/providers/`.
   - Updated `askMemberAI(member_name, query, provider, local_model)` and `askAI(query, provider, local_model)` to transmit the selected provider and local model.
2. **AI Provider & Model Selector (`ChatHeader.jsx` & `ChatHeader.css`):**
   - Added compact, theme-compliant dropdown controls in the AI chat card header.
   - Dynamically populated strictly from `GET /medlife/providers/`.
   - Persists user preferences (`medlife_ai_provider`, `medlife_ai_model`) in `localStorage`.
3. **Modal Error Presentation (`PatientConsultationView.jsx` & `AdminPortalView.jsx`):**
   - Implemented inline modal error banners (`{modalError && <Banner variant="error">...}`), resolving the issue where errors were occluded behind dark modal backdrops.
   - Added `disabled={submitting}` locking to prevent duplicate request dispatching.
   - Enhanced member ID resolution to utilize existing access grant data where available.
