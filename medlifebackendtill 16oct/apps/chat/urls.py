# Purpose: Exact saved-chat routes used by React.
# Keep trailing slashes because the frontend requests these exact paths.
from django.urls import path
from . import views
urlpatterns = [
    path("fetchChat/", views.fetchchat, name="fetch-chat"),
    path("saveChat/", views.savechat, name="save-chat"),
]
