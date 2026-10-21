# MedLife Account Roles

MedLife has exactly three product roles, stored on `apps.accounts.models.Account.role`:

- `patient`: default for public email/password signup and new Google-linked accounts.
- `doctor`: assigned only by the authorized doctor-application approval workflow; the account must also have an approved `DoctorProfile`.
- `super_admin`: the single MedLife product administrator, separate from Django `is_staff` and `is_superuser`.

A database conditional unique constraint (`one_medlife_super_admin`) enforces **at most one** account with `role="super_admin"` on the configured PostgreSQL database. A deployment has **exactly one** only after the provisioning command succeeds.

## Provision the first Super Admin

1. Create and verify the account using the normal MedLife signup flow.
2. Apply migrations during a planned deployment window: `python manage.py migrate`.
3. Run the command using the account's exact email:

   ```bash
   python manage.py provision_super_admin admin@example.com
   ```

The command does not create accounts or set passwords. It refuses to promote a target if another Super Admin is already designated, if it detects multiple current Super Admins, or if the target has an approved doctor profile.

## Deliberate transfer

To transfer the role from the current Super Admin to another existing account, use:

```bash
python manage.py provision_super_admin new-admin@example.com --transfer-from current-admin@example.com
```

The exact current Super Admin email is required. The command demotes the old account to `patient` and promotes the target in one database transaction. Plan and review transfers carefully; the command does not set Django `is_staff` or `is_superuser`.

If the database already contains multiple Super Admin role values, the unique constraint will prevent adding it during migration; resolve conflicting data before deploying. Do not choose an administrator automatically. The migration backfills approved doctors as `doctor`, leaves all other existing accounts as `patient`, and does not create a Super Admin.

## Check role consistency

Run:

```bash
python manage.py check_account_roles
```

This command reports role/profile mismatches and the number of designated Super Admin accounts without changing data.

## Identity endpoint

`GET /medlife/account/` requires the existing bearer token and preserves `email` and `created_at`. It adds:

- `role`: `patient`, `doctor`, or `super_admin`.
- `dashboard`: `patient`, `doctor`, or `admin`.
- `doctor_status`: doctor profile status or the latest application status, if any.
- `doctor_application_status`: latest application status, if any.

Example patient response:

```json
{
  "email": "patient@example.com",
  "created_at": "2026-01-01T00:00:00+00:00",
  "role": "patient",
  "dashboard": "patient",
  "doctor_status": "pending",
  "doctor_application_status": "pending"
}
```

The timestamp is illustrative. A pending or rejected application does not grant doctor privileges. A role/profile mismatch fails closed for dashboard selection and doctor-specific APIs.

## Authorization boundaries

- Only `super_admin` accounts can review applications and manage doctor invitations.
- Doctor-specific operations require both `role="doctor"` and an approved `DoctorProfile`.
- Patient profile, AI, chat and document endpoints require `role="patient"` and retain existing ownership checks.
- Consent grants and record ownership continue to limit doctor access to medical records.
- Django Admin remains a separate technical maintenance interface. MedLife Super Admin provisioning does not set Django `is_staff` or `is_superuser`.

Legacy `MEDLIFE_SUPER_ADMIN_EMAILS` and `MEDLIFE_DOCTOR_REVIEWER_EMAILS` values no longer authorize anyone. Remove those entries from deployment environment configuration after upgrading. The backend does not use a separate product reviewer role.
