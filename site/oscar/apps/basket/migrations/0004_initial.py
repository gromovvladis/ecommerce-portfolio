# Generated by Django 4.2.11 on 2024-12-18 13:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("voucher", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("store", "0001_initial"),
        ("basket", "0003_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="basket",
            name="owner",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="baskets",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Владелец",
            ),
        ),
        migrations.AddField(
            model_name="basket",
            name="store",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="baskets",
                to="store.store",
                verbose_name="Магазин",
            ),
        ),
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
