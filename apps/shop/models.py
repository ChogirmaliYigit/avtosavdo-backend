import decimal

from core.models import BaseModel
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User


class Category(BaseModel):
    title = models.CharField(max_length=500, unique=True)
    image = models.ImageField(upload_to="categories/")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="sub_categories",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = "categories"


class Product(BaseModel):
    title = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    discount_percentage = models.FloatField(
        validators=[MinValueValidator(0.00), MaxValueValidator(100)]
    )

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


class ProductImage(BaseModel):
    image = models.ImageField(upload_to="products/")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )

    def __str__(self):
        return f"{self.product.title} ({self.pk})"

    class Meta:
        db_table = "product_images"


class CartItem(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_cart_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="on_cart"
    )
    count = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    @property
    def price(self):
        return decimal.Decimal(self.count) * self.product.real_price

    class Meta:
        db_table = "cart_items"


class Order(BaseModel):
    IN_PROCESSING = "in_processing"
    CONFIRMED = "confirmed"
    PERFORMING = "performing"
    SUCCESS = "success"
    CANCELED = "canceled"
    PAYMENT_CANCELED = "payment_canceled"
    DELETED = "deleted"
    REFUNDED = "refunded"

    STATUSES = (
        (IN_PROCESSING, "Jarayonda"),
        (CONFIRMED, "Tasdiqlangan"),
        (PERFORMING, "Amalga oshirilyabdi"),
        (SUCCESS, "Bajarilgan"),
        (CANCELED, "Bekor qilingan"),
        (PAYMENT_CANCELED, "To'lov bekor qilingan"),
        (REFUNDED, "Qaytarilgan"),
    )

    PICKUP = "pickup"
    DELIVERY = "delivery"

    DELIVERY_TYPES = (
        (PICKUP, "Olib ketish"),
        (DELIVERY, "Yetkazib berish"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=255, choices=STATUSES, default=IN_PROCESSING)
    paid = models.BooleanField(default=False)
    note = models.CharField(max_length=255, null=True, blank=True)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES)

    def __str__(self):
        return f"{self.user.full_name or self.user.phone_number} ({self.pk})"

    class Meta:
        db_table = "orders"


class OrderProduct(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="orders"
    )
    count = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = "order_products"


@receiver(post_save, sender=Order)
def move_user_to_blocked(sender, instance=None, created=False, **kwargs):
    if not created and instance.user.orders.filter(status=Order.CANCELED).count() == 3:
        try:
            instance.user.is_blocked = True
            instance.save()
        except Exception as err:
            print("Error while making user `is_blocked`:", err)
