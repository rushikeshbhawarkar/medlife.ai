# # Purpose: PostgreSQL-backed tests for the image-to-text (OCR) endpoints: success, persistence, validation,
# # size limits, OCR failures, authentication, and cross-user isolation.
# # Add a test here whenever the documents API behaviour or OCR rules change.
# import io
# import shutil
# from unittest import skipUnless
# from unittest.mock import patch

# from django.test import TestCase, override_settings
# from PIL import Image, ImageDraw, ImageFont
# from rest_framework.test import APIClient

# from apps.accounts.models import Account
# from apps.core.authentication import issue_account_token
# from apps.documents.models import ScannedDocument
# from apps.members.models import FamilyMember

# HAS_TESSERACT = shutil.which("tesseract") is not None
# FONT_CANDIDATES = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf", "arial.ttf", "Arial.ttf"]


# def _font(size):
#     for name in FONT_CANDIDATES:
#         try:
#             return ImageFont.truetype(name, size)
#         except OSError:
#             continue
#     return ImageFont.load_default(size=size)


# def make_image_bytes(lines=("Paracetamol 500 mg", "Take ONE tablet twice daily"), fmt="PNG", size=(1000, 300)):
#     image = Image.new("RGB", size, "white")
#     draw = ImageDraw.Draw(image)
#     y = 40
#     for line in lines:
#         draw.text((40, y), line, fill="black", font=_font(48))
#         y += 90
#     buffer = io.BytesIO()
#     image.save(buffer, format=fmt)
#     return buffer.getvalue()


# def upload(data, name="label.png", content_type="image/png"):
#     from django.core.files.uploadedfile import SimpleUploadedFile
#     return SimpleUploadedFile(name, data, content_type=content_type)


# class DocumentsAPITests(TestCase):
#     def setUp(self):
#         self.account = Account.objects.create(email="owner@example.com")
#         self.other = Account.objects.create(email="other@example.com")
#         self.client = APIClient()
#         self.auth(self.account)

#     def auth(self, account):
#         self.client.credentials(HTTP_AUTHORIZATION="Bearer " + issue_account_token(account))

#     def scan(self, data=None, **extra):
#         payload = {"image": upload(data if data is not None else make_image_bytes()), **extra}
#         return self.client.post("/medlife/documents/scan/", payload, format="multipart")

#     # --- success and persistence -------------------------------------------------------------
#     @skipUnless(HAS_TESSERACT, "Tesseract is not installed")
#     def test_valid_image_is_extracted_saved_and_retrievable(self):
#         r = self.scan(documentType="medicine_label")
#         self.assertEqual(r.status_code, 201, r.content)
#         body = r.json()
#         self.assertIn("Paracetamol", body["description"])
#         self.assertIn("500", body["description"])
#         self.assertEqual(body["documentType"], "medicine_label")
#         self.assertFalse(body["isConfirmed"])
#         self.assertIn("notice", body)
#         doc = ScannedDocument.objects.get(pk=body["id"])  # actually persisted
#         self.assertEqual(doc.account, self.account)
#         self.assertEqual(doc.description, body["description"])
#         self.assertEqual(doc.ocr_text, body["description"])
#         fetched = self.client.get(f"/medlife/documents/{doc.pk}/")
#         self.assertEqual(fetched.status_code, 200)
#         self.assertEqual(fetched.json()["description"], doc.description)
#         listed = self.client.get("/medlife/documents/").json()["documents"]
#         self.assertEqual([d["id"] for d in listed], [doc.pk])

#     @skipUnless(HAS_TESSERACT, "Tesseract is not installed")
#     def test_scan_can_be_linked_to_own_member(self):
#         FamilyMember.objects.create(account=self.account, slot=1, first_name="Asha")
#         r = self.scan(member_name="member1")
#         self.assertEqual(r.status_code, 201)
#         self.assertEqual(r.json()["memberName"], "member1")
#         filtered = self.client.get("/medlife/documents/", {"member_name": "member1"}).json()["documents"]
#         self.assertEqual(len(filtered), 1)

