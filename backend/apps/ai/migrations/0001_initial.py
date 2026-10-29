# Generated for privacy-minimal AI provider disclosure auditing.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("accounts", "0006_account_cloud_ai_consent_fields"),
    ]
    operations = [
        migrations.CreateModel(
            name="AIProviderAudit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(max_length=24)),
                ("model", models.CharField(blank=True, default="", max_length=120)),
                ("outcome", models.CharField(choices=[("succeeded", "Succeeded"), ("failed", "Failed"), ("blocked_no_consent", "Blocked: consent required")], max_length=24)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("account", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ai_provider_audits", to="accounts.account")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
    ]
