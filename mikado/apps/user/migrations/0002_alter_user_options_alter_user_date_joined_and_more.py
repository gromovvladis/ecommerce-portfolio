# Generated by Django 4.2.11 on 2024-05-17 13:23

from django.db import migrations, models
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "ordering": [
                    "username",
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_active",
                    "is_email_verified",
                    "date_joined",
                    "last_login",
                ],
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
        ),
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Дата регистрации"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, max_length=254, verbose_name="Email"),
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(blank=True, max_length=255, verbose_name="Имя"),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(
                default=True,
                help_text="Активен пользователь или нет",
                verbose_name="Активен",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_email_verified",
            field=models.BooleanField(
                default=False,
                help_text="Email подтвержден или нет",
                verbose_name="Email verified",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_staff",
            field=models.BooleanField(
                default=False,
                help_text="Повар \\ Курьер \\ Менеджер и т.д.",
                verbose_name="Статус сотрудника",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_login",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Дата последнего входа "
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(blank=True, max_length=255, verbose_name="Фамилия"),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Формат телефона: '+79950750075",
                max_length=12,
                region=None,
                unique=True,
                verbose_name="Номер телефона",
            ),
        ),
    ]
