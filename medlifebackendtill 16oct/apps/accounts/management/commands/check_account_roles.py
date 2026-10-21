from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import Account
from apps.doctors.models import DoctorProfile


class Command(BaseCommand):
    help = "Report inconsistent MedLife account roles and doctor profile statuses without changing data."

    def handle(self, *args, **options):
        errors = []
        super_admin_count = Account.objects.filter(role=Account.Role.SUPER_ADMIN).count()
        if super_admin_count != 1:
            errors.append(f"Expected exactly one designated Super Admin after provisioning; found {super_admin_count}.")

        approved_non_doctors = DoctorProfile.objects.filter(
            status=DoctorProfile.Status.APPROVED
        ).exclude(account__role=Account.Role.DOCTOR).select_related("account")
        for profile in approved_non_doctors:
            errors.append(
                f"Approved doctor profile id={profile.pk} belongs to account id={profile.account_id} "
                f"with role={profile.account.role!r}; expected 'doctor'."
            )

        for account in Account.objects.filter(role=Account.Role.DOCTOR).iterator():
            if not DoctorProfile.objects.filter(
                account=account, status=DoctorProfile.Status.APPROVED
            ).exists():
                errors.append(
                    f"Account id={account.pk} ({account.email}) has role='doctor' without an approved DoctorProfile."
                )

        if errors:
            for error in errors:
                self.stderr.write(self.style.ERROR(error))
            raise CommandError("Account-role consistency check failed. No data was changed.")

        self.stdout.write(self.style.SUCCESS(
            f"Role consistency check passed: one Super Admin; "
            f"{Account.objects.filter(role=Account.Role.DOCTOR).count()} doctor account(s); "
            f"{Account.objects.filter(role=Account.Role.PATIENT).count()} patient account(s)."
        ))
