# Generated by Django 4.2.11 on 2024-10-16 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("partner", "0003_stockrecord_is_public"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="evotor_id",
            field=models.CharField(
                blank=True, max_length=128, verbose_name="ID Эвотор"
            ),
        ),
    ]
