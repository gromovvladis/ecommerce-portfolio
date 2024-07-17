# Generated by Django 4.2.11 on 2024-06-26 07:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserAddress",
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
                    "line1",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Улица, дом"
                    ),
                ),
                (
                    "line2",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Квартира"
                    ),
                ),
                (
                    "line3",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Подъезд"
                    ),
                ),
                (
                    "line4",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Этаж"
                    ),
                ),
                (
                    "search_text",
                    models.TextField(
                        editable=False,
                        verbose_name="Адрес для поиска. Используется только для поиска",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Коментарий курьеру по поводу адреса доставки",
                        verbose_name="Коментарий курьеру",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Адрес пользователя",
                "verbose_name_plural": "Адреса пользователей",
                "abstract": False,
            },
        ),
    ]
