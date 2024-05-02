from rest_framework import serializers
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

    def validate(self, data):
        orders = self.context.get("orders", [])
        if not orders:
            raise serializers.ValidationError({"orders": "This field is required."})
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        orders = self.context.get("orders")

        total_price = 0
        product_ids = {item["product"] for item in orders}
        products = Product.objects.filter(id__in=product_ids)
        price_mapping = {product.id: product.real_price for product in products}

        order_product_objects = []
        for item in orders:
            product_id = item["product"]
            count = item["count"]

            if product_id in price_mapping:
                total_price += price_mapping[product_id] * count
            else:
                print(f"Price for product {product_id} not found.")

            order_product_objects.append(
                OrderProduct(
                    product_id=product_id,
                    count=count,
                    order=None,
                )
            )

        if validated_data.get("full_name"):
            request.user.full_name = validated_data.get("full_name")
            request.user.save()

        order_data = {
            "user": request.user,
            "total_price": total_price,
            "status": Order.IN_PROCESSING,
            "paid": False,
            "delivery_type": validated_data.get("delivery_type", Order.PICKUP),
            "note": validated_data.get("note", ""),
            "secondary_phone_number": validated_data.get("secondary_phone_number"),
            "address": validated_data.get("address"),
        }

        order = Order.objects.create(**order_data)
        # Set the order attribute for each OrderProduct object
        for order_product in order_product_objects:
            order_product.order = order

        # Bulk creates the OrderProduct objects
        OrderProduct.objects.bulk_create(order_product_objects)
        return order

    class Meta:
        model = Order
        fields = (
            "id",
            "total_price",
            "status",
            "paid",
            "delivery_type",
            "note",
            "secondary_phone_number",
            "address",
        )
