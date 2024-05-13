from django.contrib import admin
from unfold.admin import ModelAdmin
from users.models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        "phone_number",
        "full_name",
        "display_is_blocked",
    )
    list_filter = ("is_blocked",)
    fields = (
        "phone_number",
        "full_name",
        "telegram_id",
        "is_blocked",
    )
    search_fields = (
        "full_name",
        "id",
        "telegram_id",
        "phone_number",
    )

    list_filter_submit = True

    def display_is_blocked(self, obj):
        return obj.is_blocked

    display_is_blocked.boolean = True
    display_is_blocked.short_description = "Блокланганми"
