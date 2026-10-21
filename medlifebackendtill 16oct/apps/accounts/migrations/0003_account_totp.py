# Purpose: Add mandatory TOTP enrollment state to accounts.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_account_password")]

    operations = [
        migrations.AddField(
            model_name="account",
            name="totp_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="account",
            name="totp_secret_encrypted",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="account",
            name="totp_pending_secret_encrypted",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="account",
            name="totp_last_verified_step",
            field=models.BigIntegerField(blank=True, default=None, null=True),
        ),
    ]
