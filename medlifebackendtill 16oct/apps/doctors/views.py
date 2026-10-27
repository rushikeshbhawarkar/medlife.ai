


# import hashlib
# import secrets
# from datetime import timedelta

# from django.conf import settings
# from django.contrib.auth.hashers import make_password
# from django.core.mail import send_mail
# from django.http import FileResponse, Http404
# from django.db import transaction
# from django.db.models import Count, Q
# from django.db.models.functions import TruncMonth
# from django.shortcuts import get_object_or_404
# from django.utils import timezone
# from django.utils.dateparse import parse_datetime
# from rest_framework import status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response

# from apps.accounts.models import Account
# from apps.core.identity import caller_email
# from apps.documents.models import ScannedDocument
# from apps.members.models import FamilyMember
# from apps.accounts.totp import decrypt_totp_secret, encrypt_totp_secret, make_totp_setup, matching_totp_step
# from .models import (
#     Appointment, AppointmentHistory, ConsultationNote, DoctorAccessGrant, DoctorApplication, DoctorAccountActivation, DoctorApplicationDocument, DoctorAuditLog, DoctorChatMessage,
#     DoctorChatRequest, DoctorInvitation, DoctorNotification, DoctorProfile,
# )


# class InvitationEmailDeliveryError(APIException):
#     status_code = 503
#     default_detail = "Invitation email could not be sent. Check the email configuration and try again."
#     default_code = "email_delivery_failed"


# def _email(account):
#     return (account.email or "").strip().lower()


# def _staff_role(account):
#     # The persisted MedLife role is authoritative. Legacy email allowlists are not authorization.
#     return "super_admin" if getattr(account, "role", "") == Account.Role.SUPER_ADMIN else ""


# def _require_staff(account, super_admin=False):
#     role = _staff_role(account)
#     if not role:
#         raise PermissionDenied("You are not authorized to perform this action.")
#     return role


# def _doctor_for(account):
#     if getattr(account, "role", "") != Account.Role.DOCTOR:
#         raise PermissionDenied("A doctor account is required.")
#     profile = DoctorProfile.objects.filter(account=account, status=DoctorProfile.Status.APPROVED).first()
#     if not profile:
#         raise PermissionDenied("An approved doctor profile is required.")
#     return profile


# def _member_for_owner(account, member_id):
#     if getattr(account, "role", "") != Account.Role.PATIENT:
#         raise PermissionDenied("Patient account access is required.")
#     # Accept the database PK (preferred) or legacy account-relative slot.
#     # Both lookups remain scoped to the authenticated account.
#     try:
#         value = int(member_id)
#     except (TypeError, ValueError):
#         raise Http404("No FamilyMember matches the given query.")
#     members = FamilyMember.objects.filter(account=account)
#     member = members.filter(pk=value).first() or members.filter(slot=value).first()
#     if member is None:
#         raise Http404("No FamilyMember matches the given query.")
#     return member


# def _active_grant(member, doctor, scope=None):
#     grants = DoctorAccessGrant.objects.filter(member=member, doctor=doctor, granted_by=member.account, active=True)
#     for grant in grants.order_by("-granted_at", "-id"):
#         if scope is None or grant.permits(scope):
#             return grant
#     return None


# def _ensure_grant(member, doctor, scopes):
#     allowed = set(DoctorAccessGrant.ALLOWED_SCOPES)
#     if not isinstance(scopes, list) or not scopes or any(not isinstance(x, str) for x in scopes):
#         raise ValidationError({"consent_scopes": "Select at least one record-sharing permission explicitly."})
#     normalized = sorted(set(scopes))
#     if any(scope not in allowed for scope in normalized):
#         raise ValidationError({"consent_scopes": "One or more consent scopes are invalid."})
#     if "profile" not in normalized:
#         raise ValidationError({"consent_scopes": "The profile scope is required for a consultation request."})
#     grant = DoctorAccessGrant.objects.filter(
#         member=member, doctor=doctor, granted_by=member.account, active=True
#     ).order_by("-granted_at", "-id").first()
#     if grant:
#         grant.scopes = normalized
#         grant.revoked_at = None
#         grant.save(update_fields=["scopes", "revoked_at"])
#         return grant
#     return DoctorAccessGrant.objects.create(member=member, doctor=doctor, granted_by=member.account, scopes=normalized)


# def _audit(actor, action, member=None, doctor=None, metadata=None):
#     return DoctorAuditLog.objects.create(actor=actor, action=action, member=member, doctor=doctor, metadata=metadata or {})


# def _notify(recipient, kind, title, message="", appointment=None, chat_request=None):
#     # Keep notification previews generic; do not place diagnoses or record contents in them.
#     return DoctorNotification.objects.create(
#         recipient=recipient, kind=kind, title=title, message=message[:500],
#         appointment=appointment, chat_request=chat_request,
#     )


# def _parse_datetime(value, field_name):
#     if not isinstance(value, str) or not value.strip():
#         raise ValidationError({field_name: "A date and time are required."})
#     dt = parse_datetime(value.strip())
#     if dt is None:
#         raise ValidationError({field_name: "Use an ISO-8601 date-time, including a timezone offset."})
#     if timezone.is_naive(dt):
#         raise ValidationError({field_name: "Include a timezone offset, for example +05:30."})
#     return dt


# def _appointment_data(appointment):
#     return {
#         "id": appointment.pk,
#         "member_id": appointment.member_id,
#         "member_name": f"{appointment.member.first_name} {appointment.member.last_name}".strip(),
#         "doctor_id": appointment.doctor_id,
#         "preferred_at": appointment.preferred_at.isoformat(),
#         "scheduled_at": appointment.scheduled_at.isoformat() if appointment.scheduled_at else None,
#         "reason": appointment.reason,
#         "patient_note": appointment.patient_note,
#         "doctor_response": appointment.doctor_response,
#         "status": appointment.status,
#         "created_at": appointment.created_at.isoformat(),
#         "updated_at": appointment.updated_at.isoformat(),
#     }


# def _record_appointment_history(appointment, actor, action, from_status="", to_status="", reason="", metadata=None):
#     return AppointmentHistory.objects.create(
#         appointment=appointment, actor=actor, action=action,
#         from_status=from_status or "", to_status=to_status or "",
#         reason=(reason or "")[:1000], metadata=metadata or {},
#     )


# def _chat_request_data(chat_request):
#     return {
#         "id": chat_request.pk,
#         "member_id": chat_request.member_id,
#         "member_name": f"{chat_request.member.first_name} {chat_request.member.last_name}".strip(),
#         "doctor_id": chat_request.doctor_id,
#         "message": chat_request.message,
#         "status": chat_request.status,
#         "created_at": chat_request.created_at.isoformat(),
#         "updated_at": chat_request.updated_at.isoformat(),
#     }


# @api_view(["GET"])
# @permission_classes([AllowAny])
# def public_doctors(request):
#     profiles = DoctorProfile.objects.filter(status=DoctorProfile.Status.APPROVED, is_available=True, account__role=Account.Role.DOCTOR).select_related("account")
#     specialty = request.query_params.get("specialty", "").strip()
#     if specialty:
#         profiles = profiles.filter(specialty__icontains=specialty)
#     return Response({"doctors": [{
#         "id": p.pk,
#         "name": p.full_name,
#         "specialty": p.specialty,
#         "qualifications": p.qualifications,
#         "clinic_name": p.clinic_name,
#         "bio": p.bio,
#         "years_experience": p.years_experience,
#         "is_available": p.is_available,
#     } for p in profiles]})



# @api_view(["GET", "PATCH"])
# @permission_classes([IsAuthenticated])
# def doctor_profile(request):
#     caller_email(request)
#     if request.user.role != Account.Role.DOCTOR:
#         raise PermissionDenied("A doctor account is required.")
#     profile = get_object_or_404(DoctorProfile, account=request.user)
#     if request.method == "GET":
#         return Response({
#             "id": profile.pk, "full_name": profile.full_name, "specialty": profile.specialty,
#             "qualifications": profile.qualifications, "registration_number": profile.registration_number,
#             "clinic_name": profile.clinic_name, "bio": profile.bio,
#             "years_experience": profile.years_experience, "status": profile.status,
#             "is_available": profile.is_available, "verified_at": profile.verified_at.isoformat() if profile.verified_at else None,
#         })
#     if profile.status != DoctorProfile.Status.APPROVED:
#         raise PermissionDenied("Only an approved doctor can update availability.")
#     if "is_available" in request.data:
#         if not isinstance(request.data["is_available"], bool):
#             raise ValidationError({"is_available": "Use true or false."})
#         profile.is_available = request.data["is_available"]
#     if "clinic_name" in request.data:
#         profile.clinic_name = str(request.data["clinic_name"]).strip()[:200]
#     if "bio" in request.data:
#         profile.bio = str(request.data["bio"]).strip()[:5000]
#     profile.save(update_fields=["is_available", "clinic_name", "bio", "updated_at"])
#     return Response({
#         "id": profile.pk, "full_name": profile.full_name, "specialty": profile.specialty,
#         "status": profile.status, "is_available": profile.is_available,
#         "clinic_name": profile.clinic_name, "bio": profile.bio,
#     })


# @api_view(["POST"])
# @permission_classes([AllowAny])
# def submit_application(request):
#     """Record an application only; do not create or modify an account."""
#     email = str(request.data.get("email", "")).strip().lower()
#     if not email or len(email) > 254 or "@" not in email:
#         raise ValidationError({"email": "Enter a valid email address."})
#     if Account.objects.filter(email__iexact=email).exists():
#         raise ValidationError({"email": "This email already belongs to an account. Use an email not attached to a patient account for the doctor application."})
#     if DoctorApplication.objects.filter(email__iexact=email, status=DoctorApplication.Status.PENDING).exists():
#         raise ValidationError({"email": "A pending application already exists for this email."})
#     full_name = str(request.data.get("full_name", "")).strip()
#     specialty = str(request.data.get("specialty", "")).strip()
#     qualifications = str(request.data.get("qualifications", "")).strip()
#     registration_number = str(request.data.get("registration_number", "")).strip()
#     if not full_name or not specialty or not qualifications or not registration_number:
#         raise ValidationError({"detail": "full_name, specialty, qualifications and registration_number are required."})
#     years = request.data.get("years_experience", 0)
#     try:
#         years = int(years)
#         if years < 0 or years > 80: raise ValueError
#     except (TypeError, ValueError):
#         raise ValidationError({"years_experience": "Enter a number from 0 to 80."})
#     uploaded_documents = request.FILES.getlist("documents") if hasattr(request, "FILES") else []
#     if len(uploaded_documents) > 10:
#         raise ValidationError({"documents": "Upload no more than 10 supporting documents."})
#     for uploaded in uploaded_documents:
#         if uploaded.size > 10 * 1024 * 1024:
#             raise ValidationError({"documents": "Each document must be 10 MB or smaller."})
#         suffix = uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else ""
#         if suffix not in {"pdf", "jpg", "jpeg", "png"}:
#             raise ValidationError({"documents": "Only PDF, JPG, JPEG, and PNG files are accepted."})
#     app = DoctorApplication.objects.create(
#         email=email, phone=str(request.data.get("phone", "")).strip()[:32],
#         address=str(request.data.get("address", "")).strip()[:3000],
#         registration_authority=str(request.data.get("registration_authority", "")).strip()[:200],
#         full_name=full_name[:150], specialty=specialty[:120], qualifications=qualifications[:255],
#         registration_number=registration_number[:120], clinic_name=str(request.data.get("clinic_name", "")).strip()[:200],
#         bio=str(request.data.get("bio", "")).strip()[:5000], years_experience=years,
#     )
#     document_types = request.data.getlist("document_types") if hasattr(request.data, "getlist") else []
#     for index, uploaded in enumerate(uploaded_documents):
#         kind = document_types[index] if index < len(document_types) else DoctorApplicationDocument.DocumentType.OTHER
#         if kind not in DoctorApplicationDocument.DocumentType.values: kind = DoctorApplicationDocument.DocumentType.OTHER
#         DoctorApplicationDocument.objects.create(application=app, document_type=kind, file=uploaded)
#     for administrator in Account.objects.filter(role=Account.Role.SUPER_ADMIN):
#         _notify(administrator, "doctor_application_received", "New doctor application", "A doctor application is awaiting review.")
#     return Response({"message": "Application submitted. No account has been created. Wait for an email decision.", "application": _application_data(app)}, status=status.HTTP_201_CREATED)


# def _application_data(app):
#     return {
#         "id": app.pk, "email": app.email or (app.account.email if app.account_id else ""),
#         "phone": app.phone, "address": app.address, "registration_authority": app.registration_authority,
#         "full_name": app.full_name, "specialty": app.specialty, "qualifications": app.qualifications,
#         "registration_number": app.registration_number, "clinic_name": app.clinic_name, "bio": app.bio,
#         "years_experience": app.years_experience, "status": app.status, "review_note": app.review_note,
#         "documents": [{"id": d.pk, "document_type": d.document_type, "uploaded_at": d.uploaded_at.isoformat()} for d in app.documents.all()],
#         "created_at": app.created_at.isoformat(), "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
#         "reviewed_by": app.reviewed_by.email if app.reviewed_by_id else None,
#     }


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def my_application(request):
#     caller_email(request)
#     app = DoctorApplication.objects.filter(email__iexact=request.user.email).order_by("-created_at", "-id").first()
#     profile = DoctorProfile.objects.filter(account=request.user).first()
#     return Response({"application": _application_data(app) if app else None, "doctor_profile": ({"id": profile.pk, "doctor_id": profile.doctor_id, "status": profile.status, "specialty": profile.specialty, "is_available": profile.is_available} if profile else None)})


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def admin_applications(request):
#     caller_email(request)
#     _require_staff(request.user)
#     state = request.query_params.get("status", "pending")
#     qs = DoctorApplication.objects.select_related("account", "reviewed_by").all()
#     if state and state != "all":
#         if state not in DoctorApplication.Status.values: raise ValidationError({"status": "Invalid application status."})
#         qs = qs.filter(status=state)
#     return Response({"applications": [_application_data(app) for app in qs]})


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def admin_application_document(request, document_id):
#     caller_email(request)
#     _require_staff(request.user, super_admin=True)
#     document = get_object_or_404(DoctorApplicationDocument.objects.select_related("application"), pk=document_id)
#     if not document.file or not document.file.storage.exists(document.file.name):
#         raise ValidationError({"detail": "The application document is unavailable."})
#     response = FileResponse(document.file.open("rb"), as_attachment=True, filename=document.file.name.rsplit("/", 1)[-1])
#     response["Cache-Control"] = "private, no-store"
#     response["X-Content-Type-Options"] = "nosniff"
#     return response


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def review_application(request, application_id):
#     """Approve/reject an application without creating an Account before doctor setup."""
#     caller_email(request)
#     _require_staff(request.user, super_admin=True)
#     decision = str(request.data.get("decision", "")).strip().lower()
#     if decision not in ("approve", "reject"):
#         raise ValidationError({"decision": "Use approve or reject."})
#     review_note = str(request.data.get("review_note", "")).strip()[:1000]
#     if decision == "reject" and not review_note:
#         raise ValidationError({"review_note": "A reason is required when rejecting an application."})
#     with transaction.atomic():
#         app = get_object_or_404(DoctorApplication.objects.select_for_update().select_related("account"), pk=application_id)
#         if app.status != DoctorApplication.Status.PENDING:
#             raise ValidationError({"detail": "This application has already been reviewed."})
#         email = (app.email or (app.account.email if app.account_id else "")).strip().lower()
#         if not email:
#             raise ValidationError({"email": "The application has no valid email address."})
#         if decision == "approve":
#             if Account.objects.filter(email__iexact=email).exists():
#                 raise ValidationError({"detail": "An account already exists for this email. No account was changed."})
#             if DoctorProfile.objects.filter(registration_number=app.registration_number).exists():
#                 raise ValidationError({"detail": "This medical registration number is already associated with another doctor."})
#             token = secrets.token_urlsafe(32)
#             activation = DoctorAccountActivation.objects.create(
#                 email=email, application=app, full_name=app.full_name, specialty=app.specialty,
#                 qualifications=app.qualifications, registration_number=app.registration_number,
#                 clinic_name=app.clinic_name, bio=app.bio, years_experience=app.years_experience,
#                 phone=app.phone, address=app.address, registration_authority=app.registration_authority,
#                 token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
#                 expires_at=timezone.now() + timedelta(hours=24),
#             )
#             frontend_url = getattr(settings, "FRONTEND_DOCTOR_ACTIVATION_URL", "http://localhost:5173/doctor-activate").rstrip("/")
#             activation_url = f"{frontend_url}#token={token}"
#             send_mail(
#                 subject="Your MedLife doctor application is approved",
#                 message=(f"Hello {app.full_name},\n\nYour MedLife doctor application has been approved.\n\nCreate your doctor account and complete password and authenticator setup here: {activation_url}\nThis link expires in 24 hours and can be used once. Do not share it.\n\nMedLife"),
#                 from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False,
#             )
#             _audit(request.user, "doctor_application_approved", metadata={"application_id": app.pk, "activation_id": activation.pk})
#         else:
#             send_mail(
#                 subject="Update on your MedLife doctor application",
#                 message=(f"Hello {app.full_name},\n\nYour MedLife doctor application was not approved at this time.\nReason: {review_note}\n\nMedLife"),
#                 from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False,
#             )
#             _audit(request.user, "doctor_application_rejected", metadata={"application_id": app.pk})
#         app.status = DoctorApplication.Status.APPROVED if decision == "approve" else DoctorApplication.Status.REJECTED
#         app.review_note = review_note
#         app.reviewed_by = request.user
#         app.reviewed_at = timezone.now()
#         app.save(update_fields=["status", "review_note", "reviewed_by", "reviewed_at", "updated_at"])
#     return Response({"application": _application_data(app), "decision": decision, "account_created": False,
#                      "message": "Approval recorded. The doctor must finish password and TOTP setup before an account is created." if decision == "approve" else "Application rejected."})


# @api_view(["POST"])
# @permission_classes([AllowAny])
# def activate_doctor_account(request):
#     """Two-stage public activation: set password and receive TOTP QR, then verify TOTP to create Account."""
#     token = str(request.data.get("token", "")).strip()
#     action = str(request.data.get("action", "setup")).strip().lower()
#     token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest() if token else ""
#     if not token:
#         raise ValidationError({"token": "Activation token is required."})

