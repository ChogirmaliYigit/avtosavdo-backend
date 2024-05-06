from core.telegram_client import TelegramClient
from django.conf import settings
from rest_framework import serializers
from shop.models import Category, Order, OrderProduct, Product


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "title",
        )


class ProductsListSerializer(serializers.ModelSerializer):
    real_price = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category_id"] = instance.category.pk
        data["image"] = self.get_product_image(instance)
        return data

    def get_product_image(self, instance):
        request = self.context.get("request")
        if instance.image and request:
            return request.build_absolute_uri(instance.image.url)
        return None

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
            "image",
        )


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
            "delivery_type": validated_data.get("delivery_type", Order.DELIVERY),
            "secondary_phone_number": validated_data.get("secondary_phone_number"),
            "address": validated_data.get("address"),
        }

        order = Order.objects.create(**order_data)

        product_names = []

        # Set the order attribute for each OrderProduct object
        for order_product in order_product_objects:
            order_product.order = order
            product_names.append(
                f"{order_product.product.title} ({order_product.count} ta)"
            )

        # Bulk creates the OrderProduct objects
        OrderProduct.objects.bulk_create(order_product_objects)

        telegram = TelegramClient(settings.BOT_TOKEN)
        telegram.send(
            "sendMessage",
            data={
                "chat_id": request.user.telegram_id,
                "text": f"№{order.pk} raqamli buyurtmangiz qabul qilindi🥳\n\nTez orada siz bilan bog'lanamiz😊",
            },
        )

        order_statuses = {
            "in_processing": "Jarayonda",
            "confirmed": "Tasdiqlangan",
            "performing": "Amalga oshirilyabdi",
            "success": "Bajarilgan",
            "canceled": "Bekor qilingan",
        }

        payment_status = "To'langan✅" if order.paid else "To'lanmagan❌"

        delivery_type = (
            "Yetkazib berish" if order.delivery_type == "delivery" else "Olib ketish"
        )

        telegram.send(
            "sendMessage",
            data={
                "chat_id": settings.GROUP_ID,
                "text": f"<b>№{order.pk} raqamli buyurtma</b>\n\n"
                f"📱Telefon raqam: <b>{request.user.phone_number}</b>\n"
                f"📦Holati: {order_statuses.get(order.status)}\n"
                f"💸To'lov holati: {payment_status}\n"
                f"🚚Yetkazib berish turi: <b>{delivery_type}</b>\n"
                f"📍Yetkazib berish manzili: <a href='https://www.google.com/maps/@{order.address.latitude},{order.address.longitude},18.5z?entry=ttu'><b>{order.address.address}</b></a>\n"
                f"📋Mahsulotlar: <b>{', '.join(product_names)}</b>\n\n"
                f"<b>💸Umumiy narx: {order.total_price} so'm</b>",
                "parse_mode": "html",
                "disable_web_page_preview": True,
            },
        )
        return order

    class Meta:
        model = Order
        fields = (
            "id",
            "total_price",
            "status",
            "paid",
            "delivery_type",
            "secondary_phone_number",
            "address",
        )
