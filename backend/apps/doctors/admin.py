




from django.contrib import admin
from .models import (
    Appointment, ConsultationNote, DoctorAccessGrant, DoctorApplication, DoctorApplicationDocument, DoctorChatMessage,
    DoctorChatRequest, DoctorInvitation, DoctorNotification, DoctorProfile, DoctorAuditLog,
)

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "account", "specialty", "status", "is_available", "verified_at")
    list_filter = ("status", "is_available", "specialty")
    search_fields = ("full_name", "account__email", "registration_number")
    readonly_fields = ("created_at", "updated_at", "verified_at")


@admin.register(DoctorApplication)
class DoctorApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "account", "specialty", "status", "created_at")
    list_filter = ("status", "specialty")
    search_fields = ("full_name", "account__email", "registration_number")
    readonly_fields = ("created_at", "updated_at", "reviewed_at")


@admin.register(DoctorInvitation)
class DoctorInvitationAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "status", "expires_at", "invited_by", "created_at")
    list_filter = ("status",)
    search_fields = ("email",)
    readonly_fields = ("token_hash", "created_at")


@admin.register(DoctorAccessGrant)
class DoctorAccessGrantAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "doctor", "active", "granted_at", "revoked_at")
    list_filter = ("active",)
    readonly_fields = ("granted_at", "revoked_at")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "doctor", "status", "preferred_at", "scheduled_at")
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at", "decided_at", "completed_at")


@admin.register(DoctorChatRequest)
class DoctorChatRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "doctor", "status", "created_at")
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at", "decided_at")


@admin.register(DoctorChatMessage)
class DoctorChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_request", "sender", "created_at")
    readonly_fields = ("created_at",)


@admin.register(ConsultationNote)
class ConsultationNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "doctor", "member", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(DoctorNotification)
class DoctorNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "kind", "title", "read_at", "created_at")
    list_filter = ("kind", "read_at")
    readonly_fields = ("created_at",)

@admin.register(DoctorAuditLog)
class DoctorAuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "actor", "member", "doctor", "created_at")
    list_filter = ("action",)
    readonly_fields = ("actor", "action", "member", "doctor", "metadata", "created_at")
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DoctorApplicationDocument)
class DoctorApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "document_type", "uploaded_at")
    list_filter = ("document_type",)
    readonly_fields = ("uploaded_at",)
