from django.urls import path

from apps.core.views import TelegramWebhookView

urlpatterns = [
    path("<str:bot_token>", TelegramWebhookView.as_view(), name="telegram-webhook"),
]
