import re

from django.db.models import Q
from rest_framework import exceptions, serializers
from users.models import Address, User


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)
    telegram_id = serializers.IntegerField(required=False)
    is_blocked = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number")
        if not phone_number:
            raise exceptions.ValidationError(
                {"phone_number": "Telefon raqam to'ldirilishi shart"}
            )

        if not re.match(
            r"^\+?998?\s?-?([0-9]{2})\s?-?(\d{3})\s?-?(\d{2})\s?-?(\d{2})$",
            phone_number,
        ):
            raise exceptions.ValidationError(
                "Noto'g'ri format! Raqamni quyidagicha formatlarda kiritishingiz mumkin!"
                "  +998XXXXXXXXX, +998-XX-XXX-XX-XX, +998 XX XXX XX XX"
            )

        if phone_number.startswith("+"):
            phone_number_without_plus = phone_number[1:]
            phone_number_with_plus = phone_number
        else:
            phone_number_without_plus = phone_number
            phone_number_with_plus = f"+{phone_number}"

        user = User.objects.filter(phone_number__icontains=phone_number_with_plus).first()
        if not user:
            user = User.objects.filter(phone_number__icontains=phone_number_without_plus).first()

        if user:
            return user

        password = f"{phone_number}_{validated_data.get('telegram_id', '')}"
        user = User.objects.create_user(
            phone_number=phone_number,
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
