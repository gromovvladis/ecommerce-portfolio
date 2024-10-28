# Generated by Django 4.2.11 on 2024-10-25 03:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("partner", "0008_alter_partner_evotor_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="barcode",
            options={
                "ordering": ("code",),
                "verbose_name": "Штрих-код",
                "verbose_name_plural": "Штрих-коды",
            },
        ),
        migrations.AlterModelOptions(
            name="partner",
            options={
                "ordering": ("name", "code"),
                "verbose_name": "Точка продажи",
                "verbose_name_plural": "Точка продажи",
            },
        ),
        migrations.AlterModelOptions(
            name="terminal",
            options={
                "ordering": ("name", "serial_number"),
                "verbose_name": "Смарт терминал Эвотор",
                "verbose_name_plural": "Смарт терминалы Эвотор",
            },
        ),
    ]
