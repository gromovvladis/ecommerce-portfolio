# Generated by Django 4.2.11 on 2025-03-20 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line1', models.CharField(blank=True, max_length=255, null=True, verbose_name='Улица, дом')),
                ('line2', models.PositiveIntegerField(blank=True, null=True, verbose_name='Квартира')),
                ('line3', models.PositiveIntegerField(blank=True, null=True, verbose_name='Подъезд')),
                ('line4', models.PositiveIntegerField(blank=True, null=True, verbose_name='Этаж')),
                ('coords_long', models.CharField(blank=True, max_length=255, null=True, verbose_name='Координаты долгота')),
                ('coords_lat', models.CharField(blank=True, max_length=255, null=True, verbose_name='Координаты широта')),
                ('search_text', models.TextField(editable=False, verbose_name='Адрес для поиска. Используется только для поиска')),
            ],
            options={
                'verbose_name': 'Адрес',
                'verbose_name_plural': 'Адреса',
            },
        ),
    ]
