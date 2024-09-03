# Generated by Django 4.2.11 on 2024-09-03 09:51

from django.db import migrations, models
import django.db.models.deletion
import oscar.core.utils
import oscar.models.fields.autoslugfield


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalogue", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Partner",
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
                        max_length=128,
                        populate_from="name",
                        unique=True,
                        verbose_name="Код",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=128,
                        verbose_name="Название",
                    ),
                ),
            ],
            options={
                "verbose_name": "Точка продажи",
                "verbose_name_plural": "Точка продажи",
                "ordering": ("name", "code"),
                "permissions": (("dashboard_access", "Can access dashboard"),),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="StockRecord",
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
                    "partner_sku",
                    models.CharField(
                        max_length=128, verbose_name="Артикул в точке продажи"
                    ),
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
                    "price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Цена продажи",
                        max_digits=12,
                        null=True,
                        verbose_name="Цена",
                    ),
                ),
                (
                    "old_price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Цена до скидки. Оставить пустым, если скидки нет",
                        max_digits=12,
                        null=True,
                        verbose_name="Цена до скидки",
                    ),
                ),
                (
                    "num_in_stock",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Количество в наличии"
                    ),
                ),
                (
                    "num_allocated",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Количество заказано"
                    ),
                ),
                (
                    "low_stock_threshold",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Граница малых запасов"
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
                    models.DateTimeField(
                        auto_now=True, db_index=True, verbose_name="Дата изменения"
                    ),
                ),
                (
                    "partner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stockrecords",
                        to="partner.partner",
                        verbose_name="Точка продажи",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stockrecords",
                        to="catalogue.product",
                        verbose_name="Продукт",
                    ),
                ),
            ],
            options={
                "verbose_name": "Товарная запись",
                "verbose_name_plural": "Товарные записи",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="StockAlert",
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
                        choices=[("Открыто", "Открыто"), ("Закрыто", "Закрыто")],
                        default="Открыто",
                        max_length=128,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "date_closed",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Дата закрытия"
                    ),
                ),
                (
                    "stockrecord",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="alerts",
                        to="partner.stockrecord",
                        verbose_name="Товарная запись",
                    ),
                ),
            ],
            options={
                "verbose_name": "Уведомление товарного запаса",
                "verbose_name_plural": "Уведомления товарных запасов",
                "ordering": ("-date_created",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PartnerAddress",
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
                    "line1",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Улица, дом"
                    ),
                ),
                (
                    "line2",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Квартира"
                    ),
                ),
                (
                    "line3",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Подъезд"
                    ),
                ),
                (
                    "line4",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Этаж"
                    ),
                ),
                (
                    "coords_long",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Координаты долгота",
                    ),
                ),
                (
                    "coords_lat",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Координаты широта",
                    ),
                ),
                (
                    "search_text",
                    models.TextField(
                        editable=False,
                        verbose_name="Адрес для поиска. Используется только для поиска",
                    ),
                ),
                (
                    "partner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to="partner.partner",
                        verbose_name="Точка продажи",
                    ),
                ),
            ],
            options={
                "verbose_name": "Адрес точки продажи",
                "verbose_name_plural": "Адреса точек продаж",
                "abstract": False,
            },
        ),
    ]
