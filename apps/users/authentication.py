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

        phone_number = request.headers.get("Authorization", "")

        try:
            data = json.loads(request.body.decode("utf-8"))
            telegram_id = data.get("telegram_id")
            if not phone_number:
            phone_number = data.get("phone_number", "")
        except json.decoder.JSONDecodeError:
            telegram_id = None

        if telegram_id:
            user = User.objects.all().filter(telegram_id=telegram_id).first()
            if user and not user.addresses.all():
                raise exceptions.ValidationError(
                    {
                        "detail": "Buyurtma berish uchun botga kirib lokatsiyangizni yuboring!"
                    }
                )
        else:
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

        if request.path.startswith("/api/v1/users/auth"):
            return user, ""

        if not user:
            raise exceptions.AuthenticationFailed("Telefon raqam to'ldirilishi shart")

        elif user.is_blocked:
            raise exceptions.ValidationError(
                {
                    "detail": "Bekor qilingan buyurtmalaringiz 3 ta bo'lganligi uchun siz admin tomonidan bloklangansiz va hozircha botdan foydalana olmaysiz."
                }
            )

        return user, ""
