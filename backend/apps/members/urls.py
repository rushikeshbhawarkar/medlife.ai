# Purpose: Exact routes used by the React member dashboard.
# Keep slash style identical to the frontend because APPEND_SLASH is disabled.
from django.urls import path
from . import views
urlpatterns = [
    path("getmember", views.getmember, name="getmember"),
    path("addmember", views.addmember, name="addmember"),
    path("editmember", views.editmember, name="editmember"),
    path("removemember", views.removemember, name="removemember"),
    path("tokens/", views.tokens, name="tokens"),
]
