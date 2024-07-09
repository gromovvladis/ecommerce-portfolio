# Generated by Django 4.2.11 on 2024-07-09 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DeliveryZona",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "number",
                    models.PositiveIntegerField(
                        unique=True, verbose_name="Номер зоны доставки"
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Описание"
                    ),
                ),
                (
                    "order_price",
                    models.PositiveIntegerField(
                        default=700, verbose_name="Минимальная цена заказа"
                    ),
                ),
                (
                    "delivery_price",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Стоимость доставки"
                    ),
                ),
                (
                    "coords",
                    models.CharField(
                        help_text="Координаты в формате: [[55.730719,37.583146],[55.719093,37.677903]]Получить можно на сайте: http://mapinit.ru/coords/",
                        max_length=510,
                        verbose_name="Координаты",
                    ),
                ),
                (
                    "isAvailable",
                    models.BooleanField(
                        max_length=255, verbose_name="Доставка доступна"
                    ),
                ),
                (
                    "isHide",
                    models.BooleanField(max_length=255, verbose_name="Убрать с карты"),
                ),
            ],
            options={
                "verbose_name": "Зона доставки",
                "verbose_name_plural": "Зоны доставки",
                "abstract": False,
            },
        ),
    ]