#     def test_each_scan_creates_a_new_record_and_never_overwrites(self):
#         with patch("apps.documents.ocr.extract_text_from_bytes") as fake:
#             from apps.documents.ocr import OCRResult
#             fake.return_value = OCRResult(text="Amoxicillin 250 mg", confidence=95.0, warnings=[])
#             first = self.scan().json()["id"]
#             second = self.scan().json()["id"]
#         self.assertNotEqual(first, second)
#         self.assertEqual(ScannedDocument.objects.filter(account=self.account).count(), 2)

#     # --- no text / bad input -------------------------------------------------------------------
#     @skipUnless(HAS_TESSERACT, "Tesseract is not installed")
#     def test_image_without_text_returns_422_and_saves_nothing(self):
#         blank = Image.new("RGB", (600, 300), "white")
#         buf = io.BytesIO()
#         blank.save(buf, format="PNG")
#         r = self.scan(buf.getvalue())
#         self.assertEqual(r.status_code, 422)
#         self.assertIn("No readable text", r.json()["detail"])
#         self.assertEqual(ScannedDocument.objects.count(), 0)

#     def test_non_image_file_with_image_extension_is_rejected(self):
#         r = self.client.post("/medlife/documents/scan/", {"image": upload(b"just some text, not a png", "fake.png")},
#                              format="multipart")
#         self.assertEqual(r.status_code, 400)
#         self.assertEqual(ScannedDocument.objects.count(), 0)

#     def test_unsupported_real_image_format_is_rejected(self):
#         buf = io.BytesIO()
#         Image.new("RGB", (50, 50), "white").save(buf, format="GIF")
#         r = self.client.post("/medlife/documents/scan/", {"image": upload(buf.getvalue(), "a.png", "image/png")},
#                              format="multipart")
#         self.assertEqual(r.status_code, 415)

#     def test_truncated_image_is_rejected(self):
#         data = make_image_bytes()
#         r = self.scan(data[: len(data) // 2])
#         self.assertEqual(r.status_code, 400)
#         self.assertEqual(ScannedDocument.objects.count(), 0)

#     def test_empty_file_and_missing_file_and_non_multipart(self):
#         self.assertEqual(self.scan(b"").status_code, 400)
#         self.assertEqual(self.client.post("/medlife/documents/scan/", {}, format="multipart").status_code, 400)
#         self.assertEqual(self.client.post("/medlife/documents/scan/", {"a": 1}, format="json").status_code, 415)

#     def test_invalid_member_name_and_document_type(self):
#         self.assertEqual(self.scan(member_name="member9").status_code, 400)
#         self.assertEqual(self.scan(documentType="selfie").status_code, 400)

#     @override_settings(OCR_MAX_UPLOAD_BYTES=1024)
#     def test_file_over_size_limit_returns_413(self):
#         data = make_image_bytes(size=(1600, 900))
#         self.assertGreater(len(data), 1024)
#         r = self.scan(data)
#         self.assertEqual(r.status_code, 413)
#         self.assertEqual(ScannedDocument.objects.count(), 0)

#     @override_settings(OCR_MAX_IMAGE_PIXELS=1000)
#     def test_image_with_too_many_pixels_returns_413(self):
#         self.assertEqual(self.scan(make_image_bytes(size=(200, 100))).status_code, 413)

#     # --- OCR failures ------------------------------------------------------------------------------
#     def test_ocr_engine_error_returns_502_without_internal_details_and_saves_nothing(self):
#         with patch("pytesseract.image_to_data", side_effect=RuntimeError("secret /usr/bin/tesseract path crash")):
#             r = self.scan()
#         self.assertEqual(r.status_code, 502)
#         self.assertNotIn("secret", r.content.decode())
#         self.assertNotIn("Traceback", r.content.decode())
#         self.assertEqual(ScannedDocument.objects.count(), 0)

