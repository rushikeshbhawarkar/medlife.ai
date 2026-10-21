# # Purpose: Authenticate API requests using short-lived signed bearer tokens.
# from django.core import signing
# from rest_framework.authentication import BaseAuthentication, get_authorization_header
# from rest_framework.exceptions import AuthenticationFailed
# from apps.accounts.models import Account

# TOKEN_SALT = "medlife.account-token.v1"
# TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days


# def issue_account_token(account):
#     return signing.dumps({"account_id": account.pk}, salt=TOKEN_SALT, compress=True)


# class AccountTokenAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         header = get_authorization_header(request).split()
#         if not header:
#             return None
#         if header[0].lower() != b"bearer":
#             return None
#         if len(header) != 2:
#             raise AuthenticationFailed("Invalid authorization header.")
#         try:
#             token = header[1].decode("utf-8")
#             payload = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
#             account_id = payload["account_id"]
#         except (UnicodeError, signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError):
#             raise AuthenticationFailed("Invalid or expired access token.")
#         try:
#             account = Account.objects.get(pk=account_id)
#         except Account.DoesNotExist:
#             raise AuthenticationFailed("Invalid or expired access token.")
#         return (account, token)

#     def authenticate_header(self, request):
#         return "Bearer"
















# # Purpose: Authenticate API requests using signed bearer tokens issued only after TOTP verification.
# from django.core import signing
# from rest_framework.authentication import BaseAuthentication, get_authorization_header
# from rest_framework.exceptions import AuthenticationFailed
# from apps.accounts.models import Account

# TOKEN_SALT = "medlife.account-token.v1"
# TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days


# def issue_account_token(account):
#     if not account.totp_enabled or not account.totp_secret_encrypted:
#         raise ValueError("Cannot issue an access token before TOTP is enabled.")
#     return signing.dumps({"account_id": account.pk, "purpose": "access"}, salt=TOKEN_SALT, compress=True)


# class AccountTokenAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         header = get_authorization_header(request).split()
#         if not header:
#             return None
#         if header[0].lower() != b"bearer":
#             return None
#         if len(header) != 2:
#             raise AuthenticationFailed("Invalid authorization header.")
#         try:
#             token = header[1].decode("utf-8")
#             payload = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
#             account_id = payload["account_id"]
#             if payload.get("purpose") != "access":
#                 raise ValueError("Wrong token purpose")
#         except (UnicodeError, signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError):
#             raise AuthenticationFailed("Invalid or expired access token.")
#         try:
#             account = Account.objects.get(pk=account_id)
#         except Account.DoesNotExist:
#             raise AuthenticationFailed("Invalid or expired access token.")
#         # Defense in depth: even a previously issued token cannot access an unenrolled account.
#         if not account.totp_enabled or not account.totp_secret_encrypted:
#             raise AuthenticationFailed("Complete TOTP setup before accessing the application.")
#         return (account, token)

#     def authenticate_header(self, request):
#         return "Bearer"











# # Purpose: Authenticate API requests using signed bearer tokens issued only after TOTP verification.
# import hmac
# from django.core import signing
# from rest_framework.authentication import BaseAuthentication, get_authorization_header
# from rest_framework.exceptions import AuthenticationFailed
# from apps.accounts.models import Account
# from apps.accounts.tokens import password_fingerprint

# TOKEN_SALT = "medlife.account-token.v1"
# TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days


# def issue_account_token(account):
#     if not account.totp_enabled or not account.totp_secret_encrypted:
#         raise ValueError("Cannot issue an access token before TOTP is enabled.")
#     # "pv" ties the token to the current password, so a password reset signs out every earlier session.
#     return signing.dumps(
#         {"account_id": account.pk, "purpose": "access", "pv": password_fingerprint(account.password)},
#         salt=TOKEN_SALT, compress=True,
#     )


# class AccountTokenAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         header = get_authorization_header(request).split()
#         if not header:
#             return None
#         if header[0].lower() != b"bearer":
#             return None
#         if len(header) != 2:
#             raise AuthenticationFailed("Invalid authorization header.")
#         try:
#             token = header[1].decode("utf-8")
#             payload = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
#             account_id = payload["account_id"]
#             if payload.get("purpose") != "access":
#                 raise ValueError("Wrong token purpose")
#         except (UnicodeError, signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError):
#             raise AuthenticationFailed("Invalid or expired access token.")
#         try:
#             account = Account.objects.get(pk=account_id)
#         except Account.DoesNotExist:
#             raise AuthenticationFailed("Invalid or expired access token.")
#         # Defense in depth: even a previously issued token cannot access an unenrolled account.
#         if not account.totp_enabled or not account.totp_secret_encrypted:
#             raise AuthenticationFailed("Complete TOTP setup before accessing the application.")
#         # Token issued before the last password change (reset) -> revoked. Tokens issued before this
#         # feature existed have no "pv" claim and stay valid until their normal 7-day expiry.
#         if "pv" in payload and not hmac.compare_digest(str(payload["pv"]), password_fingerprint(account.password)):
#             raise AuthenticationFailed("Invalid or expired access token.")
#         return (account, token)

