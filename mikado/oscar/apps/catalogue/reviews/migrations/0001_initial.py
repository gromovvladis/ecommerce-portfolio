# Generated by Django 4.2.11 on 2024-04-01 14:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import oscar.apps.catalogue.reviews.utils
import oscar.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalogue", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductReview",
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
                    "score",
                    models.SmallIntegerField(
                        choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)],
                        verbose_name="Score",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=255,
                        validators=[oscar.core.validators.non_whitespace],
                        verbose_name="Title",
                    ),
                ),
                ("body", models.TextField(verbose_name="Body")),
                (
                    "name",
                    models.CharField(blank=True, max_length=255, verbose_name="Name"),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="Email"),
                ),
                ("homepage", models.URLField(blank=True, verbose_name="URL")),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[
                            (0, "Requires moderation"),
                            (1, "Approved"),
                            (2, "Rejected"),
                        ],
                        default=oscar.apps.catalogue.reviews.utils.get_default_review_status,
                        verbose_name="Status",
                    ),
                ),
                (
                    "total_votes",
                    models.IntegerField(default=0, verbose_name="Total Votes"),
                ),
                (
                    "delta_votes",
                    models.IntegerField(
                        db_index=True, default=0, verbose_name="Delta Votes"
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="catalogue.product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Product review",
                "verbose_name_plural": "Product reviews",
                "ordering": ["-delta_votes", "id"],
                "abstract": False,
                "unique_together": {("product", "user")},
            },
        ),
        migrations.CreateModel(
            name="Vote",
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
                    "delta",
                    models.SmallIntegerField(
                        choices=[(1, "Up"), (-1, "Down")], verbose_name="Delta"
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "review",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="reviews.productreview",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review_votes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Vote",
                "verbose_name_plural": "Votes",
                "ordering": ["-date_created"],
                "abstract": False,
                "unique_together": {("user", "review")},
            },
        ),
    ]
