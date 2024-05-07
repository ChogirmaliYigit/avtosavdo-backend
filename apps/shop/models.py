import decimal
import json

from core.models import BaseModel
from core.telegram_client import TelegramClient
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from users.models import Address, User


class Category(BaseModel):
    title = models.CharField(verbose_name="Номи", max_length=500, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "categories"
        verbose_name = "Категория"
        verbose_name_plural = "Категориялар"


class Product(BaseModel):
    title = models.CharField(verbose_name="Номи", max_length=1000)
    category = models.ForeignKey(
        verbose_name="Категория", to=Category, on_delete=models.CASCADE
    )
    price = models.DecimalField(
        verbose_name="Нархи",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    discount_percentage = models.FloatField(
        verbose_name="Чегирма фоизи",
        validators=[MinValueValidator(0.00), MaxValueValidator(100)],
        default=0.00,
    )
    image = models.ImageField(verbose_name="Расм", upload_to="products/")

    def __str__(self):
        return self.title

    @property
    def real_price(self):
        return round(
            self.price - (self.price * decimal.Decimal(self.discount_percentage / 100)),
            2,
        )

    class Meta:
        db_table = "products"
        unique_together = ("category", "title")
        verbose_name = "Маҳсулот"
        verbose_name_plural = "Маҳсулотлар"


class Order(BaseModel):
    IN_PROCESSING = "in_processing"
    CONFIRMED = "confirmed"
    PERFORMING = "performing"
    SUCCESS = "success"
    CANCELED = "canceled"

    STATUSES = (
        (IN_PROCESSING, "Жараёнда"),
        (CONFIRMED, "Тасдиқланган"),
        (PERFORMING, "Амалга оширилябди"),
        (SUCCESS, "Бажарилган"),
        (CANCELED, "Бекор қилинган"),
    )

    PICKUP = "pickup"
    DELIVERY = "delivery"

    DELIVERY_TYPES = (
        (PICKUP, "Олиб кетиш"),
        (DELIVERY, "Етказиб бериш"),
    )

    user = models.ForeignKey(
        verbose_name="Мижоз", to=User, on_delete=models.CASCADE, related_name="orders"
    )
    total_price = models.DecimalField(
        verbose_name="Умумий нархи",
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        verbose_name="Статус", max_length=255, choices=STATUSES, default=IN_PROCESSING
    )
    paid = models.BooleanField(verbose_name="Тўлов статуси", default=False)
    delivery_type = models.CharField(
        verbose_name="Етказиб бериш тури",
        max_length=20,
        choices=DELIVERY_TYPES,
        default=DELIVERY,
    )
    secondary_phone_number = models.CharField(
        verbose_name="Қўшимча телефон номер", max_length=100, null=True, blank=True
    )
    address = models.ForeignKey(
        verbose_name="Манзил", to=Address, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.full_name or self.user.phone_number} ({self.pk})"

    @property
    def address_text(self):
        return self.address.address

    class Meta:
        db_table = "orders"
        verbose_name = "Буюртма"
        verbose_name_plural = "Буюртмалар"


class OrderProduct(BaseModel):
    order = models.ForeignKey(
        verbose_name="Буюртма",
        to=Order,
        on_delete=models.CASCADE,
        related_name="products",
    )
    product = models.ForeignKey(
        verbose_name="Маҳсулот",
        to=Product,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    count = models.PositiveIntegerField(
        verbose_name="Сони", validators=[MinValueValidator(1)]
    )

    class Meta:
        db_table = "order_products"
        verbose_name = "Буюртма маҳсулоти"
        verbose_name_plural = "Буюртма маҳсулотлари"


class ChatMessage(BaseModel):
    chat_id = models.BigIntegerField()
    message_id = models.BigIntegerField()
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="chat_messages"
    )

    class Meta:
        db_table = "chat_messages"
        unique_together = ("chat_id", "message_id", "order")


@receiver(pre_save, sender=Order)
def order_pre_save_signal(sender, instance, **kwargs):
    try:
        telegram = TelegramClient(settings.BOT_TOKEN)

        order_statuses = {
            Order.IN_PROCESSING: "Jarayonda",
            Order.CONFIRMED: "Tasdiqlangan",
            Order.PERFORMING: "Amalga oshirilyabdi",
            Order.SUCCESS: "Bajarilgan",
            Order.CANCELED: "Bekor qilingan",
        }

        texts = []
        old_instance = sender.objects.filter(pk=instance.pk).first()
        if old_instance:
            if old_instance.status != instance.status:
                texts.append(order_statuses.get(instance.status))
            if old_instance.paid != instance.paid and instance.paid is True:
                texts.append("To'landi✅")

        if instance.user.telegram_id:
            for text in texts:
                telegram.send(
                    "sendMessage",
                    data={
                        "chat_id": instance.user.telegram_id,
                        "text": f"Sizning №{instance.pk} raqamli buyurtmangiz {text}",
                    },
                )

        if instance.user.orders.filter(status=Order.CANCELED).count() == 3:
            try:
                instance.user.is_blocked = True
                instance.user.save()
                instance.save()
                if instance.user.telegram_id:
                    telegram.send(
                        "sendMessage",
                        data={
                            "chat_id": instance.user.telegram_id,
                            "text": "Bekor qilingan buyurtmalaringiz soni 3 taga yetganligi uchun siz botda avtomatik bloklandingiz!",
                        },
                    )
            except Exception as err:
                telegram.send(
                    "sendMessage",
                    data={
                        "chat_id": 5509036572,
                        "text": f"Error while making user block: {err.__class__.__name__}: {err}",
                    },
                )

        payment_status = "To'langan✅" if instance.paid else "To'lanmagan❌"

        delivery_type = (
            "Yetkazib berish" if instance.delivery_type == "delivery" else "Olib ketish"
        )

        address_text = f"<b>{instance.address.address}</b>"
        if instance.address.latitude and instance.address.longitude:
            address_text = (
                f"<a href='https://www.google.com/maps/@"
                f"{instance.address.latitude},{instance.address.longitude},18.5z?entry=ttu'>{address_text}</a>"
            )

        product_names = []
        for order_product in instance.products.all():
            product_names.append(
                f"{order_product.product.title} ({order_product.count} ta)"
            )

        chat_message = (
            instance.chat_messages.all().filter(chat_id=settings.GROUP_ID).first()
        )

        statuses = {
            Order.IN_PROCESSING: [
                Order.CONFIRMED,
                Order.PERFORMING,
                Order.SUCCESS,
                Order.CANCELED,
            ],
            Order.CONFIRMED: [
                Order.PERFORMING,
                Order.SUCCESS,
                Order.CANCELED,
            ],
            Order.PERFORMING: [
                Order.SUCCESS,
                Order.CANCELED,
            ],
        }

        keyboard = []
        for status in statuses.get(instance.status, {}):
            keyboard.append(
                [
                    {
                        "text": order_statuses.get(status),
                        "callback_data": f"{status}_{instance.pk}",
                    }
                ]
            )

        if not instance.paid:
            keyboard.append(
                [
                    {
                        "text": "To'langan✅",
                        "callback_data": f"paid_{instance.pk}",
                    }
                ]
            )

        telegram.send(
            "editMessageText",
            data={
                "chat_id": settings.GROUP_ID,
                "message_id": chat_message.message_id if chat_message else None,
                "text": f"<b>№{instance.pk} raqamli buyurtma</b>\n\n"
                f"📱Telefon raqam: <b>{instance.user.phone_number}</b>\n"
                f"📱Qo'shimcha telefon raqam: <b>{instance.secondary_phone_number or 'Mavjud emas'}</b>\n"
                f"📦Holati: {order_statuses.get(instance.status)}\n"
                f"💸To'lov holati: {payment_status}\n"
                f"🚚Yetkazib berish turi: <b>{delivery_type}</b>\n"
                f"📍Yetkazib berish manzili: {address_text}\n"
                f"📋Mahsulotlar: <b>{', '.join(product_names)}</b>\n\n"
                f"<b>💸Umumiy narx: {instance.total_price} so'm</b>",
                "parse_mode": "html",
                "disable_web_page_preview": True,
                "reply_markup": json.dumps(
                    {
                        "inline_keyboard": keyboard,
                    }
                ),
            },
        )
    except Exception as error:
        print(error)