#     def authenticate_header(self, request):
#         return "Bearer"











# # Purpose: Authenticate API requests using signed bearer tokens issued only after TOTP verification.
# import hmac
# from django.core import signing
# from rest_framework.authentication import BaseAuthentication, get_authorization_header
# from rest_framework.exceptions import AuthenticationFailed
# from apps.accounts.models import Account
# from apps.accounts.tokens import password_fingerprint

# TOKEN_SALT = "medlife.account-token.v1"
# TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days


# def issue_account_token(account):
#     if not account.google_sub and (not account.totp_enabled or not account.totp_secret_encrypted):
#         raise ValueError("Cannot issue an access token before TOTP is enabled for a password-only account.")
#     # "pv" ties the token to the current password, so a password reset signs out every earlier session.
#     return signing.dumps(
#         {"account_id": account.pk, "purpose": "access", "pv": password_fingerprint(account.password)},
#         salt=TOKEN_SALT, compress=True,
#     )


# class AccountTokenAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         header = get_authorization_header(request).split()
#         if not header:
#             return None
#         if header[0].lower() != b"bearer":
#             return None
#         if len(header) != 2:
#             raise AuthenticationFailed("Invalid authorization header.")
#         try:
#             token = header[1].decode("utf-8")
#             payload = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
#             account_id = payload["account_id"]
#             if payload.get("purpose") != "access":
#                 raise ValueError("Wrong token purpose")
#         except (UnicodeError, signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError):
#             raise AuthenticationFailed("Invalid or expired access token.")
#         try:
#             account = Account.objects.get(pk=account_id)
#         except Account.DoesNotExist:
#             raise AuthenticationFailed("Invalid or expired access token.")
#         # Password-only accounts still require TOTP. Google-linked accounts deliberately
#         # bypass TOTP so OAuth sign-in can enter the application directly.
#         if not account.google_sub and (not account.totp_enabled or not account.totp_secret_encrypted):
#             raise AuthenticationFailed("Complete TOTP setup before accessing the application.")
#         # Token issued before the last password change (reset) -> revoked. Tokens issued before this
#         # feature existed have no "pv" claim and stay valid until their normal 7-day expiry.
#         if "pv" in payload and not hmac.compare_digest(str(payload["pv"]), password_fingerprint(account.password)):
#             raise AuthenticationFailed("Invalid or expired access token.")
#         return (account, token)

#     def authenticate_header(self, request):
#         return "Bearer"














# Purpose: Authenticate API requests using signed bearer tokens issued only after TOTP verification.
import hmac
from django.core import signing
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from apps.accounts.models import Account
from apps.accounts.tokens import password_fingerprint

TOKEN_SALT = "medlife.account-token.v1"
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days


def issue_account_token(account):
    if not account.google_sub and (not account.totp_enabled or not account.totp_secret_encrypted):
        raise ValueError("Cannot issue an access token before TOTP is enabled for a password-only account.")
    # "pv" ties the token to the current password, so a password reset signs out every earlier session.
    return signing.dumps(
        {"account_id": account.pk, "purpose": "access", "pv": password_fingerprint(account.password)},
        salt=TOKEN_SALT, compress=True,
    )


class AccountTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header:
            return None
        if header[0].lower() != b"bearer":
            return None
        if len(header) != 2:
            raise AuthenticationFailed("Invalid authorization header.")
        try:
            token = header[1].decode("utf-8")
            payload = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
            account_id = payload["account_id"]
            if payload.get("purpose") != "access":
                raise ValueError("Wrong token purpose")
        except (UnicodeError, signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError):
            raise AuthenticationFailed("Invalid or expired access token.")
        try:
            account = Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            raise AuthenticationFailed("Invalid or expired access token.")
        # Password-only accounts still require TOTP. Google-linked accounts can use OAuth,
        # while password-based login separately requires TOTP verification.
        if not account.google_sub and (not account.totp_enabled or not account.totp_secret_encrypted):
            raise AuthenticationFailed("Complete TOTP setup before accessing the application.")
        # Token issued before the last password change (reset) -> revoked. Tokens issued before this
        # feature existed have no "pv" claim and stay valid until their normal 7-day expiry.
        if "pv" in payload and not hmac.compare_digest(str(payload["pv"]), password_fingerprint(account.password)):
            raise AuthenticationFailed("Invalid or expired access token.")
        return (account, token)

    def authenticate_header(self, request):
        return "Bearer"

