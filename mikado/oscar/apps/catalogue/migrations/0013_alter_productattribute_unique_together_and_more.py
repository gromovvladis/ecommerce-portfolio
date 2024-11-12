# Generated by Django 4.2.11 on 2024-11-12 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0012_productattribute_is_variant"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="productattribute",
            unique_together={("attribute", "product", "product_class")},
        ),
        migrations.RemoveField(
            model_name="product",
            name="variant",
        ),
        migrations.AlterField(
            model_name="productattribute",
            name="is_variant",
            field=models.BooleanField(
                default=False, verbose_name="Используется для вариаций?"
            ),
        ),
    ]
