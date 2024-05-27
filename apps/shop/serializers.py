import decimal
import json

from core.telegram_client import TelegramClient
from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from shop.models import Category, ChatMessage, Order, OrderProduct, Product
from users.models import Address


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
    address = serializers.CharField(required=True)

    def validate(self, data):
        orders = self.context.get("orders", [])
        if not orders:
            raise serializers.ValidationError({"orders": "This field is required."})
        return data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        orders = self.context.get("orders")

        product_ids = [item["product"] for item in orders]
        products = Product.objects.filter(id__in=product_ids).values(
            "id", "price", "title", "discount_percentage"
        )
        price_mapping = {
            product["id"]: round(
                product["price"]
                - (
                    product["price"]
                    * decimal.Decimal(product["discount_percentage"] / 100)
                ),
                2,
            )
            for product in products
        }
        title_mapping = {product["id"]: product["title"] for product in products}

        order_product_objects = []
        total_price = sum(
            price_mapping[item["product"]] * item["count"] for item in orders
        )

        for item in orders:
            order_product_objects.append(
                OrderProduct(product_id=item["product"], count=item["count"])
            )

        # Update user full name if provided
        if "full_name" in validated_data:
            request.user.full_name = validated_data["full_name"]
            request.user.save()

        # Retrieve or create address
        address_data = {
            "user": request.user,
            "address": validated_data["address"],
        }
        address, created = Address.objects.get_or_create(**address_data)

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status=Order.IN_PROCESSING,
            paid=False,
            delivery_type=validated_data.get("delivery_type", Order.DELIVERY),
            secondary_phone_number=validated_data.get("secondary_phone_number"),
            address=address,
        )

        # Associate order with OrderProduct objects and bulk create
        for order_product in order_product_objects:
            order_product.order = order
        OrderProduct.objects.bulk_create(order_product_objects)

        product_names = [
            f"{title_mapping[order_product.product_id]} ({order_product.count} ta)"
            for order_product in order_product_objects
        ]

        # Prepare and send Telegram message
        telegram = TelegramClient(settings.BOT_TOKEN)
        order_statuses = {
            Order.IN_PROCESSING: "Jarayonda",
            Order.CONFIRMED: "Tasdiqlangan",
            Order.PERFORMING: "Amalga oshirilyabdi",
            Order.SUCCESS: "Yetkazib berilgan",
            Order.CANCELED: "Bekor qilingan",
        }

        payment_status = "To'langan✅" if order.paid else "To'lanmagan❌"
        delivery_type = (
            "Yetkazib berish"
            if order.delivery_type == Order.DELIVERY
            else "Olib ketish"
        )
        address_text = f"<b>{order.address.address}</b>"
        if order.address.latitude and order.address.longitude:
            address_text = (
                f"<a href='https://www.google.com/maps/@{order.address.latitude},"
                f"{order.address.longitude},18.5z?entry=ttu'>{address_text}</a>"
            )

        statuses = {
            Order.IN_PROCESSING: [
                Order.CONFIRMED,
                Order.PERFORMING,
                Order.SUCCESS,
                Order.CANCELED,
            ],
            Order.CONFIRMED: [Order.PERFORMING, Order.SUCCESS, Order.CANCELED],
            Order.PERFORMING: [Order.SUCCESS, Order.CANCELED],
        }

        keyboard = [
            [{"text": order_statuses[status], "callback_data": f"{status}_{order.pk}"}]
            for status in statuses.get(order.status, [])
        ]

        if not order.paid:
            keyboard.append(
                [{"text": "To'langan✅", "callback_data": f"paid_{order.pk}"}]
            )

        response = telegram.send(
            "sendMessage",
            data={
                "chat_id": settings.GROUP_ID,
                "text": (
                    f"<b>№{order.pk} raqamli buyurtma</b>\n\n"
                    f"📱Telefon raqam: <b>{request.user.phone_number}</b>\n"
                    f"📱Qo'shimcha telefon raqam: <b>{order.secondary_phone_number or 'Mavjud emas'}</b>\n"
                    f"📦Holati: {order_statuses.get(order.status)}\n"
                    f"💸To'lov holati: {payment_status}\n"
                    f"🚚Yetkazib berish turi: <b>{delivery_type}</b>\n"
                    f"📍Yetkazib berish manzili: {address_text}\n"
                    f"📋Mahsulotlar: <b>{', '.join(product_names)}</b>\n\n"
                    f"<b>💸Umumiy narx: {order.total_price} so'm</b>"
                ),
                "parse_mode": "html",
                "disable_web_page_preview": True,
                "reply_markup": json.dumps({"inline_keyboard": keyboard}),
            },
        )

        result = response.get("result", {})
        try:
            ChatMessage.objects.create(
                chat_id=settings.GROUP_ID,
                message_id=result.get("message_id"),
                order=order,
            )
        except Exception as err:
            print(
                f"Error while creating ChatMessage object: {err.__class__.__name__} {err}"
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


class OrderDetailSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    def get_phone_number(self, order):
        return order.user.phone_number

    def get_address(self, order):
        return {
            "address": order.address.address,
            "latitude": order.address.latitude,
            "longitude": order.address.longitude,
        }

    def get_products(self, order):
        return [
            {"title": product.title, "count": product.count}
            for product in order.products.all()
        ]

    class Meta:
        model = Order
        fields = (
            "id",
            "phone_number",
            "secondary_phone_number",
            "status",
            "paid",
            "delivery_type",
            "address",
            "products",
            "total_price",
        )
