from django.db import migrations, models
from django.db.models import Q


def backfill_approved_doctors(apps, schema_editor):
    Account = apps.get_model("accounts", "Account")
    DoctorProfile = apps.get_model("doctors", "DoctorProfile")
    approved_account_ids = DoctorProfile.objects.using(schema_editor.connection.alias).filter(
        status="approved"
    ).values_list("account_id", flat=True)
    Account.objects.using(schema_editor.connection.alias).filter(
        pk__in=approved_account_ids
    ).update(role="doctor")


def noop_reverse(apps, schema_editor):
    # Role assignments are now authoritative data; do not guess prior values on rollback.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_account_google_sub"),
        ("doctors", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="role",
            field=models.CharField(
                choices=[
                    ("super_admin", "Super Admin"),
                    ("doctor", "Doctor"),
                    ("patient", "Patient"),
                ],
                db_index=True,
                default="patient",
                max_length=16,
            ),
        ),
        migrations.RunPython(backfill_approved_doctors, noop_reverse),
        migrations.AddConstraint(
            model_name="account",
            constraint=models.UniqueConstraint(
                fields=("role",),
                condition=Q(role="super_admin"),
                name="one_medlife_super_admin",
            ),
        ),
    ]
