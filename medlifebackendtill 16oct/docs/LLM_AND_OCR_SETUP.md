# Medlife local LLM and OCR setup

## Local Llama 3.1 8B through Ollama

1. Install Ollama for Windows from https://ollama.com/download.
2. In PowerShell run `ollama pull llama3.1:8b`.
3. Test the model with `ollama run llama3.1:8b`.
4. In the backend `.env`, set:

```dotenv
AI_PROVIDER=ollama
AI_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://127.0.0.1:11434
AI_TIMEOUT_SECONDS=120
AI_API_KEY=
```

`AI_API_KEY` is unused for Ollama. Keep Ollama running while Django handles chat requests. The Django process calls `http://127.0.0.1:11434/api/chat`; no browser request goes directly to Ollama.

## Switch to a different local model

Pull the desired model with Ollama, then change only `AI_MODEL`, for example `AI_MODEL=qwen2.5:7b`. Use the exact model tag shown by `ollama list`.

## Switch to an API-key provider

For OpenAI, set `AI_PROVIDER=openai`, `AI_MODEL` to a model supported by your account, and `AI_API_KEY` to the server-side key. The default `AI_BASE_URL` is OpenAI's Chat Completions endpoint.

For another service that supports the OpenAI Chat Completions request format, set `AI_PROVIDER=openai_compatible`, `AI_BASE_URL` to that provider's full chat-completions URL, `AI_MODEL` to its model identifier, and `AI_API_KEY` to its key. Never put provider API keys in React/Vite variables or return them to the browser.

The AI provider interface is `apps/ai/providers/base.py`; provider selection is in `apps/ai/providers/factory.py`. Existing request limits, member authorization, profile context and API routes are retained. This adapter expects a standard OpenAI-compatible `choices[0].message.content` response; a provider with a different protocol needs its own adapter.

## OCR setup on Windows

The Django OCR component uses Pillow + pytesseract, but `pytesseract` is only a Python wrapper. Install the Tesseract OCR program separately. If it is not on PATH, set `TESSERACT_CMD` to its executable path, commonly:

```dotenv
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
OCR_LANGUAGES=eng
OCR_MAX_UPLOAD_MB=5
OCR_TIMEOUT_SECONDS=30
```

Restart Django after editing `.env`. Check that Tesseract is available by running `tesseract --version` in PowerShell.

## OCR review and member health description

- `POST /medlife/documents/scan/` accepts multipart form data with `image`, optional `documentType`, and optional `member_name` (`member1` through `member4`). It stores extracted text as a draft; it does not immediately treat unreviewed OCR as trusted profile data.
- `PATCH /medlife/documents/<id>/` with `{"description":"corrected text"}` saves corrections and clears confirmation.
- After verifying the extracted text, call the same endpoint with `{"isConfirmed":true}`. If the scan is linked to a family member, the reviewed text is synchronized into that member's existing `medical_description` without overwriting the member's other notes.
- If the description is corrected, the previous generated section is removed until the correction is confirmed again. Deleting the scan removes only its generated section. Existing manually entered notes remain.
- Only confirmed OCR text is included in the selected member's AI context, because medicine names and dosages can be misread. Always compare extracted text with the original document.
- `GET /medlife/documents/?member_name=member1` lists that member's scans; `GET /medlife/documents/<id>/` reads one; `DELETE /medlife/documents/<id>/` deletes it. All document routes require the normal Bearer access token.

## Validation

Run `python manage.py check`, `python manage.py makemigrations --check`, and `python manage.py test apps.ai.tests apps.documents.tests` with your project virtual environment and PostgreSQL available. The new provider unit tests mock outbound HTTP; they do not require Ollama to be running. The document API tests use Django's test database and some OCR tests skip if the Tesseract executable is unavailable.


## OCR engine

Text extraction uses Tesseract only (the Tesseract setup above). There is no engine switch: `OCR_ENGINE`, the TrOCR/PaddleOCR settings and the medication dictionary were removed. The scan endpoint returns the extracted text, confidence and warnings; it does not return structured medication data.
