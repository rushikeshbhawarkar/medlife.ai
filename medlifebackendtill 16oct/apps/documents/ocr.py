# Purpose: Validates an uploaded image and extracts its text with Tesseract OCR (via pytesseract).
# Pure processing only: no database access or permanent image storage; Django may use temporary upload storage for larger files, and extracted text is never logged.
# Edit this file to change accepted image types, preprocessing, or warning rules.
import io
import re
from dataclasses import dataclass, field

from django.conf import settings
from PIL import Image, ImageOps, UnidentifiedImageError
from rest_framework.exceptions import APIException

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "BMP"}  # decided from file CONTENT, never the extension
MAX_TEXT_CHARS = 20000
LOW_WORD_CONFIDENCE = 50
LOW_NUMBER_CONFIDENCE = 80
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_LANG_RE = re.compile(r"^[A-Za-z0-9_]+(\+[A-Za-z0-9_]+)*$")


class InvalidImage(APIException):
    status_code = 400
    default_detail = "The uploaded file is not a valid image."
    default_code = "invalid_image"


class UnsupportedImage(APIException):
    status_code = 415
    default_detail = "Unsupported image type. Upload a JPEG, PNG, WEBP or BMP image."
    default_code = "unsupported_image"


class ImageTooLarge(APIException):
    status_code = 413
    default_detail = "The image is too large."
    default_code = "image_too_large"


class NoTextFound(APIException):
    status_code = 422
    default_detail = ("No readable text was found in the image. Try a sharper, well-lit, "
                      "straight-on photo. Nothing was saved.")
    default_code = "no_text_found"


class OCRUnavailable(APIException):
    status_code = 503
    default_detail = "Text extraction is temporarily unavailable on the server."
    default_code = "ocr_unavailable"


class OCRFailed(APIException):
    status_code = 502
    default_detail = "The image could not be processed. Nothing was saved."
    default_code = "ocr_failed"


@dataclass
class OCRResult:
    text: str
    confidence: float | None
    warnings: list = field(default_factory=list)


def check_declared_size(content_length):
    """Reject obviously oversized requests before the body is parsed (allows ~64 KB of multipart overhead)."""
    try:
        declared = int(content_length or 0)
    except (TypeError, ValueError):
        return
    if declared > settings.OCR_MAX_UPLOAD_BYTES + 64 * 1024:
        raise ImageTooLarge(_too_large_message())


def _too_large_message():
    return f"The image must be {settings.OCR_MAX_UPLOAD_BYTES // (1024 * 1024)} MB or smaller."


def read_upload(uploaded_file):
    """Return the uploaded file's bytes, enforcing the size limit while reading."""
    if uploaded_file.size > settings.OCR_MAX_UPLOAD_BYTES:
        raise ImageTooLarge(_too_large_message())
    data = uploaded_file.read(settings.OCR_MAX_UPLOAD_BYTES + 1)
    if len(data) > settings.OCR_MAX_UPLOAD_BYTES:
        raise ImageTooLarge(_too_large_message())
    if not data:
        raise InvalidImage("The uploaded file is empty.")
    return data


def load_image(data):
    """Open and fully decode the image, validating its real format and dimensions."""
    try:
        image = Image.open(io.BytesIO(data))
        image_format = image.format
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
        raise InvalidImage() from None
    if image_format not in ALLOWED_FORMATS:
        raise UnsupportedImage()
    width, height = image.size
    if width < 1 or height < 1 or width * height > settings.OCR_MAX_IMAGE_PIXELS:
        raise ImageTooLarge("The image dimensions are too large. Use a smaller photo.")
    try:
        image.load()  # surfaces truncated / corrupted files here instead of inside Tesseract
        image = ImageOps.exif_transpose(image)
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        raise InvalidImage("The image appears to be corrupted or incomplete.") from None
    return image


def _preprocess(image):
    """Light, content-preserving cleanup: flatten transparency, grayscale, scale, stretch contrast."""
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        image = Image.alpha_composite(background, rgba)
    image = image.convert("L")
    width, height = image.size
    short, long_ = min(width, height), max(width, height)
    scale = 1.0
    if short < 1000:
        scale = min(2.0, 1000 / short)
    if long_ * scale > 3500:
        scale = 3500 / long_
    if abs(scale - 1.0) > 0.01:
        image = image.resize((max(1, int(width * scale)), max(1, int(height * scale))), Image.LANCZOS)
    return ImageOps.autocontrast(image)


def _clean(text):
    return _CONTROL_CHARS.sub("", text).replace("\r\n", "\n").replace("\r", "\n")


def _language():
    lang = settings.OCR_LANGUAGES
    return lang if _LANG_RE.fullmatch(lang) else "eng"


def extract_text(image):
    """Run Tesseract on a validated PIL image and return the text plus confidence and warnings."""
    try:
        import pytesseract
        from pytesseract import Output
    except ImportError:
        raise OCRUnavailable() from None
    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
    prepared = _preprocess(image)
    try:
        data = pytesseract.image_to_data(prepared, lang=_language(), config="--psm 3",
                                         output_type=Output.DICT, timeout=settings.OCR_TIMEOUT_SECONDS)
    except pytesseract.TesseractNotFoundError:
        raise OCRUnavailable() from None
    except Exception:  # timeout, missing language data, engine crash... never leak details to the client
        raise OCRFailed() from None

    rows, current_key = [], None  # rows: (block number, words on that line)
    confidences, number_confidences = [], []
    for i, raw in enumerate(data.get("text", [])):
        word = _clean(str(raw)).strip()
        try:
            conf = float(data["conf"][i])
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        if not word or conf < 0:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        if key != current_key:
            rows.append((key[0], []))
            current_key = key
        rows[-1][1].append(word)
        confidences.append(conf)
        if any(ch.isdigit() for ch in word):
            number_confidences.append(conf)

    out, previous_block = [], None
    for block, words in rows:
        if previous_block is not None and block != previous_block:
            out.append("")  # blank line between text blocks
        out.append(" ".join(words))
        previous_block = block
    text = "\n".join(out).strip()
    if not confidences or not re.search(r"[A-Za-z0-9À-￿]", text):
        raise NoTextFound()

    warnings = []
    mean = round(sum(confidences) / len(confidences), 1)
    if mean < settings.OCR_MIN_CONFIDENCE:
        warnings.append(f"Low overall OCR confidence ({mean}%). The text may be inaccurate or incomplete.")
    low_words = sum(1 for c in confidences if c < LOW_WORD_CONFIDENCE)
    if low_words and low_words / len(confidences) > 0.25:
        warnings.append(f"{low_words} of {len(confidences)} words were read with low confidence.")
    uncertain_numbers = sum(1 for c in number_confidences if c < LOW_NUMBER_CONFIDENCE)
    if uncertain_numbers:
        warnings.append(f"{uncertain_numbers} number(s), possibly doses or strengths, were read with low "
                        "confidence. Check them against the original.")
    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS]
        warnings.append("The extracted text was too long and has been truncated.")
    return OCRResult(text=text, confidence=mean, warnings=warnings)


def extract_text_from_bytes(data):
    return extract_text(load_image(data))
