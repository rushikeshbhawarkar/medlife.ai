
# # # from django.urls import path
# # # from . import views

# # # urlpatterns = [
# # #     path("doctor/admin/dashboard/", views.admin_dashboard_overview, name="doctor-admin-dashboard"),
# # #     path("doctor/admin/doctors/", views.admin_doctors, name="doctor-admin-doctors"),
# # #     path("doctor/admin/patients/", views.admin_patients, name="doctor-admin-patients"),
# # #     path("doctor/admin/analytics/", views.admin_analytics, name="doctor-admin-analytics"),
# # #     path("doctor/admin/audit-log/", views.admin_audit_log, name="doctor-admin-audit-log"),
# # #     path("doctor/admin/appointments/<int:appointment_id>/history/", views.admin_appointment_history, name="doctor-admin-appointment-history"),
# # #     path("doctors/", views.public_doctors, name="doctor-directory"),
# # #     path("doctor/profile/", views.doctor_profile, name="doctor-profile"),
# # #     path("doctor/applications/", views.submit_application, name="doctor-application-submit"),
# # #     path("doctor/activate-account/", views.activate_doctor_account, name="doctor-account-activate"),
# # #     path("doctor/applications/me/", views.my_application, name="doctor-application-me"),
# # #     path("doctor/admin/applications/", views.admin_applications, name="doctor-admin-applications"),
# # #     path("doctor/admin/applications/<int:application_id>/review/", views.review_application, name="doctor-admin-application-review"),
# # #     path("doctor/admin/applications/documents/<int:document_id>/", views.admin_application_document, name="doctor-admin-application-document"),
# # #     path("doctor/admin/invitations/", views.admin_invitations, name="doctor-admin-invitations"),
# # #     path("doctor/invitations/accept/", views.accept_invitation, name="doctor-invitation-accept"),
# # #     path("doctor/access-grants/", views.access_grants, name="doctor-access-grants"),
# # #     path("doctor/access-grants/<int:grant_id>/revoke/", views.revoke_access_grant, name="doctor-access-grant-revoke"),
# # #     path("doctor/shared-records/<int:member_id>/", views.shared_records, name="doctor-shared-records"),
# # #     path("doctor/appointments/", views.appointments, name="doctor-appointments"),
# # #     path("doctor/appointments/<int:appointment_id>/decision/", views.appointment_decision, name="doctor-appointment-decision"),
# # #     path("doctor/appointments/<int:appointment_id>/cancel/", views.cancel_appointment, name="doctor-appointment-cancel"),
# # #     path("doctor/appointments/<int:appointment_id>/complete/", views.complete_appointment, name="doctor-appointment-complete"),
# # #     path("doctor/appointments/<int:appointment_id>/notes/", views.consultation_note, name="doctor-consultation-note"),
# # #     path("doctor/chat-requests/", views.chat_requests, name="doctor-chat-requests"),
# # #     path("doctor/chat-requests/<int:chat_request_id>/cancel/", views.cancel_chat_request, name="doctor-chat-request-cancel"),
# # #     path("doctor/chat-requests/<int:chat_request_id>/decision/", views.chat_request_decision, name="doctor-chat-request-decision"),
# # #     path("doctor/chat-requests/<int:chat_request_id>/messages/", views.chat_messages, name="doctor-chat-messages"),
# # #     path("doctor/notifications/", views.notifications, name="doctor-notifications"),
# # #     path("doctor/notifications/<int:notification_id>/read/", views.mark_notification_read, name="doctor-notification-read"),
# # # ]





# # from django.urls import path
# # from . import views

