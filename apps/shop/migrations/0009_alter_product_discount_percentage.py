# Generated by Django 5.0.4 on 2024-05-02 14:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0008_order_address_order_secondary_phone_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="discount_percentage",
            field=models.FloatField(
                default=0.0,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(100),
                ],
            ),
        ),
    ]
