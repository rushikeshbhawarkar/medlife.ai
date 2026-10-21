# Purpose: Converts all DRF errors into the {"detail": "..."} shape expected by the frontend.
# Edit this file when the API needs a new shared error format.
from rest_framework.views import exception_handler

def detail_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    data = response.data
    if isinstance(data, dict) and "detail" in data:
        message = data["detail"]
    elif isinstance(data, dict):
        message = next(iter(data.values()), "Invalid request.")
        if isinstance(message, (list, tuple)):
            message = message[0] if message else "Invalid request."
        if isinstance(message, dict):
            message = next(iter(message.values()), "Invalid request.")
    else:
        message = data or "Invalid request."
    response.data = {"detail": str(message)}
    return response
