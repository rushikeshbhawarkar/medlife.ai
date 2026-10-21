# MedLife doctor consultation API

This feature extends the existing `Account`, `FamilyMember`, and medical-document records. It does not create a second login system. All authenticated routes use the existing MedLife bearer token.

## Configuration

Doctor invitations use the existing Django email configuration and `FRONTEND_DOCTOR_INVITATION_URL`. No Super Admin or reviewer email allowlist is used for authorization.

Provision the first Super Admin from an existing MedLife account after applying migrations:

```bash
python manage.py migrate
python manage.py provision_super_admin admin@example.com
```

Doctor application review and invitation management require the persisted `super_admin` role. The backend has no separate product reviewer role. See [ACCOUNT_ROLES.md](ACCOUNT_ROLES.md) for safe provisioning and deliberate transfer instructions.

## Routes

All paths below are prefixed with `/medlife`. Except for `GET /doctors/`, these routes require `Authorization: Bearer <access_token>`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/doctors/` | List approved, available doctors; optional `?specialty=cardiology` |
| GET/PATCH | `/doctor/profile/` | Read doctor profile or update availability, clinic and bio |
| POST | `/doctor/applications/` | Submit a doctor application |
| GET | `/doctor/applications/me/` | Read current account's latest application/profile status |
| GET | `/doctor/admin/applications/` | Super Admin list; optional `?status=pending` or `?status=all` |
| POST | `/doctor/admin/applications/<id>/review/` | Approve/reject an application |
| GET/POST | `/doctor/admin/invitations/` | Super Admin list/create invitations |
| POST | `/doctor/invitations/accept/` | Accept invitation and submit application |
| GET/POST | `/doctor/access-grants/` | Patient list/create record-sharing grants |
| POST | `/doctor/access-grants/<id>/revoke/` | Patient revoke a grant |
| GET | `/doctor/shared-records/<member_id>/` | Assigned doctor view currently authorized records |
| GET/POST | `/doctor/appointments/` | List appointments (`?role=patient` or `?role=doctor`) / patient request |
| POST | `/doctor/appointments/<id>/decision/` | Assigned doctor accept/reject request |
| POST | `/doctor/appointments/<id>/cancel/` | Patient or assigned doctor cancel an eligible appointment |
| POST | `/doctor/appointments/<id>/complete/` | Assigned doctor mark accepted appointment complete |
| GET/POST | `/doctor/appointments/<id>/notes/` | Patient view note; authorized assigned doctor create/update note |
| GET/POST | `/doctor/chat-requests/` | List requests (`?role=patient` or `?role=doctor`) / patient request chat |
| POST | `/doctor/chat-requests/<id>/decision/` | Assigned doctor accept/reject chat request |
| POST | `/doctor/chat-requests/<id>/cancel/` | Patient or assigned doctor cancel an eligible chat request |
| GET/POST | `/doctor/chat-requests/<id>/messages/` | Read/send text messages after acceptance and while consent is active |
| GET | `/doctor/notifications/` | List own notifications; `?unread=true` filters unread |
| POST | `/doctor/notifications/<id>/read/` | Mark own notification read |

## Example request bodies

### Apply as a doctor

```json
{
  "full_name": "Dr Example",
  "specialty": "General Medicine",
  "qualifications": "MBBS, MD",
  "registration_number": "REG-12345",
  "clinic_name": "Example Clinic",
  "bio": "General physician",
  "years_experience": 5
}
```

### Super Admin invite

```json
{"email": "doctor@example.com"}
```

Invitation email delivery must be configured. The invited doctor must sign in using the invited email, then submit the token and professional details to `/doctor/invitations/accept/`. Invitations expire after seven days. Invitation acceptance is not doctor approval.

### Patient request appointment

```json
{
  "member_id": 1,
  "doctor_id": 1,
  "preferred_at": "2027-01-15T10:30:00+05:30",
  "reason": "Routine consultation",
  "patient_note": "",
  "consent_scopes": ["profile", "documents", "consultation_notes"]
}
```

### Doctor accept appointment

```json
{
  "decision": "accept",
  "scheduled_at": "2027-01-15T11:00:00+05:30",
  "doctor_response": "Confirmed for 11 AM"
}
```

To reject, send `{"decision":"reject","doctor_response":"..."}`. An appointment request is not confirmed until accepted with a future schedule.

### Patient request online chat

```json
{
  "member_id": 1,
  "doctor_id": 1,
  "message": "I would like to discuss a recent health concern.",
  "consent_scopes": ["profile"]
}
```

### Record-sharing consent

```json
{
  "member_id": 1,
  "doctor_id": 1,
  "scopes": ["profile", "documents", "consultation_notes"]
}
```

Allowed scopes are `profile`, `documents`, and `consultation_notes`. The member must belong to the authenticated account. Patients can revoke a grant; subsequent doctor record reads and chat messaging are blocked when required consent is inactive.

## State and privacy rules

- Only approved and available doctors appear in the public directory.
- Application review, invitation creation, consent changes, medical-record access, consultation-note access/updates and doctor-chat message activity are audited.
- Doctors can access only their own requests and records covered by an active consent grant.
- Patient-facing notification text is deliberately generic and avoids diagnosis/record content.
- Chat is persisted text messaging polled through the API; this is not WebSocket/real-time push.
- Appointment requests are accepted/rejected by the assigned doctor. Exact duplicate accepted appointment times for the same doctor are rejected. Only accepted appointments can be completed.
- The invitation page and patient/doctor dashboards are frontend work and are not included in this backend-only update.

## Local setup and verification

1. Back up the database.
2. Configure the existing email settings and provision the single Super Admin using `provision_super_admin`.
3. Activate the same Python virtual environment used by the current backend.
4. Install the project's existing development dependencies if they are not already installed.
5. Run `python manage.py check`.
6. Run `python manage.py makemigrations --check --dry-run` to check model/migration consistency.
7. Run `python manage.py migrate`.
8. Run `python manage.py test apps.doctors apps.accounts apps.members apps.chat apps.ai apps.documents`.
9. Test the new routes with the examples above and an access token from the existing signin/Google signin flow.

The backend uses PostgreSQL by design. A successful Python syntax check alone does not prove database connectivity, migrations, SMTP delivery, Google token verification, OCR binaries/models, or a local Ollama server are working.
