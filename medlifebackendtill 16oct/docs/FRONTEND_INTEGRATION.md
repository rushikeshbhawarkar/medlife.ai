# Frontend integration for member chat and OCR

The provider change does not require a React change: the browser continues to call Django, and Django calls the configured LLM provider. The frontend must use the member-specific chat route and complete the OCR review/confirmation flow for the new profile synchronization to work.

## Member-specific chat

Use `POST /medlife/chat/ask/`, not the legacy general-purpose `GET /medlife/prompt/`, when the answer should use the selected member's health profile. Send the existing access token and the member's actual key (`member1`, `member2`, etc.):

```javascript
const response = await fetch(`${API_BASE}/chat/ask/`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${accessToken}`,
  },
  body: JSON.stringify({ member_name: selectedMemberKey, query }),
});
const data = await response.json();
if (!response.ok) throw new Error(data.detail || "Chat request failed");
const answer = data.answer;
```

`API_BASE` in this example is `http://127.0.0.1:8000/medlife`; do not append another `/medlife` in the fetch path.

## OCR upload and review

1. Upload the file as multipart `image`, include `member_name` for the selected member and optional `documentType` (`prescription`, `medicine_label`, or `other`). Do not manually set the multipart `Content-Type`; the browser supplies the boundary.
2. Include `Authorization: Bearer <accessToken>`.
3. Show the returned `description`, `warnings`, and confidence to the user. Allow correction before confirming.
4. If corrected, send `PATCH /documents/<id>/` with `{"description":"corrected text"}`. This deliberately clears confirmation.
5. After the user checks the text against the original, send `PATCH /documents/<id>/` with `{"isConfirmed":true}`. Only then does the backend sync the text to the selected member's `medical_description`.
6. Refresh that member's data if the UI shows `medicalDescription` in the profile. Chat requests will load the updated value from the backend automatically.

Example upload:

```javascript
const form = new FormData();
form.append("image", file);
form.append("documentType", "prescription");
form.append("member_name", selectedMemberKey);
const response = await fetch(`${API_BASE}/documents/scan/`, {
  method: "POST",
  headers: { Authorization: `Bearer ${accessToken}` },
  body: form,
});
```

Document routes are `POST /documents/scan/`, `GET /documents/`, `GET /documents/<id>/`, `PATCH /documents/<id>/`, and `DELETE /documents/<id>/`. All require the normal access token issued after successful TOTP verification. Existing chat history endpoints do not change.