#     with transaction.atomic():
#         activation = DoctorAccountActivation.objects.select_for_update(of=("self",)).select_related("application", "invitation").filter(token_hash=token_hash).first()
#         if not activation or activation.consumed_at or activation.expires_at <= timezone.now():
#             raise ValidationError({"token": "This activation link is invalid, expired, or already used. Contact MedLife for a new link."})
#         if activation.application_id and activation.application.status != DoctorApplication.Status.APPROVED:
#             raise ValidationError({"token": "This doctor application has not been approved."})
#         if activation.invitation_id and activation.invitation.status != DoctorInvitation.Status.ACCEPTED:
#             raise ValidationError({"token": "This invitation is not accepted or is no longer valid."})

#         if action == "setup":
#             password = str(request.data.get("password", ""))
#             confirm_password = str(request.data.get("confirm_password", ""))
#             if len(password) < 8 or len(password) > 128:
#                 raise ValidationError({"password": "Use a password between 8 and 128 characters."})
#             if password != confirm_password:
#                 raise ValidationError({"confirm_password": "Passwords do not match."})
#             secret, provisioning_uri, qr_data_url = make_totp_setup(activation.email)
#             activation.pending_password_hash = make_password(password)
#             activation.pending_totp_secret_encrypted = encrypt_totp_secret(secret)
#             next_token = secrets.token_urlsafe(32)
#             activation.token_hash = hashlib.sha256(next_token.encode("utf-8")).hexdigest()
#             activation.save(update_fields=["pending_password_hash", "pending_totp_secret_encrypted", "token_hash"])
#             return Response({"message": "Password saved for setup. Scan the QR code and verify your authenticator.",
#                              "action": "verify_totp", "token": next_token, "email": activation.email,
#                              "provisioning_uri": provisioning_uri, "qr_code": qr_data_url})

#         if action != "complete":
#             raise ValidationError({"action": "Use setup or complete."})
#         if not activation.pending_password_hash or not activation.pending_totp_secret_encrypted:
#             raise ValidationError({"detail": "Complete the password setup stage first."})
#         try:
#             secret = decrypt_totp_secret(activation.pending_totp_secret_encrypted)
#         except ValueError:
#             raise ValidationError({"detail": "Authenticator setup could not be read. Restart account activation."})
#         code = str(request.data.get("code", "")).strip()
#         matched_step = matching_totp_step(secret, code)
#         if matched_step is None:
#             raise ValidationError({"code": "The authenticator code is invalid or expired."})
#         email = activation.email.strip().lower()
#         if Account.objects.filter(email__iexact=email).exists():
#             raise ValidationError({"email": "An account already exists for this email. Contact MedLife support."})
#         if DoctorProfile.objects.filter(registration_number=activation.registration_number).exists():
#             raise ValidationError({"registration_number": "This medical registration number is already associated with another doctor."})
#         account = Account.objects.create(
#             email=email, role=Account.Role.DOCTOR, password=activation.pending_password_hash,
#             totp_enabled=True, totp_secret_encrypted=activation.pending_totp_secret_encrypted,
#             totp_pending_secret_encrypted="", totp_last_verified_step=matched_step,
#         )
#         profile = DoctorProfile.objects.create(
#             account=account, doctor_id=f"MLD{account.pk:06d}", full_name=activation.full_name,
#             specialty=activation.specialty, qualifications=activation.qualifications,
#             registration_number=activation.registration_number, clinic_name=activation.clinic_name,
#             bio=activation.bio, years_experience=activation.years_experience,
#             status=DoctorProfile.Status.APPROVED, is_available=True, verified_at=timezone.now(),
#         )
#         activation.account = account
#         activation.consumed_at = timezone.now()
#         activation.pending_password_hash = ""
#         activation.pending_totp_secret_encrypted = ""
#         activation.save(update_fields=["account", "consumed_at", "pending_password_hash", "pending_totp_secret_encrypted"])
#         if activation.invitation_id:
#             activation.invitation.accepted_by = account
#             activation.invitation.save(update_fields=["accepted_by"])
#         _audit(account, "doctor_account_created", doctor=profile, metadata={"activation_id": activation.pk, "source": "application" if activation.application_id else "invitation"})
#         try:
#             send_mail(
#                 subject="Welcome to MedLife — your doctor account is ready",
#                 message=f"Hello {profile.full_name},\n\nYour MedLife doctor account has been created successfully. You can now sign in using {email} and your password.\n\nWelcome to MedLife!",
#                 from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False,
#             )
#         except Exception:
#             # Account creation is complete; a mail-server issue must not undo verified credentials.
#             pass
#     return Response({"message": "Doctor account created successfully. A confirmation email will be sent if email delivery is available.",
#                      "account_created": True, "doctor_id": profile.doctor_id})


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def admin_invitations(request):
#     # The submitted email is the invitee, not the signed-in administrator.
#     _require_staff(request.user, super_admin=True)
#     if request.method == "GET":
#         items = DoctorInvitation.objects.select_related("invited_by", "accepted_by").prefetch_related("activations").all()[:200]
#         return Response({"invitations": [{
#             "id": i.pk, "email": i.email,
#             "status": "expired" if i.status == DoctorInvitation.Status.PENDING and i.is_expired() else i.status,
#             "email_status": "sent",
#             "account_created": bool(i.accepted_by_id),
#             "activation_pending": bool(i.status == DoctorInvitation.Status.ACCEPTED and not i.accepted_by_id),
#             "expires_at": i.expires_at.isoformat(), "created_at": i.created_at.isoformat(),
#             "invited_by": i.invited_by.email,
#         } for i in items]})
#     email = str(request.data.get("email", "")).strip().lower()
#     if not email or "@" not in email or len(email) > 254:
#         raise ValidationError({"email": "Enter a valid email address."})
#     if Account.objects.filter(email__iexact=email).exists():
#         raise ValidationError({"email": "An account already exists for this email. A doctor invitation cannot replace an existing account."})
#     if DoctorInvitation.objects.filter(email__iexact=email, status=DoctorInvitation.Status.PENDING, expires_at__gt=timezone.now()).exists():
#         raise ValidationError({"email": "A valid pending invitation already exists for this email."})
#     token = secrets.token_urlsafe(32)
#     token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
#     invitation = DoctorInvitation.objects.create(
#         email=email, token_hash=token_hash, expires_at=timezone.now() + timedelta(days=7),
#         invited_by=request.user,
#     )
#     frontend_url = getattr(settings, "FRONTEND_DOCTOR_INVITATION_URL", "http://localhost:5173/doctor-invitation").rstrip("/")
#     invitation_url = f"{frontend_url}#token={token}"
#     try:
#         send_mail(
#             subject="Invitation to join MedLife as a doctor",
#             message=f"You have been invited to apply as a MedLife doctor. Open this secure link to accept or reject the invitation and, if accepted, create your doctor account: {invitation_url}\nThis invitation expires in 7 days.",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[email], fail_silently=False,
#         )
#     except Exception as exc:
#         invitation.delete()
#         raise InvitationEmailDeliveryError() from exc
#     _audit(request.user, "doctor_invitation_created", metadata={"invitation_id": invitation.pk, "email": email})
#     return Response({"message": "Invitation email sent.", "invitation_id": invitation.pk, "expires_at": invitation.expires_at.isoformat()}, status=status.HTTP_201_CREATED)


# @api_view(["POST"])
# @permission_classes([AllowAny])
# def accept_invitation(request):
#     """Accept/reject a Super Admin invitation without requiring a patient account."""
#     token = str(request.data.get("token", "")).strip()
#     decision = str(request.data.get("decision", "accept")).strip().lower()
#     if not token:
#         raise ValidationError({"token": "Invitation token is required."})
#     if decision not in ("accept", "reject"):
#         raise ValidationError({"decision": "Use accept or reject."})
#     token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
#     with transaction.atomic():
#         invitation = DoctorInvitation.objects.select_for_update().select_related("invited_by").filter(token_hash=token_hash).first()
#         if not invitation:
#             raise ValidationError({"token": "Invitation is invalid or expired."})
#         if invitation.status != DoctorInvitation.Status.PENDING or invitation.is_expired():
#             if invitation.status == DoctorInvitation.Status.PENDING and invitation.is_expired():
#                 invitation.status = DoctorInvitation.Status.EXPIRED
#                 invitation.save(update_fields=["status"])
#             raise ValidationError({"token": "Invitation is invalid, expired, or already used."})
#         if Account.objects.filter(email__iexact=invitation.email).exists():
#             raise ValidationError({"email": "An account already exists for this email. Contact MedLife support."})
#         if decision == "reject":
#             invitation.status = DoctorInvitation.Status.REJECTED
#             invitation.save(update_fields=["status"])
#             _audit(invitation.invited_by, "doctor_invitation_rejected", metadata={"invitation_id": invitation.pk, "email": invitation.email})
#             return Response({"message": "Invitation rejected. No account was created.", "status": invitation.status})

#         fields = {key: str(request.data.get(key, "")).strip() for key in ("full_name", "specialty", "qualifications", "registration_number")}
#         if not all(fields.values()):
#             raise ValidationError({"detail": "full_name, specialty, qualifications and registration_number are required when accepting an invitation."})
#         try:
#             years = int(request.data.get("years_experience", 0))
#             if years < 0 or years > 80:
#                 raise ValueError
#         except (TypeError, ValueError):
#             raise ValidationError({"years_experience": "Enter a number from 0 to 80."})
#         if DoctorProfile.objects.filter(registration_number=fields["registration_number"][:120]).exists():
#             raise ValidationError({"registration_number": "This medical registration number is already associated with another doctor."})
#         token_for_setup = secrets.token_urlsafe(32)
#         activation = DoctorAccountActivation.objects.create(
#             email=invitation.email.strip().lower(), invitation=invitation,
#             full_name=fields["full_name"][:150], specialty=fields["specialty"][:120],
#             qualifications=fields["qualifications"][:255], registration_number=fields["registration_number"][:120],
#             clinic_name=str(request.data.get("clinic_name", "")).strip()[:200],
#             bio=str(request.data.get("bio", "")).strip()[:5000], years_experience=years,
#             phone=str(request.data.get("phone", "")).strip()[:32], address=str(request.data.get("address", "")).strip()[:3000],
#             registration_authority=str(request.data.get("registration_authority", "")).strip()[:200],
#             token_hash=hashlib.sha256(token_for_setup.encode("utf-8")).hexdigest(),
#             expires_at=timezone.now() + timedelta(hours=24),
#         )
#         invitation.status = DoctorInvitation.Status.ACCEPTED
#         invitation.save(update_fields=["status"])
#         _audit(invitation.invited_by, "doctor_invitation_accepted", metadata={"invitation_id": invitation.pk, "activation_id": activation.pk})
#     return Response({"message": "Invitation accepted. Continue to create your doctor account.", "status": invitation.status,
#                      "activation_token": token_for_setup, "activation_expires_at": activation.expires_at.isoformat()}, status=status.HTTP_201_CREATED)


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def access_grants(request):
#     caller_email(request)
#     if request.user.role != Account.Role.PATIENT:
#         raise PermissionDenied("Patient account access is required.")
#     if request.method == "GET":
#         grants = DoctorAccessGrant.objects.filter(granted_by=request.user).select_related("member", "doctor__account")
#         return Response({"grants": [{
#             "id": g.pk, "member_id": g.member_id, "member_name": f"{g.member.first_name} {g.member.last_name}".strip(),
#             "doctor_id": g.doctor_id, "doctor_email": g.doctor.account.email,
#             "scopes": g.scopes, "active": g.active, "granted_at": g.granted_at.isoformat(),
#             "revoked_at": g.revoked_at.isoformat() if g.revoked_at else None,
#         } for g in grants]})
#     member = _member_for_owner(request.user, request.data.get("member_id"))
#     doctor = get_object_or_404(DoctorProfile, pk=request.data.get("doctor_id"), status=DoctorProfile.Status.APPROVED)
#     scopes = request.data.get("scopes")
#     grant = _ensure_grant(member, doctor, scopes)
#     _audit(request.user, "doctor_record_access_granted", member=member, doctor=doctor, metadata={"grant_id": grant.pk, "scopes": grant.scopes})
#     return Response({"grant_id": grant.pk, "member_id": member.pk, "doctor_id": doctor.pk, "scopes": grant.scopes, "active": grant.active}, status=status.HTTP_201_CREATED)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def revoke_access_grant(request, grant_id):
#     caller_email(request)
#     if request.user.role != Account.Role.PATIENT:
#         raise PermissionDenied("Patient account access is required.")
#     grant = get_object_or_404(DoctorAccessGrant, pk=grant_id, granted_by=request.user)
#     if grant.active:
#         grant.active = False
#         grant.revoked_at = timezone.now()
#         grant.save(update_fields=["active", "revoked_at"])
#         _audit(request.user, "doctor_record_access_revoked", member=grant.member, doctor=grant.doctor, metadata={"grant_id": grant.pk})
#     return Response({"message": "Medical-record access revoked.", "grant_id": grant.pk, "active": False})


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def shared_records(request, member_id):
#     caller_email(request)
#     doctor = _doctor_for(request.user)
#     member = get_object_or_404(FamilyMember, pk=member_id)
#     grant = _active_grant(member, doctor, "profile")
#     if not grant:
#         raise PermissionDenied("The patient has not granted active access to this member's profile.")
#     _audit(request.user, "doctor_shared_records_viewed", member=member, doctor=doctor, metadata={"scopes": grant.scopes})
#     data = {
#         "member_id": member.pk,
#         "member_name": f"{member.first_name} {member.last_name}".strip(),
#         "height": member.height, "weight": member.weight, "blood_pressure": member.blood_pressure,
#         "a1c": str(member.a1c) if member.a1c is not None else None,
#         "medicine": member.medicine, "medical_description": member.medical_description,
#         "consent_scopes": grant.scopes,
#     }
#     if grant.permits("documents"):
#         data["documents"] = [{
#             "id": doc.pk, "document_type": doc.document_type, "description": doc.description,
#             "is_confirmed": doc.is_confirmed, "created_at": doc.created_at.isoformat(),
#         } for doc in ScannedDocument.objects.filter(account=member.account, member=member).order_by("-created_at")[:100]]
#     if grant.permits("consultation_notes"):
#         data["consultation_notes"] = [{
#             "appointment_id": note.appointment_id, "content": note.content,
#             "created_at": note.created_at.isoformat(), "updated_at": note.updated_at.isoformat(),
#         } for note in ConsultationNote.objects.filter(member=member).select_related("appointment").order_by("-updated_at")[:100]]
#     return Response(data)


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def appointments(request):
#     caller_email(request)
#     if request.method == "GET":
#         role = request.query_params.get("role", "patient").strip().lower()
#         if role == "admin":
#             _require_staff(request.user, super_admin=True)
#             qs = Appointment.objects.all()
#         elif role == "doctor":
#             doctor = _doctor_for(request.user)
#             qs = Appointment.objects.filter(doctor=doctor)
#         elif role == "patient":
#             if request.user.role != Account.Role.PATIENT:
#                 raise PermissionDenied("Patient account access is required.")
#             qs = Appointment.objects.filter(requested_by=request.user)
#         else:
#             raise ValidationError({"role": "Use patient, doctor or admin."})

#         state = request.query_params.get("status", "").strip().lower()
#         if state:
#             if state not in Appointment.Status.values:
#                 raise ValidationError({"status": "Invalid appointment status."})
#             qs = qs.filter(status=state)
#         doctor_id = request.query_params.get("doctor_id")
#         patient_id = request.query_params.get("patient_id")
#         date_from = request.query_params.get("date_from")
#         date_to = request.query_params.get("date_to")
#         if doctor_id:
#             qs = qs.filter(doctor_id=doctor_id)
#         if patient_id:
#             qs = qs.filter(member__account_id=patient_id)
#         if date_from:
#             from django.utils.dateparse import parse_date
#             parsed = parse_date(date_from)
#             if not parsed: raise ValidationError({"date_from": "Use YYYY-MM-DD."})
#             qs = qs.filter(preferred_at__date__gte=parsed)
#         if date_to:
#             from django.utils.dateparse import parse_date
#             parsed = parse_date(date_to)
#             if not parsed: raise ValidationError({"date_to": "Use YYYY-MM-DD."})
#             qs = qs.filter(preferred_at__date__lte=parsed)
#         try:
#             limit = min(max(int(request.query_params.get("limit", "100")), 1), 200)
#         except (TypeError, ValueError):
#             raise ValidationError({"limit": "Use an integer from 1 to 200."})
#         items = qs.select_related("member", "member__account", "doctor__account", "requested_by", "booked_by").order_by("-created_at", "-id")[:limit]
#         result = []
#         for a in items:
#             item = _appointment_data(a)
#             # Administrative overview needs booking metadata, not patient-entered clinical narrative.
#             item.pop("reason", None)
#             item.pop("patient_note", None)
#             item.update({
#                 "patient_account_id": a.member.account_id,
#                 "patient_email": a.member.account.email,
#                 "doctor_name": a.doctor.full_name,
#                 "doctor_email": a.doctor.account.email,
#                 "requested_by_email": a.requested_by.email,
#                 "booked_by_email": a.booked_by.email if a.booked_by_id else None,
#             })
#             result.append(item)
#         return Response({"appointments": result, "limit": limit})

