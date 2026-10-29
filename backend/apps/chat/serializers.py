# Purpose: Validates chat message payloads sent by the frontend.
# Edit when the frontend's {role, text, ts} message contract changes.
from rest_framework import serializers

class ChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "ai"])
    text = serializers.CharField(max_length=20000, allow_blank=True)
    ts = serializers.IntegerField(min_value=0)

class SaveChatSerializer(serializers.Serializer):
    chat = ChatMessageSerializer(many=True, max_length=1000)
