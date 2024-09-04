# Generated by Django 4.2.11 on 2024-09-04 07:29

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("user", "0001_initial"),
        ("partner", "0002_initial"),
        ("order", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Courier",
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
                        choices=[("pedestrian", "Пешеход"), ("driving", "Автокурьер")],
                        default="driving",
                        max_length=50,
                    ),
                ),
                (
                    "profile",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="user.profile"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Курьер",
                "verbose_name_plural": "Курьеры",
                "ordering": ["user", "profile"],
                "get_latest_by": "user_username",
                "abstract": False,
                "unique_together": {("user", "type")},
            },
        ),
        migrations.CreateModel(
            name="DeliveryOrder",
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
                ("pickup_time", models.DateTimeField()),
                ("delivery_time", models.DateTimeField()),
                (
                    "courier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="delivery.courier",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="order.order"
                    ),
                ),
                (
                    "partner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="partner.partner",
                    ),
                ),
            ],
            options={
                "verbose_name": "Заказ доставки",
                "verbose_name_plural": "Заказы доставки",
                "ordering": ["-delivery_time"],
                "abstract": False,
                "index_together": {("pickup_time", "delivery_time")},
            },
        ),
        migrations.CreateModel(
            name="DeliveryZona",
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
                        blank=True, max_length=255, null=True, verbose_name="Название"
                    ),
                ),
                (
                    "order_price",
                    models.PositiveIntegerField(
                        default=700, verbose_name="Минимальная цена заказа"
                    ),
                ),
                (
                    "delivery_price",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Стоимость доставки"
                    ),
                ),
                (
                    "coords",
                    models.CharField(
                        help_text="Координаты в формате: [[55.730719,37.583146],[55.719093,37.677903]] Получить можно на сайте: http://mapinit.ru/coords/",
                        max_length=1020,
                        verbose_name="Координаты",
                    ),
                ),
                (
                    "isAvailable",
                    models.BooleanField(
                        default=True, max_length=255, verbose_name="Доставка доступна"
                    ),
                ),
                (
                    "isHide",
                    models.BooleanField(
                        default=False, max_length=255, verbose_name="Убрать с карты"
                    ),
                ),
            ],
            options={
                "verbose_name": "Зона доставки",
                "verbose_name_plural": "Зоны доставки",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Trip",
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
                ("start_point_coords", models.CharField(max_length=255)),
                ("start_point_address", models.CharField(max_length=255)),
                ("start_zona_id", models.IntegerField()),
                ("end_point_coords", models.CharField(max_length=255)),
                ("end_point_address", models.CharField(max_length=255)),
                ("end_zona_id", models.IntegerField()),
                ("duration", models.DurationField()),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("distance", models.FloatField()),
            ],
            options={
                "verbose_name": "Маршрут",
                "verbose_name_plural": "Маршруты",
                "ordering": ["start_time"],
                "abstract": False,
                "index_together": {("start_time", "end_time")},
            },
        ),
        migrations.CreateModel(
            name="Route",
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
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                (
                    "courier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="delivery.courier",
                    ),
                ),
                ("trips", models.ManyToManyField(to="delivery.trip")),
            ],
            options={
                "verbose_name": "Маршрут курьера",
                "verbose_name_plural": "Маршруты курьеров",
                "ordering": ["start_time"],
                "abstract": False,
                "index_together": {("start_time", "end_time")},
            },
        ),
        migrations.CreateModel(
            name="DeliverySession",
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
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("open_time", models.DateTimeField(auto_now_add=True)),
                ("close_time", models.DateTimeField()),
                ("couriers", models.ManyToManyField(to="delivery.courier")),
                ("orders", models.ManyToManyField(to="delivery.deliveryorder")),
                ("partners", models.ManyToManyField(to="partner.partner")),
            ],
            options={
                "verbose_name": "Торговая сессия",
                "verbose_name_plural": "Торговые сессии",
                "ordering": ["-date"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CourierShift",
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
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("orders_completed", models.IntegerField(default=0)),
                ("distance_traveled", models.FloatField(default=0.0)),
                ("time_on_road", models.DurationField(default=datetime.timedelta(0))),
                (
                    "courier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="delivery.courier",
                    ),
                ),
                ("routes", models.ManyToManyField(to="delivery.route")),
            ],
            options={
                "verbose_name": "Смена курьера",
                "verbose_name_plural": "Смены курьера",
                "ordering": ["-start_time"],
                "get_latest_by": "end_time",
                "abstract": False,
                "unique_together": {("courier", "start_time")},
            },
        ),
    ]
