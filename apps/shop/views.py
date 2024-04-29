from django.shortcuts import get_object_or_404
from rest_framework import generics, response, status, views
from shop.models import CartItem, Category, Order, Product
from shop.serializers import (
    CartItemDetailSerializer,
    CartItemSerializer,
    CategoryListSerializer,
    OrderListSerializer,
    ProductsListSerializer,
)


class CategoryListView(generics.ListAPIView):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ProductListView(generics.ListAPIView):
    serializer_class = ProductsListSerializer
    queryset = Product.objects.all()


class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


class CartItemRetrieveUpdateDestroyView(views.APIView):
    serializer_class = CartItemDetailSerializer

    def get(self, request, product_id):
        cart_item = get_object_or_404(CartItem, product_id=product_id)
        serializer = self.serializer_class(
            instance=cart_item, context={"request": request}
        )
        return response.Response(serializer.data, status.HTTP_200_OK)

    def put(self, request, product_id):
        cart_item = get_object_or_404(CartItem, product_id=product_id)
        serializer = self.serializer_class(
            instance=cart_item, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({}, status.HTTP_200_OK)

    def delete(self, request, product_id):
        cart_item = get_object_or_404(CartItem, product_id=product_id)
        cart_item.delete()
        return response.Response({}, status.HTTP_204_NO_CONTENT)


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
