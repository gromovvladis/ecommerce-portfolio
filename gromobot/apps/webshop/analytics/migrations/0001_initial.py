# Generated by Django 4.2.11 on 2025-03-20 09:42

from decimal import Decimal
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
            name='ProductRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_views', models.PositiveIntegerField(default=0, verbose_name='Просмотры товара')),
                ('num_basket_additions', models.PositiveIntegerField(default=0, verbose_name='Дополнения корзины')),
                ('num_purchases', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Покупки')),
                ('score', models.FloatField(default=0.0, verbose_name='Счет')),
            ],
            options={
                'verbose_name': 'Запись товара',
                'verbose_name_plural': 'Записи товаров',
                'ordering': ['-num_purchases'],
            },
        ),
        migrations.CreateModel(
            name='UserProductView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Просмотр товара пользователем',
                'verbose_name_plural': 'Просмотры товара пользователями',
                'ordering': ['-pk'],
            },
        ),
        migrations.CreateModel(
            name='UserSearch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.CharField(db_index=True, max_length=255, verbose_name='Поисковое условие')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Поисковый запрос пользователя',
                'verbose_name_plural': 'Поисковые запросы пользователей',
                'ordering': ['-pk'],
            },
        ),
        migrations.CreateModel(
            name='UserRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_product_views', models.PositiveIntegerField(default=0, verbose_name='Просмотры товара')),
                ('num_basket_additions', models.PositiveIntegerField(default=0, verbose_name='Дополнения корзины')),
                ('num_orders', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Количество заказов')),
                ('num_order_lines', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Количество позиций')),
                ('num_order_items', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Количество товаров')),
                ('total_spent', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Общая сумма покупок')),
                ('date_last_order', models.DateTimeField(blank=True, null=True, verbose_name='Дата последнего заказа')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Запись пользователя',
                'verbose_name_plural': 'Записи пользователей',
            },
        ),
    ]
