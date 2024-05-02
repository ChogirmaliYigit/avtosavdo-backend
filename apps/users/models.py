from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.core.models import BaseModel
from apps.users.queryset.user import UserManager


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=1000, null=True, blank=True)
    phone_number = models.CharField(max_length=100, unique=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"

    objects = UserManager()

    class Meta:
        db_table = "users"


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "addresses"