# # urlpatterns = [
# #     path("doctor/admin/dashboard/", views.admin_dashboard_overview, name="doctor-admin-dashboard"),
# #     path("doctor/admin/doctors/", views.admin_doctors, name="doctor-admin-doctors"),
# #     path("doctor/admin/patients/", views.admin_patients, name="doctor-admin-patients"),
# #     path("doctor/admin/analytics/", views.admin_analytics, name="doctor-admin-analytics"),
# #     path("doctor/admin/audit-log/", views.admin_audit_log, name="doctor-admin-audit-log"),
# #     path("doctor/admin/appointments/<int:appointment_id>/history/", views.admin_appointment_history, name="doctor-admin-appointment-history"),
# #     path("doctors/", views.public_doctors, name="doctor-directory"),
# #     path("doctor/profile/", views.doctor_profile, name="doctor-profile"),
# #     path("doctor/dashboard/", views.doctor_dashboard_overview, name="doctor-dashboard-overview"),
# #     path("doctor/availability/", views.doctor_availability, name="doctor-availability"),
# #     path("doctor/applications/", views.submit_application, name="doctor-application-submit"),
# #     path("doctor/activate-account/", views.activate_doctor_account, name="doctor-account-activate"),
# #     path("doctor/applications/me/", views.my_application, name="doctor-application-me"),
# #     path("doctor/admin/applications/", views.admin_applications, name="doctor-admin-applications"),
# #     path("doctor/admin/applications/<int:application_id>/review/", views.review_application, name="doctor-admin-application-review"),
# #     path("doctor/admin/applications/documents/<int:document_id>/", views.admin_application_document, name="doctor-admin-application-document"),
# #     path("doctor/admin/invitations/", views.admin_invitations, name="doctor-admin-invitations"),
# #     path("doctor/invitations/accept/", views.accept_invitation, name="doctor-invitation-accept"),
# #     path("doctor/access-grants/", views.access_grants, name="doctor-access-grants"),
# #     path("doctor/access-grants/<int:grant_id>/revoke/", views.revoke_access_grant, name="doctor-access-grant-revoke"),
# #     path("doctor/patients/", views.doctor_patients, name="doctor-patients"),
# #     path("doctor/shared-records/<int:member_id>/", views.shared_records, name="doctor-shared-records"),
# #     path("doctor/appointments/", views.appointments, name="doctor-appointments"),
# #     path("doctor/appointments/<int:appointment_id>/decision/", views.appointment_decision, name="doctor-appointment-decision"),
# #     path("doctor/appointments/<int:appointment_id>/cancel/", views.cancel_appointment, name="doctor-appointment-cancel"),
# #     path("doctor/appointments/<int:appointment_id>/complete/", views.complete_appointment, name="doctor-appointment-complete"),
# #     path("doctor/appointments/<int:appointment_id>/reschedule/", views.request_reschedule, name="doctor-appointment-reschedule-request"),
# #     path("doctor/reschedule-requests/", views.reschedule_requests, name="doctor-reschedule-requests"),
# #     path("doctor/reschedule-requests/<int:request_id>/decision/", views.decide_reschedule, name="doctor-reschedule-decision"),
# #     path("doctor/appointments/<int:appointment_id>/notes/", views.consultation_note, name="doctor-consultation-note"),
# #     path("doctor/appointments/<int:appointment_id>/notes/revisions/", views.consultation_note_revisions, name="doctor-consultation-note-revisions"),
# #     path("doctor/appointments/<int:appointment_id>/summary/", views.consultation_summary_download, name="doctor-consultation-summary"),
# #     path("doctor/chat-requests/", views.chat_requests, name="doctor-chat-requests"),
# #     path("doctor/chat-requests/<int:chat_request_id>/cancel/", views.cancel_chat_request, name="doctor-chat-request-cancel"),
# #     path("doctor/chat-requests/<int:chat_request_id>/decision/", views.chat_request_decision, name="doctor-chat-request-decision"),
# #     path("doctor/chat-requests/<int:chat_request_id>/messages/", views.chat_messages, name="doctor-chat-messages"),
# #     path("doctor/chat-requests/<int:chat_request_id>/close/", views.close_chat, name="doctor-chat-close"),
# #     path("doctor/notifications/", views.notifications, name="doctor-notifications"),
# #     path("doctor/notifications/<int:notification_id>/read/", views.mark_notification_read, name="doctor-notification-read"),
# # ]







# from django.urls import path
# from . import views

