from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.chat.models import ChatMessage


class Command(BaseCommand):
    help = (
        "Delete saved chat messages not updated for N days (a member's chat is rewritten as a whole on each save, "
        "so this removes conversations nobody has touched). Run it from cron / a scheduler, e.g. daily."
    )

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=90, help="Retention period in days (default 90).")
        parser.add_argument("--dry-run", action="store_true", help="Only report how many messages would be deleted.")

    def handle(self, *args, **options):
        days = options["days"]
        if days < 1:
            raise CommandError("--days must be at least 1.")
        cutoff = timezone.now() - timedelta(days=days)
        stale = ChatMessage.objects.filter(created_at__lt=cutoff)
        count = stale.count()
        if options["dry_run"]:
            self.stdout.write(f"{count} chat message(s) older than {days} days would be deleted.")
            return
        stale.delete()
        self.stdout.write(f"Deleted {count} chat message(s) older than {days} days.")
