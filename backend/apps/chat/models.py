# # Purpose: Persists ordered chat messages for a family member, including original millisecond timestamps.
# # Edit when the saved chat message contract changes; update the migration too.
# from django.db import models
# from apps.members.models import FamilyMember

# class ChatMessage(models.Model):
#     class Role(models.TextChoices):
#         USER = "user", "User"
#         AI = "ai", "AI"

#     member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="chat_messages")
#     position = models.PositiveIntegerField()
#     role = models.CharField(max_length=4, choices=Role.choices)
#     text = models.TextField(max_length=20000)
#     ts = models.BigIntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["position"]
#         constraints = [models.UniqueConstraint(fields=["member", "position"], name="uniq_chat_position_per_member")]
#         indexes = [models.Index(fields=["member", "position"], name="chat_member_position_idx")]

#     def __str__(self):
#         return f"{self.member.key} message {self.position}"




# Purpose: Persists ordered chat messages for a family member, including original millisecond timestamps.
# Edit when the saved chat message contract changes; update the migration too.
from django.db import models
from apps.members.models import FamilyMember
from .fields import EncryptedTextField

class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        AI = "ai", "AI"

    member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="chat_messages")
    position = models.PositiveIntegerField()
    role = models.CharField(max_length=4, choices=Role.choices)
    text = EncryptedTextField(max_length=20000)  # encrypted at rest (see apps/chat/crypto.py)
    ts = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]
        constraints = [models.UniqueConstraint(fields=["member", "position"], name="uniq_chat_position_per_member")]
        indexes = [models.Index(fields=["member", "position"], name="chat_member_position_idx")]

    def __str__(self):
        return f"{self.member.key} message {self.position}"
