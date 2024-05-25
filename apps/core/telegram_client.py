import requests


class TelegramClient:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    def send(self, method: str, data: dict):
        response = requests.post(
            f"https://api.telegram.org/bot{self.bot_token}/{method}",
            data=data,
            timeout=60,
        ).json()
        return response
