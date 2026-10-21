# # Purpose: Owns scan -> OCR -> save logic and per-account ownership rules for scanned documents.
# # Every query is scoped to the authenticated account, so one user can never read or change another's records.
# from django.db import transaction
# from rest_framework.exceptions import NotFound
# from apps.members.models import FamilyMember
# from . import ocr
# from .models import ScannedDocument


# def _member_for(account, member_name):
#     if not member_name:
#         return None
#     try:
#         return FamilyMember.objects.get(account=account, slot=int(member_name[6:]))
#     except FamilyMember.DoesNotExist:
#         raise NotFound("Member not found")


# def _owned(account, pk):
#     try:
#         return ScannedDocument.objects.select_related("member").get(pk=pk, account=account)
#     except ScannedDocument.DoesNotExist:
#         # 404 (not 403) so the existence of other users' records is not revealed.
#         raise NotFound("Document not found")


# def scan_image(account, upload, document_type, member_name):
#     member = _member_for(account, member_name)
#     data = ocr.read_upload(upload)
#     result = ocr.extract_text_from_bytes(data)  # raises a clean API error on any failure; nothing saved then
#     return ScannedDocument.objects.create(
#         account=account, member=member, document_type=document_type,
#         ocr_text=result.text, description=result.text,
#         ocr_confidence=result.confidence, warnings=result.warnings,
#     )


# def list_documents(account, member_name=""):
#     queryset = ScannedDocument.objects.select_related("member").filter(account=account)
#     if member_name:
#         queryset = queryset.filter(member=_member_for(account, member_name))
#     return list(queryset)


# def get_document(account, pk):
#     return _owned(account, pk)


# @transaction.atomic
# def update_document(account, pk, values):
#     doc = ScannedDocument.objects.select_for_update().get(pk=_owned(account, pk).pk)
#     if "description" in values:
#         doc.description = values["description"]
#     if "isConfirmed" in values:
#         doc.is_confirmed = values["isConfirmed"]
#     elif "description" in values:
#         doc.is_confirmed = False  # corrected text must be re-confirmed
#     doc.save()
#     return _owned(account, pk)


# def delete_document(account, pk):
#     _owned(account, pk).delete()
#     return {"ok": True}














# # Purpose: Owns scan -> OCR -> save logic and per-account ownership rules for scanned documents.
# # Every query is scoped to the authenticated account, so one user can never read or change another's records.
# import re

# from django.db import transaction
# from rest_framework.exceptions import NotFound
# from apps.members.models import FamilyMember
# from . import ocr
# from .models import ScannedDocument


# def _member_for(account, member_name):
#     if not member_name:
#         return None
#     try:
#         return FamilyMember.objects.get(account=account, slot=int(member_name[6:]))
#     except FamilyMember.DoesNotExist:
#         raise NotFound("Member not found")


# def _owned(account, pk):
#     try:
#         return ScannedDocument.objects.select_related("member").get(pk=pk, account=account)
#     except ScannedDocument.DoesNotExist:
#         # 404 (not 403) so the existence of other users' records is not revealed.
#         raise NotFound("Document not found")


# def scan_image(account, upload, document_type, member_name):
#     member = _member_for(account, member_name)
#     data = ocr.read_upload(upload)
#     result = ocr.extract_text_from_bytes(data)  # raises a clean API error on any failure; nothing saved then
#     return ScannedDocument.objects.create(
#         account=account, member=member, document_type=document_type,
#         ocr_text=result.text, description=result.text,
#         ocr_confidence=result.confidence, warnings=result.warnings,
#     )


# def list_documents(account, member_name=""):
#     queryset = ScannedDocument.objects.select_related("member").filter(account=account)
#     if member_name:
#         queryset = queryset.filter(member=_member_for(account, member_name))
#     return list(queryset)


# def get_document(account, pk):
#     return _owned(account, pk)


# def _sync_confirmed_description(doc):
#     """Mirror a reviewed scan into medical_description without overwriting user-entered notes.

#     A document-specific section marker lets later edits/deletion replace only this scan's text.
#     Unconfirmed OCR is deliberately excluded from the AI member context.
#     """
#     if not doc.member_id:
#         return

#     member = FamilyMember.objects.select_for_update().get(pk=doc.member_id, account=doc.account)
#     start = f"[Scanned document #{doc.pk} - {doc.get_document_type_display()}]"
#     end = f"[/Scanned document #{doc.pk}]"
#     section = re.compile(r"(?:\n\n)?" + re.escape(start) + r"\n.*?\n" + re.escape(end), re.DOTALL)
#     description = section.sub("", member.medical_description or "").strip()

