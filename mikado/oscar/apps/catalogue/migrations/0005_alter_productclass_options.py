# Generated by Django 4.2.11 on 2024-10-25 04:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0004_alter_productclass_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="productclass",
            options={
                "ordering": ["name"],
                "permissions": (
                    ("full_access", "Полный доступ к продуктам"),
                    ("read", "Просматривать товары и категории"),
                    ("change_price_and_stockrecord", "Изменять цену и наличие товаров"),
                    ("change_stockrecord", "Изменять наличие товаров"),
                ),
                "verbose_name": "Класс товара",
                "verbose_name_plural": "Классы товара",
            },
        ),
    ]
