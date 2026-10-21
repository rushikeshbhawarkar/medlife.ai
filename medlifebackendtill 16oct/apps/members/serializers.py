# # Purpose: Validates camelCase profile fields sent by the existing React frontend.
# # Edit when the member form fields or API validation rules change.
# import re
# from decimal import Decimal, InvalidOperation
# from rest_framework import serializers

# class MemberInputSerializer(serializers.Serializer):
#     firstName = serializers.CharField(max_length=100, allow_blank=False, trim_whitespace=True)
#     lastName = serializers.CharField(max_length=100, allow_blank=True, required=False, default="")
#     dob = serializers.CharField(max_length=10, allow_blank=True, required=False, default="")
#     gender = serializers.CharField(max_length=40, allow_blank=True, required=False, default="")
#     race = serializers.CharField(max_length=100, allow_blank=True, required=False, default="")
#     height = serializers.CharField(max_length=30, allow_blank=True, required=False, default="")
#     weight = serializers.CharField(max_length=30, allow_blank=True, required=False, default="")
#     a1c = serializers.CharField(max_length=20, allow_blank=True, required=False, default="")
#     bloodPressure = serializers.CharField(max_length=7, allow_blank=True, required=False, default="")
#     medicine = serializers.CharField(max_length=2000, allow_blank=True, required=False, default="")
#     tokens = serializers.IntegerField(required=False, write_only=True)

#     def validate_a1c(self, value):
#         if not value.strip():
#             return None
#         try:
#             number = Decimal(value)
#         except (InvalidOperation, ValueError):
#             raise serializers.ValidationError("A1C must be a number.")
#         if not number.is_finite() or number < 0 or number > 100:
#             raise serializers.ValidationError("A1C must be between 0 and 100.")
#         return number

#     def validate_bloodPressure(self, value):
#         if value and not re.fullmatch(r"\d{2,3}/\d{2,3}", value.strip()):
#             raise serializers.ValidationError("Blood pressure must use the format NNN/NN.")
#         return value.strip()

#     def validate_dob(self, value):
#         if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
#             raise serializers.ValidationError("Date of birth must use YYYY-MM-DD.")
#         return value

#     def to_model_values(self):
#         d = self.validated_data
#         return {
#             "first_name": d["firstName"], "last_name": d.get("lastName", ""),
#             "dob": d.get("dob", ""), "gender": d.get("gender", ""),
#              "race": d.get("race", ""), "height": d.get("height", ""),
#             "weight": d.get("weight", ""), "a1c": (d.get("a1c") or None),
#             "blood_pressure": d.get("bloodPressure", ""),
#             "medicine": d.get("medicine", ""),
#         }

# def member_to_frontend(member):
#     return {
#         "firstName": member.first_name, "lastName": member.last_name, "dob": member.dob,
#         "gender": member.gender, "race": member.race, "height": member.height, "weight": member.weight,
#         "a1c": "" if member.a1c is None else str(member.a1c).rstrip("0").rstrip("."),
#         "bloodPressure": member.blood_pressure, "medicine": member.medicine,
#         "tokens": member.tokens_used,
#     }




# # Purpose: Validates camelCase profile fields sent by the existing React frontend.
# # Edit when the member form fields or API validation rules change.
# import re
# from decimal import Decimal, InvalidOperation
# from rest_framework import serializers

# class MemberInputSerializer(serializers.Serializer):
#     firstName = serializers.CharField(max_length=100, allow_blank=False, trim_whitespace=True)
#     lastName = serializers.CharField(max_length=100, allow_blank=True, required=False, default="")
#     dob = serializers.CharField(max_length=10, allow_blank=True, required=False, default="")
#     gender = serializers.CharField(max_length=40, allow_blank=True, required=False, default="")
#     race = serializers.CharField(max_length=100, allow_blank=True, required=False, default="")
#     height = serializers.CharField(max_length=30, allow_blank=True, required=False, default="")
#     weight = serializers.CharField(max_length=30, allow_blank=True, required=False, default="")
#     a1c = serializers.CharField(max_length=20, allow_blank=True, required=False, default="")
#     bloodPressure = serializers.CharField(max_length=7, allow_blank=True, required=False, default="")
#     medicine = serializers.CharField(max_length=2000, allow_blank=True, required=False, default="")
#     medicalDescription = serializers.CharField(max_length=20000, allow_blank=True, required=False, default="")
#     tokens = serializers.IntegerField(required=False, write_only=True)

#     def validate_a1c(self, value):
#         if not value.strip():
#             return None
#         try:
#             number = Decimal(value)
#         except (InvalidOperation, ValueError):
#             raise serializers.ValidationError("A1C must be a number.")
#         if not number.is_finite() or number < 0 or number > 100:
#             raise serializers.ValidationError("A1C must be between 0 and 100.")
#         return number

