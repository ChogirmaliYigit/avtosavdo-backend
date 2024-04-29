from django.contrib import admin
from unfold.admin import ModelAdmin
from users.models import BlockedUser, CustomToken, User


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        "phone_number",
        "full_name",
        "username",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "is_active",
        "is_staff",
    )
    fields = (
        "phone_number",
        "full_name",
        "username",
        "telegram_id",
        "latitude",
        "longitude",
        "is_active",
        "is_staff",
    )
    search_fields = (
        "full_name",
        "username",
        "id",
        "telegram_id",
        "phone_number",
    )

    list_filter_submit = True


@admin.register(CustomToken)
class CustomTokenAdmin(ModelAdmin):
    list_display = (
        "key",
        "user",
        "created",
        "expires_at",
    )
    fields = (
        "key",
        "user",
        "expires_at",
    )
    search_fields = list_display


@admin.register(BlockedUser)
class BlockedUserAdmin(ModelAdmin):
    list_display = (
        "phone_number",
        "full_name",
        "username",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "is_active",
        "is_staff",
    )
    fields = (
        "phone_number",
        "full_name",
        "username",
        "telegram_id",
        "latitude",
        "longitude",
        "is_active",
        "is_staff",
    )
    search_fields = (
        "full_name",
        "username",
        "id",
        "telegram_id",
        "phone_number",
    )

    list_filter_submit = True
