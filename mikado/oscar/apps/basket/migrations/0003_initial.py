# Generated by Django 4.2.11 on 2024-06-10 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("basket", "0002_initial"),
        ("voucher", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="basket",
            name="vouchers",
            field=models.ManyToManyField(
                blank=True, to="voucher.voucher", verbose_name="Промокод"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="line",
            unique_together={("basket", "line_reference")},
        ),
    ]
