# Generated by Django 4.2.11 on 2025-02-28 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TelegramMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("new-order", "Уведомление о новом заказе"),
                            ("status-order", "Уведомление об изменении статуса заказа"),
                            ("technical", "Техническое уведомление"),
                            ("offer", "Уведомление о персональном предложении"),
                            ("misc", "Без типа"),
                        ],
                        default="misc",
                        max_length=128,
                        verbose_name="Тип сообщения",
                    ),
                ),
                ("message", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "date_sent",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата отправки"
                    ),
                ),
            ],
            options={
                "verbose_name": "Сообщение Телеграм",
                "verbose_name_plural": "Сообщения Телеграм",
                "ordering": ["type"],
            },
        ),
        migrations.CreateModel(
            name="TelegramSupportChat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "telegram_id",
                    models.CharField(max_length=10, verbose_name="ID Telegram"),
                ),
                (
                    "chat_id",
                    models.CharField(max_length=10, verbose_name="ID Telegram"),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания ображения"
                    ),
                ),
            ],
            options={
                "verbose_name": "Обращение в поддержку Телеграм",
                "verbose_name_plural": "Обращение в поддержку Телеграм",
            },
        ),
    ]
