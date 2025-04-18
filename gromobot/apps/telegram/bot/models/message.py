from asgiref.sync import sync_to_async
from core.loading import get_model

TelegramMessage = get_model("telegram", "TelegramMessage")


@sync_to_async
def get_history_messages(user_id: int):
    messages = TelegramMessage.objects.filter(user_id=user_id)

    if not messages.exists():
        return ("Нет отправленных сообщений.",)
    else:
        msg_list = []
        for msg in messages:
            TelegramMessage.TYPE_CHOICES
            type = next(
                (
                    description
                    for key, description in TelegramMessage.TYPE_CHOICES
                    if key == msg.type
                ),
                "Без типа",
            )
            order_msg = (
                f"<b>{msg.message}</b>\n"
                f"Время отправки: {msg.date_sent.strftime('%d.%m.%Y %H:%M')}\n"
                f"Тип: {type}\n"
            )

            msg_list.append(order_msg)

        return msg_list
