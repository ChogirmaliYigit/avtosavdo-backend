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
    external_id = models.CharField(max_length=500, null=True, blank=True)

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
    external_id = models.CharField(max_length=500, null=True, blank=True)

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
        (SUCCESS, "Етказиб берилган"),
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
            Order.SUCCESS: "Yetkazib berilgan",
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

            reply_markup = json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Menu",
                                "web_app": {
                                    "url": settings.WEB_APP_URL,
                                },
                            }
                        ]
                    ]
                }
            )

            data = {
                "chat_id": instance.user.telegram_id,
                "reply_markup": reply_markup,
            }
            if hasattr(settings, "IMAGE_FILE_ID"):
                data["photo"] = settings.IMAGE_FILE_ID
                data[
                    "caption"
                ] = "Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊"
                method = "sendPhoto"
            else:
                method = "sendMessage"
                data[
                    "text"
                ] = "Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊"

            res = telegram.send(
                method,
                data=data,
            )

            if (
                not res.get("ok")
                and res.get("description")
                == "Bad Request: wrong file identifier/HTTP URL specified"
            ):
                telegram.send(
                    "sendMessage",
                    data={
                        "chat_id": instance.user.telegram_id,
                        "text": "Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊",
                        "reply_markup": reply_markup,
                    },
                )

        if instance.user.orders.filter(status=Order.CANCELED).count() == 3:
            try:
                instance.user.is_blocked = True
                instance.user.save()
            except Exception as err:
                telegram.send(
                    "sendMessage",
                    data={
                        "chat_id": 5509036572,
                        "text": f"Error while making user block: {err.__class__.__name__}: {err}",
                    },
                )
    except Exception as error:
        print(error)