#     def test_missing_ocr_engine_returns_503(self):
#         import pytesseract
#         with patch("pytesseract.image_to_data", side_effect=pytesseract.TesseractNotFoundError()):
#             r = self.scan()
#         self.assertEqual(r.status_code, 503)
#         self.assertEqual(ScannedDocument.objects.count(), 0)

#     def test_low_confidence_result_is_saved_with_warnings(self):
#         fake = {"text": ["Metformin", "5OO", "mg"], "conf": ["30", "20", "40"], "block_num": [1, 1, 1],
#                 "par_num": [1, 1, 1], "line_num": [1, 1, 1]}
#         with patch("pytesseract.image_to_data", return_value=fake):
#             r = self.scan()
#         self.assertEqual(r.status_code, 201)
#         body = r.json()
#         self.assertEqual(body["processingStatus"], "low_confidence")
#         self.assertEqual(body["description"], "Metformin 5OO mg")  # preserved exactly, never "corrected"
#         self.assertTrue(any("confidence" in w for w in body["warnings"]))
#         self.assertTrue(any("number" in w for w in body["warnings"]))
#         self.assertEqual(ScannedDocument.objects.get(pk=body["id"]).warnings, body["warnings"])

#     # --- authentication -----------------------------------------------------------------------------
#     def test_endpoints_require_authentication(self):
#         anon = APIClient()
#         doc = ScannedDocument.objects.create(account=self.account, ocr_text="x", description="x")
#         calls = [anon.post("/medlife/documents/scan/", {"image": upload(make_image_bytes())}, format="multipart"),
#                  anon.get("/medlife/documents/"), anon.get(f"/medlife/documents/{doc.pk}/"),
#                  anon.patch(f"/medlife/documents/{doc.pk}/", {"description": "y"}, format="json"),
#                  anon.delete(f"/medlife/documents/{doc.pk}/")]
#         for response in calls:
#             self.assertEqual(response.status_code, 401)
#             self.assertIn("detail", response.json())
#         self.assertEqual(ScannedDocument.objects.count(), 1)

#     def test_email_query_param_is_not_accepted_as_authentication(self):
#         r = APIClient().get("/medlife/documents/", {"email": "owner@example.com"})
#         self.assertEqual(r.status_code, 401)

#     def test_invalid_token_is_rejected(self):
#         self.client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
#         self.assertEqual(self.client.get("/medlife/documents/").status_code, 401)

#     # --- ownership ----------------------------------------------------------------------------------
#     def test_user_cannot_access_modify_or_delete_another_users_record(self):
#         theirs = ScannedDocument.objects.create(account=self.other, ocr_text="secret", description="secret")
#         url = f"/medlife/documents/{theirs.pk}/"
#         self.assertEqual(self.client.get(url).status_code, 404)
#         self.assertEqual(self.client.patch(url, {"description": "hacked"}, format="json").status_code, 404)
#         self.assertEqual(self.client.delete(url).status_code, 404)
#         self.assertEqual(self.client.get("/medlife/documents/").json(), {"documents": []})
#         theirs.refresh_from_db()
#         self.assertEqual(theirs.description, "secret")

#     def test_cannot_attach_scan_to_another_users_member(self):
#         FamilyMember.objects.create(account=self.other, slot=1, first_name="Eve")
#         r = self.scan(member_name="member1")  # owner has no member1
#         self.assertEqual(r.status_code, 404)
#         self.assertEqual(ScannedDocument.objects.count(), 0)

