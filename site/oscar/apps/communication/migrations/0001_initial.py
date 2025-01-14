# Generated by Django 4.2.11 on 2025-01-14 06:23

import django.core.validators
from django.db import migrations, models
import oscar.models.fields.autoslugfield


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CommunicationEventType",
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
                    "code",
                    oscar.models.fields.autoslugfield.AutoSlugField(
                        allow_unicode=True,
                        blank=True,
                        editable=False,
                        help_text="Код, используемый для программного поиска этого события",
                        max_length=128,
                        overwrite=True,
                        populate_from="name",
                        separator="_",
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Код может содержать только заглавные буквы (A-Z)цифры и подчеркивания, и не могут начинаться с цифры.",
                                regex="^[A-Z_][0-9A-Z_]*$",
                            )
                        ],
                        verbose_name="Код",
                    ),
                ),
                (
                    "name",
                    models.CharField(db_index=True, max_length=255, verbose_name="Имя"),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("Order related", "Связанный с заказом"),
                            ("User related", "Связанный с пользователем"),
                        ],
                        default="Order related",
                        max_length=255,
                        verbose_name="Категория",
                    ),
                ),
                (
                    "email_subject_template",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Шаблон темы электронного письма",
                    ),
                ),
                (
                    "email_body_template",
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name="Шаблон тела электронного письма",
                    ),
                ),
                (
                    "email_body_html_template",
                    models.TextField(
                        blank=True,
                        help_text="HTML шаблон",
                        null=True,
                        verbose_name="HTML-шаблон тела электронного письма",
                    ),
                ),
                (
                    "sms_template",
                    models.CharField(
                        blank=True,
                        help_text="SMS шаблон",
                        max_length=170,
                        null=True,
                        verbose_name="SMS шаблон",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "date_updated",
                    models.DateTimeField(auto_now=True, verbose_name="Дата изменения"),
                ),
            ],
            options={
                "verbose_name": "Событие уведомления",
                "verbose_name_plural": "События уведомлений",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Email",
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
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, null=True, verbose_name="Email"
                    ),
                ),
                ("subject", models.TextField(max_length=255, verbose_name="Тема")),
                ("body_text", models.TextField(verbose_name="Тело Text")),
                ("body_html", models.TextField(blank=True, verbose_name="Тело HTML")),
                (
                    "date_sent",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата отправки"
                    ),
                ),
            ],
            options={
                "verbose_name": "Email",
                "verbose_name_plural": "Emails",
                "ordering": ["-date_sent"],
            },
        ),
        migrations.CreateModel(
            name="Notification",
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
                ("subject", models.CharField(max_length=255)),
                (
                    "description",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("body", models.TextField()),
                (
                    "location",
                    models.CharField(
                        choices=[("Inbox", "Входящие"), ("Archive", "Архив")],
                        default="Inbox",
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Success", "Успешно"),
                            ("Info", "Инфо"),
                            ("Warning", "Предупреждение"),
                            ("Canceled", "Отмена"),
                        ],
                        default="Info",
                        max_length=32,
                    ),
                ),
                ("date_sent", models.DateTimeField(auto_now_add=True)),
                ("date_read", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Уведомление",
                "verbose_name_plural": "Уведомления",
                "ordering": ("-date_sent",),
            },
        ),
    ]
