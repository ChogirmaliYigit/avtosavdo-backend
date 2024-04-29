from django.urls import path
from shop.views import (
    CartItemListCreateView,
    CartItemRetrieveUpdateDestroyView,
    CategoryListView,
    ProductListView,
)

urlpatterns = [
    path("categories", CategoryListView.as_view(), name="categories-list"),
    path("products", ProductListView.as_view(), name="products-list"),
    path("cart", CartItemListCreateView.as_view(), name="cart-item-list-create"),
    path(
        "cart/<int:product_id>",
        CartItemRetrieveUpdateDestroyView.as_view(),
        name="cart-item-detail-update-delete",
    ),
]
