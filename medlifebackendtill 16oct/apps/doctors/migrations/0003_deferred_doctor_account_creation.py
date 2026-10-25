from django.db import migrations, models
import django.db.models.deletion


def backfill_activation_details(apps, schema_editor):
    Activation = apps.get_model("doctors", "DoctorAccountActivation")
    alias = schema_editor.connection.alias
    for activation in Activation.objects.using(alias).select_related("account", "application").all():
        updates = []
        if not activation.email and activation.account_id:
            activation.email = activation.account.email
            updates.append("email")
        if activation.application_id:
            app = activation.application
            for field in ("full_name", "specialty", "qualifications", "registration_number", "clinic_name", "bio", "years_experience"):
                if not getattr(activation, field):
                    setattr(activation, field, getattr(app, field))
                    updates.append(field)
        if updates:
            activation.save(using=alias, update_fields=updates)


class Migration(migrations.Migration):
    dependencies = [
        ("doctors", "0002_independent_doctor_applications"),
    ]

    operations = [
        migrations.AddField("doctoraccountactivation", "email", models.EmailField(db_index=True, default="", max_length=254)),
        migrations.AddField("doctoraccountactivation", "invitation", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="activations", to="doctors.doctorinvitation")),
        migrations.AddField("doctoraccountactivation", "full_name", models.CharField(default="", max_length=150)),
        migrations.AddField("doctoraccountactivation", "specialty", models.CharField(default="", max_length=120)),
        migrations.AddField("doctoraccountactivation", "qualifications", models.CharField(default="", max_length=255)),
        migrations.AddField("doctoraccountactivation", "registration_number", models.CharField(default="", max_length=120)),
        migrations.AddField("doctoraccountactivation", "clinic_name", models.CharField(blank=True, default="", max_length=200)),
        migrations.AddField("doctoraccountactivation", "bio", models.TextField(blank=True, default="")),
        migrations.AddField("doctoraccountactivation", "years_experience", models.PositiveSmallIntegerField(default=0)),
        migrations.AddField("doctoraccountactivation", "phone", models.CharField(blank=True, default="", max_length=32)),
        migrations.AddField("doctoraccountactivation", "address", models.TextField(blank=True, default="")),
        migrations.AddField("doctoraccountactivation", "registration_authority", models.CharField(blank=True, default="", max_length=200)),
        migrations.AddField("doctoraccountactivation", "pending_password_hash", models.CharField(blank=True, default="", max_length=128)),
        migrations.AddField("doctoraccountactivation", "pending_totp_secret_encrypted", models.TextField(blank=True, default="")),
        migrations.RunPython(backfill_activation_details, migrations.RunPython.noop),
        migrations.AlterField("doctoraccountactivation", "account", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="doctor_activations", to="accounts.account")),
        migrations.AlterField("doctoraccountactivation", "application", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="activations", to="doctors.doctorapplication")),
        migrations.AlterField("doctorinvitation", "status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected"), ("expired", "Expired"), ("revoked", "Revoked")], db_index=True, max_length=12)),
    ]
