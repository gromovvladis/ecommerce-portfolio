import asyncio
from asyncio.log import logger
from django.template import loader
from celery import shared_task
from oscar.apps.telegram.commands import async_send_telegram_message_to_users, send_telegram_message_to_users, get_staffs
from oscar.core.loading import get_model
from django.contrib.auth import get_user_model

Notification = get_model("communication", "Notification")
User = get_user_model()

@shared_task
def _notify_admin_about_new_order(ctx: dict):

    subject = "Пользовательский заказ"
    message_tpl = loader.get_template("oscar/customer/alerts/staff_new_order_message.html")
    description = "Заказ №%s успешно создан!" % (ctx['number'])
    admins = User.objects.filter(is_staff=True)

    for user in admins:
        Notification.objects.create(
            recipient=user, 
            order_id=ctx["order_id"],
            subject=subject, 
            body=message_tpl.render(ctx).strip(), 
            description=description,
            status="Success"
        )

@shared_task()
def _notify_customer_about_new_order(ctx: dict):
    
    subject = "Новый заказ"
    message_tpl = loader.get_template("oscar/customer/alerts/new_order_message.html")
    description = "Заказ №%s успешно создан!" % (ctx['number'])

    ctx['description'] = description

    Notification.objects.create(
        recipient_id=ctx['user_id'],
        order_id=ctx["order_id"],
        subject=subject,
        body=message_tpl.render(ctx).strip(), 
        description=description,
        status="Success"
    )

@shared_task()
def _notify_customer_about_order_status(ctx: dict):
    
    subject = "Статус заказа изменен"
    message_tpl = loader.get_template("oscar/customer/alerts/order_status_chenged_message.html")
    description = "Новый статус заказа №%s - %s" % (ctx['number'], ctx['new_status'])

    status="Info"

    if ctx['status'] == "Отменен":
        status="Canceled"

    if ctx['status'] == "Обрабатывается" or ctx['status'] == "Ожидает оплаты":
        status="Warning"

    context = {
        'title': "Просмотреть заказ №%s" % ctx['number'],
        'url': ctx['url'],
        'new_status': ctx['new_status'],
    }

    Notification.objects.create(
        recipient_id=ctx['user_id'],
        order_id=ctx["order_id"],
        subject=subject,
        body=message_tpl.render(context).strip(),
        description=description,
        status=status,
    )

@shared_task
def _send_telegram_message_to_users(msg: str, parse_mode: str = None):
    send_telegram_message_to_users(msg, parse_mode)
