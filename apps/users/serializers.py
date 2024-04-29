from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    def create(self, validated_data):
        password = (
            f"{validated_data.get('phone_number')}_{validated_data.get('telegram_id')}"
        )
        user = User.objects.create_user(
            full_name=validated_data.get("full_name"),
            username=validated_data.get("username"),
            password=password,
            phone_number=validated_data.get("phone_number"),
            telegram_id=validated_data.get("telegram_id"),
            is_active=True,
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
            "username",
            "full_name",
            "password",
            "token",
        )
