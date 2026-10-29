# Purpose: Initial schema for family profiles, token limits, and account/slot uniqueness.
# Edit migrations only through Django makemigrations after changing models.
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="FamilyMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slot", models.PositiveSmallIntegerField()),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(blank=True, default="", max_length=100)),
                ("dob", models.CharField(blank=True, default="", max_length=10)),
                ("gender", models.CharField(blank=True, default="", max_length=40)),
                ("race", models.CharField(blank=True, default="", max_length=100)),
                ("height", models.CharField(blank=True, default="", max_length=30)),
                ("weight", models.CharField(blank=True, default="", max_length=30)),
                ("a1c", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("blood_pressure", models.CharField(blank=True, default="", max_length=7)),
                ("medicine", models.CharField(blank=True, default="", max_length=2000)),
                ("tokens_used", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="members", to="accounts.account")),
            ],
            options={"ordering": ["slot"]},
        ),
        migrations.AddConstraint(
            model_name="familymember",
            constraint=models.UniqueConstraint(fields=("account", "slot"), name="uniq_member_slot_per_account"),
        ),
        migrations.AddConstraint(
            model_name="familymember",
            constraint=models.CheckConstraint(condition=models.Q(("slot__gte", 1), ("slot__lte", 4)), name="member_slot_1_to_4"),
        ),
        migrations.AddConstraint(
            model_name="familymember",
            constraint=models.CheckConstraint(condition=models.Q(("tokens_used__gte", 0), ("tokens_used__lte", 100)), name="member_tokens_0_to_100"),
        ),
        migrations.AddIndex(
            model_name="familymember",
            index=models.Index(fields=["account", "slot"], name="member_account_slot_idx"),
        ),
    ]
