# Generated by Django 4.2.11 on 2024-10-25 03:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("delivery", "0003_alter_courier_profile"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="deliveryzona",
            options={
                "permissions": (
                    ("full_access", "Полный доступ"),
                    ("read", "Просматривать доставки"),
                    ("change_delivery", "Изменять доставки"),
                ),
                "verbose_name": "Зона доставки",
                "verbose_name_plural": "Зоны доставки",
            },
        ),
    ]
