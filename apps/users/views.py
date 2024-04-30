from drf_yasg import openapi, utils
from rest_framework import exceptions, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import UserSerializer


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @utils.swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["phone_number", "password"],
            properties={
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
                ),
            },
        ),
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: "Invalid input",
            status.HTTP_401_UNAUTHORIZED: "Invalid phone number or password",
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

        user = User.objects.filter(
            phone_number=phone_number, telegram_id=telegram_id
        ).first()
        if not user:
            raise exceptions.ValidationError("Phone number or telegram_id is invalid")

        # Return the user data if authentication is successful
        return Response(UserSerializer(instance=user).data, status=status.HTTP_200_OK)
