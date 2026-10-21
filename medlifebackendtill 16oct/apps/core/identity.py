# Purpose: The single boundary for "who is calling". The caller is the account named in the verified bearer token.
# Views never trust an `email` sent by the browser; it is only accepted if it matches the token's account.
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request


def _normalize(value) -> str:
    return str(value or "").strip().lower()


def caller_email(request: Request) -> str:
    """Return the authenticated account's email.

    The frontend still sends `email` for backward compatibility. It is NOT used to pick the
    account; if present it must match the token, otherwise the request is refused (403).
    """
    token_email = _normalize(request.user.email)
    supplied = request.query_params.get("email") or (request.data.get("email") if isinstance(request.data, dict) else "")
    if _normalize(supplied) and _normalize(supplied) != token_email:
        raise PermissionDenied("The email does not match the signed-in account.")
    return token_email
