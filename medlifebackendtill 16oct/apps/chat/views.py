# # Purpose: HTTP adapters for fetching and replacing saved chat messages.
# # Edit this file when chat endpoint request or response shapes change.
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from apps.core.identity import caller_email
# from .serializers import SaveChatSerializer
# from .services import fetch_chat, save_chat

# @api_view(["GET"])
# def fetchchat(request):
#     return Response(fetch_chat(caller_email(request), request.query_params.get("member_name", "")))

# @api_view(["POST"])
# def savechat(request):
#     email = caller_email(request)
#     name = request.query_params.get("member_name", "")
#     serializer = SaveChatSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     return Response(save_chat(email, name, serializer.validated_data["chat"]))








from apps.core.permissions import PatientRolePermission
# Purpose: HTTP adapters for fetching and replacing saved chat messages.
# Edit this file when chat endpoint request or response shapes change.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.core.identity import caller_email
from .serializers import SaveChatSerializer
from .services import fetch_chat, save_chat

@api_view(["GET"])
@permission_classes([PatientRolePermission])
def fetchchat(request):
    return Response(fetch_chat(caller_email(request), request.query_params.get("member_name", "")))

@api_view(["POST"])
@permission_classes([PatientRolePermission])
def savechat(request):
    email = caller_email(request)
    name = request.query_params.get("member_name", "")
    serializer = SaveChatSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(save_chat(email, name, serializer.validated_data["chat"]))
