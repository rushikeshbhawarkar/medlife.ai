# Purpose: Initial schema for ordered, cascade-deleted chat messages.
# Edit migrations only through Django makemigrations after changing models.
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("members", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="ChatMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("position", models.PositiveIntegerField()),
                ("role", models.CharField(choices=[("user", "User"), ("ai", "AI")], max_length=4)),
                ("text", models.TextField(max_length=20000)),
                ("ts", models.BigIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chat_messages", to="members.familymember")),
            ],
            options={"ordering": ["position"]},
        ),
        migrations.AddConstraint(
            model_name="chatmessage",
            constraint=models.UniqueConstraint(fields=("member", "position"), name="uniq_chat_position_per_member"),
        ),
        migrations.AddIndex(
            model_name="chatmessage",
            index=models.Index(fields=["member", "position"], name="chat_member_position_idx"),
        ),
    ]
