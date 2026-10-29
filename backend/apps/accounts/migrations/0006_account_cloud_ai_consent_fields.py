
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_account_role"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        """
                        ALTER TABLE accounts_account
                        ADD COLUMN IF NOT EXISTS cloud_ai_consent
                        boolean NOT NULL DEFAULT FALSE;
                        """,
                        """
                        ALTER TABLE accounts_account
                        ADD COLUMN IF NOT EXISTS cloud_ai_consent_at
                        timestamp with time zone NULL;
                        """,
                    ],
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="account",
                    name="cloud_ai_consent",
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name="account",
                    name="cloud_ai_consent_at",
                    field=models.DateTimeField(
                        null=True,
                        blank=True,
                    ),
                ),
            ],
        ),
    ]

