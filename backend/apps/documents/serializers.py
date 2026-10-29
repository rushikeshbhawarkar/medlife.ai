# Purpose: Validates scan-upload and review/correction requests and shapes responses in camelCase.
# Edit when the request fields or response contract of the documents endpoints change.
import re
from rest_framework import serializers
from .models import ScannedDocument

NOTICE = ("Text was extracted automatically and may contain errors, especially for handwriting. "
          "Check it against the original before relying on it. It is not verified medical advice.")


class ScanUploadSerializer(serializers.Serializer):
    image = serializers.FileField(error_messages={
        "required": "An image file is required (multipart field named 'image').",
        "invalid": "An image file is required (multipart field named 'image').",
        "empty": "The uploaded file is empty.",
    })
    documentType = serializers.ChoiceField(choices=ScannedDocument.DocumentType.choices,
                                           required=False, default=ScannedDocument.DocumentType.OTHER)
    member_name = serializers.CharField(required=False, allow_blank=True, default="", max_length=10)

    def validate_member_name(self, value):
        value = value.strip()
        if value and not re.fullmatch(r"member[1-4]", value):
            raise serializers.ValidationError("Invalid member_name.")
        return value


class DocumentUpdateSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=20000, required=False, allow_blank=False, trim_whitespace=False)
    isConfirmed = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError({"detail": "Provide description and/or isConfirmed."})
        if "description" in attrs and not attrs["description"].strip():
            raise serializers.ValidationError({"description": "The description cannot be blank."})
        return attrs


def document_to_frontend(doc, include_notice=True):
    data = {
        "id": doc.pk,
        "description": doc.description,
        "documentType": doc.document_type,
        "memberName": doc.member.key if doc.member_id else None,
        "processingStatus": "low_confidence" if doc.warnings else "ok",
        "ocrConfidence": doc.ocr_confidence,
        "warnings": list(doc.warnings),
        "isConfirmed": doc.is_confirmed,
        "isEdited": doc.description != doc.ocr_text,
        "createdAt": doc.created_at.isoformat(),
        "updatedAt": doc.updated_at.isoformat(),
    }
    if include_notice:
        data["notice"] = NOTICE
    return data



