# pylint: disable=W0621, unused-argument
from decimal import Decimal as D

from apps.webshop.templatetags.currency_filters import currency
from core.loading import get_class, get_classes, get_model

BasketDiscount, SHIPPING_DISCOUNT, ZERO_DISCOUNT = get_classes(
    "webshop.offer.results", ["BasketDiscount", "SHIPPING_DISCOUNT", "ZERO_DISCOUNT"]
)
CoverageCondition, ValueCondition = get_classes(
    "webshop.offer.conditions", ["CoverageCondition", "ValueCondition"]
)
range_anchor = get_class("webshop.offer.utils", "range_anchor")

__all__ = [
    "PercentageDiscountBenefit",
    "AbsoluteDiscountBenefit",
    "FixedUnitDiscountBenefit",
    "FixedPriceBenefit",
    "ShippingBenefit",
    "MultibuyDiscountBenefit",
    "ShippingAbsoluteDiscountBenefit",
    "ShippingFixedPriceBenefit",
    "ShippingPercentageDiscountBenefit",
]

Benefit = get_model("offer", "Benefit")


def apply_discount(line, discount, quantity, offer=None):
    """
    Apply a given discount to the passed basket
    """
    line.discount(discount, quantity, offer=offer)


class PercentageDiscountBenefit(Benefit):
    """
    An offer benefit that gives a percentage discount
    """

    _description = "%(value)s%% скидка на %(range)s"

    @property
    def name(self):
        return self._description % {"value": self.value, "range": self.range.name}

    @property
    def description(self):
        return self._description % {
            "value": self.value,
            "range": range_anchor(self.range),
        }

    class Meta:
        app_label = "offer"
        proxy = True
        verbose_name = "Процентная скидка"
        verbose_name_plural = "Процентные скидки"

    # pylint: disable=unused-argument
    def apply(
        self,
        basket,
        condition,
        offer,
        discount_percent=None,
        max_total_discount=None,
        **kwargs
    ):
        if discount_percent is None:
            discount_percent = self.value

        discount_amount_available = max_total_discount

        line_tuples = self.get_applicable_lines(offer, basket)
        discount_percent = min(discount_percent, D("100.0"))
        discount = D("0.00")
        affected_items = 0
        max_affected_items = self._effective_max_affected_items()
        for price, line in line_tuples:
            affected_items += line.quantity_with_offer_discount(offer)
            if affected_items >= max_affected_items:
                break
            if discount_amount_available == 0:
                break

            quantity_affected = min(
                line.quantity_without_offer_discount(offer),
                max_affected_items - affected_items,
            )
            if quantity_affected <= 0:
                break

            line_discount = self.round(
                discount_percent / D("100.0") * price * int(quantity_affected),
                basket.currency,
            )

            if discount_amount_available is not None:
                line_discount = min(line_discount, discount_amount_available)
                discount_amount_available -= line_discount

            apply_discount(line, line_discount, quantity_affected, offer)

            affected_items += quantity_affected
            discount += line_discount

        return BasketDiscount(discount)


