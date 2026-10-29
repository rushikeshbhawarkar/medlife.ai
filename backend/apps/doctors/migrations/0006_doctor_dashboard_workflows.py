from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_account_cloud_ai_consent_fields"),
        ("doctors", "0005_superadmin_dashboard_foundation"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationnote",
            name="sections",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="consultationnote",
            name="finalized_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="ConsultationNoteRevision",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField(max_length=20000)),
                ("sections", models.JSONField(blank=True, default=dict)),
                ("finalized_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("note", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="revisions", to="doctors.consultationnote")),
                ("revised_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="consultation_note_revisions", to="accounts.account")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="DoctorAvailabilitySlot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weekday", models.PositiveSmallIntegerField(help_text="Monday=0 through Sunday=6")),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="availability_slots", to="doctors.doctorprofile")),
            ],
            options={"ordering": ["weekday", "start_time", "id"]},
        ),
        migrations.AddConstraint(
            model_name="doctoravailabilityslot",
            constraint=models.CheckConstraint(condition=models.Q(("weekday__gte", 0), ("weekday__lte", 6)), name="doctor_availability_weekday_valid"),
        ),
        migrations.AddConstraint(
            model_name="doctoravailabilityslot",
            constraint=models.CheckConstraint(condition=models.Q(("start_time__lt", models.F("end_time"))), name="doctor_availability_time_order"),
        ),
        migrations.AddConstraint(
            model_name="doctoravailabilityslot",
            constraint=models.UniqueConstraint(fields=("doctor", "weekday", "start_time", "end_time"), name="doctor_availability_slot_unique"),
        ),
        migrations.AddIndex(
            model_name="doctoravailabilityslot",
            index=models.Index(fields=["doctor", "weekday", "is_active"], name="doctor_availability_idx"),
        ),
        migrations.CreateModel(
            name="AppointmentRescheduleRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("proposed_at", models.DateTimeField()),
                ("reason", models.CharField(blank=True, default="", max_length=1000)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected"), ("cancelled", "Cancelled")], db_index=True, default="pending", max_length=16)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("appointment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reschedule_requests", to="doctors.appointment")),
                ("decided_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="appointment_reschedule_decisions", to="accounts.account")),
                ("requested_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointment_reschedule_requests", to="accounts.account")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.AddIndex(
            model_name="appointmentreschedulerequest",
            index=models.Index(fields=["appointment", "status"], name="appt_reschedule_status_idx"),
        ),
    ]
