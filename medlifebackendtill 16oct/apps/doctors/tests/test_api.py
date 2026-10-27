from datetime import time, timedelta
import hashlib
import secrets

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.accounts.tokens import password_fingerprint
from django.core import signing
from apps.members.models import FamilyMember
from apps.doctors.models import (
    Appointment, AppointmentRescheduleRequest, ConsultationNote, DoctorAccessGrant,
    DoctorApplication, DoctorAccountActivation, DoctorAvailabilitySlot, DoctorChatRequest,
    DoctorInvitation, DoctorProfile,
)


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

    def test_public_application_approval_defers_account_creation_until_activation(self):
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
            self.assertFalse(Account.objects.filter(email="new-applicant@example.com").exists())
            from apps.doctors.models import DoctorAccountActivation
            activation = DoctorAccountActivation.objects.get(application_id=application_id)
            self.assertEqual(activation.email, "new-applicant@example.com")
            self.assertIsNone(activation.account_id)
            self.assertEqual(activation.full_name, "Dr Applicant")


    def test_invitation_acceptance_does_not_require_patient_account_or_create_account_early(self):
        admin = Account.objects.create(email="invite-admin@example.com", role=Account.Role.SUPER_ADMIN)
        raw_token = secrets.token_urlsafe(32)
        invitation = DoctorInvitation.objects.create(
            email="invited-doctor@example.com",
            token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
            expires_at=timezone.now() + timedelta(days=7), invited_by=admin,
        )
        response = APIClient().post("/medlife/doctor/invitations/accept/", {
            "token": raw_token, "decision": "accept", "full_name": "Dr Invited",
            "specialty": "Dermatology", "qualifications": "MBBS", "registration_number": "REG-INV-1",
            "years_experience": 2,
        }, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, DoctorInvitation.Status.ACCEPTED)
        self.assertFalse(Account.objects.filter(email="invited-doctor@example.com").exists())
        activation = DoctorAccountActivation.objects.get(invitation=invitation)
        self.assertIsNone(activation.account_id)
        self.assertEqual(activation.full_name, "Dr Invited")

    def test_invitation_rejection_does_not_create_account(self):
        admin = Account.objects.create(email="reject-admin@example.com", role=Account.Role.SUPER_ADMIN)
        raw_token = secrets.token_urlsafe(32)
        invitation = DoctorInvitation.objects.create(
            email="reject-doctor@example.com",
            token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
            expires_at=timezone.now() + timedelta(days=7), invited_by=admin,
        )
        response = APIClient().post("/medlife/doctor/invitations/accept/", {
            "token": raw_token, "decision": "reject",
        }, format="json")
        self.assertEqual(response.status_code, 200, response.json())
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, DoctorInvitation.Status.REJECTED)
        self.assertFalse(Account.objects.filter(email="reject-doctor@example.com").exists())

    def test_doctor_account_is_created_only_after_password_and_totp_setup(self):
        from django.test import override_settings
        from apps.accounts.totp import decrypt_totp_secret
        import pyotp
        admin = Account.objects.create(email="activation-admin@example.com", role=Account.Role.SUPER_ADMIN)
        app = DoctorApplication.objects.create(
            email="activate-doctor@example.com", full_name="Dr Activate", specialty="Neurology",
            qualifications="MBBS", registration_number="REG-ACT-1", status=DoctorApplication.Status.APPROVED,
        )
        raw_token = secrets.token_urlsafe(32)
        activation = DoctorAccountActivation.objects.create(
            email=app.email, application=app, full_name=app.full_name, specialty=app.specialty,
            qualifications=app.qualifications, registration_number=app.registration_number,
            token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
            expires_at=timezone.now() + timedelta(hours=24),
        )
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="MedLife <no-reply@medlife.test>"):
            setup = APIClient().post("/medlife/doctor/activate-account/", {
                "token": raw_token, "action": "setup", "password": "StrongPassword123", "confirm_password": "StrongPassword123",
            }, format="json")
            self.assertEqual(setup.status_code, 200, setup.json())
            self.assertFalse(Account.objects.filter(email=app.email).exists())
            activation.refresh_from_db()
            secret = decrypt_totp_secret(activation.pending_totp_secret_encrypted)
            completed = APIClient().post("/medlife/doctor/activate-account/", {
                "token": setup.json()["token"], "action": "complete", "code": pyotp.TOTP(secret).now(),
            }, format="json")
            self.assertEqual(completed.status_code, 200, completed.json())
            doctor_account = Account.objects.get(email=app.email)
            self.assertEqual(doctor_account.role, Account.Role.DOCTOR)
            self.assertTrue(doctor_account.totp_enabled)
            self.assertTrue(DoctorProfile.objects.filter(account=doctor_account, status=DoctorProfile.Status.APPROVED).exists())
            activation.refresh_from_db()
            self.assertIsNotNone(activation.consumed_at)

    def test_patient_account_cannot_be_converted_by_doctor_application(self):
        submitted = APIClient().post("/medlife/doctor/applications/", {
            "email": self.patient.email, "full_name": "Dr Patient", "specialty": "Cardiology",
            "qualifications": "MBBS", "registration_number": "REG-APP-2", "years_experience": 1,
        }, format="json")
        self.assertEqual(submitted.status_code, 400)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.role, Account.Role.PATIENT)

    def test_doctor_dashboard_overview_returns_appointment_and_chat_counts(self):
        response = self.doctor_client.get("/medlife/doctor/dashboard/")
        self.assertEqual(response.status_code, 200, response.json())
        self.assertIn("pending_appointment_requests", response.json()["counts"])
        self.assertIn("pending_chat_requests", response.json()["counts"])

    def test_doctor_can_manage_weekly_availability_slots(self):
        response = self.doctor_client.post("/medlife/doctor/availability/", {
            "weekday": 1, "start_time": "09:00", "end_time": "12:00",
        }, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(DoctorAvailabilitySlot.objects.filter(doctor=self.doctor).count(), 1)
        overlap = self.doctor_client.post("/medlife/doctor/availability/", {
            "weekday": 1, "start_time": "11:00", "end_time": "13:00",
        }, format="json")
        self.assertEqual(overlap.status_code, 400)

    def test_patient_can_request_reschedule_and_doctor_must_decide(self):
        grant = DoctorAccessGrant.objects.create(member=self.member, doctor=self.doctor,
            granted_by=self.patient, scopes=["profile", "consultation_notes"], active=True)
        appointment = Appointment.objects.create(member=self.member, doctor=self.doctor,
            requested_by=self.patient, preferred_at=timezone.now() + timedelta(days=3),
            scheduled_at=timezone.now() + timedelta(days=3), status=Appointment.Status.ACCEPTED)
        proposed = (timezone.now() + timedelta(days=5)).isoformat()
        requested = self.patient_client.post(f"/medlife/doctor/appointments/{appointment.pk}/reschedule/",
            {"proposed_at": proposed, "reason": "Schedule conflict"}, format="json")
        self.assertEqual(requested.status_code, 201, requested.json())
        request_id = requested.json()["reschedule_request"]["id"]
        decided = self.doctor_client.post(f"/medlife/doctor/reschedule-requests/{request_id}/decision/",
            {"decision": "accept"}, format="json")
        self.assertEqual(decided.status_code, 200, decided.json())
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.ACCEPTED)
        self.assertEqual(appointment.scheduled_at.isoformat(), proposed)

    def test_finalized_consultation_note_amendment_preserves_revision(self):
        DoctorAccessGrant.objects.create(member=self.member, doctor=self.doctor,
            granted_by=self.patient, scopes=["profile", "consultation_notes"], active=True)
        appointment = Appointment.objects.create(member=self.member, doctor=self.doctor,
            requested_by=self.patient, preferred_at=timezone.now() + timedelta(days=1),
            scheduled_at=timezone.now() + timedelta(days=1), status=Appointment.Status.ACCEPTED)
        url = f"/medlife/doctor/appointments/{appointment.pk}/notes/"
        created = self.doctor_client.post(url, {"action": "finalize", "sections": {
            "symptoms": "Headache", "assessment": "Needs follow-up"}}, format="json")
        self.assertEqual(created.status_code, 201, created.json())
        amended = self.doctor_client.post(url, {"action": "amend", "sections": {
            "symptoms": "Headache for two days", "assessment": "Needs follow-up"}}, format="json")
        self.assertEqual(amended.status_code, 200, amended.json())
        self.assertEqual(amended.json()["revision_count"], 1)
        history = self.doctor_client.get(f"{url}revisions/")
        self.assertEqual(history.status_code, 200, history.json())
        self.assertEqual(len(history.json()["revisions"]), 1)

    def test_super_admin_can_review_and_intervene_in_doctor_availability(self):
        admin = Account.objects.create(email="availability-admin@example.com", role=Account.Role.SUPER_ADMIN)
        admin_client = APIClient()
        admin_client.credentials(**bearer_for(admin))
        slot = DoctorAvailabilitySlot.objects.create(
            doctor=self.doctor, weekday=2, start_time=time(9, 0), end_time=time(12, 0), is_active=True,
        )

        reviewed = admin_client.get("/medlife/doctor/admin/availability/")
        self.assertEqual(reviewed.status_code, 200, reviewed.json())
        doctor_data = next(item for item in reviewed.json()["doctors"] if item["doctor_id"] == self.doctor.pk)
        self.assertEqual(doctor_data["slots"][0]["id"], slot.pk)

        changed = admin_client.post("/medlife/doctor/admin/availability/", {
            "action": "set_slot_active", "doctor_id": self.doctor.pk,
            "slot_id": slot.pk, "is_active": False, "reason": "Temporary schedule adjustment",
        }, format="json")
        self.assertEqual(changed.status_code, 200, changed.json())
        slot.refresh_from_db()
        self.assertFalse(slot.is_active)

    def test_patient_cannot_use_super_admin_availability_controls(self):
        response = self.patient_client.get("/medlife/doctor/admin/availability/")
        self.assertEqual(response.status_code, 403)

    def test_super_admin_can_cancel_an_appointment(self):
        admin = Account.objects.create(email="cancel-admin@example.com", role=Account.Role.SUPER_ADMIN)
        appointment = Appointment.objects.create(member=self.member, doctor=self.doctor,
            requested_by=self.patient, preferred_at=timezone.now() + timedelta(days=2))
        admin_client = APIClient()
        admin_client.credentials(**bearer_for(admin))
        response = admin_client.post(f"/medlife/doctor/appointments/{appointment.pk}/cancel/",
            {"reason": "Administrative cancellation"}, format="json")
        self.assertEqual(response.status_code, 200, response.json())
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CANCELLED)

    def test_accepted_chat_can_be_closed_and_history_read(self):
        DoctorAccessGrant.objects.create(member=self.member, doctor=self.doctor,
            granted_by=self.patient, scopes=["profile"], active=True)
        chat = DoctorChatRequest.objects.create(member=self.member, doctor=self.doctor,
            requested_by=self.patient, status=DoctorChatRequest.Status.ACCEPTED)
        closed = self.doctor_client.post(f"/medlife/doctor/chat-requests/{chat.pk}/close/", {}, format="json")
        self.assertEqual(closed.status_code, 200, closed.json())
        history = self.doctor_client.get(f"/medlife/doctor/chat-requests/{chat.pk}/messages/")
        self.assertEqual(history.status_code, 200, history.json())