#     # --- review / correction -------------------------------------------------------------------------
#     def test_owner_can_correct_and_confirm_description_without_losing_original_ocr_text(self):
#         doc = ScannedDocument.objects.create(account=self.account, ocr_text="Metformin 5OO mg",
#                                              description="Metformin 5OO mg", warnings=["x"])
#         url = f"/medlife/documents/{doc.pk}/"
#         r = self.client.patch(url, {"description": "Metformin 500 mg"}, format="json")
#         self.assertEqual(r.status_code, 200)
#         self.assertFalse(r.json()["isConfirmed"])
#         self.assertTrue(r.json()["isEdited"])
#         r = self.client.patch(url, {"isConfirmed": True}, format="json")
#         self.assertTrue(r.json()["isConfirmed"])
#         doc.refresh_from_db()
#         self.assertEqual(doc.ocr_text, "Metformin 5OO mg")
#         self.assertEqual(doc.description, "Metformin 500 mg")
#         self.assertEqual(self.client.patch(url, {}, format="json").status_code, 400)
#         self.assertEqual(self.client.patch(url, {"description": "   "}, format="json").status_code, 400)

#     def test_owner_can_delete_and_member_removal_cascades(self):
#         member = FamilyMember.objects.create(account=self.account, slot=1, first_name="Asha")
#         a = ScannedDocument.objects.create(account=self.account, ocr_text="a", description="a")
#         ScannedDocument.objects.create(account=self.account, member=member, ocr_text="b", description="b")
#         self.assertEqual(self.client.delete(f"/medlife/documents/{a.pk}/").status_code, 200)
#         self.assertEqual(self.client.get(f"/medlife/documents/{a.pk}/").status_code, 404)
#         member.delete()
#         self.assertEqual(ScannedDocument.objects.count(), 0)











# Purpose: PostgreSQL-backed tests for the image-to-text (OCR) endpoints: success, persistence, validation,
# size limits, OCR failures, authentication, and cross-user isolation.
# Add a test here whenever the documents API behaviour or OCR rules change.
import io
import shutil
from unittest import skipUnless
from unittest.mock import patch

from django.test import TestCase, override_settings
from PIL import Image, ImageDraw, ImageFont
from rest_framework.test import APIClient

from apps.core.authentication import issue_account_token
from apps.core.tests.helpers import auth_client
from apps.documents.models import ScannedDocument
from apps.members.models import FamilyMember

HAS_TESSERACT = shutil.which("tesseract") is not None
FONT_CANDIDATES = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf", "arial.ttf", "Arial.ttf"]


def _font(size):
    for name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def make_image_bytes(lines=("Paracetamol 500 mg", "Take ONE tablet twice daily"), fmt="PNG", size=(1000, 300)):
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    y = 40
    for line in lines:
        draw.text((40, y), line, fill="black", font=_font(48))
        y += 90
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def upload(data, name="label.png", content_type="image/png"):
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(name, data, content_type=content_type)


