import re

from django.db.models import Q
from rest_framework import exceptions, serializers
from users.models import Address, User


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)
    telegram_id = serializers.IntegerField(required=False)
    is_blocked = serializers.BooleanField(read_only=True)

    def validate_phone_number(self, value):
        if not value:
            raise exceptions.ValidationError(
                {"phone_number": "Telefon raqam to'ldirilishi shart"}
            )

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
        password = f"{validated_data.get('phone_number')}_{validated_data.get('telegram_id', '')}"
        user = User.objects.create_user(
            phone_number=validated_data.get("phone_number"),
            full_name=validated_data.get("full_name"),
            password=password,
            telegram_id=validated_data.get("telegram_id"),
            is_blocked=False,
            is_staff=False,
        )
        return user

    def to_representation(self, instance):
        phone_number = self.context.get("phone_number")
        if phone_number and not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
        data = super().to_representation(instance)
        data["addresses"] = AddressListSerializer(
            Address.objects.filter(
                Q(user__phone_number=phone_number)
                | Q(user__phone_number=phone_number[1:])
            ),
            many=True,
        ).data
        return data

    class Meta:
        model = User
        fields = (
            "phone_number",
            "telegram_id",
            "full_name",
            "is_blocked",
        )


class AddressListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "address",
            "latitude",
            "longitude",
        )
