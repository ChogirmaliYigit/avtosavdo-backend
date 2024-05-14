from django.urls import path
from shop.views import (
    CategoryListView,
    IntegrateView,
    OrderListCreateView,
    ProductListView,
)

urlpatterns = [
    path("categories", CategoryListView.as_view(), name="categories-list-create"),
    path("products", ProductListView.as_view(), name="products-list-create"),
    path("orders", OrderListCreateView.as_view(), name="orders-list-create"),
    path("integrate", IntegrateView.as_view(), name="integrate"),
]
