# Generated by Django 4.2.11 on 2025-01-14 06:23

import datetime
from django.db import migrations, models
import django.db.models.deletion
import oscar.core.utils
import oscar.models.fields.autoslugfield


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("address", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BarCode",
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
                    models.CharField(
                        max_length=128, unique=True, verbose_name="Штрих-код"
                    ),
                ),
            ],
            options={
                "verbose_name": "Штрих-код",
                "verbose_name_plural": "Штрих-коды",
                "ordering": ("code",),
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
            ],
            options={
                "verbose_name": "Уведомление товарного запаса",
                "verbose_name_plural": "Уведомления товарных запасов",
                "ordering": ("-date_created",),
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
                    "evotor_code",
                    models.CharField(
                        blank=True,
                        help_text="Эвотор код, для связи товара и товарной записи",
                        max_length=25,
                        verbose_name="Эвотор Code",
                    ),
                ),
                (
                    "price_currency",
                    models.CharField(
                        default=oscar.core.utils.get_default_currency,
                        help_text="Валюта. Рубли = RUB",
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
                    "cost_price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Цена закупки товара",
                        max_digits=12,
                        null=True,
                        verbose_name="Цена закупки",
                    ),
                ),
                (
                    "tax",
                    models.CharField(
                        choices=[
                            ("NO_VAT", "Без НДС."),
                            ("VAT_0", "Основная ставка 0%"),
                            ("VAT_10", "Основная ставка 10%."),
                            ("VAT_10_110", "Расчётная ставка 10%."),
                            (
                                "VAT_18",
                                "Основная ставка 18%. С первого января 2019 года может указывать как на 18%, так и на 20% ставку.",
                            ),
                            (
                                "VAT_18_118",
                                "Расчётная ставка 18%. С первого января 2019 года может указывать как на 18%, так и на 20% ставку.",
                            ),
                        ],
                        default="NO_VAT",
                        max_length=128,
                        verbose_name="Налог в процентах",
                    ),
                ),
                (
                    "num_in_stock",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="В наличии",
                        null=True,
                        verbose_name="Количество в наличии",
                    ),
                ),
                (
                    "num_allocated",
                    models.IntegerField(
                        blank=True,
                        help_text="Заказано",
                        null=True,
                        verbose_name="Количество заказано",
                    ),
                ),
                (
                    "low_stock_threshold",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Граница малых запасов",
                        null=True,
                        verbose_name="Граница малых запасов",
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Товар доступен к покупке",
                        verbose_name="Доступен",
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
            ],
            options={
                "verbose_name": "Товарная запись",
                "verbose_name_plural": "Товарные записи",
            },
        ),
        migrations.CreateModel(
            name="Store",
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
                        overwrite=True,
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
                (
                    "evotor_id",
                    models.CharField(
                        blank=True, max_length=128, null=True, verbose_name="ID Эвотор"
                    ),
                ),
                (
                    "start_worktime",
                    models.TimeField(
                        default=datetime.time(9, 0), verbose_name="Время начала смены"
                    ),
                ),
                (
                    "end_worktime",
                    models.TimeField(
                        default=datetime.time(21, 0),
                        verbose_name="Время окончания смены",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Магазин доступен для клиентов?",
                        verbose_name="Активен",
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
                "verbose_name": "Магазин",
                "verbose_name_plural": "Магазины",
                "ordering": ("name", "code"),
            },
        ),
        migrations.CreateModel(
            name="Terminal",
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
                    models.CharField(
                        blank=True, max_length=128, verbose_name="Название"
                    ),
                ),
                (
                    "evotor_id",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="ID Эвотор"
                    ),
                ),
                (
                    "model",
                    models.CharField(
                        blank=True,
                        max_length=128,
                        null=True,
                        verbose_name="Модель терминала",
                    ),
                ),
                (
                    "imei",
                    models.CharField(
                        blank=True,
                        max_length=128,
                        null=True,
                        unique=True,
                        verbose_name="Код imei",
                    ),
                ),
                (
                    "serial_number",
                    models.CharField(
                        max_length=128, unique=True, verbose_name="Серийный номер"
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
                "verbose_name": "Смарт терминал Эвотор",
                "verbose_name_plural": "Смарт терминалы Эвотор",
                "ordering": ("name", "serial_number"),
            },
        ),
        migrations.CreateModel(
            name="StoreAddress",
            fields=[
                (
                    "address_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="address.address",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to="store.store",
                        verbose_name="Магазин",
                    ),
                ),
            ],
            options={
                "verbose_name": "Адрес магазина",
                "verbose_name_plural": "Адреса магазинов",
            },
            bases=("address.address",),
        ),
        migrations.AddField(
            model_name="store",
            name="terminals",
            field=models.ManyToManyField(
                blank=True,
                related_name="stores",
                to="store.terminal",
                verbose_name="Терминал",
            ),
        ),
    ]
