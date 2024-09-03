# Generated by Django 4.2.11 on 2024-09-03 09:51

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import oscar.core.utils
import oscar.models.fields.autoslugfield


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CommunicationEvent",
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
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Дата создания"
                    ),
                ),
            ],
            options={
                "verbose_name": "Событие связи",
                "verbose_name_plural": "События связи",
                "ordering": ["-date_created"],
                "abstract": False,
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
                    "partner_name",
                    models.CharField(
                        blank=True,
                        max_length=128,
                        verbose_name="Название точки продажи",
                    ),
                ),
                (
                    "partner_sku",
                    models.CharField(
                        max_length=128, verbose_name="Артикул в точке продажи"
                    ),
                ),
                (
                    "partner_line_reference",
                    models.CharField(
                        blank=True,
                        help_text="Это номер позиции, который партнер использует в своей системе.",
                        max_length=128,
                        verbose_name="Код точки продажи",
                    ),
                ),
                (
                    "partner_line_notes",
                    models.TextField(
                        blank=True, verbose_name="Примечание точки продажи"
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=255, verbose_name=("Название продукта", "Название")
                    ),
                ),
                (
                    "upc",
                    models.CharField(
                        blank=True,
                        max_length=128,
                        null=True,
                        verbose_name="Товарный код продукта UPC",
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(default=1, verbose_name="Количество"),
                ),
                (
                    "line_price",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="Цена"
                    ),
                ),
                (
                    "line_price_before_discounts",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        verbose_name="Цена без учета скидок",
                    ),
                ),
                (
                    "unit_price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        verbose_name="Цена за единицу товара",
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
                    "status",
                    models.CharField(blank=True, max_length=255, verbose_name="Статус"),
                ),
            ],
            options={
                "verbose_name": "Позиция заказа",
                "verbose_name_plural": "Позиции заказа",
                "ordering": ["pk"],
                "abstract": False,
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
                ("type", models.CharField(max_length=128, verbose_name="Тип")),
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
                "verbose_name_plural": "Атрибуты позиций",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="LinePrice",
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
                    "quantity",
                    models.PositiveIntegerField(default=1, verbose_name="Количество"),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="Цена"
                    ),
                ),
                (
                    "shipping",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                        verbose_name="Доставка",
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
            ],
            options={
                "verbose_name": "Цена позиции",
                "verbose_name_plural": "Цены позиций",
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Order",
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
                    "number",
                    models.CharField(
                        db_index=True,
                        max_length=128,
                        unique=True,
                        verbose_name="Номер заказа",
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
                    "total",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="Сумма заказа"
                    ),
                ),
                (
                    "shipping",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                        verbose_name="Плата за доставку",
                    ),
                ),
                (
                    "shipping_method",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="Способ доставки"
                    ),
                ),
                (
                    "status",
                    models.CharField(blank=True, max_length=100, verbose_name="Статус"),
                ),
                ("date_placed", models.DateTimeField(db_index=True, editable=False)),
                ("order_time", models.DateTimeField(blank=True, db_index=True)),
                (
                    "date_finish",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                ("has_review", models.BooleanField(db_index=True, default=False)),
                (
                    "is_open",
                    models.BooleanField(
                        db_index=True, default=False, verbose_name="Заказ просмотрен"
                    ),
                ),
            ],
            options={
                "verbose_name": "Заказ",
                "verbose_name_plural": "Заказы",
                "ordering": ["-date_placed"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OrderDiscount",
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
                    "category",
                    models.CharField(
                        choices=[
                            ("Корзина", "Скидка на элементы корзины"),
                            ("Доставка", "Скидка на доставку"),
                            ("Отложенная", "Отложенная скидка"),
                        ],
                        default="Корзина",
                        max_length=64,
                        verbose_name="Категория скидки",
                    ),
                ),
                (
                    "offer_id",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="ID Предложения"
                    ),
                ),
                (
                    "offer_name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=128,
                        verbose_name="Название предложения",
                    ),
                ),
                (
                    "voucher_id",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="D Промокода"
                    ),
                ),
                (
                    "voucher_code",
                    models.CharField(
                        blank=True, db_index=True, max_length=128, verbose_name="Код"
                    ),
                ),
                (
                    "frequency",
                    models.PositiveIntegerField(null=True, verbose_name="Частота"),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="Сумма"
                    ),
                ),
                ("message", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Скидка в заказе",
                "verbose_name_plural": "Скидки в заказах",
                "ordering": ["pk"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OrderLineDiscount",
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
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                        verbose_name="Скидка позиции",
                    ),
                ),
            ],
            options={
                "verbose_name": "Скидка позиции заказа",
                "verbose_name_plural": "Скидки позиций заказов",
                "ordering": ["pk"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PaymentEvent",
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
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Дата создания"
                    ),
                ),
            ],
            options={
                "verbose_name": "Платежное событие",
                "verbose_name_plural": "Платежные события",
                "ordering": ["-date_created"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PaymentEventType",
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
                    models.CharField(max_length=128, unique=True, verbose_name="Имя"),
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
            ],
            options={
                "verbose_name": "Тип платежного события",
                "verbose_name_plural": "Типы платежных событий",
                "ordering": ("name",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ShippingAddress",
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
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Коментарий курьеру по поводу адреса доставки",
                        verbose_name="Коментарий курьеру",
                    ),
                ),
            ],
            options={
                "verbose_name": "Адрес доставки",
                "verbose_name_plural": "Адреса доставки",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ShippingEvent",
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
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Это может быть номер отправки или номер отслеживания.",
                        verbose_name="Заметка события",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Дата создания"
                    ),
                ),
            ],
            options={
                "verbose_name": "Событие доставки",
                "verbose_name_plural": "События доставки",
                "ordering": ["-date_created"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ShippingEventType",
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
                    models.CharField(max_length=255, unique=True, verbose_name="Имя"),
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
            ],
            options={
                "verbose_name": "Тип события доставки",
                "verbose_name_plural": "Типы событий доставки",
                "ordering": ("name",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Surcharge",
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
                        max_length=128, verbose_name="Название дополнительного сбора"
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        max_length=128, verbose_name="Код дополнительных сборов"
                    ),
                ),
                (
                    "money",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                        verbose_name="Сумма дополнительных сборов",
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
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="surcharges",
                        to="order.order",
                        verbose_name="Дополнительные сборы",
                    ),
                ),
            ],
            options={
                "verbose_name": "Дополнительный сбор",
                "verbose_name_plural": "Дополнительные сборы",
                "ordering": ["pk"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ShippingEventQuantity",
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
                ("quantity", models.PositiveIntegerField(verbose_name="Количество")),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="line_quantities",
                        to="order.shippingevent",
                        verbose_name="Событие",
                    ),
                ),
                (
                    "line",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shipping_event_quantities",
                        to="order.line",
                        verbose_name="Позиция",
                    ),
                ),
            ],
            options={
                "verbose_name": "Событие доставки - Количество",
                "verbose_name_plural": "События доставок - Количества",
            },
        ),
        migrations.AddField(
            model_name="shippingevent",
            name="event_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="order.shippingeventtype",
                verbose_name="Тип события",
            ),
        ),
        migrations.AddField(
            model_name="shippingevent",
            name="lines",
            field=models.ManyToManyField(
                related_name="shipping_events",
                through="order.ShippingEventQuantity",
                to="order.line",
                verbose_name="Позиции",
            ),
        ),
        migrations.AddField(
            model_name="shippingevent",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shipping_events",
                to="order.order",
                verbose_name="Заказ",
            ),
        ),
        migrations.CreateModel(
            name="PaymentEventQuantity",
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
                ("quantity", models.PositiveIntegerField(verbose_name="Количество")),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="line_quantities",
                        to="order.paymentevent",
                        verbose_name="Событие",
                    ),
                ),
                (
                    "line",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_event_quantities",
                        to="order.line",
                        verbose_name="Позиция",
                    ),
                ),
            ],
            options={
                "verbose_name": "Событие платежа - Количество",
                "verbose_name_plural": "События платежей - Количества",
            },
        ),
        migrations.AddField(
            model_name="paymentevent",
            name="event_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="order.paymenteventtype",
                verbose_name="Тип события",
            ),
        ),
        migrations.AddField(
            model_name="paymentevent",
            name="lines",
            field=models.ManyToManyField(
                through="order.PaymentEventQuantity",
                to="order.line",
                verbose_name="Позиции",
            ),
        ),
        migrations.AddField(
            model_name="paymentevent",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_events",
                to="order.order",
                verbose_name="Заказ",
            ),
        ),
        migrations.AddField(
            model_name="paymentevent",
            name="shipping_event",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_events",
                to="order.shippingevent",
            ),
        ),
        migrations.CreateModel(
            name="OrderStatusChange",
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
                    "old_status",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Старый статус"
                    ),
                ),
                (
                    "new_status",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Новый статус"
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_changes",
                        to="order.order",
                        verbose_name="Изменение статуса заказа",
                    ),
                ),
            ],
            options={
                "verbose_name": "Изменение статуса заказа",
                "verbose_name_plural": "Изменения статусов заказов",
                "ordering": ["-date_created"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OrderNote",
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
                    "note_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Комментарий к заказу", "Комментарий к заказу"),
                            ("Заметка менеджера", "Заметка менеджера"),
                            ("Заметка персоналу", "Заметка персоналу"),
                            ("Системная заметка", "Системная заметка"),
                        ],
                        default="Заметка менеджера",
                        max_length=30,
                        verbose_name="Тип примечания",
                    ),
                ),
                ("message", models.TextField(verbose_name="Сообщение")),
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
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notes",
                        to="order.order",
                        verbose_name="Заказ",
                    ),
                ),
            ],
            options={
                "verbose_name": "Примечание к заказу",
                "verbose_name_plural": "Примечания к заказам",
                "ordering": ["-date_updated"],
                "abstract": False,
            },
        ),
    ]
