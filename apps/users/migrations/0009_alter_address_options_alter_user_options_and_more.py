# Generated by Django 5.0.4 on 2024-05-04 09:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0008_alter_address_latitude_alter_address_longitude_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="address",
            options={"verbose_name": "Манзил", "verbose_name_plural": "Манзиллар"},
        ),
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "Мижоз", "verbose_name_plural": "Мижозлар"},
        ),
        migrations.RemoveField(
            model_name="user",
            name="username",
        ),
        migrations.AlterField(
            model_name="address",
            name="address",
            field=models.TextField(blank=True, null=True, verbose_name="Манзил"),
        ),
        migrations.AlterField(
            model_name="address",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Сана"),
        ),
        migrations.AlterField(
            model_name="address",
            name="latitude",
            field=models.FloatField(blank=True, null=True, verbose_name="Кенглик"),
        ),
        migrations.AlterField(
            model_name="address",
            name="longitude",
            field=models.FloatField(blank=True, null=True, verbose_name="Узунлик"),
        ),
        migrations.AlterField(
            model_name="address",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="addresses",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Мижоз",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Сана"),
        ),
        migrations.RemoveField(
            model_name="user",
            name="full_name",
        ),
        migrations.AlterField(
            model_name="user",
            name="is_blocked",
            field=models.BooleanField(default=False, verbose_name="Блоклаш"),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_staff",
            field=models.BooleanField(default=False, verbose_name="Админ қилиш"),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="Телефон номер"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="telegram_id",
            field=models.BigIntegerField(
                blank=True, null=True, verbose_name="Телеграм ID"
            ),
        ),
    ]
