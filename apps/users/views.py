from core.utils import check_user_location, get_address_by_location
from drf_yasg import openapi, utils
from rest_framework import exceptions, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Address, User
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
        if request.user:
            return Response(
                UserSerializer(
                    instance=request.user,
                    context={"phone_number": request.user.phone_number},
                ).data,
                status=status.HTTP_200_OK,
            )

        phone_number = request.data.get("phone_number")
        telegram_id = request.data.get("telegram_id")

        if telegram_id:
            user = User.objects.all().filter(telegram_id=telegram_id).first()
            if user and not user.addresses.all():
                raise exceptions.ValidationError(
                    {
                        "detail": "Buyurtma berish uchun botga kirib lokatsiyangizni yuboring!"
                    }
                )

        else:
            if not phone_number:
                raise exceptions.ValidationError(
                    {"phone_number": "Telefon raqam to'ldirilishi shart"}
                )

            user = User.objects.filter(phone_number=phone_number).first()

            if not user:
                serializer = UserSerializer(
                    data=request.data, context={"phone_number": phone_number}
                )
                serializer.is_valid(raise_exception=True)
                user = serializer.save()

        if user and user.is_blocked:
            raise exceptions.ValidationError(
                {
                    "detail": "Bekor qilingan buyurtmalaringiz 3 ta bo'lganligi uchun siz admin tomonidan bloklangansiz va botdan foydalana olmaysiz."
                }
            )

        elif user:
            # Return the user data if authentication is successful
            return Response(
                UserSerializer(
                    instance=user, context={"phone_number": phone_number}
                ).data,
                status=status.HTTP_200_OK,
            )


class UpdateUserDataView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]
    authentication_classes = []

    def put(self, request, telegram_id: int):
        user = User.objects.filter(telegram_id=telegram_id).first()
        if not user:
            user = User.objects.create_user(
                phone_number=f"+{telegram_id}",
                password=str(telegram_id),
                telegram_id=telegram_id,
            )
        if user:
            phone_number = request.data.get("phone_number")
            latitude = request.data.get("latitude")
            longitude = request.data.get("longitude")
            address = request.data.get("address")

            if phone_number:
                user.phone_number = phone_number

            if latitude and longitude:
                address_data = {
                    "user": user,
                    "latitude": latitude,
                    "longitude": longitude,
                }
                address = Address.objects.filter(**address_data).first()
                if not address:
                    address_data["address"] = get_address_by_location(
                        latitude, longitude
                    )

                    if check_user_location(latitude, longitude):
                        Address.objects.create(**address_data)
                    else:
                        return Response(
                            {
                                "message": "Siz bepul yetkazib berish doirasidan tashqarida bo'lganingiz sababli qo'shimcha to'lov orqali buyurtma berish uchun +998771164949 telefon nomeriga bog'laning."
                            },
                            status.HTTP_403_FORBIDDEN,
                        )
            elif address:
                Address.objects.create(user=user, address=address)

            user.save()
            return Response({}, status.HTTP_200_OK)
        else:
            return Response({}, status.HTTP_404_NOT_FOUND)


class AllUsersListView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]
    authentication_classes = []

    def get(self, request):
        serializer = UserSerializer(
            User.objects.filter(telegram_id__isnull=False),
            many=True,
            context={"phone_number": "qoshkopiravtosavdo"},
        )
        return Response(serializer.data, status.HTTP_200_OK)
