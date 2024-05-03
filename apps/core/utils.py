import json
import re
import ssl

import certifi
from core.telegram_client import TelegramClient
from django.conf import settings
from geopy.geocoders import Nominatim
from users.models import Address, User


def start(data, token):
    telegram = TelegramClient(token)
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    user = User.objects.filter(telegram_id=chat_id).first()
    reply_markup = None
    if not user:
        text = "Telefon raqamingizni +998901234567 formatida yozib yuboring yoki quyidagi tugmani bosing"
        reply_markup = json.dumps(
            {
                "keyboard": [
                    [
                        {
                            "text": "Telefon raqamni yuborish",
                            "request_contact": True,
                        }
                    ]
                ],
                "resize_keyboard": True,
            }
        )
    elif user.is_blocked:
        text = "Bekor qilingan buyurtmalaringiz 3 ta bo'lganligi uchun siz admin tomonidan bloklangansiz va botdan foydalana olmaysiz."
    else:
        address = Address.objects.filter(user=user)
        if not address:
            text = "Manzilingizni yuboring"
            reply_markup = json.dumps(
                {
                    "keyboard": [
                        [
                            {
                                "text": "Lokatsiyani yuborish",
                                "request_location": True,
                            }
                        ]
                    ],
                    "resize_keyboard": True,
                }
            )
        else:
            text = "Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊"
            reply_markup = json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Menu",
                                "web_app": {
                                    "url": settings.WEB_APP_URL,
                                },
                            }
                        ]
                    ]
                }
            )

    if text == "Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊":
        send_success_message(telegram, chat_id)
    else:
        telegram.send(
            "sendMessage",
            data={
                "chat_id": chat_id,
                "text": text,
                "reply_markup": reply_markup,
            },
        )


def set_phone_number(data, token):
    telegram = TelegramClient(token)
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    user = User.objects.filter(telegram_id=chat_id).first()
    reply_markup = None

    if data.get("message", {}).get("contact", {}).get("phone_number", None):
        phone_number = (
            data.get("message", {}).get("contact", {}).get("phone_number", None)
        )
    else:
        phone_number = data.get("message", {}).get("text", None)

    if not re.match(
        r"^\+?998?\s?-?([0-9]{2})\s?-?(\d{3})\s?-?(\d{2})\s?-?(\d{2})$",
        phone_number,
    ):
        text = (
            "Noto'g'ri format! Raqamni quyidagicha formatlarda kiritishingiz mumkin!\n\n"
            "+998XXXXXXXXX, +998-XX-XXX-XX-XX, +998 XX XXX XX XX"
        )
    else:
        if (
            User.objects.filter(phone_number=phone_number)
            .exclude(telegram_id=chat_id)
            .first()
        ):
            text = "Bu telefon raqami oldin ro'yxatdan o'tgan"
        else:
            if not user:
                user = User.objects.create_user(
                    phone_number=phone_number,
                    password=str(chat_id),
                    telegram_id=chat_id,
                )
            user.phone_number = phone_number
            user.save()

            text = "Telefon saqlandi✅\n\nManzilingizni yuboring"
            reply_markup = json.dumps(
                {
                    "keyboard": [
                        [
                            {
                                "text": "Lokatsiyani yuborish",
                                "request_location": True,
                            }
                        ]
                    ],
                    "resize_keyboard": True,
                }
            )

    telegram.send(
        "sendMessage",
        data={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup,
        },
    )


def set_location(data, token):
    telegram = TelegramClient(token)
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user = User.objects.filter(telegram_id=chat_id).first()

    latitude = message.get("location", {}).get("latitude")
    longitude = message.get("location", {}).get("longitude")
    address_data = {
        "user": user,
        "latitude": latitude,
        "longitude": longitude,
    }

    address = Address.objects.filter(**address_data).first()

    if not address:
        address_data["address"] = get_address_by_location(latitude, longitude)
        Address.objects.create(**address_data)

    telegram.send(
        "sendMessage",
        data={
            "chat_id": chat_id,
            "text": "Lokatsiya saqlandi✅",
            "reply_markup": json.dumps(
                {
                    "keyboard": [
                        [
                            {
                                "text": "Lokatsiya qo'shish",
                                "request_location": True,
                            }
                        ],
                        [
                            {
                                "text": "Telefon raqamni yangilash",
                                "request_contact": True,
                            }
                        ],
                    ],
                    "resize_keyboard": True,
                }
            ),
        },
    )

    send_success_message(telegram, chat_id)


def send_success_message(telegram: TelegramClient, chat_id):
    reply_markup = json.dumps(
        {
            "inline_keyboard": [
                [
                    {
                        "text": "Menu",
                        "web_app": {
                            "url": settings.WEB_APP_URL,
                        },
                    }
                ]
            ]
        }
    )

    data = {
        "chat_id": chat_id,
        "reply_markup": reply_markup,
    }
    if settings.IMAGE_FILE_ID:
        data["photo"] = settings.IMAGE_FILE_ID
        data["caption"] = "Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊"
        method = "sendPhoto"
    else:
        method = "sendMessage"
        data["text"] = "Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊"

    res = telegram.send(
        method,
        data=data,
    )

    if (
        not res.get("ok")
        and res.get("description")
        == "Bad Request: wrong file identifier/HTTP URL specified"
    ):
        telegram.send(
            "sendMessage",
            data={
                "chat_id": chat_id,
                "text": "Mahsulotlarimiz buyurtma berishingizni kutib turishibdi😊",
                "reply_markup": reply_markup,
            },
        )


def get_address_by_location(latitude, longitude):
    ca_file = certifi.where()
    context = ssl.create_default_context(cafile=ca_file)
    geolocator = Nominatim(user_agent="qasr-restaurant-bot", ssl_context=context)
    location = geolocator.reverse((latitude, longitude), language="uz")
    return ", ".join(location.address.split(",")[:3])
