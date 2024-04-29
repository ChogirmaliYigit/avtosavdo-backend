from django.contrib.auth import authenticate
from drf_yasg import openapi, utils
from rest_framework import generics, permissions, status, validators
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import UserSerializer


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @utils.swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["telegram_id", "phone_number", "latitude", "longitude"],
            properties={
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
                ),
            },
        ),
        responses={
            status.HTTP_201_CREATED: UserSerializer,
            status.HTTP_400_BAD_REQUEST: "Invalid input",
        },
    )
    def post(self, request):
        user = authenticate(
            phone_number=request.data.get("phone_number"),
            password=request.data.get("password"),
        )
        if not user:
            raise validators.ValidationError("Phone number or password is invalid")
        return Response(UserSerializer(instance=user).data, status.HTTP_200_OK)
