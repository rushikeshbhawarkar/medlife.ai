# MedLife doctor application workflow

## Intended lifecycle

1. Public patient signup remains the only account-creation facility.
2. `POST /medlife/doctor/applications/` accepts an unauthenticated application and does not create an Account.
3. A pending application is visible to Super Admins at `GET /medlife/doctor/admin/applications/`.
4. A Super Admin approves or rejects it through `POST /medlife/doctor/admin/applications/<id>/review/`.
5. Approval creates a separate `doctor` Account, an approved DoctorProfile, and a unique Doctor ID (`MLD...`). The existing patient account is never converted.
6. Approval email contains the Doctor ID and a single-use password-setup link valid for 24 hours. Rejection sends a decision email and creates no account.
7. The activation form submits `token`, `password`, and `confirm_password` to `POST /medlife/doctor/activate-account/`.
8. The doctor uses the shared sign-in page after activation. The backend role remains authoritative for dashboard routing.

## Application request

The public endpoint accepts JSON for text fields, or multipart form data when files are included. Text fields: `email`, `full_name`, `phone`, `address`, `specialty`, `qualifications`, `registration_number`, `registration_authority`, `clinic_name`, `bio`, and `years_experience`. For multipart requests, add up to 10 files using repeated `documents` fields and optional repeated `document_types` fields (`medical_registration`, `qualification`, `identity`, `other`). Each file must be 10 MB or smaller and have a PDF, JPG, JPEG, or PNG extension.

An email already attached to an account cannot be used for a new doctor application. This prevents application approval from converting an existing patient account. A person who wants both account types must keep them separate; the single Account model permits only one role per account.

## Document review

Application metadata includes document IDs and types. Authorized Super Admins can download a document through `GET /medlife/doctor/admin/applications/documents/<document_id>/`. The endpoint requires authentication and the persisted Super Admin role, and sends the file as a private download.

## Configuration

Set `FRONTEND_DOCTOR_ACTIVATION_URL` in `.env` to the frontend password-setup page. Development default: `http://localhost:5173/doctor-activate`. The emailed token is placed in the URL fragment, not a query parameter. Configure working SMTP settings for approval/rejection emails.

## Migrations and tests

Run `python manage.py migrate` to apply `doctors.0002_independent_doctor_applications`. Then run `python manage.py test apps.doctors.tests apps.accounts.tests.test_roles` in the project's configured Python environment.
