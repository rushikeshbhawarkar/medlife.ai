# # Purpose: Test helper that signs a test client in with a real signed bearer token.
# from django.core.cache import cache
# from rest_framework.test import APIClient
# from apps.accounts.models import Account
# from apps.core.authentication import issue_account_token


# def auth_client(email="test@example.com"):
#     """Return (APIClient carrying a valid token, Account). Clears the cache so rate limits start fresh."""
#     cache.clear()
#     account, _ = Account.objects.get_or_create(email=email.strip().lower())
#     client = APIClient()
#     client.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_account_token(account)}")
#     return client, account




# Purpose: Test helper that signs a test client in with a verified account token.
from django.core.cache import cache
from rest_framework.test import APIClient
from apps.accounts.models import Account
from apps.accounts.totp import encrypt_totp_secret
from apps.core.authentication import issue_account_token
import pyotp


def auth_client(email="test@example.com"):
    """Return (APIClient carrying a valid token, Account)."""
    cache.clear()
    account, _ = Account.objects.get_or_create(email=email.strip().lower())
    if not account.totp_enabled or not account.totp_secret_encrypted:
        account.totp_enabled = True
        account.totp_secret_encrypted = encrypt_totp_secret(pyotp.random_base32())
        account.save(update_fields=["totp_enabled", "totp_secret_encrypted"])
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_account_token(account)}")
    return client, account
