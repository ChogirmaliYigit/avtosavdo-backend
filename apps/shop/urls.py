from django.urls import path
from shop.views import (
    CartItemListCreateView,
    CartItemRetrieveUpdateDestroyView,
    CategoryListView,
    OrderListCreateView,
    ProductListView,
)

urlpatterns = [
    path("categories", CategoryListView.as_view(), name="categories-list-create"),
    path("products", ProductListView.as_view(), name="products-list-create"),
    path("cart", CartItemListCreateView.as_view(), name="cart-item-list-create"),
    path(
        "cart/<int:product_id>",
        CartItemRetrieveUpdateDestroyView.as_view(),
        name="cart-item-detail-update-delete",
    ),
    path("orders", OrderListCreateView.as_view(), name="orders-list-create"),
]
