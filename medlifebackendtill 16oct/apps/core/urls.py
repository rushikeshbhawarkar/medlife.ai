# Purpose: Routes shared by the whole backend.
# Edit when adding or renaming a shared endpoint.
from django.urls import path
from .views import health
urlpatterns = [path("health/", health, name="health")]
