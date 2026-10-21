# # Purpose: Root URL map. Add one include per feature app; all frontend API paths live under /medlife/.
# # Edit this file when adding a new feature app or shared endpoint.
# from django.contrib import admin
# from django.urls import include, path

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("medlife/", include("apps.core.urls")),
#     path("medlife/", include("apps.accounts.urls")),
#     path("medlife/", include("apps.members.urls")),
#     path("medlife/", include("apps.chat.urls")),
#     path("medlife/", include("apps.ai.urls")),
#     path("medlife/", include("apps.documents.urls")),
# ]




# Purpose: Root URL map. Add one include per feature app; all frontend API paths live under /medlife/.
# Edit this file when adding a new feature app or shared endpoint.
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("medlife/", include("apps.core.urls")),
    path("medlife/", include("apps.accounts.urls")),
    path("medlife/", include("apps.members.urls")),
    path("medlife/", include("apps.chat.urls")),
    path("medlife/", include("apps.ai.urls")),
    path("medlife/", include("apps.documents.urls")),
    path("medlife/", include("apps.doctors.urls")),
]