# urlpatterns = [
#     path("doctor/admin/dashboard/", views.admin_dashboard_overview, name="doctor-admin-dashboard"),
#     path("doctor/admin/doctors/", views.admin_doctors, name="doctor-admin-doctors"),
#     path("doctor/admin/availability/", views.admin_availability, name="doctor-admin-availability"),
#     path("doctor/admin/patients/", views.admin_patients, name="doctor-admin-patients"),
#     path("doctor/admin/analytics/", views.admin_analytics, name="doctor-admin-analytics"),
#     path("doctor/admin/audit-log/", views.admin_audit_log, name="doctor-admin-audit-log"),
#     path("doctor/admin/appointments/<int:appointment_id>/history/", views.admin_appointment_history, name="doctor-admin-appointment-history"),
#     path("doctors/", views.public_doctors, name="doctor-directory"),
#     path("doctor/profile/", views.doctor_profile, name="doctor-profile"),
#     path("doctor/dashboard/", views.doctor_dashboard_overview, name="doctor-dashboard-overview"),
#     path("doctor/availability/", views.doctor_availability, name="doctor-availability"),
#     path("doctor/applications/", views.submit_application, name="doctor-application-submit"),
#     path("doctor/activate-account/", views.activate_doctor_account, name="doctor-account-activate"),
#     path("doctor/applications/me/", views.my_application, name="doctor-application-me"),
#     path("doctor/admin/applications/", views.admin_applications, name="doctor-admin-applications"),
#     path("doctor/admin/applications/<int:application_id>/review/", views.review_application, name="doctor-admin-application-review"),
#     path("doctor/admin/applications/documents/<int:document_id>/", views.admin_application_document, name="doctor-admin-application-document"),
#     path("doctor/admin/invitations/", views.admin_invitations, name="doctor-admin-invitations"),
#     path("doctor/invitations/accept/", views.accept_invitation, name="doctor-invitation-accept"),
#     path("doctor/access-grants/", views.access_grants, name="doctor-access-grants"),
#     path("doctor/access-grants/<int:grant_id>/revoke/", views.revoke_access_grant, name="doctor-access-grant-revoke"),
#     path("doctor/patients/", views.doctor_patients, name="doctor-patients"),
#     path("doctor/shared-records/<int:member_id>/", views.shared_records, name="doctor-shared-records"),
#     path("doctor/appointments/", views.appointments, name="doctor-appointments"),
#     path("doctor/appointments/<int:appointment_id>/decision/", views.appointment_decision, name="doctor-appointment-decision"),
#     path("doctor/appointments/<int:appointment_id>/cancel/", views.cancel_appointment, name="doctor-appointment-cancel"),
#     path("doctor/appointments/<int:appointment_id>/complete/", views.complete_appointment, name="doctor-appointment-complete"),
#     path("doctor/appointments/<int:appointment_id>/reschedule/", views.request_reschedule, name="doctor-appointment-reschedule-request"),
#     path("doctor/reschedule-requests/", views.reschedule_requests, name="doctor-reschedule-requests"),
#     path("doctor/reschedule-requests/<int:request_id>/decision/", views.decide_reschedule, name="doctor-reschedule-decision"),
#     path("doctor/appointments/<int:appointment_id>/notes/", views.consultation_note, name="doctor-consultation-note"),
#     path("doctor/appointments/<int:appointment_id>/notes/revisions/", views.consultation_note_revisions, name="doctor-consultation-note-revisions"),
#     path("doctor/appointments/<int:appointment_id>/summary/", views.consultation_summary_download, name="doctor-consultation-summary"),
#     path("doctor/chat-requests/", views.chat_requests, name="doctor-chat-requests"),
#     path("doctor/chat-requests/<int:chat_request_id>/cancel/", views.cancel_chat_request, name="doctor-chat-request-cancel"),
#     path("doctor/chat-requests/<int:chat_request_id>/decision/", views.chat_request_decision, name="doctor-chat-request-decision"),
#     path("doctor/chat-requests/<int:chat_request_id>/messages/", views.chat_messages, name="doctor-chat-messages"),
#     path("doctor/chat-requests/<int:chat_request_id>/close/", views.close_chat, name="doctor-chat-close"),
#     path("doctor/notifications/", views.notifications, name="doctor-notifications"),
#     path("doctor/notifications/<int:notification_id>/read/", views.mark_notification_read, name="doctor-notification-read"),
# ]







from django.urls import path
from . import views

