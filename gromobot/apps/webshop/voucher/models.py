from decimal import Decimal

from core.compat import AUTH_USER_MODEL
from django.core import exceptions
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class VoucherSet(models.Model):
    """A collection of vouchers (potentially auto-generated)

    a VoucherSet is a group of voucher that are generated
    automatically.

    - count: the number of vouchers in the set. If this is kept at
    zero, vouchers are created when and as needed.

    - code_length: the length of the voucher code. Codes are by default created
    with groups of 4 characters: XXXX-XXXX-XXXX. The dashes (-) do not count for
    the code_length.

    - :py:attr:`.start_datetime` and :py:attr:`.end_datetime` together define the validity
      range for all vouchers in the set.
    """

    name = models.CharField(verbose_name="Имя", max_length=100, unique=True)
    count = models.PositiveIntegerField(verbose_name="Количество ваучеров")
    code_length = models.IntegerField(verbose_name="Длина кода кода", default=12)
    description = models.TextField(verbose_name="Описание")
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    start_datetime = models.DateTimeField("Дата и время начала")
    end_datetime = models.DateTimeField("Дата и время окончания")

    class Meta:
        app_label = "voucher"
        get_latest_by = "date_created"
        ordering = ["-date_created"]
        verbose_name = "Набор ваучеров"
        verbose_name_plural = "Наборы ваучеров"

    def __str__(self):
        return self.name

    def clean(self):
        if (
            self.start_datetime
            and self.end_datetime
            and (self.start_datetime > self.end_datetime)
        ):
            raise exceptions.ValidationError(
                "Дата окончания должна быть позже даты начала."
            )

    def update_count(self):
        vouchers_count = self.vouchers.count()
        if self.count != vouchers_count:
            self.count = vouchers_count
            self.save()

    def is_active(self, test_datetime=None):
        """Test whether this voucher set is currently active."""
        test_datetime = test_datetime or timezone.now()
        return self.start_datetime <= test_datetime <= self.end_datetime

    @property
    def num_basket_additions(self):
        value = self.vouchers.aggregate(result=Sum("num_basket_additions"))
        return value["result"]

    @property
    def num_orders(self):
        value = self.vouchers.aggregate(result=Sum("num_orders"))
        return value["result"]

    @property
    def total_discount(self):
        value = self.vouchers.aggregate(result=Sum("total_discount"))
        return value["result"]


