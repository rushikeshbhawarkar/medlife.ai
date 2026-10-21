# Purpose: Associate a MedLife account with its stable Google OpenID Connect subject.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_account_totp")]

    operations = [
        migrations.AddField(
            model_name="account",
            name="google_sub",
            field=models.CharField(blank=True, editable=False, max_length=255, null=True, unique=True),
        ),
    ]
