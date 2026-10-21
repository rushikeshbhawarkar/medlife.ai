from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.accounts.tokens import password_fingerprint
from django.core import signing
from apps.members.models import FamilyMember
from apps.doctors.models import Appointment, DoctorAccessGrant, DoctorApplication, DoctorProfile


def bearer_for(account):
    token = signing.dumps(
        {"account_id": account.pk, "purpose": "access", "pv": password_fingerprint(account.password)},
        salt="medlife.account-token.v1",
        compress=True,
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class DoctorApiTests(TestCase):
    def setUp(self):
        self.patient = Account.objects.create(email="patient@example.com", google_sub="google-patient")
        self.doctor_account = Account.objects.create(email="doctor@example.com", google_sub="google-doctor", role=Account.Role.DOCTOR)
        self.member = FamilyMember.objects.create(
            account=self.patient, slot=1, first_name="Asha", last_name="Test",
            height="165 cm", weight="60 kg", blood_pressure="120/80",
            medical_description="Patient-shared medical history",
        )
        self.doctor = DoctorProfile.objects.create(
            account=self.doctor_account, full_name="Dr Example", specialty="General Medicine",
            qualifications="MBBS", registration_number="REG-TEST-1",
            status=DoctorProfile.Status.APPROVED, is_available=True,
        )
        self.patient_client = APIClient()
        self.patient_client.credentials(**bearer_for(self.patient))
        self.doctor_client = APIClient()
        self.doctor_client.credentials(**bearer_for(self.doctor_account))

    def test_public_directory_lists_only_approved_available_doctors(self):
        response = APIClient().get("/medlife/doctors/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()["doctors"]], [self.doctor.pk])

    def test_patient_can_request_and_doctor_can_accept_appointment(self):
        preferred = (timezone.now() + timedelta(days=3)).isoformat()
        response = self.patient_client.post("/medlife/doctor/appointments/", {
            "member_id": self.member.pk,
            "doctor_id": self.doctor.pk,
            "preferred_at": preferred,
            "reason": "Routine consultation",
            "consent_scopes": ["profile", "documents", "consultation_notes"],
        }, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        appointment_id = response.json()["appointment"]["id"]
        self.assertTrue(DoctorAccessGrant.objects.filter(
            member=self.member, doctor=self.doctor, active=True,
        ).exists())

        scheduled = (timezone.now() + timedelta(days=3, hours=1)).isoformat()
        decision = self.doctor_client.post(
            f"/medlife/doctor/appointments/{appointment_id}/decision/",
            {"decision": "accept", "scheduled_at": scheduled},
            format="json",
        )
        self.assertEqual(decision.status_code, 200, decision.json())
        self.assertEqual(decision.json()["appointment"]["status"], Appointment.Status.ACCEPTED)

    def test_doctor_cannot_read_member_without_active_consent(self):
        response = self.doctor_client.get(f"/medlife/doctor/shared-records/{self.member.pk}/")
        self.assertEqual(response.status_code, 403)

    def test_chat_request_acceptance_and_messaging_require_active_consent(self):
        requested = self.patient_client.post("/medlife/doctor/chat-requests/", {
            "member_id": self.member.pk,
            "doctor_id": self.doctor.pk,
            "message": "I would like an online consultation.",
            "consent_scopes": ["profile"],
        }, format="json")
        self.assertEqual(requested.status_code, 201, requested.json())
        chat_id = requested.json()["chat_request"]["id"]
        accepted = self.doctor_client.post(
            f"/medlife/doctor/chat-requests/{chat_id}/decision/",
            {"decision": "accept"},
            format="json",
        )
        self.assertEqual(accepted.status_code, 200, accepted.json())
        sent = self.patient_client.post(
            f"/medlife/doctor/chat-requests/{chat_id}/messages/",
            {"text": "Hello doctor"},
            format="json",
        )
        self.assertEqual(sent.status_code, 201, sent.json())
        self.assertEqual(sent.json()["message"]["text"], "Hello doctor")

    def test_revoked_consent_blocks_doctor_record_access(self):
        grant = DoctorAccessGrant.objects.create(
            member=self.member, doctor=self.doctor, granted_by=self.patient,
            scopes=["profile"], active=True,
        )
        allowed = self.doctor_client.get(f"/medlife/doctor/shared-records/{self.member.pk}/")
        self.assertEqual(allowed.status_code, 200, allowed.json())
        revoked = self.patient_client.post(f"/medlife/doctor/access-grants/{grant.pk}/revoke/", {}, format="json")
        self.assertEqual(revoked.status_code, 200, revoked.json())
        blocked = self.doctor_client.get(f"/medlife/doctor/shared-records/{self.member.pk}/")
        self.assertEqual(blocked.status_code, 403)

    def test_public_application_creates_no_account_and_approval_creates_doctor_account(self):
        from django.test import override_settings
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="MedLife <no-reply@medlife.test>"):
            submitted = APIClient().post("/medlife/doctor/applications/", {
                "email": "new-applicant@example.com", "full_name": "Dr Applicant",
                "specialty": "Cardiology", "qualifications": "MBBS, MD",
                "registration_number": "REG-APP-1", "phone": "1234567890",
                "registration_authority": "State Medical Council", "years_experience": 3,
            }, format="json")
            self.assertEqual(submitted.status_code, 201, submitted.json())
            self.assertFalse(Account.objects.filter(email="new-applicant@example.com").exists())
            reviewer = Account.objects.create(email="reviewer@example.com", role=Account.Role.SUPER_ADMIN)
            reviewer_client = APIClient()
            reviewer_client.credentials(**bearer_for(reviewer))
            application_id = submitted.json()["application"]["id"]
            reviewed = reviewer_client.post(f"/medlife/doctor/admin/applications/{application_id}/review/", {"decision": "approve"}, format="json")
            self.assertEqual(reviewed.status_code, 200, reviewed.json())
            doctor_account = Account.objects.get(email="new-applicant@example.com")
            self.assertEqual(doctor_account.role, Account.Role.DOCTOR)
            profile = DoctorProfile.objects.get(account=doctor_account)
            self.assertTrue(profile.doctor_id.startswith("MLD"))
            self.assertEqual(doctor_account.password, "")
            self.assertTrue(doctor_account.doctor_activations.exists())

    def test_patient_account_cannot_be_converted_by_doctor_application(self):
        submitted = APIClient().post("/medlife/doctor/applications/", {
            "email": self.patient.email, "full_name": "Dr Patient", "specialty": "Cardiology",
            "qualifications": "MBBS", "registration_number": "REG-APP-2", "years_experience": 1,
        }, format="json")
        self.assertEqual(submitted.status_code, 400)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.role, Account.Role.PATIENT)
