# Generated by Django 4.2.11 on 2025-03-20 09:42

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('offer', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Это будет показано на странице оформленияи корзине, как только купон будет введен', max_length=128, unique=True, verbose_name='Имя')),
                ('code', models.CharField(db_index=True, help_text='Нечувствителен к регистру/пробелы не допускаются', max_length=128, unique=True, verbose_name='Код')),
                ('usage', models.CharField(choices=[('Single use', 'Может быть использован один раз одним клиентом'), ('Multi-use', 'Может использоваться несколько раз несколькими клиентами'), ('Once per customer', 'Можно использовать только один раз для каждого клиента.')], default='Multi-use', max_length=128, verbose_name='Использований')),
                ('start_datetime', models.DateTimeField(db_index=True, verbose_name='Дата и время начала')),
                ('end_datetime', models.DateTimeField(db_index=True, verbose_name='Дата и время окончания')),
                ('num_basket_additions', models.PositiveIntegerField(default=0, verbose_name='Раз добавлено в корзину')),
                ('num_orders', models.PositiveIntegerField(default=0, verbose_name='Количество заказов')),
                ('total_discount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Общая скидка')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('offers', models.ManyToManyField(limit_choices_to={'offer_type': 'Voucher'}, related_name='vouchers', to='offer.conditionaloffer', verbose_name='Предложения')),
            ],
            options={
                'verbose_name': 'Промокод',
                'verbose_name_plural': 'Промокоды',
                'ordering': ['-date_created'],
                'get_latest_by': 'date_created',
            },
        ),
        migrations.CreateModel(
            name='VoucherSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Имя')),
                ('count', models.PositiveIntegerField(verbose_name='Количество ваучеров')),
                ('code_length', models.IntegerField(default=12, verbose_name='Длина кода кода')),
                ('description', models.TextField(verbose_name='Описание')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('start_datetime', models.DateTimeField(verbose_name='Дата и время начала')),
                ('end_datetime', models.DateTimeField(verbose_name='Дата и время окончания')),
            ],
            options={
                'verbose_name': 'Набор ваучеров',
                'verbose_name_plural': 'Наборы ваучеров',
                'ordering': ['-date_created'],
                'get_latest_by': 'date_created',
            },
        ),
        migrations.CreateModel(
            name='VoucherApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order', verbose_name='Заказ')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('voucher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='voucher.voucher', verbose_name='Промокод')),
            ],
            options={
                'verbose_name': 'Предложение промокода',
                'verbose_name_plural': 'Предложения промокодов',
                'ordering': ['-date_created'],
            },
        ),
        migrations.AddField(
            model_name='voucher',
            name='voucher_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vouchers', to='voucher.voucherset'),
        ),
    ]
