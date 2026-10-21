from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q
import django.utils.timezone


def backfill_application_emails_and_doctor_ids(apps, schema_editor):
    DoctorApplication = apps.get_model("doctors", "DoctorApplication")
    DoctorProfile = apps.get_model("doctors", "DoctorProfile")
    alias = schema_editor.connection.alias
    for app in DoctorApplication.objects.using(alias).select_related("account").all():
        if app.account_id and not app.email:
            app.email = app.account.email
            app.save(update_fields=["email"], using=alias)
    for profile in DoctorProfile.objects.using(alias).all():
        if not profile.doctor_id:
            profile.doctor_id = f"MLD{profile.account_id:06d}"
            profile.save(update_fields=["doctor_id"], using=alias)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_account_role"),
        ("doctors", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctorprofile",
            name="doctor_id",
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="doctorapplication",
            name="email",
            field=models.EmailField(db_index=True, default="", max_length=254),
        ),
        migrations.AddField(
            model_name="doctorapplication",
            name="phone",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
        migrations.AddField(
            model_name="doctorapplication",
            name="address",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="doctorapplication",
            name="registration_authority",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.RunPython(backfill_application_emails_and_doctor_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="doctorapplication",
            name="account",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="doctor_applications", to="accounts.account"),
        ),
        migrations.CreateModel(
            name="DoctorApplicationDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("document_type", models.CharField(choices=[("medical_registration", "Medical registration certificate"), ("qualification", "Qualification certificate"), ("identity", "Identity document"), ("other", "Other supporting document")], default="other", max_length=32)),
                ("file", models.FileField(upload_to="doctor_applications/%Y/%m/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="doctors.doctorapplication")),
            ],
            options={"ordering": ["uploaded_at", "id"]},
        ),
        migrations.CreateModel(
            name="DoctorAccountActivation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token_hash", models.CharField(max_length=64, unique=True)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="doctor_activations", to="accounts.account")),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activations", to="doctors.doctorapplication")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
    ]
