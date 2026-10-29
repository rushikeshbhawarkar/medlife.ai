from django.db import migrations

import apps.chat.fields
from apps.chat.crypto import decrypt_text, encrypt_text, is_encrypted


def _rewrite(apps, schema_editor, transform, wants_encrypted):
    """Rewrite stored text with raw SQL so we see exactly what is in the column (no field conversion)."""
    model = apps.get_model("chat", "ChatMessage")
    table = schema_editor.connection.ops.quote_name(model._meta.db_table)
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"SELECT id, text FROM {table}")
        rows = cursor.fetchall()
        updates = [(transform(text), pk) for pk, text in rows if is_encrypted(text) != wants_encrypted]
        if updates:
            cursor.executemany(f"UPDATE {table} SET text = %s WHERE id = %s", updates)


def encrypt_existing(apps, schema_editor):
    _rewrite(apps, schema_editor, encrypt_text, wants_encrypted=True)


def decrypt_existing(apps, schema_editor):
    _rewrite(apps, schema_editor, decrypt_text, wants_encrypted=False)


class Migration(migrations.Migration):
    dependencies = [("chat", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="chatmessage",
            name="text",
            field=apps.chat.fields.EncryptedTextField(max_length=20000),
        ),
        migrations.RunPython(encrypt_existing, decrypt_existing),
    ]
