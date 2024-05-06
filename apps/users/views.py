from drf_yasg import openapi, utils
from rest_framework import exceptions, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import UserSerializer


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @utils.swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                "telegram_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: "Invalid input",
            status.HTTP_401_UNAUTHORIZED: "Invalid phone number",
        },
    )
    def post(self, request):
        if request.user.is_authenticated:
            raise exceptions.ValidationError(
                {
                    "detail": "Siz allaqachon tizimga kirgansiz! Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊"
                }
            )

        phone_number = request.data.get("phone_number")
        telegram_id = request.data.get("telegram_id")

        if telegram_id:
            user = User.objects.all().filter(telegram_id=telegram_id).first()
            if user:
                if not user.addresses.all():
                    return exceptions.ValidationError(
                        {
                            "detail": "Buyurtma berish uchun botga kirib lokatsiyangizni yuboring!"
                        }
                    )

        else:
            if not phone_number:
                phone_number = request.headers.get("Authorization", "")
            if not phone_number:
                raise exceptions.ValidationError(
                    {"phone_number": "Telefon raqam to'ldirilishi shart!!!"}
                )

            user = User.objects.filter(phone_number=phone_number).first()
            if not user:
                serializer = UserSerializer(
                    data=request.data, context={"phone_number": phone_number}
                )
                serializer.is_valid(raise_exception=True)
                user = serializer.save()

        if user.is_blocked:
            raise exceptions.ValidationError(
                {
                    "detail": "Bekor qilingan buyurtmalaringiz 3 ta bo'lganligi uchun siz admin tomonidan bloklangansiz va botdan foydalana olmaysiz."
                }
            )

        # Return the user data if authentication is successful
        return Response(
            UserSerializer(instance=user, context={"phone_number": phone_number}).data,
            status=status.HTTP_200_OK,
        )
