import decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from users.models import User


class Category(BaseModel):
    title = models.CharField(max_length=500, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="categories/")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="sub_categories", null=True, blank=True,
    )

    def __str__(self): return self.title

    class Meta:
        db_table = "categories"


class Product(BaseModel):
    title = models.CharField(max_length=1000)
    description = models.TextField(null=True,  blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    discount_percentage = models.FloatField(validators=[MinValueValidator(0.00), MaxValueValidator(100)])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    def __str__(self): return self.title

    @property
    def real_price(self):
        return round(self.price - (self.price * decimal.Decimal(self.discount_percentage / 100)), 2)

    class Meta:
        db_table = "products"
        unique_together = ("category", "title")


class ProductImage(BaseModel):
    image = models.ImageField(upload_to="products/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

    def __str__(self): return f"{self.product.title} ({self.pk})"

    class Meta:
        db_table = "product_images"


class CartItem(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="on_cart")
    count = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    @property
    def total_price(self):
        return decimal.Decimal(self.count) * self.product.real_price

    class Meta:
        db_table = "cart_items"
