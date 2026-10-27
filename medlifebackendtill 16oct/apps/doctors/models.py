
# from django.db import models
# from django.db.models import Q
# from django.utils import timezone
# from apps.accounts.models import Account
# from apps.members.models import FamilyMember


# class DoctorProfile(models.Model):
#     class Status(models.TextChoices):
#         PENDING = "pending", "Pending verification"
#         APPROVED = "approved", "Approved"
#         REJECTED = "rejected", "Rejected"
#         SUSPENDED = "suspended", "Suspended"

#     account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="doctor_profile")
#     doctor_id = models.CharField(max_length=32, unique=True, null=True, blank=True, db_index=True)
#     full_name = models.CharField(max_length=150)
#     specialty = models.CharField(max_length=120)
#     qualifications = models.CharField(max_length=255)
#     registration_number = models.CharField(max_length=120, unique=True)
#     clinic_name = models.CharField(max_length=200, blank=True, default="")
#     bio = models.TextField(blank=True, default="")
#     years_experience = models.PositiveSmallIntegerField(default=0)
#     status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
#     is_available = models.BooleanField(default=True)
#     verified_at = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["account__email"]
#         indexes = [models.Index(fields=["status", "is_available"], name="doctor_status_avail_idx")]

#     def __str__(self):
#         return f"{self.account.email} ({self.specialty})"


# class DoctorApplication(models.Model):
#     class Status(models.TextChoices):
#         PENDING = "pending", "Pending"
#         APPROVED = "approved", "Approved"
#         REJECTED = "rejected", "Rejected"

#     # An application is independent of any account. Account is populated only for legacy rows.
#     account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="doctor_applications")
#     email = models.EmailField(max_length=254, db_index=True, default="")
#     phone = models.CharField(max_length=32, blank=True, default="")
#     address = models.TextField(blank=True, default="")
#     registration_authority = models.CharField(max_length=200, blank=True, default="")
#     full_name = models.CharField(max_length=150)
#     specialty = models.CharField(max_length=120)
#     qualifications = models.CharField(max_length=255)
#     registration_number = models.CharField(max_length=120)
#     clinic_name = models.CharField(max_length=200, blank=True, default="")
#     bio = models.TextField(blank=True, default="")
#     years_experience = models.PositiveSmallIntegerField(default=0)
#     status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
#     review_note = models.CharField(max_length=1000, blank=True, default="")
#     reviewed_by = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_doctor_applications")
#     reviewed_at = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["created_at", "id"]
#         constraints = [
#             models.UniqueConstraint(fields=["account"], condition=Q(status="pending"), name="one_pending_doctor_app_per_account")
#         ]

#     def __str__(self):
#         return f"Application {self.pk}: {self.email or (self.account.email if self.account_id else 'unknown email')} ({self.status})"


# class DoctorApplicationDocument(models.Model):
#     class DocumentType(models.TextChoices):
#         MEDICAL_REGISTRATION = "medical_registration", "Medical registration certificate"
#         QUALIFICATION = "qualification", "Qualification certificate"
#         IDENTITY = "identity", "Identity document"
#         OTHER = "other", "Other supporting document"

#     application = models.ForeignKey(DoctorApplication, on_delete=models.CASCADE, related_name="documents")
#     document_type = models.CharField(max_length=32, choices=DocumentType.choices, default=DocumentType.OTHER)
#     file = models.FileField(upload_to="doctor_applications/%Y/%m/")
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["uploaded_at", "id"]



# class DoctorAccountActivation(models.Model):
#     """Single-use onboarding state. No Account is created until password and TOTP are verified."""
#     email = models.EmailField(max_length=254, db_index=True, default="")
#     account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="doctor_activations")
#     application = models.ForeignKey(DoctorApplication, null=True, blank=True, on_delete=models.CASCADE, related_name="activations")
#     invitation = models.ForeignKey("DoctorInvitation", null=True, blank=True, on_delete=models.CASCADE, related_name="activations")
#     full_name = models.CharField(max_length=150, default="")
#     specialty = models.CharField(max_length=120, default="")
#     qualifications = models.CharField(max_length=255, default="")
#     registration_number = models.CharField(max_length=120, default="")
#     clinic_name = models.CharField(max_length=200, blank=True, default="")
#     bio = models.TextField(blank=True, default="")
#     years_experience = models.PositiveSmallIntegerField(default=0)
#     phone = models.CharField(max_length=32, blank=True, default="")
#     address = models.TextField(blank=True, default="")
#     registration_authority = models.CharField(max_length=200, blank=True, default="")
#     pending_password_hash = models.CharField(max_length=128, blank=True, default="")
#     pending_totp_secret_encrypted = models.TextField(blank=True, default="")
#     token_hash = models.CharField(max_length=64, unique=True)
#     expires_at = models.DateTimeField(db_index=True)
#     consumed_at = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-created_at", "-id"]


