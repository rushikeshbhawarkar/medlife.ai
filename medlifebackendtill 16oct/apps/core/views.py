# Purpose: Shared lightweight health endpoint for checking whether Django is responding.
# Edit this file for non-feature-specific diagnostic endpoints; never return secrets here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})
