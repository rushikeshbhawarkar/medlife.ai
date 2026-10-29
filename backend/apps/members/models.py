# Purpose: Stores a family member profile and server-controlled question token count.
# Edit when adding/removing profile fields; then create and commit a migration.
from django.db import models
from django.db.models import Q
from apps.accounts.models import Account

class FamilyMember(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="members")
    slot = models.PositiveSmallIntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, default="")
    dob = models.CharField(max_length=10, blank=True, default="")
    gender = models.CharField(max_length=40, blank=True, default="")
    race = models.CharField(max_length=100, blank=True, default="")
    height = models.CharField(max_length=30, blank=True, default="")
    weight = models.CharField(max_length=30, blank=True, default="")
    a1c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure = models.CharField(max_length=7, blank=True, default="")
    medicine = models.CharField(max_length=2000, blank=True, default="")
    medical_description = models.TextField(blank=True, default="")
    tokens_used = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slot"]
        constraints = [
            models.UniqueConstraint(fields=["account", "slot"], name="uniq_member_slot_per_account"),
            models.CheckConstraint(condition=Q(slot__gte=1) & Q(slot__lte=4), name="member_slot_1_to_4"),
            models.CheckConstraint(condition=Q(tokens_used__gte=0) & Q(tokens_used__lte=100), name="member_tokens_0_to_100"),
        ]
        indexes = [models.Index(fields=["account", "slot"], name="member_account_slot_idx")]

    @property
    def key(self):
        return f"member{self.slot}"

    def __str__(self):
        return f"{self.key} ({self.first_name} {self.last_name})".strip()
