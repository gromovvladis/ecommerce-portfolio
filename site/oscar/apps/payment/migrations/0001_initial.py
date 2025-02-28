# Generated by Django 4.2.11 on 2025-02-28 07:53

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import oscar.core.utils
import oscar.models.fields.autoslugfield


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("order", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bankcard",
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
                    "card_type",
                    models.CharField(max_length=128, verbose_name="Тип карты"),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=255, verbose_name="Имя"),
                ),
                ("number", models.CharField(max_length=32, verbose_name="Номер")),
                (
                    "expiry_date",
                    models.DateField(verbose_name="Дата истечения срока действия"),
                ),
            ],
            options={
                "verbose_name": "Банковская карта",
                "verbose_name_plural": "Банковские карты",
            },
        ),
        migrations.CreateModel(
            name="Source",
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
                    "currency",
                    models.CharField(
                        default=oscar.core.utils.get_default_currency,
                        max_length=12,
                        verbose_name="Валюта",
                    ),
                ),
                (
                    "amount_allocated",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        verbose_name="Сумма для оплаты",
                    ),
                ),
                (
                    "amount_debited",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        verbose_name="Сумма оплачено",
                    ),
                ),
                (
                    "amount_refunded",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        verbose_name="Сумма возвращено",
                    ),
                ),
                (
                    "reference",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Референс"
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sources",
                        to="order.order",
                        verbose_name="Заказ",
                    ),
                ),
            ],
            options={
                "verbose_name": "Источник оплаты",
                "verbose_name_plural": "Источники оплаты",
                "ordering": ["pk"],
                "permissions": (
                    ("full_access", "Полный доступ к источникам оплаты"),
                    ("read", "Просматривать платежи и возвраты"),
                    ("make_refund", "Остуществлять возвраты"),
                ),
            },
        ),
        migrations.CreateModel(
            name="SourceType",
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
                    "name",
                    models.CharField(db_index=True, max_length=128, verbose_name="Имя"),
                ),
                (
                    "code",
                    oscar.models.fields.autoslugfield.AutoSlugField(
                        allow_unicode=True,
                        blank=True,
                        editable=False,
                        help_text="Это используется в формах для идентификации этого типа источника.",
                        max_length=128,
                        overwrite=True,
                        populate_from="name",
                        unique=True,
                        verbose_name="Код",
                    ),
                ),
            ],
            options={
                "verbose_name": "Тип источника оплаты",
                "verbose_name_plural": "Типы источников оплаты",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Transaction",
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
                    "txn_type",
                    models.CharField(blank=True, max_length=128, verbose_name="Тип"),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="Сумма"
                    ),
                ),
                (
                    "reference",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="Референс"
                    ),
                ),
                (
                    "status",
                    models.CharField(blank=True, max_length=128, verbose_name="Статус"),
                ),
                (
                    "is_included",
                    models.BooleanField(
                        default=False, verbose_name="Транзакция учтена в источнике"
                    ),
                ),
                ("receipt", models.BooleanField(default=False, verbose_name="Чек ОФД")),
                ("paid", models.BooleanField(default=False, verbose_name="Оплачено")),
                (
                    "refundable",
                    models.BooleanField(default=False, verbose_name="Возврат возможен"),
                ),
                (
                    "evotor_id",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="ID Эвотор"
                    ),
                ),
                (
                    "payment_id",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="Код оплаты"
                    ),
                ),
                (
                    "refund_id",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="Код возврата"
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="payment.source",
                        verbose_name="Источник",
                    ),
                ),
            ],
            options={
                "verbose_name": "Транзакция",
                "verbose_name_plural": "Транзакции",
                "ordering": ["-date_created"],
            },
        ),
        migrations.AddField(
            model_name="source",
            name="source_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sources",
                to="payment.sourcetype",
                verbose_name="Тип источника",
            ),
        ),
    ]