# class DoctorInvitation(models.Model):
#     class Status(models.TextChoices):
#         PENDING = "pending", "Pending"
#         ACCEPTED = "accepted", "Accepted"
#         REJECTED = "rejected", "Rejected"
#         EXPIRED = "expired", "Expired"
#         REVOKED = "revoked", "Revoked"

#     email = models.EmailField(db_index=True)
#     token_hash = models.CharField(max_length=64, unique=True)
#     expires_at = models.DateTimeField()
#     status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
#     invited_by = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="doctor_invitations_sent")
#     accepted_by = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="doctor_invitations_accepted")
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-created_at", "-id"]

#     def is_expired(self):
#         return self.expires_at <= timezone.now()

#     def __str__(self):
#         return f"Doctor invitation to {self.email} ({self.status})"


# class DoctorAccessGrant(models.Model):
#     ALLOWED_SCOPES = ("profile", "documents", "consultation_notes")
#     member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="doctor_access_grants")
#     doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="access_grants")
#     granted_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="doctor_access_grants_made")
#     scopes = models.JSONField(default=list)
#     active = models.BooleanField(default=True, db_index=True)
#     granted_at = models.DateTimeField(auto_now_add=True)
#     revoked_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         ordering = ["-granted_at", "-id"]
#         indexes = [models.Index(fields=["member", "doctor", "active"], name="doctor_grant_lookup_idx")]

#     def permits(self, scope):
#         return self.active and scope in (self.scopes or [])

#     def __str__(self):
#         return f"Grant member={self.member_id} doctor={self.doctor_id} active={self.active}"


# class Appointment(models.Model):
#     class Status(models.TextChoices):
#         REQUESTED = "requested", "Requested"
#         ACCEPTED = "accepted", "Accepted"
#         REJECTED = "rejected", "Rejected"
#         CANCELLED = "cancelled", "Cancelled"
#         COMPLETED = "completed", "Completed"

#     member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="doctor_appointments")
#     doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="appointments")
#     requested_by = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="appointments_requested")
#     preferred_at = models.DateTimeField()
#     scheduled_at = models.DateTimeField(null=True, blank=True)
#     reason = models.CharField(max_length=1000, blank=True, default="")
#     patient_note = models.CharField(max_length=2000, blank=True, default="")
#     doctor_response = models.CharField(max_length=1000, blank=True, default="")
#     status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED, db_index=True)
#     decided_at = models.DateTimeField(null=True, blank=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-created_at", "-id"]
#         indexes = [
#             models.Index(fields=["doctor", "status", "preferred_at"], name="appointment_doc_status_idx"),
#             models.Index(fields=["member", "status"], name="appointment_member_status_idx"),
#         ]

#     def __str__(self):
#         return f"Appointment {self.pk} ({self.status})"


# class DoctorChatRequest(models.Model):
#     class Status(models.TextChoices):
#         REQUESTED = "requested", "Requested"
#         ACCEPTED = "accepted", "Accepted"
#         REJECTED = "rejected", "Rejected"
#         CANCELLED = "cancelled", "Cancelled"
#         CLOSED = "closed", "Closed"

#     member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="doctor_chat_requests")
#     doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="chat_requests")
#     requested_by = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="doctor_chat_requests")
#     message = models.CharField(max_length=1000, blank=True, default="")
#     status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED, db_index=True)
#     decided_at = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-created_at", "-id"]
#         indexes = [models.Index(fields=["doctor", "status"], name="docchat_doc_status_idx")]

#     def __str__(self):
#         return f"Doctor chat request {self.pk} ({self.status})"


# class DoctorChatMessage(models.Model):
#     chat_request = models.ForeignKey(DoctorChatRequest, on_delete=models.CASCADE, related_name="messages")
#     sender = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="doctor_chat_messages")
#     text = models.TextField(max_length=20000)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["created_at", "id"]

