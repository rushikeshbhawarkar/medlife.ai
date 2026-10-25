


# Purpose: HTTP adapters for scanning an image into a saved description and reviewing saved scans.
# Uses the existing bearer-token authentication (from /medlife/signin) on these views only.
import re

from rest_framework.decorators import api_view, authentication_classes, parser_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# i added
from apps.core.permissions import PatientRolePermission

from apps.core.authentication import AccountTokenAuthentication
from . import ocr, services
from .serializers import DocumentUpdateSerializer, ScanUploadSerializer, document_to_frontend


@api_view(["POST"])
@authentication_classes([AccountTokenAuthentication])
@permission_classes([PatientRolePermission])
@parser_classes([MultiPartParser])
def scan(request):
    ocr.check_declared_size(request.META.get("CONTENT_LENGTH"))  # before the body is parsed
    serializer = ScanUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data
    doc = services.scan_image(request.user, d["image"], d["documentType"], d["member_name"])
    return Response(document_to_frontend(doc), status=201)


@api_view(["GET"])
@authentication_classes([AccountTokenAuthentication])
@permission_classes([PatientRolePermission])
def document_list(request):
    member_name = request.query_params.get("member_name", "").strip()
    if member_name and not re.fullmatch(r"member[1-4]", member_name):  # same rule as the scan upload
        raise ValidationError({"member_name": "Invalid member_name."})
    docs = services.list_documents(request.user, member_name)
    return Response({"documents": [document_to_frontend(d, include_notice=False) for d in docs]})


@api_view(["GET", "PATCH", "DELETE"])
@authentication_classes([AccountTokenAuthentication])
@permission_classes([PatientRolePermission])
@parser_classes([JSONParser])
def document_detail(request, pk):
    if request.method == "DELETE":
        return Response(services.delete_document(request.user, pk))
    if request.method == "PATCH":
        serializer = DocumentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(document_to_frontend(services.update_document(request.user, pk, serializer.validated_data)))
    return Response(document_to_frontend(services.get_document(request.user, pk)))
