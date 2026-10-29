from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.core import signing
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.accounts.tokens import password_fingerprint
from apps.doctors.models import DoctorApplication, DoctorProfile


def bearer_for(account):
    token = signing.dumps(
        {"account_id": account.pk, "purpose": "access", "pv": password_fingerprint(account.password)},
        salt="medlife.account-token.v1",
        compress=True,
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class AccountRoleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient = Account.objects.create(email="patient-role@example.com", password="unused")
        self.admin = Account.objects.create(
            email="admin-role@example.com", password="unused", role=Account.Role.SUPER_ADMIN
        )
        self.patient_client = APIClient()
        self.patient_client.credentials(**bearer_for(self.patient))
        self.admin_client = APIClient()
        self.admin_client.credentials(**bearer_for(self.admin))

    def test_signup_ignores_client_supplied_privileged_role(self):
        response = self.client.post(
            "/medlife/signup",
            {"email": "new-patient@example.com", "password": "LongSecurePassword!45", "role": "super_admin"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.json())
        account = Account.objects.get(email="new-patient@example.com")
        self.assertEqual(account.role, Account.Role.PATIENT)

    def test_identity_returns_authoritative_role_and_dashboard(self):
        response = self.patient_client.get("/medlife/account/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], "patient")
        self.assertEqual(response.json()["dashboard"], "patient")
        self.assertEqual(response.json()["email"], self.patient.email)

        response = self.admin_client.get("/medlife/account/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], "super_admin")
        self.assertEqual(response.json()["dashboard"], "admin")

    def test_patient_cannot_access_super_admin_application_list(self):
        response = self.patient_client.get("/medlife/doctor/admin/applications/")
        self.assertEqual(response.status_code, 403)

    def test_patient_cannot_access_patient_data_as_another_role_or_mutate_role(self):
        response = self.admin_client.get("/medlife/getmember")
        self.assertEqual(response.status_code, 403)
        response = self.patient_client.get("/medlife/account/?role=super_admin")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], Account.Role.PATIENT)

    def test_super_admin_provisioning_refuses_second_designation(self):
        target = Account.objects.create(email="second-admin@example.com")
        with self.assertRaises(CommandError):
            call_command("provision_super_admin", target.email)
        target.refresh_from_db()
        self.assertEqual(target.role, Account.Role.PATIENT)

    def test_database_constraint_prevents_second_super_admin(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Account.objects.create(email="another-admin@example.com", role=Account.Role.SUPER_ADMIN)

    def test_pending_application_is_independent_of_patient_accounts(self):
        application = DoctorApplication.objects.create(
            email="pending-doctor@example.com", full_name="Test Doctor", specialty="General Medicine",
            qualifications="MBBS", registration_number="PENDING-ROLE-1",
        )
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.role, Account.Role.PATIENT)
        self.assertFalse(Account.objects.filter(email=application.email).exists())
        response = self.admin_client.get("/medlife/doctor/admin/applications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["applications"][0]["email"], application.email)

    def test_approval_creates_new_doctor_account_and_rejection_creates_none(self):
        from django.test import override_settings
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="MedLife <no-reply@medlife.test>"):
            application = DoctorApplication.objects.create(
                email="approved-doctor@example.com", full_name="Test Doctor", specialty="General Medicine",
                qualifications="MBBS", registration_number="APPROVE-ROLE-1",
            )
            response = self.admin_client.post(f"/medlife/doctor/admin/applications/{application.pk}/review/", {"decision": "approve"}, format="json")
            self.assertEqual(response.status_code, 200, response.json())
            doctor = Account.objects.get(email=application.email)
            self.assertEqual(doctor.role, Account.Role.DOCTOR)
            self.assertEqual(doctor.password, "")
            self.assertTrue(DoctorProfile.objects.get(account=doctor).doctor_id)
            self.assertEqual(self.patient.role, Account.Role.PATIENT)

            rejected = DoctorApplication.objects.create(
                email="rejected-doctor@example.com", full_name="Rejected Doctor", specialty="General Medicine",
                qualifications="MBBS", registration_number="REJECT-ROLE-1",
            )
            response = self.admin_client.post(f"/medlife/doctor/admin/applications/{rejected.pk}/review/", {"decision": "reject"}, format="json")
            self.assertEqual(response.status_code, 200, response.json())
            self.assertFalse(Account.objects.filter(email=rejected.email).exists())

    def test_doctor_activation_link_sets_password_once(self):
        import re
        from django.core import mail
        from django.test import override_settings
        from django.contrib.auth.hashers import check_password
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="MedLife <no-reply@medlife.test>", FRONTEND_DOCTOR_ACTIVATION_URL="http://localhost:5173/doctor-activate"):
            application = DoctorApplication.objects.create(
                email="activation-doctor@example.com", full_name="Activation Doctor", specialty="General Medicine",
                qualifications="MBBS", registration_number="ACTIVATE-ROLE-1",
            )
            response = self.admin_client.post(f"/medlife/doctor/admin/applications/{application.pk}/review/", {"decision": "approve"}, format="json")
            self.assertEqual(response.status_code, 200, response.json())
            token_match = re.search(r"#token=([^\s]+)", mail.outbox[-1].body)
            self.assertIsNotNone(token_match)
            token = token_match.group(1)
            activation = self.client.post("/medlife/doctor/activate-account/", {"token": token, "password": "SecureDoctorPass!55", "confirm_password": "SecureDoctorPass!55"}, format="json")
            self.assertEqual(activation.status_code, 200, activation.json())
            account = Account.objects.get(email=application.email)
            self.assertTrue(check_password("SecureDoctorPass!55", account.password))
            reused = self.client.post("/medlife/doctor/activate-account/", {"token": token, "password": "AnotherSecurePass!55", "confirm_password": "AnotherSecurePass!55"}, format="json")
            self.assertEqual(reused.status_code, 400)

    def test_patient_cannot_use_doctor_profile_endpoint(self):
        response = self.patient_client.get("/medlife/doctor/profile/")
        self.assertEqual(response.status_code, 403)


class SuperAdminProvisioningCommandTests(TestCase):
    def test_provisions_existing_account_without_creating_or_setting_password(self):
        account = Account.objects.create(email="initial-admin@example.com", password="")
        call_command("provision_super_admin", account.email)
        account.refresh_from_db()
        self.assertEqual(account.role, Account.Role.SUPER_ADMIN)
        self.assertEqual(account.password, "")
        self.assertEqual(Account.objects.filter(role=Account.Role.SUPER_ADMIN).count(), 1)

    def test_does_not_create_missing_target_account(self):
        with self.assertRaises(CommandError):
            call_command("provision_super_admin", "missing-admin@example.com")
        self.assertFalse(Account.objects.filter(email="missing-admin@example.com").exists())