#     def __str__(self):
#         return f"Doctor chat message {self.pk}"


# class ConsultationNote(models.Model):
#     appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="consultation_note")
#     doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="consultation_notes")
#     member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="consultation_notes")
#     content = models.TextField(max_length=20000)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-updated_at", "-id"]

#     def __str__(self):
#         return f"Consultation note for appointment {self.appointment_id}"


# class DoctorNotification(models.Model):
#     recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="doctor_notifications")
#     kind = models.CharField(max_length=50)
#     title = models.CharField(max_length=200)
#     message = models.CharField(max_length=500, blank=True, default="")
#     appointment = models.ForeignKey(Appointment, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
#     chat_request = models.ForeignKey(DoctorChatRequest, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
#     read_at = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-created_at", "-id"]
#         indexes = [models.Index(fields=["recipient", "read_at"], name="doctor_notif_read_idx")]

#     def __str__(self):
#         return f"{self.title} for {self.recipient.email}"


# class DoctorAuditLog(models.Model):
#     actor = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="doctor_audit_events")
#     action = models.CharField(max_length=80, db_index=True)
#     member = models.ForeignKey(FamilyMember, null=True, blank=True, on_delete=models.SET_NULL, related_name="doctor_audit_events")
#     doctor = models.ForeignKey(DoctorProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_events")
#     metadata = models.JSONField(default=dict, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-created_at", "-id"]
#         indexes = [models.Index(fields=["action", "-created_at"], name="doctor_audit_action_idx")]

#     def __str__(self):
#         return f"{self.action} by {self.actor.email}"





from django.db import models
from django.db.models import Q
from django.utils import timezone
from apps.accounts.models import Account
from apps.members.models import FamilyMember


class DoctorProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending verification"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"

    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="doctor_profile")
    doctor_id = models.CharField(max_length=32, unique=True, null=True, blank=True, db_index=True)
    full_name = models.CharField(max_length=150)
    specialty = models.CharField(max_length=120)
    qualifications = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=120, unique=True)
    clinic_name = models.CharField(max_length=200, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    years_experience = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    is_available = models.BooleanField(default=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["account__email"]
        indexes = [models.Index(fields=["status", "is_available"], name="doctor_status_avail_idx")]

    def __str__(self):
        return f"{self.account.email} ({self.specialty})"


class DoctorApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    # An application is independent of any account. Account is populated only for legacy rows.
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="doctor_applications")
    email = models.EmailField(max_length=254, db_index=True, default="")
    phone = models.CharField(max_length=32, blank=True, default="")
    address = models.TextField(blank=True, default="")
    registration_authority = models.CharField(max_length=200, blank=True, default="")
    full_name = models.CharField(max_length=150)
    specialty = models.CharField(max_length=120)
    qualifications = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=120)
    clinic_name = models.CharField(max_length=200, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    years_experience = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    review_note = models.CharField(max_length=1000, blank=True, default="")
    reviewed_by = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_doctor_applications")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]
        constraints = [
            models.UniqueConstraint(fields=["account"], condition=Q(status="pending"), name="one_pending_doctor_app_per_account")
        ]

    def __str__(self):
        return f"Application {self.pk}: {self.email or (self.account.email if self.account_id else 'unknown email')} ({self.status})"


class DoctorApplicationDocument(models.Model):
    class DocumentType(models.TextChoices):
        MEDICAL_REGISTRATION = "medical_registration", "Medical registration certificate"
        QUALIFICATION = "qualification", "Qualification certificate"
        IDENTITY = "identity", "Identity document"
        OTHER = "other", "Other supporting document"

    application = models.ForeignKey(DoctorApplication, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=32, choices=DocumentType.choices, default=DocumentType.OTHER)
    file = models.FileField(upload_to="doctor_applications/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at", "id"]



class DoctorAccountActivation(models.Model):
    """Single-use onboarding state. No Account is created until password and TOTP are verified."""
    email = models.EmailField(max_length=254, db_index=True, default="")
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="doctor_activations")
    application = models.ForeignKey(DoctorApplication, null=True, blank=True, on_delete=models.CASCADE, related_name="activations")
    invitation = models.ForeignKey("DoctorInvitation", null=True, blank=True, on_delete=models.CASCADE, related_name="activations")
    full_name = models.CharField(max_length=150, default="")
    specialty = models.CharField(max_length=120, default="")
    qualifications = models.CharField(max_length=255, default="")
    registration_number = models.CharField(max_length=120, default="")
    clinic_name = models.CharField(max_length=200, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    years_experience = models.PositiveSmallIntegerField(default=0)
    phone = models.CharField(max_length=32, blank=True, default="")
    address = models.TextField(blank=True, default="")
    registration_authority = models.CharField(max_length=200, blank=True, default="")
    pending_password_hash = models.CharField(max_length=128, blank=True, default="")
    pending_totp_secret_encrypted = models.TextField(blank=True, default="")
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField(db_index=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class DoctorInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    email = models.EmailField(db_index=True)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    invited_by = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="doctor_invitations_sent")
    accepted_by = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="doctor_invitations_accepted")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def is_expired(self):
        return self.expires_at <= timezone.now()

    def __str__(self):
        return f"Doctor invitation to {self.email} ({self.status})"


