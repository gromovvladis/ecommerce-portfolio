# Generated by Django 4.2.11 on 2025-01-14 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("order", "0001_initial"),
        ("store", "0001_initial"),
        ("delivery", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverysession",
            name="stores",
            field=models.ManyToManyField(to="store.store"),
        ),
        migrations.AddField(
            model_name="deliveryorder",
            name="courier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="delivery.courier",
            ),
        ),
        migrations.AddField(
            model_name="deliveryorder",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="order.order"
            ),
        ),
        migrations.AddField(
            model_name="deliveryorder",
            name="store",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="store.store",
            ),
        ),
        migrations.AddField(
            model_name="couriershift",
            name="courier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="delivery.courier"
            ),
        ),
        migrations.AddField(
            model_name="couriershift",
            name="routes",
            field=models.ManyToManyField(to="delivery.route"),
        ),
    ]
