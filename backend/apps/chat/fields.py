from django.db import models

from .crypto import decrypt_text, encrypt_text


class EncryptedTextField(models.TextField):
    """TextField that is encrypted in the database and plain text in Python.

    The column type is unchanged (text), so no schema change is needed. Callers (serializers, services,
    tests) keep reading and writing normal strings.
    """

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_text(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        return encrypt_text(value)
