import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

ALLOWED_UPDATES = ["message", "callback_query"]


class Command(BaseCommand):
    help = "Set webhook for bot"

    def handle(self, *args, **options):
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}"
        requests.get(f"{url}/deleteWebhook", params={"drop_pending_updates": True})
        params = {
            "url": f"{settings.BACKEND_URL}/core/{settings.BOT_TOKEN}",
            "allowed_updates": json.dumps(ALLOWED_UPDATES),
        }

        res = requests.get(f"{url}/setWebhook", params=params)
        print(res.json())
