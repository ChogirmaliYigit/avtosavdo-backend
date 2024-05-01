from django.db import transaction
from django.db.models import ExpressionWrapper, F, FloatField, Sum
from rest_framework import exceptions, serializers
from shop.models import CartItem, Category, Order, OrderProduct, Product, ProductImage


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
        data["category_id"] = instance.category.pk
        data["images"] = ProductImagesListSerializer(
            instance.images.all(), many=True, context=self.context
        ).data
        return data

    def get_real_price(self, product):
        return product.real_price

    class Meta:
        model = Product
        fields = (
            "category_id",
            "id",
            "title",
            "price",
            "discount_percentage",
            "real_price",
        )


class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product"] = ProductsListSerializer(
            instance.product, context=self.context
        ).data
        return data

    def get_total_price(self, cart_item):
        return cart_item.price

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
        fields = ("count",)


class OrderListSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )

    def create(self, validated_data):
        request = self.context.get("request")
        cart_items = request.user.user_cart_items.all()
        if cart_items:
            total_price = (
                cart_items.aggregate(
                    total_price=Sum(
                        ExpressionWrapper(
                            F("product__price")
                            - (
                                F("product__price")
                                * F("product__discount_percentage")
                                / 100
                            ),
                            output_field=FloatField(),
                        )
                        * F("count")
                    )
                )["total_price"]
                or 0
            )
            order_data = {
                "user": request.user,
                "total_price": total_price,
                "status": Order.IN_PROCESSING,
                "paid": False,
                "delivery_type": validated_data.get("delivery_type", Order.PICKUP),
                "note": validated_data.get("note", ""),
            }

            with transaction.atomic():
                order = Order.objects.create(**order_data)
                order_products = []
                for cart_item in cart_items:
                    order_products.append(
                        OrderProduct(
                            order=order,
                            product=cart_item.product,
                            count=cart_item.count,
                        )
                    )
                OrderProduct.objects.bulk_create(order_products)

                cart_items.delete()

            return order
        raise exceptions.ValidationError(
            {
                "detail": "Savatchangiz bo'sh. Buyurtma berish uchun oldin mahsulotlarni savatchangizga qo'shing!"
            }
        )

    class Meta:
        model = Order
        fields = (
            "id",
            "total_price",
            "status",
            "paid",
            "delivery_type",
            "note",
        )