class AbsoluteDiscountBenefit(Benefit):
    """
    An offer benefit that gives an absolute discount
    """

    _description = "%(value)s скидка на %(range)s"

    @property
    def name(self):
        return self._description % {
            "value": currency(self.value),
            "range": self.range.name.lower(),
        }

    @property
    def description(self):
        return self._description % {
            "value": currency(self.value),
            "range": range_anchor(self.range),
        }

    class Meta:
        app_label = "offer"
        proxy = True
        verbose_name = "Абсолютная скидка"
        verbose_name_plural = "Абсолютные скидки"

    def apply(
        self,
        basket,
        condition,
        offer,
        discount_amount=None,
        max_total_discount=None,
        **kwargs
    ):
        if discount_amount is None:
            discount_amount = self.value

        # Fetch basket lines that are in the range and available to be used in
        # an offer.
        line_tuples = self.get_applicable_lines(offer, basket)

        # Determine which lines can have the discount applied to them
        max_affected_items = self._effective_max_affected_items()
        num_affected_items = 0
        affected_items_total = D("0.00")
        lines_to_discount = []
        for price, line in line_tuples:
            if num_affected_items >= max_affected_items:
                break
            qty = min(
                line.quantity_without_offer_discount(offer),
                max_affected_items - num_affected_items,
            )
            lines_to_discount.append((line, price, qty))
            num_affected_items += qty
            affected_items_total += qty * price

        # Ensure we don't try to apply a discount larger than the total of the
        # matching items.
        discount = min(discount_amount, affected_items_total)
        if max_total_discount is not None:
            discount = min(discount, max_total_discount)

        if discount == 0:
            return ZERO_DISCOUNT

        # spreading the discount is a policy decision that may not apply

        # Apply discount equally amongst them
        applied_discount = D("0.00")
        last_line_idx = len(lines_to_discount) - 1
        for i, (line, price, qty) in enumerate(lines_to_discount):
            if i == last_line_idx:
                # If last line, then take the delta as the discount to ensure
                # the total discount is correct and doesn't mismatch due to
                # rounding.
                line_discount = discount - applied_discount
            else:
                # Calculate a weighted discount for the line
                line_discount = self.round(
                    ((price * qty) / affected_items_total) * discount, basket.currency
                )
            apply_discount(line, line_discount, qty, offer)
            applied_discount += line_discount

        return BasketDiscount(discount)


class FixedUnitDiscountBenefit(AbsoluteDiscountBenefit):
    """
    An offer benefit that gives an absolute discount on each applicable product.
    """

    class Meta:
        app_label = "offer"
        proxy = True
        verbose_name = "Фиксированная скидка за единицу"
        verbose_name_plural = "Фиксированные скидки за единицу"

    def get_lines_to_discount(self, offer, line_tuples):
        # Determine which lines can have the discount applied to them
        max_affected_items = self._effective_max_affected_items()
        num_affected_items = 0
        lines_to_discount = []
        for price, line in line_tuples:
            if line.line_price_incl_discounts == 0:
                continue
            if num_affected_items >= max_affected_items:
                break
            qty = min(
                line.quantity_without_offer_discount(offer),
                max_affected_items - num_affected_items,
            )
            lines_to_discount.append((line, price, qty))
            num_affected_items += qty
        return lines_to_discount

    def apply(
        self,
        basket,
        condition,
        offer,
        discount_amount=None,
        max_total_discount=None,
        **kwargs
    ):
        # Fetch basket lines that are in the range and available to be used in an offer.
        line_tuples = self.get_applicable_lines(offer, basket)
        lines_to_discount = self.get_lines_to_discount(offer, line_tuples)

        applied_discount = D("0.00")
        for line, price, qty in lines_to_discount:
            # If price is less than the fixed discount, then it will be free.
            line_discount = min(price * qty, self.value * qty)
            apply_discount(line, line_discount, qty, offer)
            applied_discount += line_discount

        return BasketDiscount(applied_discount)


