# Generated by Django 5.0.4 on 2024-05-04 09:53

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0011_remove_category_image"),
        ("users", "0009_alter_address_options_alter_user_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="productimage",
            name="product",
        ),
        migrations.AlterModelOptions(
            name="category",
            options={
                "verbose_name": "Категория",
                "verbose_name_plural": "Категориялар",
            },
        ),
        migrations.AlterModelOptions(
            name="order",
            options={"verbose_name": "Буюртма", "verbose_name_plural": "Буюртмалар"},
        ),
        migrations.AlterModelOptions(
            name="orderproduct",
            options={
                "verbose_name": "Буюртма маҳсулоти",
                "verbose_name_plural": "Буюртма маҳсулотлари",
            },
        ),
        migrations.AlterModelOptions(
            name="product",
            options={"verbose_name": "Маҳсулот", "verbose_name_plural": "Маҳсулотлар"},
        ),
        migrations.RemoveField(
            model_name="category",
            name="parent",
        ),
        migrations.RemoveField(
            model_name="order",
            name="note",
        ),
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(upload_to="products/", verbose_name="Расм"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="category",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Сана"),
        ),
        migrations.AlterField(
            model_name="category",
            name="title",
            field=models.CharField(max_length=500, unique=True, verbose_name="Номи"),
        ),
        migrations.AlterField(
            model_name="order",
            name="address",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="users.address",
                verbose_name="Манзил",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Сана"),
        ),
        migrations.AlterField(
            model_name="order",
            name="delivery_type",
            field=models.CharField(
                choices=[("pickup", "Олиб кетиш"), ("delivery", "Етказиб бериш")],
                max_length=20,
                verbose_name="Етказиб бериш тури",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="paid",
            field=models.BooleanField(default=False, verbose_name="Тўлов статуси"),
        ),
        migrations.AlterField(
            model_name="order",
            name="secondary_phone_number",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="Қўшимча телефон номер",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("in_processing", "Жараёнда"),
                    ("confirmed", "Тасдиқланган"),
                    ("performing", "Амалга оширилябди"),
                    ("success", "Бажарилган"),
                    ("canceled", "Бекор қилинган"),
                ],
                default="in_processing",
                max_length=255,
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="total_price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=15,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Умумий нархи",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Мижоз",
            ),
        ),
        migrations.AlterField(
            model_name="orderproduct",
            name="count",
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Сони",
            ),
        ),
        migrations.AlterField(
            model_name="orderproduct",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Сана"),
        ),
        migrations.AlterField(
            model_name="orderproduct",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="shop.order",
                verbose_name="Буюртма",
            ),
        ),
        migrations.AlterField(
            model_name="orderproduct",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="shop.product",
                verbose_name="Маҳсулот",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="shop.category",
                verbose_name="Категория",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Сана"),
        ),
        migrations.AlterField(
            model_name="product",
            name="discount_percentage",
            field=models.FloatField(
                default=0.0,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name="Чегирма фоизи",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Нархи",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="title",
            field=models.CharField(max_length=1000, verbose_name="Номи"),
        ),
        migrations.DeleteModel(
            name="CartItem",
        ),
        migrations.DeleteModel(
            name="ProductImage",
        ),
    ]
