import requests
from django.conf import settings
from django.db import IntegrityError
from drf_yasg import openapi, utils
from rest_framework import generics, permissions, response, status, views
from shop.models import Category, Order, Product
from shop.serializers import (
    CategoryListSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    ProductsListSerializer,
)


class CategoryListView(generics.ListAPIView):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()
    authentication_classes = []
    permission_classes = []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ProductListView(generics.ListAPIView):
    serializer_class = ProductsListSerializer
    queryset = Product.objects.all()
    authentication_classes = []
    permission_classes = []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    @utils.swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["orders"],
            properties={
                "orders": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "product": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                        required=["product", "count"],
                    ),
                ),
                "full_name": openapi.Schema(type=openapi.TYPE_STRING),
                "delivery_type": openapi.Schema(type=openapi.TYPE_STRING),
                "secondary_phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                "address": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={status.HTTP_201_CREATED: "{}"},
    )
    def post(self, request, *args, **kwargs):
        try:
            orders = request.data.pop("orders")
        except KeyError:
            orders = []
        serializer = self.serializer_class(
            data=request.data, context={"orders": orders, "request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({}, status.HTTP_201_CREATED)


class OrderUpdateView(generics.UpdateAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [
        permissions.AllowAny,
    ]
    authentication_classes = []

    def get_queryset(self):
        return Order.objects.all()


class IntegrateView(views.APIView):
    def post(self, request, *args, **kwargs):
        res = requests.get(
            "https://web.alipos.uz/external/menu",
            headers={"access-token": settings.ALIPOS_ACCESS_TOKEN},
        ).json()

        product_objects = []
        for cat in res.get("categories"):
            category, created = Category.objects.get_or_create(
                title=cat.get("name"), external_id=cat.get("id")
            )
            for product in res.get("products"):
                if product.get("categoryId") == cat.get("id"):
                    try:
                        product_objects.append(
                            Product(
                                title=product.get("name"),
                                external_id=product.get("id"),
                                price=product.get("price"),
                                category=category,
                            )
                        )
                    except IntegrityError:
                        pass

        for product_object in product_objects:
            try:
                product_object.save()
            except IntegrityError:
                pass

        return response.Response({}, status.HTTP_201_CREATED)
