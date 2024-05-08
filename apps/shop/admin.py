from django.contrib import admin
from shop.models import Category, Order, OrderProduct, Product
from unfold.admin import ModelAdmin, StackedInline


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("title",)
    fields = list_display
    search_fields = list_display + ("id",)


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("title", "category", "price", "discount_percentage", "image")
    fields = list_display
    list_filter = ("category",)
    list_filter_submit = True


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
        "secondary_phone_number",
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
