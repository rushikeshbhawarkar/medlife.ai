# Purpose: Stores an email-based account and its hashed password.
# Edit when account-level data or future authentication relationships change; then create a migration.
# from django.db import models

# class Account(models.Model):
#     email = models.EmailField(max_length=254, unique=True)
#     # Django-hashed password (never plain text). Empty means an older email-only account with no password yet.
#     password = models.CharField(max_length=128, blank=True, default="")
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["id"]

#     def __str__(self):
#         return self.email




# # Purpose: Stores an email-based account and its hashed password.
# # Edit when account-level data or future authentication relationships change; then create a migration.
# from django.db import models

# class Account(models.Model):
#     email = models.EmailField(max_length=254, unique=True)
#     # Django-hashed password (never plain text). Empty means an older email-only account with no password yet.
#     password = models.CharField(max_length=128, blank=True, default="")
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["id"]

#     @property
#     def is_authenticated(self):
#         return True

#     @property
#     def is_anonymous(self):
#         return False

#     def __str__(self):
#         return self.email






# # Purpose: Stores account credentials and mandatory TOTP enrollment state.
# # When account-level fields change, create a Django migration.
# from django.db import models


# class Account(models.Model):
#     email = models.EmailField(max_length=254, unique=True)
#     # Django-hashed password (never plaintext).
#     password = models.CharField(max_length=128, blank=True, default="")
#     # TOTP setup remains pending until the user verifies a code from their authenticator.
#     totp_enabled = models.BooleanField(default=False)
#     totp_secret_encrypted = models.TextField(blank=True, default="")
#     totp_pending_secret_encrypted = models.TextField(blank=True, default="")
#     # Prevents accepting the same TOTP time-step more than once.
#     totp_last_verified_step = models.BigIntegerField(null=True, blank=True, default=None)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["id"]

#     @property
#     def is_authenticated(self):
#         return True

#     @property
#     def is_anonymous(self):
#         return False

#     def __str__(self):
#         return self.email






# # Purpose: Stores account credentials and mandatory TOTP enrollment state.
# # When account-level fields change, create a Django migration.
# from django.db import models


# class Account(models.Model):
#     email = models.EmailField(max_length=254, unique=True)
#     # Stable Google OpenID Connect subject. Null for accounts that have not linked Google.
#     google_sub = models.CharField(max_length=255, unique=True, null=True, blank=True, editable=False)
#     # Django-hashed password (never plaintext).
#     password = models.CharField(max_length=128, blank=True, default="")
#     # TOTP setup remains pending until the user verifies a code from their authenticator.
#     totp_enabled = models.BooleanField(default=False)
#     totp_secret_encrypted = models.TextField(blank=True, default="")
#     totp_pending_secret_encrypted = models.TextField(blank=True, default="")
#     # Prevents accepting the same TOTP time-step more than once.
#     totp_last_verified_step = models.BigIntegerField(null=True, blank=True, default=None)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["id"]

#     @property
#     def is_authenticated(self):
#         return True

#     @property
#     def is_anonymous(self):
#         return False

#     def __str__(self):
#         return self.email







# Purpose: Stores account credentials and mandatory TOTP enrollment state.
# When account-level fields change, create a Django migration.
from django.db import models
from django.db.models import Q


class Account(models.Model):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        DOCTOR = "doctor", "Doctor"
        PATIENT = "patient", "Patient"

    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.PATIENT, db_index=True)
    # Stable Google OpenID Connect subject. Null for accounts that have not linked Google.
    google_sub = models.CharField(max_length=255, unique=True, null=True, blank=True, editable=False)
    # Django-hashed password (never plaintext).
    password = models.CharField(max_length=128, blank=True, default="")
    # TOTP setup remains pending until the user verifies a code from their authenticator.
    totp_enabled = models.BooleanField(default=False)
    totp_secret_encrypted = models.TextField(blank=True, default="")
    totp_pending_secret_encrypted = models.TextField(blank=True, default="")
    # Prevents accepting the same TOTP time-step more than once.
    totp_last_verified_step = models.BigIntegerField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["role"],
                condition=Q(role="super_admin"),
                name="one_medlife_super_admin",
            ),
        ]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.email
