# Generated by Django 4.2.11 on 2025-01-14 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("order", "0001_initial"),
        ("communication", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="order",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="order.order"
            ),
        ),
    ]