class FixedPriceBenefit(Benefit):
    """
    An offer benefit that gives the items in the condition for a
    fixed price.  This is useful for "bundle" offers.

    Note that we ignore the benefit range here and only give a fixed price
    for the products in the condition range.  The condition cannot be a value
    condition.

    We also ignore the max_affected_items setting.
    """

    _description = "Товары, соответствующие условию, продаются за %(amount)s"

    @property
    def name(self):
        return self._description % {"amount": currency(self.value)}

    class Meta:
        app_label = "offer"
        proxy = True
        verbose_name = "Фиксированная скидка"
        verbose_name_plural = "Фиксированные скидки"

    def apply(self, basket, condition, offer, **kwargs):
        if isinstance(condition, ValueCondition):
            return ZERO_DISCOUNT

        # Fetch basket lines that are in the range and available to be used in
        # an offer.
        line_tuples = self.get_applicable_lines(offer, basket, range=condition.range)
        if not line_tuples:
            return ZERO_DISCOUNT

        # Determine the lines to consume
        num_permitted = int(condition.value)
        num_affected = 0
        value_affected = D("0.00")
        covered_lines = []
        for price, line in line_tuples:
            if isinstance(condition, CoverageCondition):
                quantity_affected = 1
            else:
                quantity_affected = min(
                    line.quantity_without_offer_discount(offer),
                    num_permitted - num_affected,
                )
            num_affected += quantity_affected
            value_affected += quantity_affected * price
            covered_lines.append((price, line, quantity_affected))
            if num_affected >= num_permitted:
                break
        discount = max(value_affected - self.value, D("0.00"))
        if not discount:
            return ZERO_DISCOUNT

        # Apply discount to the affected lines
        discount_applied = D("0.00")
        last_line = covered_lines[-1][1]
        for price, line, quantity in covered_lines:
            if line == last_line:
                # If last line, we just take the difference to ensure that
                # rounding doesn't lead to an off-by-one error
                line_discount = discount - discount_applied
            else:
                line_discount = self.round(
                    discount * (price * quantity) / value_affected, basket.currency
                )
            apply_discount(line, line_discount, quantity, offer)
            discount_applied += line_discount
        return BasketDiscount(discount)


class MultibuyDiscountBenefit(Benefit):
    _description = "Самый дешевый товар из %(range)s бесплатно"

    @property
    def name(self):
        return self._description % {"range": self.range.name.lower()}

    @property
    def description(self):
        return self._description % {"range": range_anchor(self.range)}

    class Meta:
        app_label = "offer"
        proxy = True
        verbose_name = "Скидка при покупке нескольких покупок"
        verbose_name_plural = "Скидки при покупке нескольких покупок"

    def apply(self, basket, condition, offer, **kwargs):
        line_tuples = self.get_applicable_lines(offer, basket)
        if not line_tuples:
            return ZERO_DISCOUNT

        discount, line = line_tuples[0]
        if line.quantity_with_offer_discount(offer) == 0:
            apply_discount(line, discount, 1, offer)

            affected_lines = [(line, discount, 1)]
            condition.consume_items(offer, basket, affected_lines)

            return BasketDiscount(discount)
        else:
            return ZERO_DISCOUNT


# =================
# Shipping benefits
# =================


class ShippingBenefit(Benefit):
    def apply(self, basket, condition, offer, **kwargs):
        condition.consume_items(offer, basket, affected_lines=())
        return SHIPPING_DISCOUNT

    class Meta:
        app_label = "offer"
        proxy = True


class ShippingAbsoluteDiscountBenefit(ShippingBenefit):
    _description = "%(amount)s скидка на стоимость доставки"

    @property
    def name(self):
        return self._description % {"amount": currency(self.value)}

    class Meta:
        app_label = "offer"
        proxy = True
        verbose_name = "Абсолютная скидка на доставку"
        verbose_name_plural = "Абсолютные скидки на доставку"

    def shipping_discount(self, charge, currency=None):
        return min(charge, self.value)


class ShippingFixedPriceBenefit(ShippingBenefit):
    _description = "Получите доставку за %(amount)s"

    @property
    def name(self):
        return self._description % {"amount": currency(self.value)}

    class Meta:
        app_label = "offer"
        proxy = True
        verbose_name = "Фиксированная цена доставки"
        verbose_name_plural = "Фиксированные цены доставки"

    def shipping_discount(self, charge, currency=None):
        if charge < self.value:
            return D("0.00")
        return charge - self.value


class ShippingPercentageDiscountBenefit(ShippingBenefit):
    _description = "%(value)s%% за вычетом стоимости доставки"

    @property
    def name(self):
        return self._description % {"value": self.value}

    class Meta:
        app_label = "offer"
        proxy = True
        verbose_name = "Процентная скидка на доставку"
        verbose_name_plural = "Процентнаые скидки на доставку"

    def shipping_discount(self, charge, currency=None):
        discount = charge * self.value / D("100.0")
        return discount.quantize(D("0.01"))
