import json

from core.utils import set_location, set_phone_number, start
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def router(request_body, token):
    """Parse telegram request and route to handlers (controllers)"""
    data = json.loads(request_body)
    message = data.get("message", {})
    chat = message.get("chat", {})
    if chat.get("type", "") == "private":
        if message.get("text") == "/start":
            start(data, token)
        elif message.get("contact", None) or message.get("text", None):
            set_phone_number(data, token)
        elif message.get("location"):
            set_location(data, token)


@csrf_exempt
def webhook(request, bot_token):
    """Run router and return success response"""
    try:
        router(request.body.decode("utf-8"), bot_token)
    except Exception as error:
        print(error)

    return JsonResponse({"ok": True})
