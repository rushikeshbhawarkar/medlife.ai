

from apps.core.permissions import PatientRolePermission
# Purpose: HTTP adapters for the frontend's member endpoints; business rules live in services.py.
# Edit this file when endpoint input/output shapes change.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.core.identity import caller_email
from .serializers import MemberInputSerializer
from . import services

@api_view(["GET"])
@permission_classes([PatientRolePermission])
def getmember(request):
    return Response(services.get_members(caller_email(request)))

@api_view(["POST"])
@permission_classes([PatientRolePermission])
def addmember(request):
    email = caller_email(request)
    serializer = MemberInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(services.add_member(email, serializer.to_model_values()), status=201)

@api_view(["POST"])
@permission_classes([PatientRolePermission])
def editmember(request):
    email = caller_email(request)
    name = request.query_params.get("member_name", "")
    serializer = MemberInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # Tokens from the browser are deliberately ignored.
    return Response(services.edit_member(email, name, serializer.to_model_values()))

@api_view(["POST"])
@permission_classes([PatientRolePermission])
def removemember(request):
    return Response(services.remove_member(caller_email(request), request.query_params.get("member_name", "")))

@api_view(["GET"])
@permission_classes([PatientRolePermission])
def tokens(request):
    count = services.consume_token(caller_email(request), request.query_params.get("member_name", ""))
    return Response({"message": str(count)})
