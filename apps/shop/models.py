import decimal

from core.models import BaseModel
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
        if instance.user.orders.filter(status=Order.CANCELED).count() == 3:
            try:
                instance.user.is_blocked = True
                instance.user.save()
            except Exception as err:
                print(f"Error while making user block: {err.__class__.__name__}: {err}")
    except Exception as error:
        print(error)