class DocumentsAPITests(TestCase):
    def setUp(self):
        # Current access tokens are issued only for accounts with completed TOTP enrollment.
        self.client, self.account = auth_client("owner@example.com")
        _, self.other = auth_client("other@example.com")
        self.auth(self.account)

    def auth(self, account):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + issue_account_token(account))

    def scan(self, data=None, **extra):
        payload = {"image": upload(data if data is not None else make_image_bytes()), **extra}
        return self.client.post("/medlife/documents/scan/", payload, format="multipart")

    # --- success and persistence -------------------------------------------------------------
    @skipUnless(HAS_TESSERACT, "Tesseract is not installed")
    @override_settings(OCR_ENGINE="tesseract")
    def test_valid_image_is_extracted_saved_and_retrievable(self):
        r = self.scan(documentType="medicine_label")
        self.assertEqual(r.status_code, 201, r.content)
        body = r.json()
        self.assertIn("Paracetamol", body["description"])
        self.assertIn("500", body["description"])
        self.assertEqual(body["documentType"], "medicine_label")
        self.assertFalse(body["isConfirmed"])
        self.assertIn("notice", body)
        doc = ScannedDocument.objects.get(pk=body["id"])  # actually persisted
        self.assertEqual(doc.account, self.account)
        self.assertEqual(doc.description, body["description"])
        self.assertEqual(doc.ocr_text, body["description"])
        fetched = self.client.get(f"/medlife/documents/{doc.pk}/")
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json()["description"], doc.description)
        listed = self.client.get("/medlife/documents/").json()["documents"]
        self.assertEqual([d["id"] for d in listed], [doc.pk])

    @skipUnless(HAS_TESSERACT, "Tesseract is not installed")
    @override_settings(OCR_ENGINE="tesseract")
    def test_scan_can_be_linked_to_own_member(self):
        FamilyMember.objects.create(account=self.account, slot=1, first_name="Asha")
        r = self.scan(member_name="member1")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["memberName"], "member1")
        filtered = self.client.get("/medlife/documents/", {"member_name": "member1"}).json()["documents"]
        self.assertEqual(len(filtered), 1)

    @override_settings(OCR_ENGINE="tesseract")
    def test_each_scan_creates_a_new_record_and_never_overwrites(self):
        with patch("apps.documents.ocr.extract_text_from_bytes") as fake:
            from apps.documents.ocr import OCRResult
            fake.return_value = OCRResult(text="Amoxicillin 250 mg", confidence=95.0, warnings=[])
            first = self.scan().json()["id"]
            second = self.scan().json()["id"]
        self.assertNotEqual(first, second)
        self.assertEqual(ScannedDocument.objects.filter(account=self.account).count(), 2)

    # --- no text / bad input -------------------------------------------------------------------
    @skipUnless(HAS_TESSERACT, "Tesseract is not installed")
    @override_settings(OCR_ENGINE="tesseract")
    def test_image_without_text_returns_422_and_saves_nothing(self):
        blank = Image.new("RGB", (600, 300), "white")
        buf = io.BytesIO()
        blank.save(buf, format="PNG")
        r = self.scan(buf.getvalue())
        self.assertEqual(r.status_code, 422)
        self.assertIn("No readable text", r.json()["detail"])
        self.assertEqual(ScannedDocument.objects.count(), 0)

    def test_non_image_file_with_image_extension_is_rejected(self):
        r = self.client.post("/medlife/documents/scan/", {"image": upload(b"just some text, not a png", "fake.png")},
                             format="multipart")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(ScannedDocument.objects.count(), 0)

    def test_unsupported_real_image_format_is_rejected(self):
        buf = io.BytesIO()
        Image.new("RGB", (50, 50), "white").save(buf, format="GIF")
        r = self.client.post("/medlife/documents/scan/", {"image": upload(buf.getvalue(), "a.png", "image/png")},
                             format="multipart")
        self.assertEqual(r.status_code, 415)

    def test_truncated_image_is_rejected(self):
        data = make_image_bytes()
        r = self.scan(data[: len(data) // 2])
        self.assertEqual(r.status_code, 400)
        self.assertEqual(ScannedDocument.objects.count(), 0)

    def test_empty_file_and_missing_file_and_non_multipart(self):
        self.assertEqual(self.scan(b"").status_code, 400)
        self.assertEqual(self.client.post("/medlife/documents/scan/", {}, format="multipart").status_code, 400)
        self.assertEqual(self.client.post("/medlife/documents/scan/", {"a": 1}, format="json").status_code, 415)

    def test_invalid_member_name_and_document_type(self):
        self.assertEqual(self.scan(member_name="member9").status_code, 400)
        self.assertEqual(self.scan(documentType="selfie").status_code, 400)

    @override_settings(OCR_MAX_UPLOAD_BYTES=1024)
    def test_file_over_size_limit_returns_413(self):
        data = make_image_bytes(size=(1600, 900))
        self.assertGreater(len(data), 1024)
        r = self.scan(data)
        self.assertEqual(r.status_code, 413)
        self.assertEqual(ScannedDocument.objects.count(), 0)

    @override_settings(OCR_MAX_IMAGE_PIXELS=1000)
    def test_image_with_too_many_pixels_returns_413(self):
        self.assertEqual(self.scan(make_image_bytes(size=(200, 100))).status_code, 413)

    # --- OCR failures ------------------------------------------------------------------------------
    @override_settings(OCR_ENGINE="tesseract")
    def test_ocr_engine_error_returns_502_without_internal_details_and_saves_nothing(self):
        with patch("pytesseract.image_to_data", side_effect=RuntimeError("secret /usr/bin/tesseract path crash")):
            r = self.scan()
        self.assertEqual(r.status_code, 502)
        self.assertNotIn("secret", r.content.decode())
        self.assertNotIn("Traceback", r.content.decode())
        self.assertEqual(ScannedDocument.objects.count(), 0)

    @override_settings(OCR_ENGINE="tesseract")
    def test_missing_ocr_engine_returns_503(self):
        import pytesseract
        with patch("pytesseract.image_to_data", side_effect=pytesseract.TesseractNotFoundError()):
            r = self.scan()
        self.assertEqual(r.status_code, 503)
        self.assertEqual(ScannedDocument.objects.count(), 0)

    @override_settings(OCR_ENGINE="tesseract")
    def test_low_confidence_result_is_saved_with_warnings(self):
        fake = {"text": ["Metformin", "5OO", "mg"], "conf": ["30", "20", "40"], "block_num": [1, 1, 1],
                "par_num": [1, 1, 1], "line_num": [1, 1, 1]}
        with patch("pytesseract.image_to_data", return_value=fake):
            r = self.scan()
        self.assertEqual(r.status_code, 201)
        body = r.json()
        self.assertEqual(body["processingStatus"], "low_confidence")
        self.assertEqual(body["description"], "Metformin 5OO mg")  # preserved exactly, never "corrected"
        self.assertTrue(any("confidence" in w for w in body["warnings"]))
        self.assertTrue(any("number" in w for w in body["warnings"]))
        self.assertEqual(ScannedDocument.objects.get(pk=body["id"]).warnings, body["warnings"])

    # --- authentication -----------------------------------------------------------------------------
    def test_endpoints_require_authentication(self):
        anon = APIClient()
        doc = ScannedDocument.objects.create(account=self.account, ocr_text="x", description="x")
        calls = [anon.post("/medlife/documents/scan/", {"image": upload(make_image_bytes())}, format="multipart"),
                 anon.get("/medlife/documents/"), anon.get(f"/medlife/documents/{doc.pk}/"),
                 anon.patch(f"/medlife/documents/{doc.pk}/", {"description": "y"}, format="json"),
                 anon.delete(f"/medlife/documents/{doc.pk}/")]
        for response in calls:
            self.assertEqual(response.status_code, 401)
            self.assertIn("detail", response.json())
        self.assertEqual(ScannedDocument.objects.count(), 1)

    def test_email_query_param_is_not_accepted_as_authentication(self):
        r = APIClient().get("/medlife/documents/", {"email": "owner@example.com"})
        self.assertEqual(r.status_code, 401)

    def test_invalid_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        self.assertEqual(self.client.get("/medlife/documents/").status_code, 401)

    # --- ownership ----------------------------------------------------------------------------------
    def test_user_cannot_access_modify_or_delete_another_users_record(self):
        theirs = ScannedDocument.objects.create(account=self.other, ocr_text="secret", description="secret")
        url = f"/medlife/documents/{theirs.pk}/"
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.patch(url, {"description": "hacked"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(url).status_code, 404)
        self.assertEqual(self.client.get("/medlife/documents/").json(), {"documents": []})
        theirs.refresh_from_db()
        self.assertEqual(theirs.description, "secret")

    def test_cannot_attach_scan_to_another_users_member(self):
        FamilyMember.objects.create(account=self.other, slot=1, first_name="Eve")
        r = self.scan(member_name="member1")  # owner has no member1
        self.assertEqual(r.status_code, 404)
        self.assertEqual(ScannedDocument.objects.count(), 0)

    # --- review / correction -------------------------------------------------------------------------
    def test_owner_can_correct_and_confirm_description_without_losing_original_ocr_text(self):
        doc = ScannedDocument.objects.create(account=self.account, ocr_text="Metformin 5OO mg",
                                             description="Metformin 5OO mg", warnings=["x"])
        url = f"/medlife/documents/{doc.pk}/"
        r = self.client.patch(url, {"description": "Metformin 500 mg"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["isConfirmed"])
        self.assertTrue(r.json()["isEdited"])
        r = self.client.patch(url, {"isConfirmed": True}, format="json")
        self.assertTrue(r.json()["isConfirmed"])
        doc.refresh_from_db()
        self.assertEqual(doc.ocr_text, "Metformin 5OO mg")
        self.assertEqual(doc.description, "Metformin 500 mg")
        self.assertEqual(self.client.patch(url, {}, format="json").status_code, 400)
        self.assertEqual(self.client.patch(url, {"description": "   "}, format="json").status_code, 400)

    def test_confirmed_scan_updates_member_medical_description_and_revisions_replace_old_text(self):
        member = FamilyMember.objects.create(
            account=self.account, slot=1, first_name="Asha", medical_description="Existing user note."
        )
        doc = ScannedDocument.objects.create(
            account=self.account, member=member, document_type="prescription",
            ocr_text="Metformin 5OO mg", description="Metformin 500 mg"
        )
        url = f"/medlife/documents/{doc.pk}/"
        response = self.client.patch(url, {"isConfirmed": True}, format="json")
        self.assertEqual(response.status_code, 200)
        member.refresh_from_db()
        self.assertIn("Existing user note.", member.medical_description)
        self.assertIn("Metformin 500 mg", member.medical_description)
        self.client.patch(url, {"description": "Metformin 850 mg"}, format="json")
        member.refresh_from_db()
        self.assertNotIn("Metformin 500 mg", member.medical_description)
        self.assertNotIn("Metformin 850 mg", member.medical_description)
        self.client.patch(url, {"isConfirmed": True}, format="json")
        member.refresh_from_db()
        self.assertIn("Metformin 850 mg", member.medical_description)
        self.assertNotIn("Metformin 500 mg", member.medical_description)

    def test_deleting_confirmed_scan_removes_only_its_member_description_section(self):
        member = FamilyMember.objects.create(
            account=self.account, slot=1, first_name="Asha", medical_description="Keep this note."
        )
        doc = ScannedDocument.objects.create(
            account=self.account, member=member, document_type="other",
            ocr_text="Allergy note", description="Allergy note", is_confirmed=True
        )
        self.client.patch(f"/medlife/documents/{doc.pk}/", {"isConfirmed": True}, format="json")
        member.refresh_from_db()
        self.assertIn("Allergy note", member.medical_description)
        self.client.delete(f"/medlife/documents/{doc.pk}/")
        member.refresh_from_db()
        self.assertEqual(member.medical_description, "Keep this note.")

    def test_owner_can_delete_and_member_removal_cascades(self):
        member = FamilyMember.objects.create(account=self.account, slot=1, first_name="Asha")
        a = ScannedDocument.objects.create(account=self.account, ocr_text="a", description="a")
        ScannedDocument.objects.create(account=self.account, member=member, ocr_text="b", description="b")
        self.assertEqual(self.client.delete(f"/medlife/documents/{a.pk}/").status_code, 200)
        self.assertEqual(self.client.get(f"/medlife/documents/{a.pk}/").status_code, 404)
        member.delete()
        self.assertEqual(ScannedDocument.objects.count(), 0)

    def test_list_with_invalid_member_name_returns_400_not_500(self):
        for bad in ("abc", "memberX", "member9", "member"):
            self.assertEqual(self.client.get("/medlife/documents/", {"member_name": bad}).status_code, 400)
        self.assertEqual(self.client.get("/medlife/documents/", {"member_name": "member1"}).status_code, 200)
