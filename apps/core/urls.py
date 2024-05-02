from django.urls import path

from apps.core.views import webhook

urlpatterns = [
    path("<str:bot_token>", webhook),
]
