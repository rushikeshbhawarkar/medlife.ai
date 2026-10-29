# Purpose: Validates authenticated, member-specific AI chat requests.
from rest_framework import serializers


class MemberQuestionSerializer(serializers.Serializer):
    member_name = serializers.RegexField(
        regex=r"^member[1-4]$",
        error_messages={"invalid": "member_name must be member1, member2, member3, or member4."},
    )
    provider = serializers.ChoiceField(
        choices=("gemini", "claude", "openai", "local", "ollama", "openai_compatible", "mock"),
        required=False,
    )
    # "model" is provider-specific and is validated against server allowlists.
    model = serializers.CharField(max_length=120, required=False, allow_blank=False)
    # Backward compatibility for clients that already send local_model.
    local_model = serializers.CharField(max_length=120, required=False, allow_blank=False)
    query = serializers.CharField(
        max_length=4000,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={"blank": "The query parameter is required."},
    )
