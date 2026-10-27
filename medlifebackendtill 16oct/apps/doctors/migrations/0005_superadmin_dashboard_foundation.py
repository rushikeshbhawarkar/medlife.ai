# Generated for the super-admin dashboard additions.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_account_cloud_ai_consent_fields"),
        ("doctors", "0004_alter_doctorinvitation_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="booked_by",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name="appointments_booked_for_patients", to="accounts.account",
            ),
        ),
        migrations.CreateModel(
            name="AppointmentHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=40)),
                ("from_status", models.CharField(blank=True, default="", max_length=16)),
                ("to_status", models.CharField(blank=True, default="", max_length=16)),
                ("reason", models.CharField(blank=True, default="", max_length=1000)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="appointment_history_actions", to="accounts.account")),
                ("appointment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="history", to="doctors.appointment")),
            ],
            options={
                "ordering": ["created_at", "id"],
                "indexes": [models.Index(fields=["appointment", "created_at"], name="appt_history_time_idx")],
            },
        ),
    ]
