# # Purpose: Rate limit for the public sign-up / sign-in endpoints (slows password guessing).
# # The limit is AUTH_RATE_LIMIT in .env (default 10/min per client IP).
# from rest_framework.throttling import AnonRateThrottle


# class AuthRateThrottle(AnonRateThrottle):
#     scope = "auth"











# Purpose: Rate limit for the public sign-up / sign-in endpoints (slows password guessing).
# The limit is AUTH_RATE_LIMIT in .env (default 10/min per client IP).
from rest_framework.throttling import AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    scope = "auth"


class PasswordResetRateThrottle(AnonRateThrottle):
    """Limits "forgot password" emails per client IP. Rate is PASSWORD_RESET_RATE_LIMIT in .env (default 5/hour)."""
    scope = "password_reset"
