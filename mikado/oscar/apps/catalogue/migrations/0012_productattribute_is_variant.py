# Generated by Django 4.2.11 on 2024-11-12 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0011_alter_attributeoptiongroup_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productattribute",
            name="is_variant",
            field=models.BooleanField(
                default=False, verbose_name="Используется для вариаций"
            ),
        ),
    ]
