from django.contrib import admin
from shop.models import CartItem, Category, Product, ProductImage
from unfold.admin import ModelAdmin


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = (
        "title",
        "parent",
        "description",
        "image",
    )
    fields = list_display
    search_fields = list_display + ("id",)
    list_filter = ("parent",)
    list_filter_submit = True


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        "title",
        "category",
        "description",
        "real_price",
    )
    fields = (
        "title",
        "category",
        "description",
        "price",
        "quantity",
        "discount_percentage",
    )
    search_fields = fields + ("id",)
    list_filter = ("category",)
    list_filter_submit = True


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = (
        "product",
        "image",
    )
    fields = list_display
    search_fields = list_display + ("id",)


@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = (
        "user",
        "product",
        "count",
        "total_price",
    )
    fields = (
        "user",
        "product",
        "count",
    )
    search_fields = fields + ("id",)
