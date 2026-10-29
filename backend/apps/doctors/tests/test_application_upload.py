import shutil
import tempfile

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.doctors.models import DoctorApplication, DoctorApplicationDocument

PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 32

FORM = {
    "email": "new.doctor@example.com",
    "full_name": "Dr Test Person",
    "specialty": "Cardiology",
    "qualifications": "MBBS, MD",
    "registration_number": "REG-12345",
    "years_experience": "7",
}


class DoctorApplicationUploadTests(TestCase):
    """Public doctor application: multipart upload must work and must be locked down."""

    def setUp(self):
        cache.clear()
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        self.client = APIClient()

    def _post(self, files=None, extra=None, email=None):
        data = dict(FORM)
        if email:
            data["email"] = email
        if extra:
            data.update(extra)
        if files is not None:
            data["documents"] = files
        return self.client.post("/medlife/doctor/applications/", data, format="multipart")

    def test_multipart_upload_with_documents_is_accepted(self):
        with override_settings(MEDIA_ROOT=self.media):
            response = self._post(files=[
                SimpleUploadedFile("registration.pdf", PDF_BYTES, content_type="application/pdf"),
                SimpleUploadedFile("degree.png", PNG_BYTES, content_type="image/png"),
                SimpleUploadedFile("id.jpg", JPEG_BYTES, content_type="image/jpeg"),
            ])
        self.assertEqual(response.status_code, 201, response.content)
        app = DoctorApplication.objects.get(email="new.doctor@example.com")
        self.assertEqual(DoctorApplicationDocument.objects.filter(application=app).count(), 3)

    def test_json_application_without_files_still_works(self):
        response = self.client.post("/medlife/doctor/applications/", FORM, format="json")
        self.assertEqual(response.status_code, 201, response.content)

    def test_file_whose_content_does_not_match_its_extension_is_rejected(self):
        with override_settings(MEDIA_ROOT=self.media):
            response = self._post(files=[
                SimpleUploadedFile("registration.pdf", b"<html><script>alert(1)</script></html>", content_type="application/pdf"),
            ])
        self.assertEqual(response.status_code, 400)
        self.assertFalse(DoctorApplication.objects.exists())

    def test_png_content_renamed_to_pdf_is_rejected(self):
        with override_settings(MEDIA_ROOT=self.media):
            response = self._post(files=[SimpleUploadedFile("scan.pdf", PNG_BYTES, content_type="application/pdf")])
        self.assertEqual(response.status_code, 400)

    def test_disallowed_extension_is_rejected(self):
        with override_settings(MEDIA_ROOT=self.media):
            response = self._post(files=[SimpleUploadedFile("run.exe", b"MZ" + b"\x00" * 20)])
        self.assertEqual(response.status_code, 400)

    def test_oversized_single_file_is_rejected(self):
        big = SimpleUploadedFile("big.pdf", PDF_BYTES + b"0" * (10 * 1024 * 1024), content_type="application/pdf")
        with override_settings(MEDIA_ROOT=self.media):
            response = self._post(files=[big])
        self.assertEqual(response.status_code, 400)

    def test_combined_upload_size_is_capped(self):
        chunk = PDF_BYTES + b"0" * (9 * 1024 * 1024)
        files = [SimpleUploadedFile(f"d{i}.pdf", chunk, content_type="application/pdf") for i in range(4)]
        with override_settings(MEDIA_ROOT=self.media):
            response = self._post(files=files)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(DoctorApplication.objects.exists())

    def test_too_many_documents_is_rejected(self):
        files = [SimpleUploadedFile(f"d{i}.pdf", PDF_BYTES, content_type="application/pdf") for i in range(11)]
        with override_settings(MEDIA_ROOT=self.media):
            response = self._post(files=files)
        self.assertEqual(response.status_code, 400)

    def test_anonymous_submissions_are_throttled_per_client(self):
        # Default limit is 3/hour per IP. Even rejected requests count, so spam cannot be retried freely.
        for _ in range(3):
            self.assertEqual(self.client.post("/medlife/doctor/applications/", {}, format="json").status_code, 400)
        blocked = self.client.post("/medlife/doctor/applications/", FORM, format="json")
        self.assertEqual(blocked.status_code, 429)
        self.assertFalse(DoctorApplication.objects.exists())
