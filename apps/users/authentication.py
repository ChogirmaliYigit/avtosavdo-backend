import json

from django.db.models import Q
from rest_framework import authentication, exceptions
from users.models import User


class CustomTokenAuthentication(authentication.BaseAuthentication):
    # List of endpoints that do not require authentication
    allowed_endpoints = [
        "/swagger/",
    ]

    def authenticate(self, request):
        if any(
            request.path.startswith(endpoint) for endpoint in self.allowed_endpoints
        ):
            return None  # No authentication required

        if request.path.startswith("/api/v1/users/auth"):
            return None  # Proceed with sign-in

        phone_number = request.headers.get("Authorization", "")
        if phone_number.startswith("+"):
            phone_number_without_plus = phone_number[1:]
            phone_number_with_plus = phone_number
        else:
            phone_number_without_plus = phone_number
            phone_number_with_plus = f"+{phone_number}"
        user = User.objects.filter(
            Q(phone_number=phone_number_with_plus)
            | Q(phone_number=phone_number_without_plus)
        ).first()

        if not user:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except json.decoder.JSONDecodeError:
                data = {}
            if data.get("telegram_id"):
                return None
            print("auth error")
            raise exceptions.AuthenticationFailed("Telefon raqam to'ldirilishi shart")

        elif user.is_blocked:
            raise exceptions.ValidationError(
                {
                    "detail": "Bekor qilingan buyurtmalaringiz 3 ta bo'lganligi uchun siz admin tomonidan bloklangansiz va hozircha botdan foydalana olmaysiz."
                }
            )

        return user, "1"
