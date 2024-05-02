import json

from rest_framework import authentication, exceptions
from users.models import User


class CustomTokenAuthentication(authentication.BaseAuthentication):
    # List of endpoints that do not require authentication
    allowed_endpoints = [
        "/swagger/",
        "/admin/",
    ]

    def authenticate(self, request):
        if any(
            request.path.startswith(endpoint) for endpoint in self.allowed_endpoints
        ):
            return None  # No authentication required

        phone_number = request.headers.get("Authorization", "")
        user = User.objects.filter(phone_number=phone_number).first()

        if request.path.startswith("/api/v1/users/auth"):
            return None  # Proceed with sign-in

        if not user:
            data = json.loads(request.body.decode("utf-8"))
            if data.get("telegram_id"):
                return None
            raise exceptions.AuthenticationFailed("phone_number not provided")

        elif user.is_blocked:
            raise exceptions.ValidationError(
                {
                    "detail": "Bekor qilingan buyurtmalaringiz 3 ta bo'lganligi uchun siz admin tomonidan bloklangansiz va botdan foydalana olmaysiz."
                }
            )

        return user