#     if request.user.role == Account.Role.SUPER_ADMIN:
#         _require_staff(request.user, super_admin=True)
#         member = get_object_or_404(FamilyMember.objects.select_related("account"), pk=request.data.get("member_id"))
#         if member.account.role != Account.Role.PATIENT:
#             raise ValidationError({"member_id": "Choose a family profile belonging to an existing patient account."})
#         doctor = get_object_or_404(DoctorProfile, pk=request.data.get("doctor_id"), status=DoctorProfile.Status.APPROVED, is_available=True)
#         preferred_at = _parse_datetime(request.data.get("preferred_at"), "preferred_at")
#         if preferred_at <= timezone.now():
#             raise ValidationError({"preferred_at": "Choose a future date and time."})
#         if not _active_grant(member, doctor, "profile"):
#             raise PermissionDenied("The patient must have an active profile-sharing consent for this doctor before an appointment can be booked.")
#         with transaction.atomic():
#             appointment = Appointment.objects.create(
#                 member=member, doctor=doctor, requested_by=member.account, booked_by=request.user,
#                 preferred_at=preferred_at, reason=str(request.data.get("reason", "")).strip()[:1000],
#                 patient_note=str(request.data.get("patient_note", "")).strip()[:2000],
#             )
#             _record_appointment_history(appointment, request.user, "admin_booked", "", appointment.status,
#                                         reason=str(request.data.get("reason", "")).strip()[:1000],
#                                         metadata={"patient_account_id": member.account_id, "member_id": member.pk})
#             _audit(request.user, "admin_appointment_booked", member=member, doctor=doctor,
#                    metadata={"appointment_id": appointment.pk, "patient_account_id": member.account_id})
#             _notify(doctor.account, "appointment_requested", "New appointment request", "An appointment has been booked for a patient and awaits your decision.", appointment=appointment)
#             _notify(member.account, "appointment_requested", "Appointment request created", "An appointment request was created for your family profile.", appointment=appointment)
#         return Response({"appointment": _appointment_data(appointment)}, status=status.HTTP_201_CREATED)

#     member = _member_for_owner(request.user, request.data.get("member_id"))
#     doctor = get_object_or_404(DoctorProfile, pk=request.data.get("doctor_id"), status=DoctorProfile.Status.APPROVED, is_available=True)
#     preferred_at = _parse_datetime(request.data.get("preferred_at"), "preferred_at")
#     if preferred_at <= timezone.now():
#         raise ValidationError({"preferred_at": "Choose a future date and time."})
#     scopes = request.data.get("consent_scopes")
#     with transaction.atomic():
#         grant = _ensure_grant(member, doctor, scopes)
#         _audit(request.user, "doctor_record_access_granted", member=member, doctor=doctor, metadata={"grant_id": grant.pk, "scopes": grant.scopes, "source": "appointment"})
#         appointment = Appointment.objects.create(
#             member=member, doctor=doctor, requested_by=request.user, preferred_at=preferred_at,
#             reason=str(request.data.get("reason", "")).strip()[:1000],
#             patient_note=str(request.data.get("patient_note", "")).strip()[:2000],
#         )
#         _record_appointment_history(appointment, request.user, "created", "", appointment.status, reason=appointment.reason)
#         _notify(doctor.account, "appointment_requested", "New appointment request", "A patient has requested an appointment.", appointment=appointment)
#         _notify(request.user, "appointment_requested", "Appointment request submitted", "Your appointment request is awaiting the doctor's decision.", appointment=appointment)
#     return Response({"appointment": _appointment_data(appointment)}, status=status.HTTP_201_CREATED)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def appointment_decision(request, appointment_id):
#     caller_email(request)
#     doctor = _doctor_for(request.user)
#     decision = str(request.data.get("decision", "")).strip().lower()
#     if decision not in ("accept", "reject"):
#         raise ValidationError({"decision": "Use accept or reject."})
#     with transaction.atomic():
#         appointment = get_object_or_404(Appointment.objects.select_for_update().select_related("member", "doctor__account", "requested_by"), pk=appointment_id, doctor=doctor)
#         if appointment.status != Appointment.Status.REQUESTED:
#             raise ValidationError({"detail": "Only requested appointments can be accepted or rejected."})
#         previous_status = appointment.status
#         if decision == "accept":
#             if not _active_grant(appointment.member, doctor, "profile"):
#                 raise PermissionDenied("The patient's record-sharing consent is no longer active.")
#             scheduled = _parse_datetime(request.data.get("scheduled_at"), "scheduled_at")
#             if scheduled <= timezone.now():
#                 raise ValidationError({"scheduled_at": "Choose a future date and time."})
#             conflict = Appointment.objects.filter(
#                 doctor=doctor, status=Appointment.Status.ACCEPTED, scheduled_at=scheduled,
#             ).exclude(pk=appointment.pk).exists()
#             if conflict:
#                 raise ValidationError({"scheduled_at": "The doctor already has an appointment at that time."})
#             appointment.status = Appointment.Status.ACCEPTED
#             appointment.scheduled_at = scheduled
#         else:
#             appointment.status = Appointment.Status.REJECTED
#         appointment.doctor_response = str(request.data.get("doctor_response", "")).strip()[:1000]
#         appointment.decided_at = timezone.now()
#         appointment.save()
#         _record_appointment_history(appointment, request.user, "doctor_decision", previous_status, appointment.status,
#                                     reason=appointment.doctor_response)
#         _audit(request.user, f"appointment_{appointment.status}", member=appointment.member, doctor=doctor,
#                metadata={"appointment_id": appointment.pk, "decision": decision})
#         _notify(appointment.requested_by, f"appointment_{appointment.status}", f"Appointment {appointment.status}", "Your appointment request status has changed.", appointment=appointment)
#         _notify(doctor.account, f"appointment_{appointment.status}", f"Appointment {appointment.status}", "The appointment request was updated.", appointment=appointment)
#     return Response({"appointment": _appointment_data(appointment)})


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def cancel_appointment(request, appointment_id):
#     caller_email(request)
#     appointment = get_object_or_404(Appointment.objects.select_related("doctor__account", "member", "requested_by"), pk=appointment_id)
#     is_patient = appointment.requested_by_id == request.user.pk and request.user.role == Account.Role.PATIENT
#     is_doctor = appointment.doctor.account_id == request.user.pk and request.user.role == Account.Role.DOCTOR
#     if is_doctor:
#         doctor = _doctor_for(request.user)
#         is_doctor = doctor.pk == appointment.doctor_id
#     if not (is_patient or is_doctor):
#         raise PermissionDenied("You cannot cancel this appointment.")
#     if appointment.status not in (Appointment.Status.REQUESTED, Appointment.Status.ACCEPTED):
#         raise ValidationError({"detail": "Only requested or accepted appointments can be cancelled."})
#     previous_status = appointment.status
#     appointment.status = Appointment.Status.CANCELLED
#     cancellation_reason = str(request.data.get("reason", "")).strip()[:1000] if is_doctor else ""
#     appointment.doctor_response = cancellation_reason or appointment.doctor_response
#     appointment.save(update_fields=["status", "doctor_response", "updated_at"])
#     _record_appointment_history(appointment, request.user, "cancelled", previous_status, appointment.status, reason=cancellation_reason)
#     _audit(request.user, "appointment_cancelled", member=appointment.member, doctor=appointment.doctor,
#            metadata={"appointment_id": appointment.pk})
#     recipient = appointment.doctor.account if is_patient else appointment.requested_by
#     _notify(recipient, "appointment_cancelled", "Appointment cancelled", "An appointment has been cancelled.", appointment=appointment)
#     return Response({"appointment": _appointment_data(appointment)})


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def complete_appointment(request, appointment_id):
#     caller_email(request)
#     doctor = _doctor_for(request.user)
#     appointment = get_object_or_404(Appointment.objects.select_related("member", "doctor__account", "requested_by"), pk=appointment_id, doctor=doctor)
#     if appointment.status != Appointment.Status.ACCEPTED:
#         raise ValidationError({"detail": "Only accepted appointments can be marked completed."})
#     previous_status = appointment.status
#     appointment.status = Appointment.Status.COMPLETED
#     appointment.completed_at = timezone.now()
#     appointment.save(update_fields=["status", "completed_at", "updated_at"])
#     _record_appointment_history(appointment, request.user, "completed", previous_status, appointment.status)
#     _audit(request.user, "appointment_completed", member=appointment.member, doctor=doctor,
#            metadata={"appointment_id": appointment.pk})
#     _notify(appointment.requested_by, "appointment_completed", "Appointment completed", "Your appointment has been marked completed.", appointment=appointment)
#     return Response({"appointment": _appointment_data(appointment)})


# @api_view(["GET", "PUT", "POST"])
# @permission_classes([IsAuthenticated])
# def consultation_note(request, appointment_id):
#     caller_email(request)
#     appointment = get_object_or_404(Appointment.objects.select_related("member", "doctor__account", "requested_by"), pk=appointment_id)
#     is_patient = appointment.requested_by_id == request.user.pk and request.user.role == Account.Role.PATIENT
#     is_doctor = appointment.doctor.account_id == request.user.pk and request.user.role == Account.Role.DOCTOR
#     if is_doctor:
#         doctor = _doctor_for(request.user)
#         is_doctor = doctor.pk == appointment.doctor_id
#     grant = _active_grant(appointment.member, appointment.doctor, "consultation_notes")
#     if request.method == "GET":
#         if not is_patient and not (is_doctor and grant):
#             raise PermissionDenied("You are not authorized to view this consultation note.")
#         note = get_object_or_404(ConsultationNote, appointment=appointment)
#         _audit(request.user, "consultation_note_viewed", member=appointment.member, doctor=appointment.doctor, metadata={"appointment_id": appointment.pk})
#         return Response({"appointment_id": appointment.pk, "content": note.content, "created_at": note.created_at.isoformat(), "updated_at": note.updated_at.isoformat()})
#     if not is_doctor or not grant:
#         raise PermissionDenied("Only the assigned doctor with active note-sharing consent can write consultation notes.")
#     if appointment.status not in (Appointment.Status.ACCEPTED, Appointment.Status.COMPLETED):
#         raise ValidationError({"detail": "Consultation notes can be written after an appointment is accepted."})
#     content = str(request.data.get("content", "")).strip()
#     if not content:
#         raise ValidationError({"content": "Consultation note content is required."})
#     note, created = ConsultationNote.objects.update_or_create(
#         appointment=appointment,
#         defaults={"doctor": appointment.doctor, "member": appointment.member, "content": content[:20000]},
#     )
#     _audit(request.user, "consultation_note_updated", member=appointment.member, doctor=appointment.doctor, metadata={"appointment_id": appointment.pk})
#     _notify(appointment.requested_by, "consultation_note_updated", "Consultation note updated", "A consultation note is available in MedLife.", appointment=appointment)
#     return Response({"appointment_id": appointment.pk, "content": note.content, "created_at": note.created_at.isoformat(), "updated_at": note.updated_at.isoformat()}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def chat_requests(request):
#     caller_email(request)
#     if request.method == "GET":
#         role = request.query_params.get("role", "patient").strip().lower()
#         if role == "doctor":
#             doctor = _doctor_for(request.user)
#             qs = DoctorChatRequest.objects.filter(doctor=doctor)
#         elif role == "patient":
#             if request.user.role != Account.Role.PATIENT:
#                 raise PermissionDenied("Patient account access is required.")
#             qs = DoctorChatRequest.objects.filter(requested_by=request.user)
#         else:
#             raise ValidationError({"role": "Use patient or doctor."})
#         state = request.query_params.get("status", "").strip().lower()
#         if state:
#             if state not in DoctorChatRequest.Status.values:
#                 raise ValidationError({"status": "Invalid chat request status."})
#             qs = qs.filter(status=state)
#         return Response({"chat_requests": [_chat_request_data(c) for c in qs.select_related("member", "doctor__account")]})

#     member = _member_for_owner(request.user, request.data.get("member_id"))
#     doctor = get_object_or_404(DoctorProfile, pk=request.data.get("doctor_id"), status=DoctorProfile.Status.APPROVED, is_available=True)
#     scopes = request.data.get("consent_scopes")
#     with transaction.atomic():
#         grant = _ensure_grant(member, doctor, scopes)
#         _audit(request.user, "doctor_record_access_granted", member=member, doctor=doctor, metadata={"grant_id": grant.pk, "scopes": grant.scopes, "source": "chat"})
#         chat = DoctorChatRequest.objects.create(
#             member=member, doctor=doctor, requested_by=request.user,
#             message=str(request.data.get("message", "")).strip()[:1000],
#         )
#         _notify(doctor.account, "chat_requested", "New online consultation request", "A patient has requested an online consultation.", chat_request=chat)
#         _notify(request.user, "chat_requested", "Online consultation request submitted", "Your request is awaiting the doctor's decision.", chat_request=chat)
#     return Response({"chat_request": _chat_request_data(chat)}, status=status.HTTP_201_CREATED)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def chat_request_decision(request, chat_request_id):
#     caller_email(request)
#     doctor = _doctor_for(request.user)
#     decision = str(request.data.get("decision", "")).strip().lower()
#     if decision not in ("accept", "reject"):
#         raise ValidationError({"decision": "Use accept or reject."})
#     chat = get_object_or_404(DoctorChatRequest.objects.select_related("member", "doctor__account", "requested_by"), pk=chat_request_id, doctor=doctor)
#     if chat.status != DoctorChatRequest.Status.REQUESTED:
#         raise ValidationError({"detail": "Only requested chats can be accepted or rejected."})
#     if decision == "accept":
#         if not _active_grant(chat.member, doctor, "profile"):
#             raise PermissionDenied("The patient's record-sharing consent is no longer active.")
#         chat.status = DoctorChatRequest.Status.ACCEPTED
#     else:
#         chat.status = DoctorChatRequest.Status.REJECTED
#     chat.decided_at = timezone.now()
#     chat.save(update_fields=["status", "decided_at", "updated_at"])
#     _notify(chat.requested_by, f"chat_{chat.status}", f"Online consultation {chat.status}", "Your online consultation request status has changed.", chat_request=chat)
#     _notify(doctor.account, f"chat_{chat.status}", f"Online consultation {chat.status}", "The online consultation request was updated.", chat_request=chat)
#     return Response({"chat_request": _chat_request_data(chat)})


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def chat_messages(request, chat_request_id):
#     caller_email(request)
#     chat = get_object_or_404(DoctorChatRequest.objects.select_related("member", "doctor__account", "requested_by"), pk=chat_request_id)
#     is_patient = chat.requested_by_id == request.user.pk and request.user.role == Account.Role.PATIENT
#     is_doctor = chat.doctor.account_id == request.user.pk and request.user.role == Account.Role.DOCTOR
#     if is_doctor:
#         doctor = _doctor_for(request.user)
#         is_doctor = doctor.pk == chat.doctor_id
#     if not (is_patient or is_doctor):
#         raise PermissionDenied("You are not a participant in this conversation.")
#     if chat.status != DoctorChatRequest.Status.ACCEPTED:
#         raise ValidationError({"detail": "Messaging is available only after the doctor accepts the request."})
#     if not _active_grant(chat.member, chat.doctor, "profile"):
#         raise PermissionDenied("The patient's record-sharing consent is no longer active.")
#     if request.method == "POST":
#         text = str(request.data.get("text", "")).strip()
#         if not text or len(text) > 20000:
#             raise ValidationError({"text": "Message must contain 1 to 20000 characters."})
#         msg = DoctorChatMessage.objects.create(chat_request=chat, sender=request.user, text=text)
#         _audit(request.user, "doctor_chat_message_sent", member=chat.member, doctor=chat.doctor, metadata={"chat_request_id": chat.pk, "message_id": msg.pk})
#         other = chat.doctor.account if is_patient else chat.requested_by
#         _notify(other, "doctor_chat_message", "New consultation message", "You have a new message in MedLife.", chat_request=chat)
#         return Response({"message": {"id": msg.pk, "sender_email": request.user.email, "text": msg.text, "created_at": msg.created_at.isoformat()}}, status=status.HTTP_201_CREATED)
#     messages = chat.messages.select_related("sender").all()[:500]
#     return Response({"messages": [{
#         "id": m.pk, "sender_email": m.sender.email, "text": m.text, "created_at": m.created_at.isoformat(),
#     } for m in messages]})


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def notifications(request):
#     caller_email(request)
#     qs = DoctorNotification.objects.filter(recipient=request.user)
#     unread = request.query_params.get("unread", "").lower()
#     if unread in ("1", "true", "yes"):
#         qs = qs.filter(read_at__isnull=True)
#     qs = qs[:200]
#     return Response({"notifications": [{
#         "id": n.pk, "kind": n.kind, "title": n.title, "message": n.message,
#         "appointment_id": n.appointment_id, "chat_request_id": n.chat_request_id,
#         "is_read": n.read_at is not None, "created_at": n.created_at.isoformat(),
#         "read_at": n.read_at.isoformat() if n.read_at else None,
#     } for n in qs]})


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def mark_notification_read(request, notification_id):
#     caller_email(request)
#     notification = get_object_or_404(DoctorNotification, pk=notification_id, recipient=request.user)
#     if notification.read_at is None:
#         notification.read_at = timezone.now()
#         notification.save(update_fields=["read_at"])
#     return Response({"id": notification.pk, "is_read": True, "read_at": notification.read_at.isoformat()})


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def cancel_chat_request(request, chat_request_id):
#     caller_email(request)
#     chat = get_object_or_404(
#         DoctorChatRequest.objects.select_related("doctor__account", "member", "requested_by"),
#         pk=chat_request_id,
#     )
#     is_patient = chat.requested_by_id == request.user.pk and request.user.role == Account.Role.PATIENT
#     is_doctor = chat.doctor.account_id == request.user.pk and request.user.role == Account.Role.DOCTOR
#     if is_doctor:
#         doctor = _doctor_for(request.user)
#         is_doctor = doctor.pk == chat.doctor_id
#     if not (is_patient or is_doctor):
#         raise PermissionDenied("You cannot cancel this chat request.")
#     if chat.status not in (DoctorChatRequest.Status.REQUESTED, DoctorChatRequest.Status.ACCEPTED):
#         raise ValidationError({"detail": "Only requested or accepted chat requests can be cancelled."})
#     chat.status = DoctorChatRequest.Status.CANCELLED
#     chat.save(update_fields=["status", "updated_at"])
#     recipient = chat.doctor.account if is_patient else chat.requested_by
#     _notify(recipient, "chat_cancelled", "Online consultation cancelled", "An online consultation request has been cancelled.", chat_request=chat)
#     _audit(request.user, "doctor_chat_request_cancelled", member=chat.member, doctor=chat.doctor, metadata={"chat_request_id": chat.pk})
#     return Response({"chat_request": _chat_request_data(chat)})