class DoctorAccessGrant(models.Model):
    ALLOWED_SCOPES = ("profile", "documents", "consultation_notes")
    member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="doctor_access_grants")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="access_grants")
    granted_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="doctor_access_grants_made")
    scopes = models.JSONField(default=list)
    active = models.BooleanField(default=True, db_index=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-granted_at", "-id"]
        indexes = [models.Index(fields=["member", "doctor", "active"], name="doctor_grant_lookup_idx")]

    def permits(self, scope):
        return self.active and scope in (self.scopes or [])

    def __str__(self):
        return f"Grant member={self.member_id} doctor={self.doctor_id} active={self.active}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="doctor_appointments")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="appointments")
    requested_by = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="appointments_requested")
    # Set only when an authorized administrator creates a booking on a patient's behalf.
    booked_by = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointments_booked_for_patients")
    preferred_at = models.DateTimeField()
    scheduled_at = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=1000, blank=True, default="")
    patient_note = models.CharField(max_length=2000, blank=True, default="")
    doctor_response = models.CharField(max_length=1000, blank=True, default="")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["doctor", "status", "preferred_at"], name="appointment_doc_status_idx"),
            models.Index(fields=["member", "status"], name="appointment_member_status_idx"),
        ]

    def __str__(self):
        return f"Appointment {self.pk} ({self.status})"


class DoctorChatRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        CLOSED = "closed", "Closed"

    member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="doctor_chat_requests")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="chat_requests")
    requested_by = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="doctor_chat_requests")
    message = models.CharField(max_length=1000, blank=True, default="")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["doctor", "status"], name="docchat_doc_status_idx")]

    def __str__(self):
        return f"Doctor chat request {self.pk} ({self.status})"


class DoctorChatMessage(models.Model):
    chat_request = models.ForeignKey(DoctorChatRequest, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="doctor_chat_messages")
    text = models.TextField(max_length=20000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Doctor chat message {self.pk}"


class ConsultationNote(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="consultation_note")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="consultation_notes")
    member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="consultation_notes")
    content = models.TextField(max_length=20000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return f"Consultation note for appointment {self.appointment_id}"


class DoctorNotification(models.Model):
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="doctor_notifications")
    kind = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    message = models.CharField(max_length=500, blank=True, default="")
    appointment = models.ForeignKey(Appointment, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    chat_request = models.ForeignKey(DoctorChatRequest, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["recipient", "read_at"], name="doctor_notif_read_idx")]

    def __str__(self):
        return f"{self.title} for {self.recipient.email}"


class DoctorAuditLog(models.Model):
    actor = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="doctor_audit_events")
    action = models.CharField(max_length=80, db_index=True)
    member = models.ForeignKey(FamilyMember, null=True, blank=True, on_delete=models.SET_NULL, related_name="doctor_audit_events")
    doctor = models.ForeignKey(DoctorProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_events")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["action", "-created_at"], name="doctor_audit_action_idx")]

    def __str__(self):
        return f"{self.action} by {self.actor.email}"



class AppointmentHistory(models.Model):
    """Append-only record of appointment creation and consequential status changes."""
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="history")
    actor = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointment_history_actions")
    action = models.CharField(max_length=40)
    from_status = models.CharField(max_length=16, blank=True, default="")
    to_status = models.CharField(max_length=16, blank=True, default="")
    reason = models.CharField(max_length=1000, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [models.Index(fields=["appointment", "created_at"], name="appt_history_time_idx")]
