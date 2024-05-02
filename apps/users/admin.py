from django.contrib import admin
from unfold.admin import ModelAdmin
from users.models import Address, User


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        "phone_number",
        "full_name",
        "is_blocked",
        "is_staff",
    )
    list_filter = (
        "is_blocked",
        "is_staff",
    )
    fields = (
        "phone_number",
        "full_name",
        "username",
        "telegram_id",
        "is_blocked",
        "is_staff",
    )
    search_fields = (
        "full_name",
        "id",
        "telegram_id",
        "phone_number",
    )

    list_filter_submit = True


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    list_display = (
        "user",
        "address",
        "latitude",
        "longitude",
    )
    fields = list_display
    search_fields = list_display + ("id",)
    list_filter = ("user",)
    list_filter_submit = True
