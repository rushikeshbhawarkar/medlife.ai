# Purpose: Adds an optional free-text medical description to existing family profiles.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="familymember",
            name="medical_description",
            field=models.TextField(blank=True, default=""),
        ),
    ]
