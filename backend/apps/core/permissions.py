from rest_framework.permissions import BasePermission

from apps.accounts.models import Account


class PatientRolePermission(BasePermission):
    message = "A patient account is required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) == Account.Role.PATIENT)


class ApprovedDoctorRolePermission(BasePermission):
    message = "An approved doctor account is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request.user, "role", None) != Account.Role.DOCTOR:
            return False
        try:
            from apps.doctors.models import DoctorProfile
            return DoctorProfile.objects.filter(
                account=request.user, status=DoctorProfile.Status.APPROVED
            ).exists()
        except Exception:
            return False


class SuperAdminRolePermission(BasePermission):
    message = "The designated MedLife Super Admin is required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) == Account.Role.SUPER_ADMIN)
