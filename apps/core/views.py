import json

from core.utils import (
    send_post,
    set_location,
    set_phone_number,
    start,
    update_order_data,
)
from django.conf import settings
from rest_framework import permissions, response, views


def router(request_body, token):
    """Parse telegram request and route to handlers (controllers)"""
    data = json.loads(request_body)
    message = data.get("message", {})
    message_chat = message.get("chat", {})
    call_chat = data.get("callback_query", {}).get("message", {}).get("chat", {})
    if message_chat.get("type", "") == "private":
        if message.get("text") == "/start":
            start(data, token)
        elif (
            message.get("text", None)
            and message.get("from", {}).get("id") in settings.ADMINS
        ):
            send_post(data, token)
        elif message.get("contact", None) or message.get("text", None):
            set_phone_number(data, token)
        elif message.get("location"):
            set_location(data, token)
    elif call_chat.get("type", "") in ["group", "supergroup"]:
        update_order_data(data, token)


class TelegramWebhookView(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, bot_token):
        """Run router and return success response"""
        try:
            router(request.body.decode("utf-8"), bot_token)
        except Exception as error:
            print("JSON error:", error)

        return response.Response({"ok": True})
