# Generated by Django 4.2.11 on 2025-02-28 10:16

import django.core.serializers.json
from django.db import migrations, models
import oscar.core.utils
import oscar.models.fields.slugfield


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Basket",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("Open", "Открыто - сейчас активна"),
                            ("Merged", "Объединено – заменено другой корзиной"),
                            ("Frozen", "Заморожено – корзину нельзя изменить"),
                            ("Submitted", "Потдвержено - заказано"),
                        ],
                        default="Open",
                        max_length=128,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "date_merged",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Дата объединения"
                    ),
                ),
                (
                    "date_submitted",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Дата подтверждения"
                    ),
                ),
            ],
            options={
                "verbose_name": "Корзина",
                "verbose_name_plural": "Корзины",
            },
        ),
        migrations.CreateModel(
            name="Line",
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
                    "line_reference",
                    oscar.models.fields.slugfield.SlugField(
                        allow_unicode=True,
                        max_length=128,
                        verbose_name="Референс позиции",
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(default=1, verbose_name="Количество"),
                ),
                (
                    "price_currency",
                    models.CharField(
                        default=oscar.core.utils.get_default_currency,
                        max_length=12,
                        verbose_name="Валюта",
                    ),
                ),
                (
                    "tax_code",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        null=True,
                        verbose_name="Налоговый код",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "date_updated",
                    models.DateTimeField(
                        auto_now=True, db_index=True, verbose_name="Дата изменения"
                    ),
                ),
            ],
            options={
                "verbose_name": "Позиция корзины",
                "verbose_name_plural": "Позиции корзины",
                "ordering": ["date_created", "pk"],
            },
        ),
        migrations.CreateModel(
            name="LineAttribute",
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
                    "value",
                    models.JSONField(
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                        verbose_name="Значение",
                    ),
                ),
            ],
            options={
                "verbose_name": "Атрибут позиции",
                "verbose_name_plural": "Атрибуты позиции",
            },
        ),
    ]
