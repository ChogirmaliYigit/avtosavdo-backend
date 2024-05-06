from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.core.models import BaseModel
from apps.users.queryset.user import UserManager


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(
        verbose_name="Тўлиқ исми", max_length=200, null=True, blank=True
    )
    phone_number = models.CharField(
        verbose_name="Телефон номер", max_length=100, unique=True
    )
    telegram_id = models.BigIntegerField(
        verbose_name="Телеграм ID", null=True, blank=True
    )

    is_staff = models.BooleanField(verbose_name="Админ қилиш", default=False)
    is_blocked = models.BooleanField(verbose_name="Блоклаш", default=False)

    USERNAME_FIELD = "phone_number"

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name or ''} ({self.phone_number})".strip()

    class Meta:
        db_table = "users"
        verbose_name = "Мижоз"
        verbose_name_plural = "Мижозлар"


class Address(BaseModel):
    user = models.ForeignKey(
        verbose_name="Мижоз",
        to=User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    address = models.TextField(verbose_name="Манзил", null=True, blank=True)
    latitude = models.FloatField(verbose_name="Кенглик", null=True, blank=True)
    longitude = models.FloatField(verbose_name="Узунлик", null=True, blank=True)

    class Meta:
        db_table = "addresses"
        verbose_name = "Манзил"
        verbose_name_plural = "Манзиллар"
