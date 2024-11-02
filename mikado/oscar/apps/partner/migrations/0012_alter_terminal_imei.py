# Generated by Django 4.2.11 on 2024-11-02 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("partner", "0011_rename_device_model_terminal_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="terminal",
            name="imei",
            field=models.CharField(
                blank=True,
                max_length=128,
                null=True,
                unique=True,
                verbose_name="Код imei",
            ),
        ),
    ]