#     if doc.is_confirmed:
#         block = f"{start}\n{doc.description.strip()}\n{end}"
#         description = f"{description}\n\n{block}" if description else block

#     if description != member.medical_description:
#         member.medical_description = description
#         member.save(update_fields=["medical_description", "updated_at"])


# @transaction.atomic
# def update_document(account, pk, values):
#     doc = ScannedDocument.objects.select_for_update().get(pk=_owned(account, pk).pk)
#     if "description" in values:
#         doc.description = values["description"]
#     if "isConfirmed" in values:
#         doc.is_confirmed = values["isConfirmed"]
#     elif "description" in values:
#         doc.is_confirmed = False  # corrected text must be re-confirmed
#     doc.save()
#     _sync_confirmed_description(doc)
#     return _owned(account, pk)


# @transaction.atomic
# def delete_document(account, pk):
#     doc = ScannedDocument.objects.select_for_update().select_related("member").get(pk=_owned(account, pk).pk)
#     # Remove only this document's generated section; preserve manually entered medical notes.
#     if doc.member_id:
#         doc.is_confirmed = False
#         _sync_confirmed_description(doc)
#     doc.delete()
#     return {"ok": True}











# # Purpose: Owns scan -> OCR -> save logic and per-account ownership rules for scanned documents.
# # Every query is scoped to the authenticated account, so one user can never read or change another's records.
# import re

# from django.conf import settings
# from django.db import transaction
# from rest_framework.exceptions import NotFound

# from apps.members.models import FamilyMember
# from . import ocr
# from .models import ScannedDocument


# def _member_for(account, member_name):
#     if not member_name:
#         return None
#     try:
#         return FamilyMember.objects.get(account=account, slot=int(member_name[6:]))
#     except FamilyMember.DoesNotExist:
#         raise NotFound("Member not found")


# def _owned(account, pk):
#     try:
#         return ScannedDocument.objects.select_related("member").get(pk=pk, account=account)
#     except ScannedDocument.DoesNotExist:
#         # 404 (not 403) so the existence of other users' records is not revealed.
#         raise NotFound("Document not found")


# def scan_image(account, upload, document_type, member_name):
#     member = _member_for(account, member_name)
#     data = ocr.read_upload(upload)
#     # The new local PaddleOCR + TrOCR ONNX pipeline is the default. Tesseract is
#     # retained unchanged as an explicitly selectable legacy engine.
#     engine = getattr(settings, "OCR_ENGINE", "trocr").strip().lower()
#     if engine == "tesseract":
#         result = ocr.extract_text_from_bytes(data)  # legacy implementation
#     elif engine == "trocr":
#         from .prescription_parser import PrescriptionParser

#         parsed = PrescriptionParser().parse_bytes(data)
#         result = ocr.OCRResult(
#             text=parsed["raw_text"],
#             confidence=parsed.get("confidence"),
#             warnings=parsed.get("warnings", []),
#         )
#     else:
#         from rest_framework.exceptions import APIException

#         class InvalidOCREngine(APIException):
#             status_code = 503
#             default_detail = "The configured OCR engine is unavailable."
#             default_code = "ocr_engine_unavailable"

#         raise InvalidOCREngine()

#     return ScannedDocument.objects.create(
#         account=account, member=member, document_type=document_type,
#         ocr_text=result.text, description=result.text,
#         ocr_confidence=result.confidence, warnings=result.warnings,
#     )


# def list_documents(account, member_name=""):
#     queryset = ScannedDocument.objects.select_related("member").filter(account=account)
#     if member_name:
#         queryset = queryset.filter(member=_member_for(account, member_name))
#     return list(queryset)


# def get_document(account, pk):
#     return _owned(account, pk)


# def _sync_confirmed_description(doc):
#     """Mirror a reviewed scan into medical_description without overwriting user-entered notes.

#     A document-specific section marker lets later edits/deletion replace only this scan's text.
#     Unconfirmed OCR is deliberately excluded from the AI member context.
#     """
#     if not doc.member_id:
#         return

#     member = FamilyMember.objects.select_for_update().get(pk=doc.member_id, account=doc.account)
#     start = f"[Scanned document #{doc.pk} - {doc.get_document_type_display()}]"
#     end = f"[/Scanned document #{doc.pk}]"
#     section = re.compile(r"(?:\n\n)?" + re.escape(start) + r"\n.*?\n" + re.escape(end), re.DOTALL)
#     description = section.sub("", member.medical_description or "").strip()

#     if doc.is_confirmed:
#         block = f"{start}\n{doc.description.strip()}\n{end}"
#         description = f"{description}\n\n{block}" if description else block