class Voucher(models.Model):
    """
    A voucher.  This is simply a link to a collection of offers.

    Note that there are three possible "usage" modes:
    (a) Single use
    (b) Multi-use
    (c) Once per customer

    Oscar enforces those modes by creating VoucherApplication
    instances when a voucher is used for an order.
    """

    name = models.CharField(
        "Имя",
        max_length=128,
        unique=True,
        help_text=(
            "Это будет показано на странице оформления"
            "и корзине, как только купон будет введен"
        ),
    )
    code = models.CharField(
        "Код",
        max_length=128,
        db_index=True,
        unique=True,
        help_text="Нечувствителен к регистру/пробелы не допускаются",
    )
    offers = models.ManyToManyField(
        "offer.ConditionalOffer",
        related_name="vouchers",
        verbose_name="Предложения",
        limit_choices_to={"offer_type": "Voucher"},
    )

    SINGLE_USE, MULTI_USE, ONCE_PER_CUSTOMER = (
        "Single use",
        "Multi-use",
        "Once per customer",
    )
    USAGE_CHOICES = (
        (SINGLE_USE, "Может быть использован один раз одним клиентом"),
        (MULTI_USE, "Может использоваться несколько раз несколькими клиентами"),
        (ONCE_PER_CUSTOMER, "Можно использовать только один раз для каждого клиента."),
    )
    usage = models.CharField(
        "Использований", max_length=128, choices=USAGE_CHOICES, default=MULTI_USE
    )

    start_datetime = models.DateTimeField("Дата и время начала", db_index=True)
    end_datetime = models.DateTimeField("Дата и время окончания", db_index=True)

    # Reporting information. Not used to enforce any consumption limits.
    num_basket_additions = models.PositiveIntegerField(
        "Раз добавлено в корзину", default=0
    )
    num_orders = models.PositiveIntegerField("Количество заказов", default=0)
    total_discount = models.DecimalField(
        "Общая скидка", decimal_places=2, max_digits=12, default=Decimal("0.00")
    )

    voucher_set = models.ForeignKey(
        "voucher.VoucherSet",
        null=True,
        blank=True,
        related_name="vouchers",
        on_delete=models.CASCADE,
    )

    date_created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = "voucher"
        ordering = ["-date_created"]
        get_latest_by = "date_created"
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.name

    def clean(self):
        if (
            self.start_datetime
            and self.end_datetime
            and (self.start_datetime > self.end_datetime)
        ):
            raise exceptions.ValidationError(
                "Дата окончания должна быть позже даты начала."
            )

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def is_active(self, test_datetime=None):
        """
        Test whether this voucher is currently active.
        """
        test_datetime = test_datetime or timezone.now()
        return self.start_datetime <= test_datetime <= self.end_datetime

    def is_expired(self):
        """
        Test whether this voucher has passed its expiration date
        """
        now = timezone.now()
        return self.end_datetime < now

    def is_available_to_user(self, user=None):
        """
        Test whether this voucher is available to the passed user.

        Returns a tuple of a boolean for whether it is successful, and a
        availability message.
        """
        is_available, message = False, ""
        if self.usage == self.SINGLE_USE:
            is_available = not self.applications.exists()
            if not is_available:
                message = "Этот промокод уже использован"
        elif self.usage == self.MULTI_USE:
            is_available = True
        elif self.usage == self.ONCE_PER_CUSTOMER:
            if not user.is_authenticated:
                is_available = False
                message = "Этот промокод доступен только авторизованным пользователям."
            else:
                is_available = not self.applications.filter(
                    voucher=self, user=user
                ).exists()
                if not is_available:
                    message = "Вы уже использовали этот промокод в предыдущем заказе."

        return is_available, message

    def is_available_for_basket(self, basket):
        """
        Tests whether this voucher is available to the passed basket.

        Returns a tuple of a boolean for whether it is successful, and a
        availability message.
        """
        is_available, message = self.is_available_to_user(user=basket.owner)
        if not is_available:
            return False, message

        is_available, message = False, "Этот промокод недоступен для этой корзины."

        for offer in self.offers.all():
            if offer.is_condition_satisfied(basket=basket):
                is_available = True
                message = ""
                break
        return is_available, message

    def record_usage(self, order, user):
        """
        Records a usage of this voucher in an order.
        """
        if user.is_authenticated:
            self.applications.create(voucher=self, order=order, user=user)
        else:
            self.applications.create(voucher=self, order=order)
        self.num_orders += 1
        self.save()

    record_usage.alters_data = True

    def record_discount(self, discount):
        """
        Record a discount that this offer has given
        """
        self.total_discount += discount["discount"]
        self.save()

    record_discount.alters_data = True


class VoucherApplication(models.Model):
    """
    For tracking how often a voucher has been used in an order.

    This is used to enforce the voucher usage mode in
    Voucher.is_available_to_user, and created in Voucher.record_usage.
    """

    voucher = models.ForeignKey(
        "voucher.Voucher",
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Промокод",
    )

    # It is possible for an anonymous user to apply a voucher so we need to
    # allow the user to be nullable
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, verbose_name="Заказ"
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = "voucher"
        ordering = ["-date_created"]
        verbose_name = "Предложение промокода"
        verbose_name_plural = "Предложения промокодов"

    def __str__(self):
        return ("'%(voucher)s' использован пользователем - '%(user)s'") % {
            "voucher": self.voucher,
            "user": self.user,
        }
