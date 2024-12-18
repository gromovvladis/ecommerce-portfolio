# Generated by Django 4.2.11 on 2024-11-25 08:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0013_groupevotor"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    phonenumber_field.modelfields.PhoneNumberField(
                        db_index=True,
                        help_text="Формат телефона: '+7 (900) 000-0000",
                        max_length=12,
                        region=None,
                        unique=True,
                        verbose_name="Номер телефона",
                    ),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="Email"),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=255, verbose_name="Имя"),
                ),
                (
                    "telegram_id",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Телеграм ID"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Повар, Курьер, Менеджер и т.д.",
                        verbose_name="Это сотрудник?",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Активен пользователь или нет",
                        verbose_name="Активен",
                    ),
                ),
                (
                    "is_email_verified",
                    models.BooleanField(
                        default=False,
                        help_text="Email подтвержден или нет",
                        verbose_name="Email verified",
                    ),
                ),
                (
                    "notif",
                    models.CharField(
                        choices=[
                            ("order", "Только уведомления о заказах"),
                            (
                                "offer",
                                "Уведомления об персональных акциях и предложениях",
                            ),
                            ("off", "Отключить уведомления"),
                        ],
                        db_index=True,
                        default="order",
                        max_length=128,
                        verbose_name="Уведомления",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Дата регистрации",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Дата последнего входа ",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
                "db_table": "auth_user",
                "ordering": [
                    "username",
                    "email",
                    "password",
                    "name",
                    "is_staff",
                    "is_active",
                    "is_email_verified",
                    "date_joined",
                    "last_login",
                ],
            },
        ),
        migrations.CreateModel(
            name="Staff",
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
                    "first_name",
                    models.CharField(max_length=255, null=True, verbose_name="Имя"),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Фамилия"
                    ),
                ),
                (
                    "middle_name",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Отчество"
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[("М", "Мужчина"), ("Ж", "Женщина")],
                        max_length=1,
                        null=True,
                        verbose_name="Пол",
                    ),
                ),
                (
                    "age",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Возраст"
                    ),
                ),
                (
                    "telegram_id",
                    models.CharField(
                        blank=True,
                        max_length=128,
                        null=True,
                        verbose_name="ID Телеграм чата",
                    ),
                ),
                (
                    "evotor_id",
                    models.CharField(
                        blank=True, max_length=128, null=True, verbose_name="ID Эвотор"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Активен сотрудник или нет",
                        verbose_name="Активен",
                    ),
                ),
                (
                    "notif",
                    models.CharField(
                        choices=[
                            ("new-order", "Только уведомления о новых заказах"),
                            (
                                "status-order",
                                "Уведомления об изменении заказов и новых заказах",
                            ),
                            ("technical", "Технические уведомления"),
                            ("off", "Отключить уведомления"),
                        ],
                        db_index=True,
                        default="new-order",
                        max_length=128,
                        verbose_name="Уведомления",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="staffs",
                        to="auth.group",
                        verbose_name="Должность",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Персонал",
                "verbose_name_plural": "Персонал",
                "db_table": "auth_staff",
                "permissions": (("full_access", "Полный доступ ко всему сайту"),),
            },
        ),
    ]
