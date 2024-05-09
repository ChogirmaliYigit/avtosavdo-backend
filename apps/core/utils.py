import json
import re
import ssl

import certifi
from core.telegram_client import TelegramClient
from django.conf import settings
from geopy.geocoders import Nominatim
from shop.models import ChatMessage, Order
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
    reply_markup = None

    if data.get("message", {}).get("contact", {}).get("phone_number", None):
        phone_number = (
            data.get("message", {}).get("contact", {}).get("phone_number", None)
        )
    else:
        phone_number = data.get("message", {}).get("text", None)

    if not phone_number.startswith("+"):
        phone_number = f"+{phone_number}"

    if not re.match(
        r"^\+?998?\s?-?([0-9]{2})\s?-?(\d{3})\s?-?(\d{2})\s?-?(\d{2})$",
        phone_number,
    ):
        text = (
            "Noto'g'ri format! Raqamni quyidagicha formatlarda kiritishingiz mumkin!\n\n"
            "+998XXXXXXXXX, +998-XX-XXX-XX-XX, +998 XX XXX XX XX"
        )
    else:
        user = User.objects.filter(phone_number=phone_number).first()
        if user:
            user.telegram_id = chat_id
        if not user:
            user = User.objects.create_user(
                phone_number=phone_number,
                password=str(chat_id),
                telegram_id=chat_id,
            )
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

        if check_user_location(latitude, longitude):
            Address.objects.create(**address_data)
        else:
            telegram.send(
                "sendMessage",
                data={
                    "chat_id": chat_id,
                    "text": "Siz bepul yetkazib berish doirasidan tashqarida bo'lganingiz sababli qo'shimcha to'lov orqali buyurtma berish uchun +998771164949 telefon nomeriga bog'laning.",
                },
            )
            return

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

    telegram.send(
        "sendMessage",
        data={
            "chat_id": chat_id,
            "text": "Assalomu aleykum!",
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


def update_order_data(data, token):
    telegram = TelegramClient(token)
    callback_query = data.get("callback_query", {})
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    data = callback_query.get("data", "")
    data, order_id = data.split("_")
    order_statuses = {
        "in_processing": "Jarayonda",
        "confirmed": "Tasdiqlangan",
        "performing": "Amalga oshirilyabdi",
        "success": "Bajarilgan",
        "canceled": "Bekor qilingan",
    }

    order = Order.objects.filter(id=int(order_id)).first()
    if order:
        if data == "paid":
            order.paid = True
        elif data in order_statuses.keys():
            order.status = data
        order.save()

        statuses = {
            Order.IN_PROCESSING: [
                Order.CONFIRMED,
                Order.PERFORMING,
                Order.SUCCESS,
                Order.CANCELED,
            ],
            Order.CONFIRMED: [
                Order.PERFORMING,
                Order.SUCCESS,
                Order.CANCELED,
            ],
            Order.PERFORMING: [
                Order.SUCCESS,
                Order.CANCELED,
            ],
        }

        keyboard = []
        for status in statuses.get(order.status, []):
            keyboard.append(
                [
                    {
                        "text": order_statuses.get(status),
                        "callback_data": f"{status}_{order.pk}",
                    }
                ]
            )

        if not order.paid:
            keyboard.append(
                [
                    {
                        "text": "To'langan✅",
                        "callback_data": f"paid_{order.pk}",
                    }
                ]
            )

        payment_status = "To'langan✅" if order.paid else "To'lanmagan❌"

        delivery_type = (
            "Yetkazib berish" if order.delivery_type == "delivery" else "Olib ketish"
        )

        address_text = f"<b>{order.address.address}</b>"
        if order.address.latitude and order.address.longitude:
            address_text = (
                f"<a href='https://www.google.com/maps/@"
                f"{order.address.latitude},{order.address.longitude},18.5z?entry=ttu'>{address_text}</a>"
            )

        product_names = []
        for order_product in order.products.all():
            product_names.append(
                f"{order_product.product.title} ({order_product.count} ta)"
            )

        chat = ChatMessage.objects.filter(
            chat_id=chat_id, message_id=message.get("id"), order=order
        ).first()

        secondary_phone_number = order.secondary_phone_number
        if secondary_phone_number == "+998":
            secondary_phone_number = "Mavjud emas"

        telegram.send(
            "editMessageText",
            data={
                "chat_id": settings.GROUP_ID,
                "message_id": chat.message_id if chat else None,
                "text": f"<b>№{order.pk} raqamli buyurtma</b>\n\n"
                f"📱Telefon raqam: <b>{order.user.phone_number}</b>\n"
                f"📱Qo'shimcha telefon raqam: <b>{secondary_phone_number}</b>\n"
                f"📦Holati: {order_statuses.get(order.status)}\n"
                f"💸To'lov holati: {payment_status}\n"
                f"🚚Yetkazib berish turi: <b>{delivery_type}</b>\n"
                f"📍Yetkazib berish manzili: {address_text}\n"
                f"📋Mahsulotlar: <b>{', '.join(product_names)}</b>\n\n"
                f"<b>💸Umumiy narx: {order.total_price} so'm</b>",
                "parse_mode": "html",
                "disable_web_page_preview": True,
                "reply_markup": json.dumps(
                    {
                        "inline_keyboard": keyboard,
                    }
                ),
            },
        )


def get_address_by_location(latitude, longitude):
    ca_file = certifi.where()
    context = ssl.create_default_context(cafile=ca_file)
    geolocator = Nominatim(user_agent="qasr-restaurant-bot", ssl_context=context)
    location = geolocator.reverse((latitude, longitude), language="uz")
    return ", ".join(location.address.split(",")[:3])


def check_user_location(latitude, longitude):
    service_areas = [
        [
            (41.522960, 60.381202),
            (41.535489, 60.378284),
            (41.549173, 60.365668),
            (41.557330, 60.342151),
            (41.546026, 60.321207),
            (41.533563, 60.316745),
            (41.516020, 60.319662),
            (41.509335, 60.353136),
            (41.511842, 60.364638),
        ]
    ]

    for area in service_areas:
        if is_inside_area(latitude, longitude, area):
            return True
    return False


def is_inside_area(latitude, longitude, area):
    # Is the location of the user to be checked
    num = len(area)
    j = num - 1
    c = False
    for i in range(num):
        if ((area[i][1] > longitude) != (area[j][1] > longitude)) and (
            latitude
            < (area[j][0] - area[i][0])
            * (longitude - area[i][1])
            / (area[j][1] - area[i][1])
            + area[i][0]
        ):
            c = not c
        j = i
    return c
