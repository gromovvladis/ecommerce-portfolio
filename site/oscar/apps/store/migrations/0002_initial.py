# Generated by Django 4.2.11 on 2024-11-25 08:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalogue", "0001_initial"),
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="store",
            name="users",
            field=models.ManyToManyField(
                blank=True,
                related_name="stores",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователи",
            ),
        ),
        migrations.AddField(
            model_name="stockrecord",
            name="bar_codes",
            field=models.ManyToManyField(
                blank=True,
                related_name="bars",
                to="store.barcode",
                verbose_name="Штрих-коды",
            ),
        ),
        migrations.AddField(
            model_name="stockrecord",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="stockrecords",
                to="catalogue.product",
                verbose_name="товар",
            ),
        ),
        migrations.AddField(
            model_name="stockrecord",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="stockrecords",
                to="store.store",
                verbose_name="Точка продажи",
            ),
        ),
        migrations.AddField(
            model_name="stockalert",
            name="stockrecord",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="alerts",
                to="store.stockrecord",
                verbose_name="Товарная запись",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="stockrecord",
            unique_together={("store", "product")},
        ),
    ]
