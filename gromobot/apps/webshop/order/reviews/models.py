from core.compat import AUTH_USER_MODEL
from django.db import models
from django.urls import reverse


class OrderReview(models.Model):
    """
    A review of a order
    """

    order = models.ForeignKey(
        "order.Order", related_name="reviews", null=True, on_delete=models.CASCADE
    )

    # Scores are between 0 and 5
    SCORE_CHOICES = tuple([(x, x) for x in range(5, 0, -1)])
    score = models.SmallIntegerField("Оценка", choices=SCORE_CHOICES)

    body = models.TextField("Текст отзыва")

    # User information.
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="order_reviews",
    )

    UNKNOWN, HELPFUL, UNHELPFUL = 0, 1, 2
    STATUS_CHOICES = (
        (UNKNOWN, "Неизвестно"),
        (HELPFUL, "Полезный"),
        (UNHELPFUL, "Неполезный"),
    )

    status = models.SmallIntegerField("Статус", choices=STATUS_CHOICES, default=UNKNOWN)

    date_created = models.DateTimeField(auto_now_add=True)

    is_open = models.BooleanField("Отзыв просмотрен", default=False, db_index=True)

    class Meta:
        app_label = "order_reviews"
        unique_together = (("order", "user"),)
        verbose_name = "Отзыв на заказ"
        verbose_name_plural = "Отзывы на заказы"

    def get_absolute_url(self):
        kwargs = {
            "order_slug": self.order.slug,
            "order_pk": self.order.id,
            "pk": self.id,
        }
        return reverse("customer:feedbacks", kwargs=kwargs)

    def __str__(self):
        return self.body

    def clean(self):
        self.body = self.body.strip()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    @property
    def reviewer_name(self):
        if self.user:
            return self.user.get_full_name()