urlpatterns = [
    path("doctor/admin/dashboard/", views.admin_dashboard_overview, name="doctor-admin-dashboard"),
    path("doctor/admin/doctors/", views.admin_doctors, name="doctor-admin-doctors"),
    path("doctor/admin/availability/", views.admin_availability, name="doctor-admin-availability"),
    path("doctor/admin/patients/", views.admin_patients, name="doctor-admin-patients"),
    path("doctor/admin/analytics/", views.admin_analytics, name="doctor-admin-analytics"),
    path("doctor/admin/audit-log/", views.admin_audit_log, name="doctor-admin-audit-log"),
    path("doctor/admin/appointments/<int:appointment_id>/history/", views.admin_appointment_history, name="doctor-admin-appointment-history"),
    path("doctors/", views.public_doctors, name="doctor-directory"),
    path("doctors/<int:doctor_id>/availability/", views.public_doctor_availability, name="public-doctor-availability"),
    path("doctor/profile/", views.doctor_profile, name="doctor-profile"),
    path("doctor/dashboard/", views.doctor_dashboard_overview, name="doctor-dashboard-overview"),
    path("doctor/availability/", views.doctor_availability, name="doctor-availability"),
    path("doctor/applications/", views.submit_application, name="doctor-application-submit"),
    path("doctor/activate-account/", views.activate_doctor_account, name="doctor-account-activate"),
    path("doctor/applications/me/", views.my_application, name="doctor-application-me"),
    path("doctor/admin/applications/", views.admin_applications, name="doctor-admin-applications"),
    path("doctor/admin/applications/<int:application_id>/review/", views.review_application, name="doctor-admin-application-review"),
    path("doctor/admin/applications/documents/<int:document_id>/", views.admin_application_document, name="doctor-admin-application-document"),
    path("doctor/admin/invitations/", views.admin_invitations, name="doctor-admin-invitations"),
    path("doctor/invitations/accept/", views.accept_invitation, name="doctor-invitation-accept"),
    path("doctor/access-grants/", views.access_grants, name="doctor-access-grants"),
    path("doctor/access-grants/<int:grant_id>/revoke/", views.revoke_access_grant, name="doctor-access-grant-revoke"),
    path("doctor/patients/", views.doctor_patients, name="doctor-patients"),
    path("doctor/shared-records/<int:member_id>/", views.shared_records, name="doctor-shared-records"),
    path("doctor/appointments/", views.appointments, name="doctor-appointments"),
    path("doctor/appointments/<int:appointment_id>/decision/", views.appointment_decision, name="doctor-appointment-decision"),
    path("doctor/appointments/<int:appointment_id>/cancel/", views.cancel_appointment, name="doctor-appointment-cancel"),
    path("doctor/appointments/<int:appointment_id>/complete/", views.complete_appointment, name="doctor-appointment-complete"),
    path("doctor/appointments/<int:appointment_id>/reschedule/", views.request_reschedule, name="doctor-appointment-reschedule-request"),
    path("doctor/reschedule-requests/", views.reschedule_requests, name="doctor-reschedule-requests"),
    path("doctor/reschedule-requests/<int:request_id>/decision/", views.decide_reschedule, name="doctor-reschedule-decision"),
    path("doctor/appointments/<int:appointment_id>/notes/", views.consultation_note, name="doctor-consultation-note"),
    path("doctor/appointments/<int:appointment_id>/notes/revisions/", views.consultation_note_revisions, name="doctor-consultation-note-revisions"),
    path("doctor/appointments/<int:appointment_id>/summary/", views.consultation_summary_download, name="doctor-consultation-summary"),
    path("doctor/chat-requests/", views.chat_requests, name="doctor-chat-requests"),
    path("doctor/chat-requests/<int:chat_request_id>/cancel/", views.cancel_chat_request, name="doctor-chat-request-cancel"),
    path("doctor/chat-requests/<int:chat_request_id>/decision/", views.chat_request_decision, name="doctor-chat-request-decision"),
    path("doctor/chat-requests/<int:chat_request_id>/messages/", views.chat_messages, name="doctor-chat-messages"),
    path("doctor/chat-requests/<int:chat_request_id>/close/", views.close_chat, name="doctor-chat-close"),
    path("doctor/notifications/", views.notifications, name="doctor-notifications"),
    path("doctor/notifications/<int:notification_id>/read/", views.mark_notification_read, name="doctor-notification-read"),
]
