# Generated by Django 4.2.11 on 2024-10-25 05:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("delivery", "0004_alter_deliveryzona_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="deliveryzona",
            options={
                "permissions": (
                    ("full_access", "Полный доступ"),
                    ("read", "Просматривать доставки"),
                    ("update_delivery", "Изменять доставки"),
                ),
                "verbose_name": "Зона доставки",
                "verbose_name_plural": "Зоны доставки",
            },
        ),
    ]
