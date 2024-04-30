import re

from rest_framework import exceptions, serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)
    telegram_id = serializers.IntegerField(required=True)
    password = serializers.CharField(required=False)
    is_blocked = serializers.BooleanField(read_only=True)
    token = serializers.SerializerMethodField()

    def validate_phone_number(self, value):
        if not re.match(
            r"^\+?998?\s?-?([0-9]{2})\s?-?(\d{3})\s?-?(\d{2})\s?-?(\d{2})$",
            value,
        ):
            raise exceptions.ValidationError(
                "Noto'g'ri format! Raqamni quyidagicha formatlarda kiritishingiz mumkin!"
                "  +998XXXXXXXXX, +998-XX-XXX-XX-XX, +998 XX XXX XX XX"
            )

        if User.objects.filter(phone_number=value).exists():
            raise exceptions.ValidationError(
                "Bu telefon raqami allaqachon ro'yxatdan o'tgan!"
            )

        return value

    def create(self, validated_data):
        password = (
            f"{validated_data.get('phone_number')}_{validated_data.get('telegram_id')}"
        )
        user = User.objects.create_user(
            full_name=validated_data.get("full_name"),
            password=password,
            phone_number=validated_data.get("phone_number"),
            telegram_id=validated_data.get("telegram_id"),
            is_blocked=False,
            is_staff=False,
        )
        return user

    def get_token(self, user):
        return user.auth_token.key

    class Meta:
        model = User
        fields = (
            "phone_number",
            "telegram_id",
            "full_name",
            "is_blocked",
            "token",
        )
