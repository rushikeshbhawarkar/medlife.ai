# Purpose: Store privacy-minimal audit metadata for AI provider disclosures.
from django.db import models


class AIProviderAudit(models.Model):
    class Outcome(models.TextChoices):
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        BLOCKED_NO_CONSENT = "blocked_no_consent", "Blocked: consent required"

    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_provider_audits",
    )
    provider = models.CharField(max_length=24)
    model = models.CharField(max_length=120, blank=True, default="")
    outcome = models.CharField(max_length=24, choices=Outcome.choices)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"AI provider audit: {self.provider} ({self.outcome})"
