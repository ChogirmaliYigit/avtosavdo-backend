from django.contrib import admin
from shop.models import CartItem, Category, Order, OrderProduct, Product, ProductImage
from unfold.admin import ModelAdmin, TabularInline


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = (
        "title",
        "parent",
        "image",
    )
    fields = list_display
    search_fields = list_display + ("id",)
    list_filter = ("parent",)
    list_filter_submit = True


class ProductImageInline(TabularInline):
    model = ProductImage
    fields = ("image",)
    extra = 1


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        "title",
        "category",
        "real_price",
        "discount_percentage",
    )
    fields = (
        "title",
        "category",
        "price",
        "discount_percentage",
    )
    search_fields = fields + ("id",)
    list_filter = ("category",)
    list_filter_submit = True
    inlines = [ProductImageInline]


@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = (
        "user",
        "product",
        "count",
        "price",
    )
    fields = (
        "user",
        "product",
        "count",
    )
    search_fields = fields + ("id",)


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "user",
        "total_price",
        "status",
        "paid",
        "delivery_type",
        "note",
    )
    fields = list_display
    search_fields = list_display + ("id",)
    list_filter = (
        "paid",
        "delivery_type",
        "status",
        "user",
    )
    list_filter_submit = True


@admin.register(OrderProduct)
class OrderProductAdmin(ModelAdmin):
    list_display = (
        "order",
        "product",
        "count",
    )
    fields = list_display
    search_fields = list_display + ("id",)
