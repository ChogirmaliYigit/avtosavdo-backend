from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from apps.core.queryset.base import BaseManager


class UserManager(BaseUserManager, BaseManager):
    """
    Custom user model manager where phone_number is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, phone_number, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not phone_number:
            raise ValueError(_("The phone number must be set"))
        user = self.filter(phone_number=phone_number).first()
        if not user:
            user = self.model(phone_number=phone_number, **extra_fields)
            user.set_password(password)
            user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        """
        Create and save a superuser with the given phone_number and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_blocked", False)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phone_number, password, **extra_fields)

    def filter(self, *args, **kwargs):
        queryset = super().filter(*args, **kwargs)
        phone_number = kwargs.get("phone_number", "")
        if phone_number and not phone_number.startswith("+"):
            queryset_ = queryset.filter(phone_number=f"+{phone_number}")
            if not queryset_:
                queryset = queryset.filter(phone_number=phone_number)
        queryset = queryset.filter(is_blocked__in=[True, False])
        return queryset
