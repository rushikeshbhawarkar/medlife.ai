# Purpose: HTTP adapters for general AI questions and authenticated member-specific chat.
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from apps.core.permissions import PatientRolePermission
from apps.core.authentication import AccountTokenAuthentication
from .serializers import MemberQuestionSerializer
from .services import answer_member_query, answer_query
from .providers.factory import available_providers


class ProviderUnavailable(APIException):
    status_code = 503
    default_detail = "The health assistant is temporarily unavailable. Please try again later."


@api_view(["GET"])
@permission_classes([PatientRolePermission])
def providers(request):
    """Return only provider choices configured by the server; never expose credentials."""
    return Response(available_providers())


@api_view(["GET"])
@permission_classes([PatientRolePermission])
def prompt(request):
    """Legacy endpoint for general questions; does not access medical profile data."""
    query = request.query_params.get("query", "")
    provider = request.query_params.get("provider")
    local_model = request.query_params.get("local_model")
    model = request.query_params.get("model")
    try:
        return Response(answer_query(request, query, provider_name=provider, local_model=local_model, model=model))
    except RuntimeError:
        raise ProviderUnavailable()


@api_view(["POST"])
@authentication_classes([AccountTokenAuthentication])
@permission_classes([PatientRolePermission])
def ask_member(request):
    """Secure endpoint: answer a question using the authenticated account's selected member."""
    serializer = MemberQuestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        answer = answer_member_query(
            request=request,
            account=request.user,
            member_name=serializer.validated_data["member_name"],
            query=serializer.validated_data["query"],
            provider_name=serializer.validated_data.get("provider"),
            local_model=serializer.validated_data.get("local_model"),
            model=serializer.validated_data.get("model"),
        )
        return Response({"answer": answer})
    except RuntimeError:
        raise ProviderUnavailable()
