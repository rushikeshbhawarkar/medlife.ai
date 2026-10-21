# # Purpose: Validates email and password values for account-related endpoints.
# # Edit when the account API accepts additional public fields.
# from rest_framework import serializers

# class EmailSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=254)

# class CredentialsSerializer(serializers.Serializer):
#     """Body of /signup and /signin. The 6-character minimum matches the frontend form."""
#     email = serializers.EmailField(max_length=254)
#     password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)

















# # Purpose: Validate account credentials and TOTP verification requests.
# from rest_framework import serializers


# class EmailSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=254)


# class CredentialsSerializer(serializers.Serializer):
#     """Body of signup, signin, and restarting an incomplete TOTP setup."""
#     email = serializers.EmailField(max_length=254)
#     password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)


# class SetupVerificationSerializer(serializers.Serializer):
#     setup_token = serializers.CharField(trim_whitespace=True)
#     code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})


# class LoginVerificationSerializer(serializers.Serializer):
#     challenge_token = serializers.CharField(trim_whitespace=True)
#     code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})













# # Purpose: Validate account credentials and TOTP verification requests.
# from rest_framework import serializers


# class EmailSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=254)


# class CredentialsSerializer(serializers.Serializer):
#     """Body of signup, signin, and restarting an incomplete TOTP setup."""
#     email = serializers.EmailField(max_length=254)
#     password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)


# class SetupVerificationSerializer(serializers.Serializer):
#     setup_token = serializers.CharField(trim_whitespace=True)
#     code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})


# class LoginVerificationSerializer(serializers.Serializer):
#     challenge_token = serializers.CharField(trim_whitespace=True)
#     code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})


# class PasswordResetConfirmSerializer(serializers.Serializer):
#     """Body of the reset-password endpoint. Strength checks that need the account run in the service."""
#     token = serializers.CharField(max_length=2048, trim_whitespace=True)
#     new_password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)
#     confirm_password = serializers.CharField(max_length=128, trim_whitespace=False, write_only=True)

#     def validate(self, attrs):
#         if attrs["new_password"] != attrs["confirm_password"]:
#             raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
#         return attrs










# # Purpose: Validate account credentials and TOTP verification requests.
# from rest_framework import serializers


# class EmailSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=254)


# class CredentialsSerializer(serializers.Serializer):
#     """Body of signup, signin, and restarting an incomplete TOTP setup."""
#     email = serializers.EmailField(max_length=254)
#     password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)


# class SetupVerificationSerializer(serializers.Serializer):
#     setup_token = serializers.CharField(trim_whitespace=True)
#     code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})


# class LoginVerificationSerializer(serializers.Serializer):
#     challenge_token = serializers.CharField(trim_whitespace=True)
#     code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})


# class PasswordResetConfirmSerializer(serializers.Serializer):
#     """Body of the reset-password endpoint. Strength checks that need the account run in the service."""
#     token = serializers.CharField(max_length=2048, trim_whitespace=True)
#     new_password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)
#     confirm_password = serializers.CharField(max_length=128, trim_whitespace=False, write_only=True)

#     def validate(self, attrs):
#         if attrs["new_password"] != attrs["confirm_password"]:
#             raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
#         return attrs


# class GoogleSignInSerializer(serializers.Serializer):
#     """Google Identity Services ID token posted by the frontend for server-side verification."""
#     id_token = serializers.CharField(max_length=8192, trim_whitespace=True, write_only=True)



















# # Purpose: Validate account credentials and TOTP verification requests.
# from rest_framework import serializers


# class EmailSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=254)


# class CredentialsSerializer(serializers.Serializer):
#     """Body of signup, signin, and restarting an incomplete TOTP setup."""
#     email = serializers.EmailField(max_length=254)
#     password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)


# class SetupVerificationSerializer(serializers.Serializer):
#     setup_token = serializers.CharField(trim_whitespace=True)
#     code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})


# class LoginVerificationSerializer(serializers.Serializer):
#     challenge_token = serializers.CharField(trim_whitespace=True)
#     code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})


# class PasswordResetConfirmSerializer(serializers.Serializer):
#     """Body of the reset-password endpoint. Strength checks that need the account run in the service."""
#     token = serializers.CharField(max_length=2048, trim_whitespace=True)
#     new_password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)
#     confirm_password = serializers.CharField(max_length=128, trim_whitespace=False, write_only=True)

#     def validate(self, attrs):
#         if attrs["new_password"] != attrs["confirm_password"]:
#             raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
#         return attrs


# class GoogleSignInSerializer(serializers.Serializer):
#     """Google Identity Services ID token posted by the frontend for server-side verification."""
#     id_token = serializers.CharField(max_length=8192, trim_whitespace=True, write_only=True)


# class PasswordChangeSerializer(serializers.Serializer):
#     """Change a password from an authenticated dashboard session."""
#     current_password = serializers.CharField(
#         max_length=128, trim_whitespace=False, write_only=True, required=False, allow_blank=True
#     )
#     new_password = serializers.CharField(
#         min_length=6, max_length=128, trim_whitespace=False, write_only=True
#     )
#     confirm_password = serializers.CharField(
#         max_length=128, trim_whitespace=False, write_only=True
#     )

#     def validate(self, attrs):
#         if attrs["new_password"] != attrs["confirm_password"]:
#             raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
#         return attrs

















# Purpose: Validate account credentials and TOTP verification requests.
from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class CredentialsSerializer(serializers.Serializer):
    """Body of signup, signin, and restarting an incomplete TOTP setup."""
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)


class SetupVerificationSerializer(serializers.Serializer):
    setup_token = serializers.CharField(trim_whitespace=True)
    code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})


class LoginVerificationSerializer(serializers.Serializer):
    challenge_token = serializers.CharField(trim_whitespace=True)
    code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Body of the reset-password endpoint. Strength checks that need the account run in the service."""
    token = serializers.CharField(max_length=2048, trim_whitespace=True)
    new_password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)
    confirm_password = serializers.CharField(max_length=128, trim_whitespace=False, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs


class GoogleSignInSerializer(serializers.Serializer):
    """Google Identity Services ID token posted by the frontend for server-side verification."""
    id_token = serializers.CharField(max_length=8192, trim_whitespace=True, write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    """Change a password from an authenticated dashboard session."""
    current_password = serializers.CharField(
        max_length=128, trim_whitespace=False, write_only=True, required=False, allow_blank=True
    )
    new_password = serializers.CharField(
        min_length=6, max_length=128, trim_whitespace=False, write_only=True
    )
    confirm_password = serializers.CharField(
        max_length=128, trim_whitespace=False, write_only=True
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs


class GooglePasswordSetupSerializer(serializers.Serializer):
    """Password fields submitted after a first Google sign-in."""
    setup_token = serializers.CharField(max_length=2048, trim_whitespace=True)
    new_password = serializers.CharField(min_length=6, max_length=128, trim_whitespace=False, write_only=True)
    confirm_password = serializers.CharField(max_length=128, trim_whitespace=False, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs


class TotpRecoveryEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class TotpRecoverySetupSerializer(serializers.Serializer):
    recovery_token = serializers.CharField(max_length=2048, trim_whitespace=True)


class TotpRecoveryVerifySerializer(TotpRecoverySetupSerializer):
    code = serializers.RegexField(regex=r"^\d{6}$", error_messages={"invalid": "Enter the six-digit authenticator code."})
