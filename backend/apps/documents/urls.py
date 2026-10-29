# Purpose: Routes for scanned documents, all under /medlife/documents/.
# Trailing slashes are used because APPEND_SLASH is disabled project-wide.
from django.urls import path
from . import views
urlpatterns = [
    path("documents/scan/", views.scan, name="documents-scan"),
    path("documents/", views.document_list, name="documents-list"),
    path("documents/<int:pk>/", views.document_detail, name="documents-detail"),
]