# # ---------------------------------------------------------------------------
# # Super-admin dashboard APIs. All endpoints require the persisted super_admin role.
# # ---------------------------------------------------------------------------
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def admin_dashboard_overview(request):
#     caller_email(request)
#     _require_staff(request.user, super_admin=True)
#     now = timezone.now()
#     month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#     patients = Account.objects.filter(role=Account.Role.PATIENT)
#     doctors = DoctorProfile.objects.select_related("account")
#     applications = DoctorApplication.objects.all()
#     appointments_qs = Appointment.objects.all()
#     status_counts = {key: 0 for key in Appointment.Status.values}
#     for row in appointments_qs.values("status").annotate(total=Count("id")):
#         status_counts[row["status"]] = row["total"]
#     recent_audit = DoctorAuditLog.objects.select_related("actor", "doctor").order_by("-created_at", "-id")[:10]
#     recent_appointments = AppointmentHistory.objects.select_related("actor", "appointment").order_by("-created_at", "-id")[:10]
#     activity = [{
#         "id": f"audit-{item.pk}", "source": "admin_audit", "action": item.action,
#         "actor": item.actor.email, "created_at": item.created_at.isoformat(),
#         "doctor_id": item.doctor_id, "metadata": item.metadata,
#     } for item in recent_audit]
#     activity.extend([{
#         "id": f"appointment-{item.pk}", "source": "appointment_history", "action": item.action,
#         "actor": item.actor.email if item.actor_id else None, "created_at": item.created_at.isoformat(),
#         "appointment_id": item.appointment_id, "from_status": item.from_status,
#         "to_status": item.to_status, "reason": item.reason,
#     } for item in recent_appointments])
#     activity.sort(key=lambda x: x["created_at"], reverse=True)
#     return Response({
#         "totals": {
#             "patients": patients.count(),
#             "doctors": doctors.count(),
#             "pending_applications": applications.filter(status=DoctorApplication.Status.PENDING).count(),
#         },
#         "doctors_by_status": {row["status"]: row["total"] for row in doctors.values("status").annotate(total=Count("id"))},
#         "applications_by_status": {row["status"]: row["total"] for row in applications.values("status").annotate(total=Count("id"))},
#         "appointments_by_status": status_counts,
#         "appointments_today": appointments_qs.filter(preferred_at__date=now.date()).count(),
#         "appointments_this_month": appointments_qs.filter(created_at__gte=month_start).count(),
#         "recent_activity": activity[:10],
#         "pending_application_alerts": [{
#             "id": app.pk, "name": app.full_name, "email": app.email,
#             "specialty": app.specialty, "created_at": app.created_at.isoformat(),
#         } for app in applications.filter(status=DoctorApplication.Status.PENDING).order_by("created_at", "id")[:10]],
#         "generated_at": now.isoformat(),
#     })


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def admin_doctors(request):
#     caller_email(request)
#     _require_staff(request.user, super_admin=True)
#     if request.method == "POST":
#         doctor_id = request.data.get("doctor_id")
#         action = str(request.data.get("action", "")).strip().lower()
#         reason = str(request.data.get("reason", "")).strip()[:1000]
#         if action not in ("suspend", "reactivate"):
#             raise ValidationError({"action": "Use suspend or reactivate."})
#         with transaction.atomic():
#             profile = get_object_or_404(DoctorProfile.objects.select_for_update().select_related("account"), pk=doctor_id)
#             previous = profile.status
#             if action == "suspend":
#                 if previous != DoctorProfile.Status.APPROVED:
#                     raise ValidationError({"detail": "Only approved doctors can be suspended."})
#                 profile.status = DoctorProfile.Status.SUSPENDED
#                 profile.is_available = False
#             else:
#                 if previous != DoctorProfile.Status.SUSPENDED:
#                     raise ValidationError({"detail": "Only suspended doctors can be reactivated."})
#                 profile.status = DoctorProfile.Status.APPROVED
#             profile.save(update_fields=["status", "is_available", "updated_at"])
#             _audit(request.user, f"doctor_{action}ed" if action == "suspend" else "doctor_reactivated",
#                    doctor=profile, metadata={"previous_status": previous, "new_status": profile.status, "reason": reason})
#         return Response({"doctor": _admin_doctor_data(profile), "action": action})

#     qs = DoctorProfile.objects.select_related("account").all()
#     query = str(request.query_params.get("q", "")).strip()
#     state = str(request.query_params.get("status", "")).strip().lower()
#     available = str(request.query_params.get("available", "")).strip().lower()
#     if query:
#         qs = qs.filter(Q(full_name__icontains=query) | Q(account__email__icontains=query) |
#                        Q(specialty__icontains=query) | Q(registration_number__icontains=query) |
#                        Q(doctor_id__icontains=query))
#     if state:
#         if state not in DoctorProfile.Status.values:
#             raise ValidationError({"status": "Invalid doctor status."})
#         qs = qs.filter(status=state)
#     if available in ("true", "false"):
#         qs = qs.filter(is_available=(available == "true"))
#     return Response({"doctors": [_admin_doctor_data(item) for item in qs.order_by("full_name", "id")[:200]]})


# def _admin_doctor_data(profile):
#     return {
#         "id": profile.pk, "doctor_id": profile.doctor_id, "account_id": profile.account_id,
#         "email": profile.account.email, "full_name": profile.full_name, "specialty": profile.specialty,
#         "qualifications": profile.qualifications, "registration_number": profile.registration_number,
#         "clinic_name": profile.clinic_name, "years_experience": profile.years_experience,
#         "status": profile.status, "is_available": profile.is_available,
#         "verified_at": profile.verified_at.isoformat() if profile.verified_at else None,
#         "created_at": profile.created_at.isoformat(), "updated_at": profile.updated_at.isoformat(),
#         "appointments_total": profile.appointments.count(),
#         "appointments_completed": profile.appointments.filter(status=Appointment.Status.COMPLETED).count(),
#         "appointments_pending": profile.appointments.filter(status=Appointment.Status.REQUESTED).count(),
#     }


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def admin_patients(request):
#     caller_email(request)
#     _require_staff(request.user, super_admin=True)
#     qs = Account.objects.filter(role=Account.Role.PATIENT).annotate(family_profile_count=Count("members", distinct=True))
#     query = str(request.query_params.get("q", "")).strip()
#     if query:
#         qs = qs.filter(email__icontains=query)
#     patients = [{
#         "id": account.pk, "email": account.email,
#         "created_at": account.created_at.isoformat(),
#         "account_status": "registered",
#         "family_profile_count": account.family_profile_count,
#     } for account in qs.order_by("-created_at", "-id")[:200]]
#     return Response({"patients": patients})


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def admin_analytics(request):
#     caller_email(request)
#     _require_staff(request.user, super_admin=True)
#     months = []
#     now = timezone.now()
#     for offset in range(5, -1, -1):
#         year = now.year
#         month = now.month - offset
#         while month <= 0:
#             month += 12
#             year -= 1
#         months.append((year, month))
#     first_year, first_month = months[0]
#     start = now.replace(year=first_year, month=first_month, day=1, hour=0, minute=0, second=0, microsecond=0)
#     def monthly_counts(qs, field):
#         counts = {}
#         for row in qs.filter(**{f"{field}__gte": start}).annotate(month=TruncMonth(field)).values("month").annotate(total=Count("id")):
#             counts[row["month"].strftime("%Y-%m")] = row["total"]
#         return [{"month": f"{year:04d}-{month:02d}", "count": counts.get(f"{year:04d}-{month:02d}", 0)} for year, month in months]
#     return Response({
#         "period": "last_6_calendar_months",
#         "patient_registrations": monthly_counts(Account.objects.filter(role=Account.Role.PATIENT), "created_at"),
#         "doctor_registrations": monthly_counts(DoctorProfile.objects.all(), "created_at"),
#         "doctor_applications": monthly_counts(DoctorApplication.objects.all(), "created_at"),
#         "appointment_bookings": monthly_counts(Appointment.objects.all(), "created_at"),
#         "generated_at": now.isoformat(),
#     })


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def admin_audit_log(request):
#     caller_email(request)
#     _require_staff(request.user, super_admin=True)
#     action = str(request.query_params.get("action", "")).strip()
#     actor = str(request.query_params.get("actor", "")).strip()
#     limit_raw = request.query_params.get("limit", "100")
#     try:
#         limit = min(max(int(limit_raw), 1), 200)
#     except (TypeError, ValueError):
#         raise ValidationError({"limit": "Use an integer from 1 to 200."})
#     logs = DoctorAuditLog.objects.select_related("actor", "doctor").all()
#     if action:
#         logs = logs.filter(action__icontains=action)
#     if actor:
#         logs = logs.filter(actor__email__icontains=actor)
#     audit_items = [{
#         "id": item.pk, "source": "admin_audit", "actor": item.actor.email,
#         "action": item.action, "created_at": item.created_at.isoformat(),
#         "doctor_id": item.doctor_id, "member_id": item.member_id, "metadata": item.metadata,
#     } for item in logs.order_by("-created_at", "-id")[:limit]]
#     history = AppointmentHistory.objects.select_related("actor").all()
#     if actor:
#         history = history.filter(actor__email__icontains=actor)
#     if action:
#         history = history.filter(action__icontains=action)
#     audit_items.extend([{
#         "id": item.pk, "source": "appointment_history", "actor": item.actor.email if item.actor_id else None,
#         "action": item.action, "created_at": item.created_at.isoformat(),
#         "appointment_id": item.appointment_id, "from_status": item.from_status,
#         "to_status": item.to_status, "reason": item.reason, "metadata": item.metadata,
#     } for item in history.order_by("-created_at", "-id")[:limit]])
#     audit_items.sort(key=lambda item: item["created_at"], reverse=True)
#     return Response({"events": audit_items[:limit], "limit": limit})


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def admin_appointment_history(request, appointment_id):
#     caller_email(request)
#     _require_staff(request.user, super_admin=True)
#     get_object_or_404(Appointment, pk=appointment_id)
#     items = AppointmentHistory.objects.filter(appointment_id=appointment_id).select_related("actor")
#     return Response({"history": [{
#         "id": item.pk, "actor": item.actor.email if item.actor_id else None,
#         "action": item.action, "from_status": item.from_status, "to_status": item.to_status,
#         "reason": item.reason, "metadata": item.metadata, "created_at": item.created_at.isoformat(),
#     } for item in items]})








import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import FileResponse, Http404, HttpResponse
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Account
from apps.core.identity import caller_email
from apps.documents.models import ScannedDocument
from apps.members.models import FamilyMember
from apps.accounts.totp import decrypt_totp_secret, encrypt_totp_secret, make_totp_setup, matching_totp_step
from .models import (
    Appointment, AppointmentHistory, AppointmentRescheduleRequest, ConsultationNote, ConsultationNoteRevision,
    DoctorAccessGrant, DoctorApplication, DoctorAccountActivation, DoctorApplicationDocument, DoctorAuditLog,
    DoctorAvailabilitySlot, DoctorChatMessage, DoctorChatRequest, DoctorInvitation, DoctorNotification, DoctorProfile,
)


class InvitationEmailDeliveryError(APIException):
    status_code = 503
    default_detail = "Invitation email could not be sent. Check the email configuration and try again."
    default_code = "email_delivery_failed"


def _email(account):
    return (account.email or "").strip().lower()


def _staff_role(account):
    # The persisted MedLife role is authoritative. Legacy email allowlists are not authorization.
    return "super_admin" if getattr(account, "role", "") == Account.Role.SUPER_ADMIN else ""


def _require_staff(account, super_admin=False):
    role = _staff_role(account)
    if not role:
        raise PermissionDenied("You are not authorized to perform this action.")
    return role


def _doctor_for(account):
    if getattr(account, "role", "") != Account.Role.DOCTOR:
        raise PermissionDenied("A doctor account is required.")
    profile = DoctorProfile.objects.filter(account=account, status=DoctorProfile.Status.APPROVED).first()
    if not profile:
        raise PermissionDenied("An approved doctor profile is required.")
    return profile


def _member_for_owner(account, member_id):
    if getattr(account, "role", "") != Account.Role.PATIENT:
        raise PermissionDenied("Patient account access is required.")
    # Accept the database PK (preferred) or legacy account-relative slot.
    # Both lookups remain scoped to the authenticated account.
    try:
        value = int(member_id)
    except (TypeError, ValueError):
        raise Http404("No FamilyMember matches the given query.")
    members = FamilyMember.objects.filter(account=account)
    member = members.filter(pk=value).first() or members.filter(slot=value).first()
    if member is None:
        raise Http404("No FamilyMember matches the given query.")
    return member


def _active_grant(member, doctor, scope=None):
    grants = DoctorAccessGrant.objects.filter(member=member, doctor=doctor, granted_by=member.account, active=True)
    for grant in grants.order_by("-granted_at", "-id"):
        if scope is None or grant.permits(scope):
            return grant
    return None


def _ensure_grant(member, doctor, scopes):
    allowed = set(DoctorAccessGrant.ALLOWED_SCOPES)
    if not isinstance(scopes, list) or not scopes or any(not isinstance(x, str) for x in scopes):
        raise ValidationError({"consent_scopes": "Select at least one record-sharing permission explicitly."})
    normalized = sorted(set(scopes))
    if any(scope not in allowed for scope in normalized):
        raise ValidationError({"consent_scopes": "One or more consent scopes are invalid."})
    if "profile" not in normalized:
        raise ValidationError({"consent_scopes": "The profile scope is required for a consultation request."})
    grant = DoctorAccessGrant.objects.filter(
        member=member, doctor=doctor, granted_by=member.account, active=True
    ).order_by("-granted_at", "-id").first()
    if grant:
        grant.scopes = normalized
        grant.revoked_at = None
        grant.save(update_fields=["scopes", "revoked_at"])
        return grant
    return DoctorAccessGrant.objects.create(member=member, doctor=doctor, granted_by=member.account, scopes=normalized)


def _audit(actor, action, member=None, doctor=None, metadata=None):
    return DoctorAuditLog.objects.create(actor=actor, action=action, member=member, doctor=doctor, metadata=metadata or {})


def _notify(recipient, kind, title, message="", appointment=None, chat_request=None):
    # Keep notification previews generic; do not place diagnoses or record contents in them.
    return DoctorNotification.objects.create(
        recipient=recipient, kind=kind, title=title, message=message[:500],
        appointment=appointment, chat_request=chat_request,
    )


