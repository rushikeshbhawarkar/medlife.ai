from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from apps.accounts.models import Account


class Command(BaseCommand):
    help = (
        "Designate an existing MedLife account as the single Super Admin. "
        "For a deliberate transfer, supply --transfer-from with the current Super Admin email."
    )

    def add_arguments(self, parser):
        parser.add_argument("email", help="Email of the existing account to designate")
        parser.add_argument(
            "--transfer-from",
            dest="transfer_from",
            help="Exact email of the currently designated Super Admin; required to transfer an existing designation",
        )

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        transfer_from = (options.get("transfer_from") or "").strip().lower()
        if not email:
            raise CommandError("A target account email is required.")
        if transfer_from and transfer_from == email:
            raise CommandError("The transfer target and current Super Admin must be different.")

        try:
            with transaction.atomic():
                # Lock the account rows to serialize provisioning on PostgreSQL. The unique
                # conditional constraint remains the final protection against concurrent commands.
                current_admins = list(
                    Account.objects.select_for_update().filter(role=Account.Role.SUPER_ADMIN).order_by("pk")
                )
                target = Account.objects.select_for_update().filter(email__iexact=email).first()
                if target is None:
                    raise CommandError(
                        "No existing account matches that email. Create and verify the account through "
                        "the normal MedLife signup flow, then rerun this command."
                    )

                if target.role == Account.Role.SUPER_ADMIN and len(current_admins) == 1:
                    self.stdout.write(self.style.SUCCESS(
                        f"{target.email} (account id {target.pk}) is already the designated MedLife Super Admin."
                    ))
                    return

                if current_admins:
                    if len(current_admins) != 1:
                        raise CommandError(
                            "Multiple Super Admin records already exist. Resolve the data conflict manually "
                            "before provisioning; no account was changed."
                        )
                    current = current_admins[0]
                    if not transfer_from or current.email.lower() != transfer_from:
                        raise CommandError(
                            "A Super Admin is already designated. To transfer the role deliberately, provide "
                            "--transfer-from with the exact current Super Admin email."
                        )
                    if current.pk == target.pk:
                        raise CommandError("The supplied transfer source and target are the same account.")
                    current.role = Account.Role.PATIENT
                    current.save(update_fields=["role"])
                elif transfer_from:
                    raise CommandError(
                        "No current Super Admin exists, so --transfer-from cannot be used. "
                        "Run the command without --transfer-from for initial provisioning."
                    )

                # A role transfer must not leave an approved DoctorProfile with a non-doctor account role.
                try:
                    from apps.doctors.models import DoctorProfile
                    if DoctorProfile.objects.filter(
                        account=target, status=DoctorProfile.Status.APPROVED
                    ).exists():
                        raise CommandError(
                            "The target account has an approved doctor profile. Resolve that doctor status "
                            "before designating it as Super Admin."
                        )
                except ImportError:
                    pass

                target.role = Account.Role.SUPER_ADMIN
                target.save(update_fields=["role"])
        except IntegrityError as exc:
            raise CommandError(
                "The database rejected this change, likely because another Super Admin was provisioned "
                "concurrently. Check the current role assignments and retry safely."
            ) from exc

        if transfer_from:
            self.stdout.write(self.style.SUCCESS(
                f"Transferred the MedLife Super Admin role from {transfer_from} to {target.email} "
                f"(account id {target.pk})."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Designated {target.email} (account id {target.pk}) as the MedLife Super Admin."
            ))