#     def validate_bloodPressure(self, value):
#         if value and not re.fullmatch(r"\d{2,3}/\d{2,3}", value.strip()):
#             raise serializers.ValidationError("Blood pressure must use the format NNN/NN.")
#         return value.strip()

#     def validate_dob(self, value):
#         if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
#             raise serializers.ValidationError("Date of birth must use YYYY-MM-DD.")
#         return value

#     def to_model_values(self):
#         d = self.validated_data
#         return {
#             "first_name": d["firstName"], "last_name": d.get("lastName", ""),
#             "dob": d.get("dob", ""), "gender": d.get("gender", ""),
#              "race": d.get("race", ""), "height": d.get("height", ""),
#             "weight": d.get("weight", ""), "a1c": (d.get("a1c") or None),
#             "blood_pressure": d.get("bloodPressure", ""),
#             "medicine": d.get("medicine", ""),
#             "medical_description": d.get("medicalDescription", ""),
#         }

# def member_to_frontend(member):
#     return {
#         "firstName": member.first_name, "lastName": member.last_name, "dob": member.dob,
#         "gender": member.gender, "race": member.race, "height": member.height, "weight": member.weight,
#         "a1c": "" if member.a1c is None else str(member.a1c).rstrip("0").rstrip("."),
#         "bloodPressure": member.blood_pressure, "medicine": member.medicine,
#         "medicalDescription": member.medical_description,
#         "tokens": member.tokens_used,
#     }









# Purpose: Validates camelCase profile fields sent by the existing React frontend.
# Edit when the member form fields or API validation rules change.
import re
from decimal import Decimal, InvalidOperation
from rest_framework import serializers

class MemberInputSerializer(serializers.Serializer):
    firstName = serializers.CharField(max_length=100, allow_blank=False, trim_whitespace=True)
    lastName = serializers.CharField(max_length=100, allow_blank=True, required=False, default="")
    dob = serializers.CharField(max_length=10, allow_blank=True, required=False, default="")
    gender = serializers.CharField(max_length=40, allow_blank=True, required=False, default="")
    race = serializers.CharField(max_length=100, allow_blank=True, required=False, default="")
    height = serializers.CharField(max_length=30, allow_blank=True, required=False, default="")
    weight = serializers.CharField(max_length=30, allow_blank=True, required=False, default="")
    a1c = serializers.CharField(max_length=20, allow_blank=True, required=False, default="")
    bloodPressure = serializers.CharField(max_length=7, allow_blank=True, required=False, default="")
    medicine = serializers.CharField(max_length=2000, allow_blank=True, required=False, default="")
    medicalDescription = serializers.CharField(max_length=20000, allow_blank=True, required=False, default="")
    tokens = serializers.IntegerField(required=False, write_only=True)

    def validate_a1c(self, value):
        if not value.strip():
            return None
        try:
            number = Decimal(value)
        except (InvalidOperation, ValueError):
            raise serializers.ValidationError("A1C must be a number.")
        if not number.is_finite() or number < 0 or number > 100:
            raise serializers.ValidationError("A1C must be between 0 and 100.")
        return number

    def validate_bloodPressure(self, value):
        if value and not re.fullmatch(r"\d{2,3}/\d{2,3}", value.strip()):
            raise serializers.ValidationError("Blood pressure must use the format NNN/NN.")
        return value.strip()

    def validate_dob(self, value):
        if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise serializers.ValidationError("Date of birth must use YYYY-MM-DD.")
        return value

    def to_model_values(self):
        d = self.validated_data
        return {
            "first_name": d["firstName"], "last_name": d.get("lastName", ""),
            "dob": d.get("dob", ""), "gender": d.get("gender", ""),
             "race": d.get("race", ""), "height": d.get("height", ""),
            "weight": d.get("weight", ""), "a1c": (d.get("a1c") or None),
            "blood_pressure": d.get("bloodPressure", ""),
            "medicine": d.get("medicine", ""),
            "medical_description": d.get("medicalDescription", ""),
        }

def member_to_frontend(member):
    return {
        "id": member.pk,
        "firstName": member.first_name, "lastName": member.last_name, "dob": member.dob,
        "gender": member.gender, "race": member.race, "height": member.height, "weight": member.weight,
        "a1c": "" if member.a1c is None else str(member.a1c).rstrip("0").rstrip("."),
        "bloodPressure": member.blood_pressure, "medicine": member.medicine,
        "medicalDescription": member.medical_description,
        "tokens": member.tokens_used,
    }
