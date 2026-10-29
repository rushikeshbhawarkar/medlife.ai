# Purpose: Adds the hashed password column to accounts; existing accounts keep an empty password until they sign up.
# Edit migrations only through Django makemigrations after changing models.
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="account",
            name="password",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
    ]
