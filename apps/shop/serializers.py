import decimal

from rest_framework import serializers
from shop.models import Category, Product, ProductImage, CartItem


class CategoryListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, category):
        request = self.context.get("request")
        if category.image and request:
            return request.build_absolute_uri(category.image.url)
        return None

    class Meta:
        model = Category
        fields = (
            "id",
            "title",
            "description",
            "parent",
            "image",
        )


class ProductImagesListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, product_image):
        request = self.context.get("request")
        if product_image.image and request:
            return request.build_absolute_uri(product_image.image.url)
        return None

    class Meta:
        model = ProductImage
        fields = ("image",)


class ProductsListSerializer(serializers.ModelSerializer):
    real_price = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category"] = CategoryListSerializer(instance=instance.category, context=self.context).data
        data["images"] = ProductImagesListSerializer(instance.images.all(), many=True, context=self.context).data
        return data

    def get_real_price(self, product):
        return product.real_price

    class Meta:
        model = Product
        fields = (
            "category",
            "id",
            "title",
            "description",
            "price",
            "discount_percentage",
            "real_price",
            "quantity",
        )


class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product"] = ProductsListSerializer(instance.product, context=self.context).data
        return data

    def get_total_price(self, cart_item):
        return cart_item.total_price

    def create(self, validated_data):
        request = self.context.get("request")
        cart_item = CartItem.objects.filter(
            user=request.user,
            product=validated_data.get("product"),
        ).first()
        if cart_item:
            cart_item.count += validated_data.get("count")
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                user=request.user,
                product=validated_data.get("product"),
                count=validated_data.get("count"),
            )
        return cart_item

    class Meta:
        model = CartItem
        fields = (
            "product",
            "count",
            "total_price",
        )


class CartItemDetailSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(required=False)

    def update(self, instance, validated_data):
        count = validated_data.get("count", 0)
        if count > 0:
            instance.count += count
            instance.save()
        return instance

    class Meta:
        model = CartItem
        fields = (
            "count",
        )
