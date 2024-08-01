# Generated by Django 4.2.11 on 2024-08-01 03:40

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("partner", "0003_alter_stockalert_status"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("order", "0003_shippingaddress_coords_lat_and_more"),
        ("delivery", "0002_alter_deliveryzona_coords"),
    ]

    operations = [
        migrations.CreateModel(
            name="AbstractCourier",
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
                ("passport_info", models.CharField(max_length=255)),
                ("vehicle_info", models.CharField(max_length=255)),
                (
                    "type",
                    models.CharField(
                        choices=[("pedestrian", "Пешеход"), ("driving", "Автокурьер")],
                        default="driving",
                        max_length=50,
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
                "ordering": ["user", "passport_info", "vehicle_info"],
                "get_latest_by": "user_username",
                "unique_together": {("user", "type")},
            },
        ),
        migrations.CreateModel(
            name="AbstractCourierShift",
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
            ],
            options={
                "verbose_name": "Смена курьера",
                "verbose_name_plural": "Смены курьера",
                "ordering": ["-start_time"],
                "get_latest_by": "end_time",
            },
        ),
        migrations.CreateModel(
            name="AbstractDeliveryOrder",
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
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="order.order"
                    ),
                ),
            ],
            options={
                "verbose_name": "Заказ доставки",
                "verbose_name_plural": "Заказы доставки",
                "ordering": ["-delivery_time"],
            },
        ),
        migrations.CreateModel(
            name="AbstractDeliverySession",
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
            ],
            options={
                "verbose_name": "Торговая сессия",
                "verbose_name_plural": "Торговые сессии",
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="AbstractKitchen",
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
                    "partner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="partner.partner",
                    ),
                ),
            ],
            options={
                "verbose_name": "Кухня",
                "verbose_name_plural": "Кухни",
                "ordering": ["partner"],
            },
        ),
        migrations.CreateModel(
            name="AbstractRoute",
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
            ],
            options={
                "verbose_name": "Маршрут курьера",
                "verbose_name_plural": "Маршруты курьеров",
                "ordering": ["start_time"],
            },
        ),
        migrations.CreateModel(
            name="AbstractTrip",
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
                "index_together": {("start_time", "end_time")},
            },
        ),
        migrations.RemoveField(
            model_name="deliveryzona",
            name="description",
        ),
        migrations.AddField(
            model_name="deliveryzona",
            name="name",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Название"
            ),
        ),
        migrations.CreateModel(
            name="Courier",
            fields=[
                (
                    "abstractcourier_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="delivery.abstractcourier",
                    ),
                ),
            ],
            bases=("delivery.abstractcourier",),
        ),
        migrations.CreateModel(
            name="CourierShift",
            fields=[
                (
                    "abstractcouriershift_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="delivery.abstractcouriershift",
                    ),
                ),
            ],
            bases=("delivery.abstractcouriershift",),
        ),
        migrations.CreateModel(
            name="DeliveryOrder",
            fields=[
                (
                    "abstractdeliveryorder_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="delivery.abstractdeliveryorder",
                    ),
                ),
            ],
            bases=("delivery.abstractdeliveryorder",),
        ),
        migrations.CreateModel(
            name="DeliverySession",
            fields=[
                (
                    "abstractdeliverysession_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="delivery.abstractdeliverysession",
                    ),
                ),
            ],
            bases=("delivery.abstractdeliverysession",),
        ),
        migrations.CreateModel(
            name="Kitchen",
            fields=[
                (
                    "abstractkitchen_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="delivery.abstractkitchen",
                    ),
                ),
            ],
            bases=("delivery.abstractkitchen",),
        ),
        migrations.CreateModel(
            name="Route",
            fields=[
                (
                    "abstractroute_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="delivery.abstractroute",
                    ),
                ),
            ],
            bases=("delivery.abstractroute",),
        ),
        migrations.CreateModel(
            name="Trip",
            fields=[
                (
                    "abstracttrip_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="delivery.abstracttrip",
                    ),
                ),
            ],
            bases=("delivery.abstracttrip",),
        ),
        migrations.AddField(
            model_name="abstractroute",
            name="courier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="delivery.courier"
            ),
        ),
        migrations.AddField(
            model_name="abstractroute",
            name="trips",
            field=models.ManyToManyField(to="delivery.trip"),
        ),
        migrations.AddField(
            model_name="abstractkitchen",
            name="orders",
            field=models.ManyToManyField(
                related_name="kitchen_orders", to="delivery.deliveryorder"
            ),
        ),
        migrations.AddField(
            model_name="abstractdeliverysession",
            name="couriers",
            field=models.ManyToManyField(to="delivery.courier"),
        ),
        migrations.AddField(
            model_name="abstractdeliverysession",
            name="orders",
            field=models.ManyToManyField(to="delivery.deliveryorder"),
        ),
        migrations.AddField(
            model_name="abstractdeliveryorder",
            name="courier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="delivery.courier",
            ),
        ),
        migrations.AddField(
            model_name="abstractdeliveryorder",
            name="kitchen",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="delivery.kitchen",
            ),
        ),
        migrations.AddField(
            model_name="abstractcouriershift",
            name="courier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="delivery.courier"
            ),
        ),
        migrations.AddField(
            model_name="abstractcouriershift",
            name="routes",
            field=models.ManyToManyField(to="delivery.route"),
        ),
        migrations.AlterIndexTogether(
            name="abstractroute",
            index_together={("start_time", "end_time")},
        ),
        migrations.AlterIndexTogether(
            name="abstractdeliveryorder",
            index_together={("pickup_time", "delivery_time")},
        ),
        migrations.AlterUniqueTogether(
            name="abstractcouriershift",
            unique_together={("courier", "start_time")},
        ),
    ]