#     if description != member.medical_description:
#         member.medical_description = description
#         member.save(update_fields=["medical_description", "updated_at"])


# @transaction.atomic
# def update_document(account, pk, values):
#     doc = ScannedDocument.objects.select_for_update().get(pk=_owned(account, pk).pk)
#     if "description" in values:
#         doc.description = values["description"]
#     if "isConfirmed" in values:
#         doc.is_confirmed = values["isConfirmed"]
#     elif "description" in values:
#         doc.is_confirmed = False  # corrected text must be re-confirmed
#     doc.save()
#     _sync_confirmed_description(doc)
#     return _owned(account, pk)


# @transaction.atomic
# def delete_document(account, pk):
#     doc = ScannedDocument.objects.select_for_update().select_related("member").get(pk=_owned(account, pk).pk)
#     # Remove only this document's generated section; preserve manually entered medical notes.
#     if doc.member_id:
#         doc.is_confirmed = False
#         _sync_confirmed_description(doc)
#     doc.delete()
#     return {"ok": True}












# Purpose: Owns scan -> OCR -> save logic and per-account ownership rules for scanned documents.
# Every query is scoped to the authenticated account, so one user can never read or change another's records.
import re

from django.db import transaction
from rest_framework.exceptions import NotFound
from apps.members.models import FamilyMember
from . import ocr
from .models import ScannedDocument


def _member_for(account, member_name):
    if not member_name:
        return None
    try:
        return FamilyMember.objects.get(account=account, slot=int(member_name[6:]))
    except FamilyMember.DoesNotExist:
        raise NotFound("Member not found")


def _owned(account, pk):
    try:
        return ScannedDocument.objects.select_related("member").get(pk=pk, account=account)
    except ScannedDocument.DoesNotExist:
        # 404 (not 403) so the existence of other users' records is not revealed.
        raise NotFound("Document not found")


def scan_image(account, upload, document_type, member_name):
    member = _member_for(account, member_name)
    data = ocr.read_upload(upload)
    # Tesseract is the only OCR engine. Raises a clean API error on any failure; nothing is saved then.
    result = ocr.extract_text_from_bytes(data)
    return ScannedDocument.objects.create(
        account=account, member=member, document_type=document_type,
        ocr_text=result.text, description=result.text,
        ocr_confidence=result.confidence, warnings=result.warnings,
    )


def list_documents(account, member_name=""):
    queryset = ScannedDocument.objects.select_related("member").filter(account=account)
    if member_name:
        queryset = queryset.filter(member=_member_for(account, member_name))
    return list(queryset)


def get_document(account, pk):
    return _owned(account, pk)


def _sync_confirmed_description(doc):
    """Mirror a reviewed scan into medical_description without overwriting user-entered notes.

    A document-specific section marker lets later edits/deletion replace only this scan's text.
    Unconfirmed OCR is deliberately excluded from the AI member context.
    """
    if not doc.member_id:
        return

    member = FamilyMember.objects.select_for_update().get(pk=doc.member_id, account=doc.account)
    start = f"[Scanned document #{doc.pk} - {doc.get_document_type_display()}]"
    end = f"[/Scanned document #{doc.pk}]"
    section = re.compile(r"(?:\n\n)?" + re.escape(start) + r"\n.*?\n" + re.escape(end), re.DOTALL)
    description = section.sub("", member.medical_description or "").strip()

    if doc.is_confirmed:
        block = f"{start}\n{doc.description.strip()}\n{end}"
        description = f"{description}\n\n{block}" if description else block

    if description != member.medical_description:
        member.medical_description = description
        member.save(update_fields=["medical_description", "updated_at"])


@transaction.atomic
def update_document(account, pk, values):
    doc = ScannedDocument.objects.select_for_update().get(pk=_owned(account, pk).pk)
    if "description" in values:
        doc.description = values["description"]
    if "isConfirmed" in values:
        doc.is_confirmed = values["isConfirmed"]
    elif "description" in values:
        doc.is_confirmed = False  # corrected text must be re-confirmed
    doc.save()
    _sync_confirmed_description(doc)
    return _owned(account, pk)


@transaction.atomic
def delete_document(account, pk):
    # of=("self",) locks only the scan row: PostgreSQL cannot lock the nullable side of the member LEFT JOIN.
    doc = (ScannedDocument.objects.select_for_update(of=("self",)).select_related("member")
           .get(pk=_owned(account, pk).pk))
    # Remove only this document's generated section; preserve manually entered medical notes.
    if doc.member_id:
        doc.is_confirmed = False
        _sync_confirmed_description(doc)
    doc.delete()
    return {"ok": True}