def _parse_datetime(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError({field_name: "A date and time are required."})
    dt = parse_datetime(value.strip())
    if dt is None:
        raise ValidationError({field_name: "Use an ISO-8601 date-time, including a timezone offset."})
    if timezone.is_naive(dt):
        raise ValidationError({field_name: "Include a timezone offset, for example +05:30."})
    return dt


def _validate_doctor_slot(doctor, value, field_name):
    """If a doctor has configured weekly slots, require the time to fall inside one."""
    configured = DoctorAvailabilitySlot.objects.filter(doctor=doctor, is_active=True)
    if not configured.exists():
        return
    local_value = timezone.localtime(value)
    clock = local_value.time().replace(tzinfo=None)
    allowed = configured.filter(weekday=local_value.weekday(), start_time__lte=clock, end_time__gt=clock).exists()
    if not allowed:
        raise ValidationError({field_name: "The selected time is outside the doctor's configured availability."})


def _appointment_data(appointment):
    return {
        "id": appointment.pk,
        "member_id": appointment.member_id,
        "member_name": f"{appointment.member.first_name} {appointment.member.last_name}".strip(),
        "doctor_id": appointment.doctor_id,
        "preferred_at": appointment.preferred_at.isoformat(),
        "scheduled_at": appointment.scheduled_at.isoformat() if appointment.scheduled_at else None,
        "reason": appointment.reason,
        "patient_note": appointment.patient_note,
        "doctor_response": appointment.doctor_response,
        "status": appointment.status,
        "created_at": appointment.created_at.isoformat(),
        "updated_at": appointment.updated_at.isoformat(),
    }


def _record_appointment_history(appointment, actor, action, from_status="", to_status="", reason="", metadata=None):
    return AppointmentHistory.objects.create(
        appointment=appointment, actor=actor, action=action,
        from_status=from_status or "", to_status=to_status or "",
        reason=(reason or "")[:1000], metadata=metadata or {},
    )


def _chat_request_data(chat_request):
    return {
        "id": chat_request.pk,
        "member_id": chat_request.member_id,
        "member_name": f"{chat_request.member.first_name} {chat_request.member.last_name}".strip(),
        "doctor_id": chat_request.doctor_id,
        "message": chat_request.message,
        "status": chat_request.status,
        "created_at": chat_request.created_at.isoformat(),
        "updated_at": chat_request.updated_at.isoformat(),
    }


@api_view(["GET"])
@permission_classes([AllowAny])
def public_doctors(request):
    profiles = DoctorProfile.objects.filter(status=DoctorProfile.Status.APPROVED, is_available=True, account__role=Account.Role.DOCTOR).select_related("account")
    specialty = request.query_params.get("specialty", "").strip()
    if specialty:
        profiles = profiles.filter(specialty__icontains=specialty)
    return Response({"doctors": [{
        "id": p.pk,
        "name": p.full_name,
        "specialty": p.specialty,
        "qualifications": p.qualifications,
        "clinic_name": p.clinic_name,
        "bio": p.bio,
        "years_experience": p.years_experience,
        "is_available": p.is_available,
    } for p in profiles]})



@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def doctor_profile(request):
    caller_email(request)
    if request.user.role != Account.Role.DOCTOR:
        raise PermissionDenied("A doctor account is required.")
    profile = get_object_or_404(DoctorProfile, account=request.user)
    if request.method == "GET":
        return Response({
            "id": profile.pk, "full_name": profile.full_name, "specialty": profile.specialty,
            "qualifications": profile.qualifications, "registration_number": profile.registration_number,
            "clinic_name": profile.clinic_name, "bio": profile.bio,
            "years_experience": profile.years_experience, "status": profile.status,
            "is_available": profile.is_available, "verified_at": profile.verified_at.isoformat() if profile.verified_at else None,
        })
    if profile.status != DoctorProfile.Status.APPROVED:
        raise PermissionDenied("Only an approved doctor can update availability.")
    if "is_available" in request.data:
        if not isinstance(request.data["is_available"], bool):
            raise ValidationError({"is_available": "Use true or false."})
        profile.is_available = request.data["is_available"]
    if "clinic_name" in request.data:
        profile.clinic_name = str(request.data["clinic_name"]).strip()[:200]
    if "bio" in request.data:
        profile.bio = str(request.data["bio"]).strip()[:5000]
    profile.save(update_fields=["is_available", "clinic_name", "bio", "updated_at"])
    return Response({
        "id": profile.pk, "full_name": profile.full_name, "specialty": profile.specialty,
        "status": profile.status, "is_available": profile.is_available,
        "clinic_name": profile.clinic_name, "bio": profile.bio,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def submit_application(request):
    """Record an application only; do not create or modify an account."""
    email = str(request.data.get("email", "")).strip().lower()
    if not email or len(email) > 254 or "@" not in email:
        raise ValidationError({"email": "Enter a valid email address."})
    if Account.objects.filter(email__iexact=email).exists():
        raise ValidationError({"email": "This email already belongs to an account. Use an email not attached to a patient account for the doctor application."})
    if DoctorApplication.objects.filter(email__iexact=email, status=DoctorApplication.Status.PENDING).exists():
        raise ValidationError({"email": "A pending application already exists for this email."})
    full_name = str(request.data.get("full_name", "")).strip()
    specialty = str(request.data.get("specialty", "")).strip()
    qualifications = str(request.data.get("qualifications", "")).strip()
    registration_number = str(request.data.get("registration_number", "")).strip()
    if not full_name or not specialty or not qualifications or not registration_number:
        raise ValidationError({"detail": "full_name, specialty, qualifications and registration_number are required."})
    years = request.data.get("years_experience", 0)
    try:
        years = int(years)
        if years < 0 or years > 80: raise ValueError
    except (TypeError, ValueError):
        raise ValidationError({"years_experience": "Enter a number from 0 to 80."})
    uploaded_documents = request.FILES.getlist("documents") if hasattr(request, "FILES") else []
    if len(uploaded_documents) > 10:
        raise ValidationError({"documents": "Upload no more than 10 supporting documents."})
    for uploaded in uploaded_documents:
        if uploaded.size > 10 * 1024 * 1024:
            raise ValidationError({"documents": "Each document must be 10 MB or smaller."})
        suffix = uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else ""
        if suffix not in {"pdf", "jpg", "jpeg", "png"}:
            raise ValidationError({"documents": "Only PDF, JPG, JPEG, and PNG files are accepted."})
    app = DoctorApplication.objects.create(
        email=email, phone=str(request.data.get("phone", "")).strip()[:32],
        address=str(request.data.get("address", "")).strip()[:3000],
        registration_authority=str(request.data.get("registration_authority", "")).strip()[:200],
        full_name=full_name[:150], specialty=specialty[:120], qualifications=qualifications[:255],
        registration_number=registration_number[:120], clinic_name=str(request.data.get("clinic_name", "")).strip()[:200],
        bio=str(request.data.get("bio", "")).strip()[:5000], years_experience=years,
    )
    document_types = request.data.getlist("document_types") if hasattr(request.data, "getlist") else []
    for index, uploaded in enumerate(uploaded_documents):
        kind = document_types[index] if index < len(document_types) else DoctorApplicationDocument.DocumentType.OTHER
        if kind not in DoctorApplicationDocument.DocumentType.values: kind = DoctorApplicationDocument.DocumentType.OTHER
        DoctorApplicationDocument.objects.create(application=app, document_type=kind, file=uploaded)
    for administrator in Account.objects.filter(role=Account.Role.SUPER_ADMIN):
        _notify(administrator, "doctor_application_received", "New doctor application", "A doctor application is awaiting review.")
    return Response({"message": "Application submitted. No account has been created. Wait for an email decision.", "application": _application_data(app)}, status=status.HTTP_201_CREATED)


def _application_data(app):
    return {
        "id": app.pk, "email": app.email or (app.account.email if app.account_id else ""),
        "phone": app.phone, "address": app.address, "registration_authority": app.registration_authority,
        "full_name": app.full_name, "specialty": app.specialty, "qualifications": app.qualifications,
        "registration_number": app.registration_number, "clinic_name": app.clinic_name, "bio": app.bio,
        "years_experience": app.years_experience, "status": app.status, "review_note": app.review_note,
        "documents": [{"id": d.pk, "document_type": d.document_type, "uploaded_at": d.uploaded_at.isoformat()} for d in app.documents.all()],
        "created_at": app.created_at.isoformat(), "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
        "reviewed_by": app.reviewed_by.email if app.reviewed_by_id else None,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_application(request):
    caller_email(request)
    app = DoctorApplication.objects.filter(email__iexact=request.user.email).order_by("-created_at", "-id").first()
    profile = DoctorProfile.objects.filter(account=request.user).first()
    return Response({"application": _application_data(app) if app else None, "doctor_profile": ({"id": profile.pk, "doctor_id": profile.doctor_id, "status": profile.status, "specialty": profile.specialty, "is_available": profile.is_available} if profile else None)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_applications(request):
    caller_email(request)
    _require_staff(request.user)
    state = request.query_params.get("status", "pending")
    qs = DoctorApplication.objects.select_related("account", "reviewed_by").all()
    if state and state != "all":
        if state not in DoctorApplication.Status.values: raise ValidationError({"status": "Invalid application status."})
        qs = qs.filter(status=state)
    return Response({"applications": [_application_data(app) for app in qs]})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_application_document(request, document_id):
    caller_email(request)
    _require_staff(request.user, super_admin=True)
    document = get_object_or_404(DoctorApplicationDocument.objects.select_related("application"), pk=document_id)
    if not document.file or not document.file.storage.exists(document.file.name):
        raise ValidationError({"detail": "The application document is unavailable."})
    response = FileResponse(document.file.open("rb"), as_attachment=True, filename=document.file.name.rsplit("/", 1)[-1])
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_application(request, application_id):
    """Approve/reject an application without creating an Account before doctor setup."""
    caller_email(request)
    _require_staff(request.user, super_admin=True)
    decision = str(request.data.get("decision", "")).strip().lower()
    if decision not in ("approve", "reject"):
        raise ValidationError({"decision": "Use approve or reject."})
    review_note = str(request.data.get("review_note", "")).strip()[:1000]
    if decision == "reject" and not review_note:
        raise ValidationError({"review_note": "A reason is required when rejecting an application."})
    with transaction.atomic():
        app = get_object_or_404(DoctorApplication.objects.select_for_update().select_related("account"), pk=application_id)
        if app.status != DoctorApplication.Status.PENDING:
            raise ValidationError({"detail": "This application has already been reviewed."})
        email = (app.email or (app.account.email if app.account_id else "")).strip().lower()
        if not email:
            raise ValidationError({"email": "The application has no valid email address."})
        if decision == "approve":
            if Account.objects.filter(email__iexact=email).exists():
                raise ValidationError({"detail": "An account already exists for this email. No account was changed."})
            if DoctorProfile.objects.filter(registration_number=app.registration_number).exists():
                raise ValidationError({"detail": "This medical registration number is already associated with another doctor."})
            token = secrets.token_urlsafe(32)
            activation = DoctorAccountActivation.objects.create(
                email=email, application=app, full_name=app.full_name, specialty=app.specialty,
                qualifications=app.qualifications, registration_number=app.registration_number,
                clinic_name=app.clinic_name, bio=app.bio, years_experience=app.years_experience,
                phone=app.phone, address=app.address, registration_authority=app.registration_authority,
                token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
                expires_at=timezone.now() + timedelta(hours=24),
            )
            frontend_url = getattr(settings, "FRONTEND_DOCTOR_ACTIVATION_URL", "http://localhost:5173/doctor-activate").rstrip("/")
            activation_url = f"{frontend_url}#token={token}"
            send_mail(
                subject="Your MedLife doctor application is approved",
                message=(f"Hello {app.full_name},\n\nYour MedLife doctor application has been approved.\n\nCreate your doctor account and complete password and authenticator setup here: {activation_url}\nThis link expires in 24 hours and can be used once. Do not share it.\n\nMedLife"),
                from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False,
            )
            _audit(request.user, "doctor_application_approved", metadata={"application_id": app.pk, "activation_id": activation.pk})
        else:
            send_mail(
                subject="Update on your MedLife doctor application",
                message=(f"Hello {app.full_name},\n\nYour MedLife doctor application was not approved at this time.\nReason: {review_note}\n\nMedLife"),
                from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False,
            )
            _audit(request.user, "doctor_application_rejected", metadata={"application_id": app.pk})
        app.status = DoctorApplication.Status.APPROVED if decision == "approve" else DoctorApplication.Status.REJECTED
        app.review_note = review_note
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.save(update_fields=["status", "review_note", "reviewed_by", "reviewed_at", "updated_at"])
    return Response({"application": _application_data(app), "decision": decision, "account_created": False,
                     "message": "Approval recorded. The doctor must finish password and TOTP setup before an account is created." if decision == "approve" else "Application rejected."})


@api_view(["POST"])
@permission_classes([AllowAny])
def activate_doctor_account(request):
    """Two-stage public activation: set password and receive TOTP QR, then verify TOTP to create Account."""
    token = str(request.data.get("token", "")).strip()
    action = str(request.data.get("action", "setup")).strip().lower()
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest() if token else ""
    if not token:
        raise ValidationError({"token": "Activation token is required."})

    with transaction.atomic():
        activation = DoctorAccountActivation.objects.select_for_update(of=("self",)).select_related("application", "invitation").filter(token_hash=token_hash).first()
        if not activation or activation.consumed_at or activation.expires_at <= timezone.now():
            raise ValidationError({"token": "This activation link is invalid, expired, or already used. Contact MedLife for a new link."})
        if activation.application_id and activation.application.status != DoctorApplication.Status.APPROVED:
            raise ValidationError({"token": "This doctor application has not been approved."})
        if activation.invitation_id and activation.invitation.status != DoctorInvitation.Status.ACCEPTED:
            raise ValidationError({"token": "This invitation is not accepted or is no longer valid."})

        if action == "setup":
            password = str(request.data.get("password", ""))
            confirm_password = str(request.data.get("confirm_password", ""))
            if len(password) < 8 or len(password) > 128:
                raise ValidationError({"password": "Use a password between 8 and 128 characters."})
            if password != confirm_password:
                raise ValidationError({"confirm_password": "Passwords do not match."})
            secret, provisioning_uri, qr_data_url = make_totp_setup(activation.email)
            activation.pending_password_hash = make_password(password)
            activation.pending_totp_secret_encrypted = encrypt_totp_secret(secret)
            next_token = secrets.token_urlsafe(32)
            activation.token_hash = hashlib.sha256(next_token.encode("utf-8")).hexdigest()
            activation.save(update_fields=["pending_password_hash", "pending_totp_secret_encrypted", "token_hash"])
            return Response({"message": "Password saved for setup. Scan the QR code and verify your authenticator.",
                             "action": "verify_totp", "token": next_token, "email": activation.email,
                             "provisioning_uri": provisioning_uri, "qr_code": qr_data_url})

        if action != "complete":
            raise ValidationError({"action": "Use setup or complete."})
        if not activation.pending_password_hash or not activation.pending_totp_secret_encrypted:
            raise ValidationError({"detail": "Complete the password setup stage first."})
        try:
            secret = decrypt_totp_secret(activation.pending_totp_secret_encrypted)
        except ValueError:
            raise ValidationError({"detail": "Authenticator setup could not be read. Restart account activation."})
        code = str(request.data.get("code", "")).strip()
        matched_step = matching_totp_step(secret, code)
        if matched_step is None:
            raise ValidationError({"code": "The authenticator code is invalid or expired."})
        email = activation.email.strip().lower()
        if Account.objects.filter(email__iexact=email).exists():
            raise ValidationError({"email": "An account already exists for this email. Contact MedLife support."})
        if DoctorProfile.objects.filter(registration_number=activation.registration_number).exists():
            raise ValidationError({"registration_number": "This medical registration number is already associated with another doctor."})
        account = Account.objects.create(
            email=email, role=Account.Role.DOCTOR, password=activation.pending_password_hash,
            totp_enabled=True, totp_secret_encrypted=activation.pending_totp_secret_encrypted,
            totp_pending_secret_encrypted="", totp_last_verified_step=matched_step,
        )
        profile = DoctorProfile.objects.create(
            account=account, doctor_id=f"MLD{account.pk:06d}", full_name=activation.full_name,
            specialty=activation.specialty, qualifications=activation.qualifications,
            registration_number=activation.registration_number, clinic_name=activation.clinic_name,
            bio=activation.bio, years_experience=activation.years_experience,
            status=DoctorProfile.Status.APPROVED, is_available=True, verified_at=timezone.now(),
        )
        activation.account = account
        activation.consumed_at = timezone.now()
        activation.pending_password_hash = ""
        activation.pending_totp_secret_encrypted = ""
        activation.save(update_fields=["account", "consumed_at", "pending_password_hash", "pending_totp_secret_encrypted"])
        if activation.invitation_id:
            activation.invitation.accepted_by = account
            activation.invitation.save(update_fields=["accepted_by"])
        _audit(account, "doctor_account_created", doctor=profile, metadata={"activation_id": activation.pk, "source": "application" if activation.application_id else "invitation"})
        try:
            send_mail(
                subject="Welcome to MedLife — your doctor account is ready",
                message=f"Hello {profile.full_name},\n\nYour MedLife doctor account has been created successfully. You can now sign in using {email} and your password.\n\nWelcome to MedLife!",
                from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False,
            )
        except Exception:
            # Account creation is complete; a mail-server issue must not undo verified credentials.
            pass
    return Response({"message": "Doctor account created successfully. A confirmation email will be sent if email delivery is available.",
                     "account_created": True, "doctor_id": profile.doctor_id})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def admin_invitations(request):
    # The submitted email is the invitee, not the signed-in administrator.
    _require_staff(request.user, super_admin=True)
    if request.method == "GET":
        items = DoctorInvitation.objects.select_related("invited_by", "accepted_by").prefetch_related("activations").all()[:200]
        return Response({"invitations": [{
            "id": i.pk, "email": i.email,
            "status": "expired" if i.status == DoctorInvitation.Status.PENDING and i.is_expired() else i.status,
            "email_status": "sent",
            "account_created": bool(i.accepted_by_id),
            "activation_pending": bool(i.status == DoctorInvitation.Status.ACCEPTED and not i.accepted_by_id),
            "expires_at": i.expires_at.isoformat(), "created_at": i.created_at.isoformat(),
            "invited_by": i.invited_by.email,
        } for i in items]})
    email = str(request.data.get("email", "")).strip().lower()
    if not email or "@" not in email or len(email) > 254:
        raise ValidationError({"email": "Enter a valid email address."})
    if Account.objects.filter(email__iexact=email).exists():
        raise ValidationError({"email": "An account already exists for this email. A doctor invitation cannot replace an existing account."})
    if DoctorInvitation.objects.filter(email__iexact=email, status=DoctorInvitation.Status.PENDING, expires_at__gt=timezone.now()).exists():
        raise ValidationError({"email": "A valid pending invitation already exists for this email."})
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    invitation = DoctorInvitation.objects.create(
        email=email, token_hash=token_hash, expires_at=timezone.now() + timedelta(days=7),
        invited_by=request.user,
    )
    frontend_url = getattr(settings, "FRONTEND_DOCTOR_INVITATION_URL", "http://localhost:5173/doctor-invitation").rstrip("/")
    invitation_url = f"{frontend_url}#token={token}"
    try:
        send_mail(
            subject="Invitation to join MedLife as a doctor",
            message=f"You have been invited to apply as a MedLife doctor. Open this secure link to accept or reject the invitation and, if accepted, create your doctor account: {invitation_url}\nThis invitation expires in 7 days.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email], fail_silently=False,
        )
    except Exception as exc:
        invitation.delete()
        raise InvitationEmailDeliveryError() from exc
    _audit(request.user, "doctor_invitation_created", metadata={"invitation_id": invitation.pk, "email": email})
    return Response({"message": "Invitation email sent.", "invitation_id": invitation.pk, "expires_at": invitation.expires_at.isoformat()}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def accept_invitation(request):
    """Accept/reject a Super Admin invitation without requiring a patient account."""
    token = str(request.data.get("token", "")).strip()
    decision = str(request.data.get("decision", "accept")).strip().lower()
    if not token:
        raise ValidationError({"token": "Invitation token is required."})
    if decision not in ("accept", "reject"):
        raise ValidationError({"decision": "Use accept or reject."})
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with transaction.atomic():
        invitation = DoctorInvitation.objects.select_for_update().select_related("invited_by").filter(token_hash=token_hash).first()
        if not invitation:
            raise ValidationError({"token": "Invitation is invalid or expired."})
        if invitation.status != DoctorInvitation.Status.PENDING or invitation.is_expired():
            if invitation.status == DoctorInvitation.Status.PENDING and invitation.is_expired():
                invitation.status = DoctorInvitation.Status.EXPIRED
                invitation.save(update_fields=["status"])
            raise ValidationError({"token": "Invitation is invalid, expired, or already used."})
        if Account.objects.filter(email__iexact=invitation.email).exists():
            raise ValidationError({"email": "An account already exists for this email. Contact MedLife support."})
        if decision == "reject":
            invitation.status = DoctorInvitation.Status.REJECTED
            invitation.save(update_fields=["status"])
            _audit(invitation.invited_by, "doctor_invitation_rejected", metadata={"invitation_id": invitation.pk, "email": invitation.email})
            return Response({"message": "Invitation rejected. No account was created.", "status": invitation.status})

        fields = {key: str(request.data.get(key, "")).strip() for key in ("full_name", "specialty", "qualifications", "registration_number")}
        if not all(fields.values()):
            raise ValidationError({"detail": "full_name, specialty, qualifications and registration_number are required when accepting an invitation."})
        try:
            years = int(request.data.get("years_experience", 0))
            if years < 0 or years > 80:
                raise ValueError
        except (TypeError, ValueError):
            raise ValidationError({"years_experience": "Enter a number from 0 to 80."})
        if DoctorProfile.objects.filter(registration_number=fields["registration_number"][:120]).exists():
            raise ValidationError({"registration_number": "This medical registration number is already associated with another doctor."})
        token_for_setup = secrets.token_urlsafe(32)
        activation = DoctorAccountActivation.objects.create(
            email=invitation.email.strip().lower(), invitation=invitation,
            full_name=fields["full_name"][:150], specialty=fields["specialty"][:120],
            qualifications=fields["qualifications"][:255], registration_number=fields["registration_number"][:120],
            clinic_name=str(request.data.get("clinic_name", "")).strip()[:200],
            bio=str(request.data.get("bio", "")).strip()[:5000], years_experience=years,
            phone=str(request.data.get("phone", "")).strip()[:32], address=str(request.data.get("address", "")).strip()[:3000],
            registration_authority=str(request.data.get("registration_authority", "")).strip()[:200],
            token_hash=hashlib.sha256(token_for_setup.encode("utf-8")).hexdigest(),
            expires_at=timezone.now() + timedelta(hours=24),
        )
        invitation.status = DoctorInvitation.Status.ACCEPTED
        invitation.save(update_fields=["status"])
        _audit(invitation.invited_by, "doctor_invitation_accepted", metadata={"invitation_id": invitation.pk, "activation_id": activation.pk})
    return Response({"message": "Invitation accepted. Continue to create your doctor account.", "status": invitation.status,
                     "activation_token": token_for_setup, "activation_expires_at": activation.expires_at.isoformat()}, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def access_grants(request):
    caller_email(request)
    if request.user.role != Account.Role.PATIENT:
        raise PermissionDenied("Patient account access is required.")
    if request.method == "GET":
        grants = DoctorAccessGrant.objects.filter(granted_by=request.user).select_related("member", "doctor__account")
        return Response({"grants": [{
            "id": g.pk, "member_id": g.member_id, "member_name": f"{g.member.first_name} {g.member.last_name}".strip(),
            "doctor_id": g.doctor_id, "doctor_email": g.doctor.account.email,
            "scopes": g.scopes, "active": g.active, "granted_at": g.granted_at.isoformat(),
            "revoked_at": g.revoked_at.isoformat() if g.revoked_at else None,
        } for g in grants]})
    member = _member_for_owner(request.user, request.data.get("member_id"))
    doctor = get_object_or_404(DoctorProfile, pk=request.data.get("doctor_id"), status=DoctorProfile.Status.APPROVED)
    scopes = request.data.get("scopes")
    grant = _ensure_grant(member, doctor, scopes)
    _audit(request.user, "doctor_record_access_granted", member=member, doctor=doctor, metadata={"grant_id": grant.pk, "scopes": grant.scopes})
    return Response({"grant_id": grant.pk, "member_id": member.pk, "doctor_id": doctor.pk, "scopes": grant.scopes, "active": grant.active}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def revoke_access_grant(request, grant_id):
    caller_email(request)
    if request.user.role != Account.Role.PATIENT:
        raise PermissionDenied("Patient account access is required.")
    grant = get_object_or_404(DoctorAccessGrant, pk=grant_id, granted_by=request.user)
    if grant.active:
        grant.active = False
        grant.revoked_at = timezone.now()
        grant.save(update_fields=["active", "revoked_at"])
        _audit(request.user, "doctor_record_access_revoked", member=grant.member, doctor=grant.doctor, metadata={"grant_id": grant.pk})
    return Response({"message": "Medical-record access revoked.", "grant_id": grant.pk, "active": False})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def doctor_patients(request):
    caller_email(request)
    doctor = _doctor_for(request.user)
    member_ids = Appointment.objects.filter(doctor=doctor).values_list("member_id", flat=True).distinct()
    members = FamilyMember.objects.filter(pk__in=member_ids).select_related("account").order_by("first_name", "last_name", "id")
    results = []
    for member in members[:200]:
        grant = _active_grant(member, doctor)
        latest = Appointment.objects.filter(doctor=doctor, member=member).order_by("-created_at", "-id").first()
        results.append({"member_id": member.pk, "member_name": f"{member.first_name} {member.last_name}".strip(),
            "patient_account_id": member.account_id, "latest_appointment_id": latest.pk if latest else None,
            "latest_appointment_status": latest.status if latest else None,
            "record_access_active": bool(grant), "record_scopes": grant.scopes if grant else []})
    return Response({"patients": results, "count": len(results)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def shared_records(request, member_id):
    caller_email(request)
    doctor = _doctor_for(request.user)
    member = get_object_or_404(FamilyMember, pk=member_id)
    grant = _active_grant(member, doctor, "profile")
    if not grant:
        raise PermissionDenied("The patient has not granted active access to this member's profile.")
    _audit(request.user, "doctor_shared_records_viewed", member=member, doctor=doctor, metadata={"scopes": grant.scopes})
    data = {
        "member_id": member.pk,
        "member_name": f"{member.first_name} {member.last_name}".strip(),
        "height": member.height, "weight": member.weight, "blood_pressure": member.blood_pressure,
        "a1c": str(member.a1c) if member.a1c is not None else None,
        "medicine": member.medicine, "medical_description": member.medical_description,
        "consent_scopes": grant.scopes,
    }
    if grant.permits("documents"):
        data["documents"] = [{
            "id": doc.pk, "document_type": doc.document_type, "description": doc.description,
            "is_confirmed": doc.is_confirmed, "created_at": doc.created_at.isoformat(),
        } for doc in ScannedDocument.objects.filter(account=member.account, member=member).order_by("-created_at")[:100]]
    if grant.permits("consultation_notes"):
        data["consultation_notes"] = [{
            "appointment_id": note.appointment_id, "content": note.content,
            "created_at": note.created_at.isoformat(), "updated_at": note.updated_at.isoformat(),
        } for note in ConsultationNote.objects.filter(member=member).select_related("appointment").order_by("-updated_at")[:100]]
    return Response(data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def appointments(request):
    caller_email(request)
    if request.method == "GET":
        role = request.query_params.get("role", "patient").strip().lower()
        if role == "admin":
            _require_staff(request.user, super_admin=True)
            qs = Appointment.objects.all()
        elif role == "doctor":
            doctor = _doctor_for(request.user)
            qs = Appointment.objects.filter(doctor=doctor)
        elif role == "patient":
            if request.user.role != Account.Role.PATIENT:
                raise PermissionDenied("Patient account access is required.")
            qs = Appointment.objects.filter(requested_by=request.user)
        else:
            raise ValidationError({"role": "Use patient, doctor or admin."})

        state = request.query_params.get("status", "").strip().lower()
        if state:
            if state not in Appointment.Status.values:
                raise ValidationError({"status": "Invalid appointment status."})
            qs = qs.filter(status=state)
        doctor_id = request.query_params.get("doctor_id")
        patient_id = request.query_params.get("patient_id")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)
        if patient_id:
            qs = qs.filter(member__account_id=patient_id)
        if date_from:
            from django.utils.dateparse import parse_date
            parsed = parse_date(date_from)
            if not parsed: raise ValidationError({"date_from": "Use YYYY-MM-DD."})
            qs = qs.filter(preferred_at__date__gte=parsed)
        if date_to:
            from django.utils.dateparse import parse_date
            parsed = parse_date(date_to)
            if not parsed: raise ValidationError({"date_to": "Use YYYY-MM-DD."})
            qs = qs.filter(preferred_at__date__lte=parsed)
        try:
            limit = min(max(int(request.query_params.get("limit", "100")), 1), 200)
        except (TypeError, ValueError):
            raise ValidationError({"limit": "Use an integer from 1 to 200."})
        items = qs.select_related("member", "member__account", "doctor__account", "requested_by", "booked_by").order_by("-created_at", "-id")[:limit]
        result = []
        for a in items:
            item = _appointment_data(a)
            # Administrative overview needs booking metadata, not patient-entered clinical narrative.
            item.pop("reason", None)
            item.pop("patient_note", None)
            item.update({
                "patient_account_id": a.member.account_id,
                "patient_email": a.member.account.email,
                "doctor_name": a.doctor.full_name,
                "doctor_email": a.doctor.account.email,
                "requested_by_email": a.requested_by.email,
                "booked_by_email": a.booked_by.email if a.booked_by_id else None,
            })
            result.append(item)
        return Response({"appointments": result, "limit": limit})

    if request.user.role == Account.Role.SUPER_ADMIN:
        _require_staff(request.user, super_admin=True)
        member = get_object_or_404(FamilyMember.objects.select_related("account"), pk=request.data.get("member_id"))
        if member.account.role != Account.Role.PATIENT:
            raise ValidationError({"member_id": "Choose a family profile belonging to an existing patient account."})
        doctor = get_object_or_404(DoctorProfile, pk=request.data.get("doctor_id"), status=DoctorProfile.Status.APPROVED, is_available=True)
        preferred_at = _parse_datetime(request.data.get("preferred_at"), "preferred_at")
        if preferred_at <= timezone.now():
            raise ValidationError({"preferred_at": "Choose a future date and time."})
        _validate_doctor_slot(doctor, preferred_at, "preferred_at")
        if not _active_grant(member, doctor, "profile"):
            raise PermissionDenied("The patient must have an active profile-sharing consent for this doctor before an appointment can be booked.")
        with transaction.atomic():
            appointment = Appointment.objects.create(
                member=member, doctor=doctor, requested_by=member.account, booked_by=request.user,
                preferred_at=preferred_at, reason=str(request.data.get("reason", "")).strip()[:1000],
                patient_note=str(request.data.get("patient_note", "")).strip()[:2000],
            )
            _record_appointment_history(appointment, request.user, "admin_booked", "", appointment.status,
                                        reason=str(request.data.get("reason", "")).strip()[:1000],
                                        metadata={"patient_account_id": member.account_id, "member_id": member.pk})
            _audit(request.user, "admin_appointment_booked", member=member, doctor=doctor,
                   metadata={"appointment_id": appointment.pk, "patient_account_id": member.account_id})
            _notify(doctor.account, "appointment_requested", "New appointment request", "An appointment has been booked for a patient and awaits your decision.", appointment=appointment)
            _notify(member.account, "appointment_requested", "Appointment request created", "An appointment request was created for your family profile.", appointment=appointment)
        return Response({"appointment": _appointment_data(appointment)}, status=status.HTTP_201_CREATED)

    member = _member_for_owner(request.user, request.data.get("member_id"))
    doctor = get_object_or_404(DoctorProfile, pk=request.data.get("doctor_id"), status=DoctorProfile.Status.APPROVED, is_available=True)
    preferred_at = _parse_datetime(request.data.get("preferred_at"), "preferred_at")
    if preferred_at <= timezone.now():
        raise ValidationError({"preferred_at": "Choose a future date and time."})
    _validate_doctor_slot(doctor, preferred_at, "preferred_at")
    scopes = request.data.get("consent_scopes")
    with transaction.atomic():
        grant = _ensure_grant(member, doctor, scopes)
        _audit(request.user, "doctor_record_access_granted", member=member, doctor=doctor, metadata={"grant_id": grant.pk, "scopes": grant.scopes, "source": "appointment"})
        appointment = Appointment.objects.create(
            member=member, doctor=doctor, requested_by=request.user, preferred_at=preferred_at,
            reason=str(request.data.get("reason", "")).strip()[:1000],
            patient_note=str(request.data.get("patient_note", "")).strip()[:2000],
        )
        _record_appointment_history(appointment, request.user, "created", "", appointment.status, reason=appointment.reason)
        _notify(doctor.account, "appointment_requested", "New appointment request", "A patient has requested an appointment.", appointment=appointment)
        _notify(request.user, "appointment_requested", "Appointment request submitted", "Your appointment request is awaiting the doctor's decision.", appointment=appointment)
    return Response({"appointment": _appointment_data(appointment)}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def appointment_decision(request, appointment_id):
    caller_email(request)
    doctor = _doctor_for(request.user)
    decision = str(request.data.get("decision", "")).strip().lower()
    if decision not in ("accept", "reject"):
        raise ValidationError({"decision": "Use accept or reject."})
    with transaction.atomic():
        appointment = get_object_or_404(Appointment.objects.select_for_update().select_related("member", "doctor__account", "requested_by"), pk=appointment_id, doctor=doctor)
        if appointment.status != Appointment.Status.REQUESTED:
            raise ValidationError({"detail": "Only requested appointments can be accepted or rejected."})
        previous_status = appointment.status
        if decision == "accept":
            if not _active_grant(appointment.member, doctor, "profile"):
                raise PermissionDenied("The patient's record-sharing consent is no longer active.")
            scheduled = _parse_datetime(request.data.get("scheduled_at"), "scheduled_at")
            if scheduled <= timezone.now():
                raise ValidationError({"scheduled_at": "Choose a future date and time."})
            _validate_doctor_slot(doctor, scheduled, "scheduled_at")
            conflict = Appointment.objects.filter(
                doctor=doctor, status=Appointment.Status.ACCEPTED, scheduled_at=scheduled,
            ).exclude(pk=appointment.pk).exists()
            if conflict:
                raise ValidationError({"scheduled_at": "The doctor already has an appointment at that time."})
            appointment.status = Appointment.Status.ACCEPTED
            appointment.scheduled_at = scheduled
        else:
            appointment.status = Appointment.Status.REJECTED
        appointment.doctor_response = str(request.data.get("doctor_response", "")).strip()[:1000]
        appointment.decided_at = timezone.now()
        appointment.save()
        _record_appointment_history(appointment, request.user, "doctor_decision", previous_status, appointment.status,
                                    reason=appointment.doctor_response)
        _audit(request.user, f"appointment_{appointment.status}", member=appointment.member, doctor=doctor,
               metadata={"appointment_id": appointment.pk, "decision": decision})
        _notify(appointment.requested_by, f"appointment_{appointment.status}", f"Appointment {appointment.status}", "Your appointment request status has changed.", appointment=appointment)
        _notify(doctor.account, f"appointment_{appointment.status}", f"Appointment {appointment.status}", "The appointment request was updated.", appointment=appointment)
    return Response({"appointment": _appointment_data(appointment)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, appointment_id):
    caller_email(request)
    appointment = get_object_or_404(Appointment.objects.select_related("doctor__account", "member", "requested_by"), pk=appointment_id)
    is_patient = appointment.requested_by_id == request.user.pk and request.user.role == Account.Role.PATIENT
    is_doctor = appointment.doctor.account_id == request.user.pk and request.user.role == Account.Role.DOCTOR
    is_admin = request.user.role == Account.Role.SUPER_ADMIN
    if is_doctor:
        doctor = _doctor_for(request.user)
        is_doctor = doctor.pk == appointment.doctor_id
    if is_admin:
        _require_staff(request.user, super_admin=True)
    if not (is_patient or is_doctor or is_admin):
        raise PermissionDenied("You cannot cancel this appointment.")
    if appointment.status not in (Appointment.Status.REQUESTED, Appointment.Status.ACCEPTED):
        raise ValidationError({"detail": "Only requested or accepted appointments can be cancelled."})
    previous_status = appointment.status
    appointment.status = Appointment.Status.CANCELLED
    cancellation_reason = str(request.data.get("reason", "")).strip()[:1000]
    if is_doctor or is_admin:
        appointment.doctor_response = cancellation_reason or appointment.doctor_response
    appointment.save(update_fields=["status", "doctor_response", "updated_at"])
    _record_appointment_history(appointment, request.user, "cancelled", previous_status, appointment.status, reason=cancellation_reason,
                                metadata={"cancelled_by_role": request.user.role})
    _audit(request.user, "appointment_cancelled", member=appointment.member, doctor=appointment.doctor,
           metadata={"appointment_id": appointment.pk, "cancelled_by_role": request.user.role})
    for recipient in {appointment.doctor.account, appointment.requested_by}:
        if recipient.pk != request.user.pk:
            _notify(recipient, "appointment_cancelled", "Appointment cancelled", "An appointment has been cancelled.", appointment=appointment)
    return Response({"appointment": _appointment_data(appointment)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_appointment(request, appointment_id):
    caller_email(request)
    doctor = _doctor_for(request.user)
    appointment = get_object_or_404(Appointment.objects.select_related("member", "doctor__account", "requested_by"), pk=appointment_id, doctor=doctor)
    if appointment.status != Appointment.Status.ACCEPTED:
        raise ValidationError({"detail": "Only accepted appointments can be marked completed."})
    previous_status = appointment.status
    appointment.status = Appointment.Status.COMPLETED
    appointment.completed_at = timezone.now()
    appointment.save(update_fields=["status", "completed_at", "updated_at"])
    _record_appointment_history(appointment, request.user, "completed", previous_status, appointment.status)
    _audit(request.user, "appointment_completed", member=appointment.member, doctor=doctor,
           metadata={"appointment_id": appointment.pk})
    _notify(appointment.requested_by, "appointment_completed", "Appointment completed", "Your appointment has been marked completed.", appointment=appointment)
    return Response({"appointment": _appointment_data(appointment)})


@api_view(["GET", "PUT", "POST"])
@permission_classes([IsAuthenticated])
def consultation_note(request, appointment_id):
    caller_email(request)
    appointment = get_object_or_404(Appointment.objects.select_related("member", "doctor__account", "requested_by"), pk=appointment_id)
    is_patient = appointment.requested_by_id == request.user.pk and request.user.role == Account.Role.PATIENT
    is_doctor = appointment.doctor.account_id == request.user.pk and request.user.role == Account.Role.DOCTOR
    if is_doctor:
        doctor = _doctor_for(request.user)
        is_doctor = doctor.pk == appointment.doctor_id
    grant = _active_grant(appointment.member, appointment.doctor, "consultation_notes")
    if request.method == "GET":
        if not is_patient and not (is_doctor and grant):
            raise PermissionDenied("You are not authorized to view this consultation note.")
        note = get_object_or_404(ConsultationNote, appointment=appointment)
        _audit(request.user, "consultation_note_viewed", member=appointment.member, doctor=appointment.doctor, metadata={"appointment_id": appointment.pk})
        return Response({"appointment_id": appointment.pk, "content": note.content, "sections": note.sections,
                         "finalized_at": note.finalized_at.isoformat() if note.finalized_at else None,
                         "created_at": note.created_at.isoformat(), "updated_at": note.updated_at.isoformat()})
    if not is_doctor or not grant:
        raise PermissionDenied("Only the assigned doctor with active note-sharing consent can write consultation notes.")
    if appointment.status not in (Appointment.Status.ACCEPTED, Appointment.Status.COMPLETED):
        raise ValidationError({"detail": "Consultation notes can be written after an appointment is accepted."})
    action = str(request.data.get("action", "save")).strip().lower()
    if action not in ("save", "finalize", "amend"):
        raise ValidationError({"action": "Use save, finalize, or amend."})
    content = str(request.data.get("content", "")).strip()
    sections = request.data.get("sections", {})
    allowed_sections = {"symptoms", "observations", "assessment", "recommendations", "follow_up"}
    if not isinstance(sections, dict) or any(k not in allowed_sections for k in sections):
        raise ValidationError({"sections": "Use an object with symptoms, observations, assessment, recommendations, and follow_up fields."})
    normalized_sections = {k: str(v).strip()[:5000] for k, v in sections.items()}
    if not content and not normalized_sections:
        raise ValidationError({"content": "Provide consultation note content or at least one structured section."})
    note = ConsultationNote.objects.filter(appointment=appointment).first()
    created = note is None
    if note is None and action == "amend":
        raise ValidationError({"detail": "Create and finalize the note before amending it."})
    if note and note.finalized_at and action != "amend":
        raise ValidationError({"detail": "This note is finalized. Use action='amend' to create an auditable amendment."})
    if note and action == "amend" and not note.finalized_at:
        raise ValidationError({"detail": "Only finalized notes can be amended. Use action='save' or 'finalize'."})
    if note and action == "amend":
        ConsultationNoteRevision.objects.create(
            note=note, revised_by=request.user, content=note.content,
            sections=note.sections, finalized_at=note.finalized_at,
        )
    if note is None:
        note = ConsultationNote.objects.create(appointment=appointment, doctor=appointment.doctor,
            member=appointment.member, content=content[:20000], sections=normalized_sections)
    else:
        note.content = content[:20000] if content else note.content
        note.sections = normalized_sections if "sections" in request.data else note.sections
    if action == "finalize":
        note.finalized_at = timezone.now()
    elif action == "amend":
        note.finalized_at = timezone.now()
    note.save()
    _audit(request.user, "consultation_note_amended" if action == "amend" else ("consultation_note_finalized" if action == "finalize" else "consultation_note_updated"),
           member=appointment.member, doctor=appointment.doctor, metadata={"appointment_id": appointment.pk, "revision_count": note.revisions.count()})
    _notify(appointment.requested_by, "consultation_note_updated", "Consultation note updated", "A consultation note is available in MedLife.", appointment=appointment)
    return Response({"appointment_id": appointment.pk, "content": note.content, "sections": note.sections,
                     "finalized_at": note.finalized_at.isoformat() if note.finalized_at else None,
                     "revision_count": note.revisions.count(), "created_at": note.created_at.isoformat(),
                     "updated_at": note.updated_at.isoformat()}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def doctor_dashboard_overview(request):
    caller_email(request)
    doctor = _doctor_for(request.user)
    now = timezone.now()
    qs = Appointment.objects.filter(doctor=doctor).select_related("member", "doctor", "requested_by")
    counts = {key: qs.filter(status=key).count() for key in Appointment.Status.values}
    pending_chats = DoctorChatRequest.objects.filter(doctor=doctor, status=DoctorChatRequest.Status.REQUESTED).count()
    active_chats = DoctorChatRequest.objects.filter(doctor=doctor, status=DoctorChatRequest.Status.ACCEPTED).count()
    upcoming = qs.filter(status=Appointment.Status.ACCEPTED, scheduled_at__gte=now).order_by("scheduled_at", "id")[:10]
    recent = qs.filter(status__in=[Appointment.Status.COMPLETED, Appointment.Status.CANCELLED, Appointment.Status.REJECTED]).order_by("-updated_at", "-id")[:10]
    return Response({
        "generated_at": now.isoformat(),
        "counts": {"appointments_today": qs.filter(status=Appointment.Status.ACCEPTED, scheduled_at__date=now.date()).count(),
                   "upcoming_appointments": qs.filter(status=Appointment.Status.ACCEPTED, scheduled_at__gte=now).count(),
                   "pending_appointment_requests": counts[Appointment.Status.REQUESTED],
                   "pending_reschedule_requests": AppointmentRescheduleRequest.objects.filter(appointment__doctor=doctor, status=AppointmentRescheduleRequest.Status.PENDING).count(),
                   "completed_appointments": counts[Appointment.Status.COMPLETED],
                   "pending_chat_requests": pending_chats, "active_chats": active_chats},
        "appointments_by_status": counts,
        "upcoming": [_appointment_data(a) for a in upcoming],
        "recent_history": [_appointment_data(a) for a in recent],
    })


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def doctor_availability(request):
    caller_email(request)
    is_admin = request.user.role == Account.Role.SUPER_ADMIN
    if request.method == "GET" and is_admin and request.query_params.get("doctor_id"):
        _require_staff(request.user, super_admin=True)
        doctor = get_object_or_404(DoctorProfile, pk=request.query_params.get("doctor_id"))
    elif request.method == "POST" and is_admin:
        _require_staff(request.user, super_admin=True)
        doctor = get_object_or_404(DoctorProfile, pk=request.data.get("doctor_id"))
        value = request.data.get("is_available")
        if not isinstance(value, bool):
            raise ValidationError({"is_available": "Use true or false."})
        if doctor.status != DoctorProfile.Status.APPROVED and value:
            raise ValidationError({"is_available": "Only an approved doctor can be marked available."})
        previous = doctor.is_available
        doctor.is_available = value
        doctor.save(update_fields=["is_available", "updated_at"])
        _audit(request.user, "admin_doctor_availability_changed", doctor=doctor,
               metadata={"previous": previous, "current": value})
        _notify(doctor.account, "availability_admin_changed", "Availability updated by MedLife", "The Super Admin has updated your availability.")
        return Response({"doctor_id": doctor.pk, "is_available": doctor.is_available})
    else:
        doctor = _doctor_for(request.user)
    if request.method == "GET":
        slots = DoctorAvailabilitySlot.objects.filter(doctor=doctor)
        return Response({"doctor_id": doctor.pk, "is_available": doctor.is_available, "slots": [
            {"id": x.pk, "weekday": x.weekday, "start_time": x.start_time.strftime("%H:%M"),
             "end_time": x.end_time.strftime("%H:%M"), "is_active": x.is_active} for x in slots
        ]})
    if request.user.role != Account.Role.DOCTOR or doctor.account_id != request.user.pk:
        raise PermissionDenied("Only the doctor can manage their availability slots.")
    if request.method == "DELETE":
        slot_id = request.query_params.get("slot_id")
        slot = get_object_or_404(DoctorAvailabilitySlot, pk=slot_id, doctor=doctor)
        slot.delete()
        _audit(request.user, "doctor_availability_slot_deleted", doctor=doctor, metadata={"slot_id": int(slot_id)})
        return Response({"deleted": True, "slot_id": int(slot_id)})
    try:
        weekday = int(request.data.get("weekday"))
    except (TypeError, ValueError):
        raise ValidationError({"weekday": "Use an integer from 0 (Monday) to 6 (Sunday)."})
    if weekday < 0 or weekday > 6:
        raise ValidationError({"weekday": "Use an integer from 0 (Monday) to 6 (Sunday)."})
    from django.utils.dateparse import parse_time
    start_time = parse_time(str(request.data.get("start_time", "")))
    end_time = parse_time(str(request.data.get("end_time", "")))
    if not start_time or not end_time or start_time >= end_time:
        raise ValidationError({"time": "Provide valid start_time and end_time in HH:MM format; start must be before end."})
    overlaps = DoctorAvailabilitySlot.objects.filter(doctor=doctor, weekday=weekday, is_active=True,
        start_time__lt=end_time, end_time__gt=start_time)
    if overlaps.exists():
        raise ValidationError({"time": "This slot overlaps an existing availability slot."})
    slot = DoctorAvailabilitySlot.objects.create(doctor=doctor, weekday=weekday, start_time=start_time, end_time=end_time)
    _audit(request.user, "doctor_availability_slot_created", doctor=doctor, metadata={"slot_id": slot.pk, "weekday": weekday})
    return Response({"slot": {"id": slot.pk, "weekday": slot.weekday, "start_time": slot.start_time.strftime("%H:%M"),
        "end_time": slot.end_time.strftime("%H:%M"), "is_active": slot.is_active}}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_reschedule(request, appointment_id):
    caller_email(request)
    appointment = get_object_or_404(Appointment.objects.select_related("doctor__account", "member", "requested_by"), pk=appointment_id)
    is_patient = request.user.role == Account.Role.PATIENT and appointment.requested_by_id == request.user.pk
    is_doctor = request.user.role == Account.Role.DOCTOR and appointment.doctor.account_id == request.user.pk
    if is_doctor:
        is_doctor = _doctor_for(request.user).pk == appointment.doctor_id
    is_admin = request.user.role == Account.Role.SUPER_ADMIN
    if is_admin:
        _require_staff(request.user, super_admin=True)
    if not (is_patient or is_doctor or is_admin):
        raise PermissionDenied("You cannot request a change to this appointment.")
    if appointment.status != Appointment.Status.ACCEPTED:
        raise ValidationError({"detail": "Only accepted appointments can be rescheduled."})
    proposed_at = _parse_datetime(request.data.get("proposed_at"), "proposed_at")
    if proposed_at <= timezone.now():
        raise ValidationError({"proposed_at": "Choose a future date and time."})
    _validate_doctor_slot(appointment.doctor, proposed_at, "proposed_at")
    if AppointmentRescheduleRequest.objects.filter(appointment=appointment, status=AppointmentRescheduleRequest.Status.PENDING).exists():
        raise ValidationError({"detail": "A rescheduling request is already pending for this appointment."})
    item = AppointmentRescheduleRequest.objects.create(appointment=appointment, requested_by=request.user,
        proposed_at=proposed_at, reason=str(request.data.get("reason", "")).strip()[:1000])
    _record_appointment_history(appointment, request.user, "reschedule_requested", appointment.status, appointment.status,
        reason=item.reason, metadata={"reschedule_request_id": item.pk, "proposed_at": proposed_at.isoformat()})
    other = appointment.requested_by if is_doctor or is_admin else appointment.doctor.account
    _notify(other, "reschedule_requested", "Appointment rescheduling requested", "A new appointment time has been proposed.", appointment=appointment)
    return Response({"reschedule_request": {"id": item.pk, "appointment_id": appointment.pk, "proposed_at": proposed_at.isoformat(),
        "reason": item.reason, "status": item.status, "requested_by": request.user.email}}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reschedule_requests(request):
    caller_email(request)
    role = request.query_params.get("role", "").strip().lower()
    if request.user.role == Account.Role.DOCTOR and role in ("", "doctor"):
        doctor = _doctor_for(request.user)
        qs = AppointmentRescheduleRequest.objects.filter(appointment__doctor=doctor)
    elif request.user.role == Account.Role.PATIENT and role in ("", "patient"):
        qs = AppointmentRescheduleRequest.objects.filter(appointment__requested_by=request.user)
    elif request.user.role == Account.Role.SUPER_ADMIN and role == "admin":
        _require_staff(request.user, super_admin=True)
        qs = AppointmentRescheduleRequest.objects.all()
    else:
        raise PermissionDenied("You cannot view these rescheduling requests.")
    state = request.query_params.get("status", "").strip().lower()
    if state:
        if state not in AppointmentRescheduleRequest.Status.values:
            raise ValidationError({"status": "Invalid rescheduling request status."})
        qs = qs.filter(status=state)
    results = []
    for item in qs.select_related("appointment__doctor", "appointment__member", "appointment__requested_by", "requested_by", "decided_by")[:200]:
        appointment = item.appointment
        results.append({"id": item.pk, "appointment_id": appointment.pk, "doctor_id": appointment.doctor_id,
            "doctor_name": appointment.doctor.full_name, "member_id": appointment.member_id,
            "member_name": f"{appointment.member.first_name} {appointment.member.last_name}".strip(),
            "current_scheduled_at": (appointment.scheduled_at or appointment.preferred_at).isoformat(),
            "proposed_at": item.proposed_at.isoformat(), "reason": item.reason, "status": item.status,
            "requested_by": item.requested_by.email, "decided_by": item.decided_by.email if item.decided_by_id else None,
            "created_at": item.created_at.isoformat(), "decided_at": item.decided_at.isoformat() if item.decided_at else None})
    return Response({"reschedule_requests": results, "count": len(results)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def decide_reschedule(request, request_id):
    caller_email(request)
    item = get_object_or_404(AppointmentRescheduleRequest.objects.select_related("appointment__doctor__account", "appointment__requested_by", "appointment__member"), pk=request_id)
    appointment = item.appointment
    is_patient = request.user.role == Account.Role.PATIENT and appointment.requested_by_id == request.user.pk
    is_doctor = request.user.role == Account.Role.DOCTOR and appointment.doctor.account_id == request.user.pk
    if is_doctor:
        is_doctor = _doctor_for(request.user).pk == appointment.doctor_id
    is_admin = request.user.role == Account.Role.SUPER_ADMIN
    if is_admin:
        _require_staff(request.user, super_admin=True)
    if not (is_patient or is_doctor or is_admin):
        raise PermissionDenied("You cannot decide this rescheduling request.")
    if item.status != AppointmentRescheduleRequest.Status.PENDING:
        raise ValidationError({"detail": "This rescheduling request is no longer pending."})
    decision = str(request.data.get("decision", "")).strip().lower()
    if decision not in ("accept", "reject"):
        raise ValidationError({"decision": "Use accept or reject."})
    # A party cannot approve its own request unless Super Admin is intervening.
    if item.requested_by_id == request.user.pk and not is_admin:
        raise PermissionDenied("The person who proposed the new time cannot approve their own request.")
    if decision == "accept":
        if appointment.status != Appointment.Status.ACCEPTED:
            raise ValidationError({"detail": "Only accepted appointments can be rescheduled."})
        _validate_doctor_slot(appointment.doctor, item.proposed_at, "proposed_at")
        conflict = Appointment.objects.filter(doctor=appointment.doctor, status=Appointment.Status.ACCEPTED,
            scheduled_at=item.proposed_at).exclude(pk=appointment.pk).exists()
        if conflict:
            raise ValidationError({"proposed_at": "The doctor already has an appointment at that time."})
        previous = appointment.scheduled_at or appointment.preferred_at
        appointment.scheduled_at = item.proposed_at
        appointment.preferred_at = item.proposed_at
        appointment.save(update_fields=["scheduled_at", "preferred_at", "updated_at"])
        item.status = AppointmentRescheduleRequest.Status.ACCEPTED
        _record_appointment_history(appointment, request.user, "rescheduled", appointment.status, appointment.status,
            reason=item.reason, metadata={"previous_at": previous.isoformat(), "new_at": item.proposed_at.isoformat(), "reschedule_request_id": item.pk})
    else:
        item.status = AppointmentRescheduleRequest.Status.REJECTED
        _record_appointment_history(appointment, request.user, "reschedule_rejected", appointment.status, appointment.status,
            reason=item.reason, metadata={"reschedule_request_id": item.pk})
    item.decided_by = request.user
    item.decided_at = timezone.now()
    item.save(update_fields=["status", "decided_by", "decided_at", "updated_at"])
    for recipient in {appointment.doctor.account, appointment.requested_by}:
        if recipient.pk != request.user.pk:
            _notify(recipient, f"reschedule_{item.status}", "Rescheduling request updated", "The proposed appointment time has been reviewed.", appointment=appointment)
    return Response({"reschedule_request": {"id": item.pk, "appointment_id": appointment.pk, "proposed_at": item.proposed_at.isoformat(),
        "status": item.status, "decided_at": item.decided_at.isoformat() if item.decided_at else None}, "appointment": _appointment_data(appointment)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def consultation_note_revisions(request, appointment_id):
    caller_email(request)
    appointment = get_object_or_404(Appointment.objects.select_related("member", "doctor__account", "requested_by"), pk=appointment_id)
    is_patient = request.user.role == Account.Role.PATIENT and appointment.requested_by_id == request.user.pk
    is_doctor = request.user.role == Account.Role.DOCTOR and appointment.doctor.account_id == request.user.pk
    if is_doctor:
        is_doctor = _doctor_for(request.user).pk == appointment.doctor_id and bool(_active_grant(appointment.member, appointment.doctor, "consultation_notes"))
    if not (is_patient or is_doctor):
        raise PermissionDenied("You cannot view this consultation note history.")
    note = get_object_or_404(ConsultationNote, appointment=appointment)
    return Response({"appointment_id": appointment.pk, "revisions": [{
        "id": item.pk, "content": item.content, "sections": item.sections,
        "finalized_at": item.finalized_at.isoformat() if item.finalized_at else None,
        "revised_by": item.revised_by.email, "created_at": item.created_at.isoformat(),
    } for item in note.revisions.select_related("revised_by").all()]})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def consultation_summary_download(request, appointment_id):
    caller_email(request)
    appointment = get_object_or_404(Appointment.objects.select_related("doctor__account", "member", "requested_by"), pk=appointment_id)
    is_patient = request.user.role == Account.Role.PATIENT and appointment.requested_by_id == request.user.pk
    is_doctor = request.user.role == Account.Role.DOCTOR and appointment.doctor.account_id == request.user.pk
    if is_doctor:
        is_doctor = _doctor_for(request.user).pk == appointment.doctor_id and bool(_active_grant(appointment.member, appointment.doctor, "consultation_notes"))
    if not (is_patient or is_doctor):
        raise PermissionDenied("You cannot download this consultation summary.")
    note = get_object_or_404(ConsultationNote, appointment=appointment)
    lines = ["MedLife Consultation Summary", f"Appointment ID: {appointment.pk}", f"Patient: {appointment.member.first_name} {appointment.member.last_name}".strip(),
        f"Doctor: {appointment.doctor.full_name}", f"Appointment time: {(appointment.scheduled_at or appointment.preferred_at).isoformat()}", ""]
    labels = {"symptoms": "Symptoms", "observations": "Observations", "assessment": "Assessment", "recommendations": "Recommendations", "follow_up": "Follow-up"}
    if note.sections:
        for key, label in labels.items():
            value = note.sections.get(key)
            if value:
                lines.extend([f"{label}:", str(value), ""])
    if note.content:
        lines.extend(["Consultation Notes:", note.content, ""])
    lines.append(f"Finalized: {note.finalized_at.isoformat() if note.finalized_at else 'No'}")
    response = HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="medlife-consultation-{appointment.pk}.txt"'
    _audit(request.user, "consultation_summary_downloaded", member=appointment.member, doctor=appointment.doctor, metadata={"appointment_id": appointment.pk})
    return response


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def chat_requests(request):
    caller_email(request)
    if request.method == "GET":
        role = request.query_params.get("role", "patient").strip().lower()
        if role == "doctor":
            doctor = _doctor_for(request.user)
            qs = DoctorChatRequest.objects.filter(doctor=doctor)
        elif role == "patient":
            if request.user.role != Account.Role.PATIENT:
                raise PermissionDenied("Patient account access is required.")
            qs = DoctorChatRequest.objects.filter(requested_by=request.user)
        else:
            raise ValidationError({"role": "Use patient or doctor."})
        state = request.query_params.get("status", "").strip().lower()
        if state:
            if state not in DoctorChatRequest.Status.values:
                raise ValidationError({"status": "Invalid chat request status."})
            qs = qs.filter(status=state)
        return Response({"chat_requests": [_chat_request_data(c) for c in qs.select_related("member", "doctor__account")]})

    member = _member_for_owner(request.user, request.data.get("member_id"))
    doctor = get_object_or_404(DoctorProfile, pk=request.data.get("doctor_id"), status=DoctorProfile.Status.APPROVED, is_available=True)
    scopes = request.data.get("consent_scopes")
    with transaction.atomic():
        grant = _ensure_grant(member, doctor, scopes)
        _audit(request.user, "doctor_record_access_granted", member=member, doctor=doctor, metadata={"grant_id": grant.pk, "scopes": grant.scopes, "source": "chat"})
        chat = DoctorChatRequest.objects.create(
            member=member, doctor=doctor, requested_by=request.user,
            message=str(request.data.get("message", "")).strip()[:1000],
        )
        _notify(doctor.account, "chat_requested", "New online consultation request", "A patient has requested an online consultation.", chat_request=chat)
        _notify(request.user, "chat_requested", "Online consultation request submitted", "Your request is awaiting the doctor's decision.", chat_request=chat)
    return Response({"chat_request": _chat_request_data(chat)}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_request_decision(request, chat_request_id):
    caller_email(request)
    doctor = _doctor_for(request.user)
    decision = str(request.data.get("decision", "")).strip().lower()
    if decision not in ("accept", "reject"):
        raise ValidationError({"decision": "Use accept or reject."})
    chat = get_object_or_404(DoctorChatRequest.objects.select_related("member", "doctor__account", "requested_by"), pk=chat_request_id, doctor=doctor)
    if chat.status != DoctorChatRequest.Status.REQUESTED:
        raise ValidationError({"detail": "Only requested chats can be accepted or rejected."})
    if decision == "accept":
        if not _active_grant(chat.member, doctor, "profile"):
            raise PermissionDenied("The patient's record-sharing consent is no longer active.")
        chat.status = DoctorChatRequest.Status.ACCEPTED
    else:
        chat.status = DoctorChatRequest.Status.REJECTED
    chat.decided_at = timezone.now()
    chat.save(update_fields=["status", "decided_at", "updated_at"])
    _notify(chat.requested_by, f"chat_{chat.status}", f"Online consultation {chat.status}", "Your online consultation request status has changed.", chat_request=chat)
    _notify(doctor.account, f"chat_{chat.status}", f"Online consultation {chat.status}", "The online consultation request was updated.", chat_request=chat)
    return Response({"chat_request": _chat_request_data(chat)})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def chat_messages(request, chat_request_id):
    caller_email(request)
    chat = get_object_or_404(DoctorChatRequest.objects.select_related("member", "doctor__account", "requested_by"), pk=chat_request_id)
    is_patient = chat.requested_by_id == request.user.pk and request.user.role == Account.Role.PATIENT
    is_doctor = chat.doctor.account_id == request.user.pk and request.user.role == Account.Role.DOCTOR
    if is_doctor:
        doctor = _doctor_for(request.user)
        is_doctor = doctor.pk == chat.doctor_id
    if not (is_patient or is_doctor):
        raise PermissionDenied("You are not a participant in this conversation.")
    if request.method == "POST" and chat.status != DoctorChatRequest.Status.ACCEPTED:
        raise ValidationError({"detail": "Messaging is available only while the conversation is active."})
    if request.method == "GET" and chat.status not in (DoctorChatRequest.Status.ACCEPTED, DoctorChatRequest.Status.CLOSED):
        raise ValidationError({"detail": "Messages are available only for accepted or closed conversations."})
    if not _active_grant(chat.member, chat.doctor, "profile"):
        raise PermissionDenied("The patient's record-sharing consent is no longer active.")
    if request.method == "POST":
        text = str(request.data.get("text", "")).strip()
        if not text or len(text) > 20000:
            raise ValidationError({"text": "Message must contain 1 to 20000 characters."})
        msg = DoctorChatMessage.objects.create(chat_request=chat, sender=request.user, text=text)
        _audit(request.user, "doctor_chat_message_sent", member=chat.member, doctor=chat.doctor, metadata={"chat_request_id": chat.pk, "message_id": msg.pk})
        other = chat.doctor.account if is_patient else chat.requested_by
        _notify(other, "doctor_chat_message", "New consultation message", "You have a new message in MedLife.", chat_request=chat)
        return Response({"message": {"id": msg.pk, "sender_email": request.user.email, "text": msg.text, "created_at": msg.created_at.isoformat()}}, status=status.HTTP_201_CREATED)
    messages = chat.messages.select_related("sender").all()[:500]
    return Response({"messages": [{
        "id": m.pk, "sender_email": m.sender.email, "text": m.text, "created_at": m.created_at.isoformat(),
    } for m in messages]})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def close_chat(request, chat_request_id):
    caller_email(request)
    chat = get_object_or_404(DoctorChatRequest.objects.select_related("doctor__account", "member", "requested_by"), pk=chat_request_id)
    is_patient = chat.requested_by_id == request.user.pk and request.user.role == Account.Role.PATIENT
    is_doctor = chat.doctor.account_id == request.user.pk and request.user.role == Account.Role.DOCTOR
    if is_doctor:
        is_doctor = _doctor_for(request.user).pk == chat.doctor_id
    if not (is_patient or is_doctor):
        raise PermissionDenied("Only a participant can close this conversation.")
    if chat.status != DoctorChatRequest.Status.ACCEPTED:
        raise ValidationError({"detail": "Only an accepted conversation can be closed."})
    chat.status = DoctorChatRequest.Status.CLOSED
    chat.save(update_fields=["status", "updated_at"])
    other = chat.doctor.account if is_patient else chat.requested_by
    _notify(other, "chat_closed", "Online consultation closed", "The online consultation has been closed.", chat_request=chat)
    _audit(request.user, "doctor_chat_closed", member=chat.member, doctor=chat.doctor, metadata={"chat_request_id": chat.pk})
    return Response({"chat_request": _chat_request_data(chat)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notifications(request):
    caller_email(request)
    qs = DoctorNotification.objects.filter(recipient=request.user)
    unread = request.query_params.get("unread", "").lower()
    if unread in ("1", "true", "yes"):
        qs = qs.filter(read_at__isnull=True)
    qs = qs[:200]
    return Response({"notifications": [{
        "id": n.pk, "kind": n.kind, "title": n.title, "message": n.message,
        "appointment_id": n.appointment_id, "chat_request_id": n.chat_request_id,
        "is_read": n.read_at is not None, "created_at": n.created_at.isoformat(),
        "read_at": n.read_at.isoformat() if n.read_at else None,
    } for n in qs]})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    caller_email(request)
    notification = get_object_or_404(DoctorNotification, pk=notification_id, recipient=request.user)
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
    return Response({"id": notification.pk, "is_read": True, "read_at": notification.read_at.isoformat()})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_chat_request(request, chat_request_id):
    caller_email(request)
    chat = get_object_or_404(
        DoctorChatRequest.objects.select_related("doctor__account", "member", "requested_by"),
        pk=chat_request_id,
    )
    is_patient = chat.requested_by_id == request.user.pk and request.user.role == Account.Role.PATIENT
    is_doctor = chat.doctor.account_id == request.user.pk and request.user.role == Account.Role.DOCTOR
    if is_doctor:
        doctor = _doctor_for(request.user)
        is_doctor = doctor.pk == chat.doctor_id
    if not (is_patient or is_doctor):
        raise PermissionDenied("You cannot cancel this chat request.")
    if chat.status not in (DoctorChatRequest.Status.REQUESTED, DoctorChatRequest.Status.ACCEPTED):
        raise ValidationError({"detail": "Only requested or accepted chat requests can be cancelled."})
    chat.status = DoctorChatRequest.Status.CANCELLED
    chat.save(update_fields=["status", "updated_at"])
    recipient = chat.doctor.account if is_patient else chat.requested_by
    _notify(recipient, "chat_cancelled", "Online consultation cancelled", "An online consultation request has been cancelled.", chat_request=chat)
    _audit(request.user, "doctor_chat_request_cancelled", member=chat.member, doctor=chat.doctor, metadata={"chat_request_id": chat.pk})
    return Response({"chat_request": _chat_request_data(chat)})


# ---------------------------------------------------------------------------
# Super-admin dashboard APIs. All endpoints require the persisted super_admin role.
# ---------------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_dashboard_overview(request):
    caller_email(request)
    _require_staff(request.user, super_admin=True)
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    patients = Account.objects.filter(role=Account.Role.PATIENT)
    doctors = DoctorProfile.objects.select_related("account")
    applications = DoctorApplication.objects.all()
    appointments_qs = Appointment.objects.all()
    status_counts = {key: 0 for key in Appointment.Status.values}
    for row in appointments_qs.values("status").annotate(total=Count("id")):
        status_counts[row["status"]] = row["total"]
    recent_audit = DoctorAuditLog.objects.select_related("actor", "doctor").order_by("-created_at", "-id")[:10]
    recent_appointments = AppointmentHistory.objects.select_related("actor", "appointment").order_by("-created_at", "-id")[:10]
    activity = [{
        "id": f"audit-{item.pk}", "source": "admin_audit", "action": item.action,
        "actor": item.actor.email, "created_at": item.created_at.isoformat(),
        "doctor_id": item.doctor_id, "metadata": item.metadata,
    } for item in recent_audit]
    activity.extend([{
        "id": f"appointment-{item.pk}", "source": "appointment_history", "action": item.action,
        "actor": item.actor.email if item.actor_id else None, "created_at": item.created_at.isoformat(),
        "appointment_id": item.appointment_id, "from_status": item.from_status,
        "to_status": item.to_status, "reason": item.reason,
    } for item in recent_appointments])
    activity.sort(key=lambda x: x["created_at"], reverse=True)
    return Response({
        "totals": {
            "patients": patients.count(),
            "doctors": doctors.count(),
            "pending_applications": applications.filter(status=DoctorApplication.Status.PENDING).count(),
        },
        "doctors_by_status": {row["status"]: row["total"] for row in doctors.values("status").annotate(total=Count("id"))},
        "applications_by_status": {row["status"]: row["total"] for row in applications.values("status").annotate(total=Count("id"))},
        "appointments_by_status": status_counts,
        "appointments_today": appointments_qs.filter(preferred_at__date=now.date()).count(),
        "appointments_this_month": appointments_qs.filter(created_at__gte=month_start).count(),
        "recent_activity": activity[:10],
        "pending_application_alerts": [{
            "id": app.pk, "name": app.full_name, "email": app.email,
            "specialty": app.specialty, "created_at": app.created_at.isoformat(),
        } for app in applications.filter(status=DoctorApplication.Status.PENDING).order_by("created_at", "id")[:10]],
        "generated_at": now.isoformat(),
    })


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def admin_doctors(request):
    caller_email(request)
    _require_staff(request.user, super_admin=True)
    if request.method == "POST":
        doctor_id = request.data.get("doctor_id")
        action = str(request.data.get("action", "")).strip().lower()
        reason = str(request.data.get("reason", "")).strip()[:1000]
        if action not in ("suspend", "reactivate"):
            raise ValidationError({"action": "Use suspend or reactivate."})
        with transaction.atomic():
            profile = get_object_or_404(DoctorProfile.objects.select_for_update().select_related("account"), pk=doctor_id)
            previous = profile.status
            if action == "suspend":
                if previous != DoctorProfile.Status.APPROVED:
                    raise ValidationError({"detail": "Only approved doctors can be suspended."})
                profile.status = DoctorProfile.Status.SUSPENDED
                profile.is_available = False
            else:
                if previous != DoctorProfile.Status.SUSPENDED:
                    raise ValidationError({"detail": "Only suspended doctors can be reactivated."})
                profile.status = DoctorProfile.Status.APPROVED
            profile.save(update_fields=["status", "is_available", "updated_at"])
            _audit(request.user, f"doctor_{action}ed" if action == "suspend" else "doctor_reactivated",
                   doctor=profile, metadata={"previous_status": previous, "new_status": profile.status, "reason": reason})
        return Response({"doctor": _admin_doctor_data(profile), "action": action})

    qs = DoctorProfile.objects.select_related("account").all()
    query = str(request.query_params.get("q", "")).strip()
    state = str(request.query_params.get("status", "")).strip().lower()
    available = str(request.query_params.get("available", "")).strip().lower()
    if query:
        qs = qs.filter(Q(full_name__icontains=query) | Q(account__email__icontains=query) |
                       Q(specialty__icontains=query) | Q(registration_number__icontains=query) |
                       Q(doctor_id__icontains=query))
    if state:
        if state not in DoctorProfile.Status.values:
            raise ValidationError({"status": "Invalid doctor status."})
        qs = qs.filter(status=state)
    if available in ("true", "false"):
        qs = qs.filter(is_available=(available == "true"))
    return Response({"doctors": [_admin_doctor_data(item) for item in qs.order_by("full_name", "id")[:200]]})


def _admin_doctor_data(profile):
    return {
        "id": profile.pk, "doctor_id": profile.doctor_id, "account_id": profile.account_id,
        "email": profile.account.email, "full_name": profile.full_name, "specialty": profile.specialty,
        "qualifications": profile.qualifications, "registration_number": profile.registration_number,
        "clinic_name": profile.clinic_name, "years_experience": profile.years_experience,
        "status": profile.status, "is_available": profile.is_available,
        "verified_at": profile.verified_at.isoformat() if profile.verified_at else None,
        "created_at": profile.created_at.isoformat(), "updated_at": profile.updated_at.isoformat(),
        "appointments_total": profile.appointments.count(),
        "appointments_completed": profile.appointments.filter(status=Appointment.Status.COMPLETED).count(),
        "appointments_pending": profile.appointments.filter(status=Appointment.Status.REQUESTED).count(),
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_patients(request):
    caller_email(request)
    _require_staff(request.user, super_admin=True)
    qs = Account.objects.filter(role=Account.Role.PATIENT).annotate(family_profile_count=Count("members", distinct=True))
    query = str(request.query_params.get("q", "")).strip()
    if query:
        qs = qs.filter(email__icontains=query)
    patients = [{
        "id": account.pk, "email": account.email,
        "created_at": account.created_at.isoformat(),
        "account_status": "registered",
        "family_profile_count": account.family_profile_count,
    } for account in qs.order_by("-created_at", "-id")[:200]]
    return Response({"patients": patients})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_analytics(request):
    caller_email(request)
    _require_staff(request.user, super_admin=True)
    months = []
    now = timezone.now()
    for offset in range(5, -1, -1):
        year = now.year
        month = now.month - offset
        while month <= 0:
            month += 12
            year -= 1
        months.append((year, month))
    first_year, first_month = months[0]
    start = now.replace(year=first_year, month=first_month, day=1, hour=0, minute=0, second=0, microsecond=0)
    def monthly_counts(qs, field):
        counts = {}
        for row in qs.filter(**{f"{field}__gte": start}).annotate(month=TruncMonth(field)).values("month").annotate(total=Count("id")):
            counts[row["month"].strftime("%Y-%m")] = row["total"]
        return [{"month": f"{year:04d}-{month:02d}", "count": counts.get(f"{year:04d}-{month:02d}", 0)} for year, month in months]
    return Response({
        "period": "last_6_calendar_months",
        "patient_registrations": monthly_counts(Account.objects.filter(role=Account.Role.PATIENT), "created_at"),
        "doctor_registrations": monthly_counts(DoctorProfile.objects.all(), "created_at"),
        "doctor_applications": monthly_counts(DoctorApplication.objects.all(), "created_at"),
        "appointment_bookings": monthly_counts(Appointment.objects.all(), "created_at"),
        "generated_at": now.isoformat(),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_audit_log(request):
    caller_email(request)
    _require_staff(request.user, super_admin=True)
    action = str(request.query_params.get("action", "")).strip()
    actor = str(request.query_params.get("actor", "")).strip()
    limit_raw = request.query_params.get("limit", "100")
    try:
        limit = min(max(int(limit_raw), 1), 200)
    except (TypeError, ValueError):
        raise ValidationError({"limit": "Use an integer from 1 to 200."})
    logs = DoctorAuditLog.objects.select_related("actor", "doctor").all()
    if action:
        logs = logs.filter(action__icontains=action)
    if actor:
        logs = logs.filter(actor__email__icontains=actor)
    audit_items = [{
        "id": item.pk, "source": "admin_audit", "actor": item.actor.email,
        "action": item.action, "created_at": item.created_at.isoformat(),
        "doctor_id": item.doctor_id, "member_id": item.member_id, "metadata": item.metadata,
    } for item in logs.order_by("-created_at", "-id")[:limit]]
    history = AppointmentHistory.objects.select_related("actor").all()
    if actor:
        history = history.filter(actor__email__icontains=actor)
    if action:
        history = history.filter(action__icontains=action)
    audit_items.extend([{
        "id": item.pk, "source": "appointment_history", "actor": item.actor.email if item.actor_id else None,
        "action": item.action, "created_at": item.created_at.isoformat(),
        "appointment_id": item.appointment_id, "from_status": item.from_status,
        "to_status": item.to_status, "reason": item.reason, "metadata": item.metadata,
    } for item in history.order_by("-created_at", "-id")[:limit]])
    audit_items.sort(key=lambda item: item["created_at"], reverse=True)
    return Response({"events": audit_items[:limit], "limit": limit})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_appointment_history(request, appointment_id):
    caller_email(request)
    _require_staff(request.user, super_admin=True)
    get_object_or_404(Appointment, pk=appointment_id)
    items = AppointmentHistory.objects.filter(appointment_id=appointment_id).select_related("actor")
    return Response({"history": [{
        "id": item.pk, "actor": item.actor.email if item.actor_id else None,
        "action": item.action, "from_status": item.from_status, "to_status": item.to_status,
        "reason": item.reason, "metadata": item.metadata, "created_at": item.created_at.isoformat(),
    } for item in items]})
