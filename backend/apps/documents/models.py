# Purpose: Stores text extracted (OCR) from an uploaded medicine label / prescription image as a description.
# The image itself is NEVER stored. Edit when fields change; then create and commit a migration.
from django.db import models
from apps.accounts.models import Account
from apps.members.models import FamilyMember


class ScannedDocument(models.Model):
    class DocumentType(models.TextChoices):
        MEDICINE_LABEL = "medicine_label", "Medicine label"
        PRESCRIPTION = "prescription", "Prescription"
        OTHER = "other", "Other"

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="scanned_documents")
    # Optional link to one of the account's family profiles. Deleting the profile deletes its scans
    # (same privacy behaviour as chat history).
    member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, null=True, blank=True,
                               related_name="scanned_documents")
    document_type = models.CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER)
    # Raw OCR output exactly as the engine produced it (after removing unsafe control characters). Never edited.
    ocr_text = models.TextField()
    # The description shown to the user. Starts equal to ocr_text; only its owner may correct it.
    description = models.TextField()
    # Mean per-word confidence reported by the OCR engine (0-100); null if unavailable.
    ocr_confidence = models.FloatField(null=True, blank=True)
    # Human-readable warnings produced during extraction (low confidence, uncertain numbers, ...).
    warnings = models.JSONField(default=list, blank=True)
    # False until the owner reviews the text and confirms it is correct.
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["account", "-created_at"], name="scandoc_account_created_idx")]

    def __str__(self):
        return f"scan {self.pk} ({self.document_type})"
