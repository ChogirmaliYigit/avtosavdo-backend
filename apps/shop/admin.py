from django.contrib import admin
from shop.models import Category, Order, OrderProduct, Product
from unfold.admin import ModelAdmin, StackedInline


class ProductInline(StackedInline):
    model = Product
    fields = ("title", "price", "discount_percentage", "image")
    extra = 1


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("title",)
    fields = list_display
    search_fields = list_display + ("id",)
    inlines = [ProductInline]


class OrderProductInline(StackedInline):
    model = OrderProduct
    fields = (
        "product",
        "count",
    )
    extra = 1


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "user",
        "total_price",
        "status",
        "paid",
        "delivery_type",
        "address_text",
    )
    fields = (
        "user",
        "total_price",
        "status",
        "paid",
        "delivery_type",
    )
    search_fields = list_display + ("id",)
    list_filter = (
        "paid",
        "delivery_type",
        "status",
        "user",
    )
    list_filter_submit = True
    inlines = [OrderProductInline]
