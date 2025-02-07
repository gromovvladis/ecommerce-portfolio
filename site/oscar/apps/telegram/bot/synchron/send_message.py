import logging
import requests

from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model

from oscar.core.loading import get_model

User = get_user_model()
Staff = get_model("user", "Staff")
TelegramMessage = get_model("telegram", "TelegramMessage")

STAFF_BOT = settings.TELEGRAM_STAFF_BOT_TOKEN
CUSTOMER_BOT = settings.TELEGRAM_CUSTOMER_BOT_TOKEN

logger = logging.getLogger("oscar.telegram")


# Синхронная функция отправки сообщения через Telegram API
def send_message(
    chat_id: int,
    text: str,
    type: str = TelegramMessage.MISC,
    user=None,
    bot_token: str = STAFF_BOT,
    **kwargs,
):
    """
    Синхронная реализация отправки сообщения через Telegram API.

    :param bot_token: Токен бота Telegram
    :param chat_id: ID чата, в который отправляется сообщение
    :param text: Текст сообщения
    :param kwargs: Дополнительные параметры, которые принимает sendMessage метод Telegram API
    :return: Ответ от Telegram API
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Разделяем текст на части, если он превышает допустимую длину
    messages = [text[i : i + 4096] for i in range(0, len(text), 4096)]

    response_data = None
    try:
        for message_part in messages:
            # Параметры запроса для каждого сообщения
            payload = {
                "chat_id": chat_id,
                "text": message_part,
                "parse_mode": "HTML",
                **kwargs,
            }

            # Отправляем сообщение в Telegram API
            response = requests.post(url, json=payload)
            response.raise_for_status()

            # Получаем JSON-ответ для каждой части сообщения
            response_data = response.json()

            if user is not None:
                # Сохраняем сообщение в базу данных
                TelegramMessage.objects.create(
                    user=user,
                    type=type,
                    message=message_part,
                )

        return response_data

    except requests.exceptions.HTTPError as http_err:
        logger.error(
            f"Ошибка HTTP запроса при отправке телеграм сообщения синхроно: {http_err}"
        )
        raise Exception(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.error(f"Ошибка при отправке телеграм сообщения синхроно: {err}")
        raise Exception(f"An error occurred: {err}")


def send_message_to_staffs(
    text: str,
    type: str = TelegramMessage.MISC,
    store_id: str = None,
    bot_token: str = STAFF_BOT,
    **kwargs,
):
    if type == TelegramMessage.TECHNICAL:
        staffs = Staff.objects.filter(
            is_active=True, notif=Staff.TECHNICAL, telegram_id__isnull=False
        ).select_related("user")
    elif type == TelegramMessage.STATUS:
        staffs = Staff.objects.filter(
            is_active=True,
            notif__in=[Staff.STATUS, Staff.TECHNICAL],
            telegram_id__isnull=False,
        ).select_related("user")
    else:
        staffs = (
            Staff.objects.filter(is_active=True, telegram_id__isnull=False)
            .exclude(notif=Staff.OFF)
            .select_related("user")
        )

    if store_id:
        staffs = staffs.filter(
            Q(user__stores__id=store_id) | Q(user__is_superuser=True)
        )

    for staff in staffs:
        send_message(staff.telegram_id, text, type, staff.user, bot_token, **kwargs)


def send_message_to_customer(
    text, user, type=TelegramMessage.MISC, bot_token=CUSTOMER_BOT, **kwargs
):
    if user.telegram_id:
        send_message(user.telegram_id, text, type, user, bot_token, **kwargs)
