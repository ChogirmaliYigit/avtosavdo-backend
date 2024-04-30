from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import CustomToken


class CustomTokenAuthentication(TokenAuthentication):
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

        try:
            key = request.headers.get("Authorization", "").split()[-1]
            token = CustomToken.objects.filter(key=key).first()
        except IndexError:
            token = None

        if not token:
            if request.path.startswith("/api/v1/users/sign-in"):
                return None  # Proceed with sign-in
            raise AuthenticationFailed("Token not provided")
        elif token and token.expires_at < timezone.now():
            raise AuthenticationFailed("Token expired")
        elif token and request.path.startswith("/api/v1/users/sign-in"):
            raise exceptions.ValidationError(
                {
                    "detail": "Siz allaqachon tizimga kirgansiz! Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊"
                }
            )

        if token.user.is_blocked:
            raise exceptions.ValidationError(
                {
                    "detail": "Bekor qilingan buyurtmalaringiz 3 ta bo'lganligi uchun siz admin tomonidan bloklangansiz va botdan foydalana olmaysiz."
                }
            )

        return token.user, token
