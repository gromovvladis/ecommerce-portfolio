from decimal import Decimal as D

import factory
from core.loading import get_class, get_model
from core.utils import slugify
from django.conf import settings
from tests import factories
from tests.factories.utils import tax_add, tax_subtract

OrderCreator = get_class("webshop.order.utils", "OrderCreator")

__all__ = [
    "BillingAddressFactory",
    "ShippingAddressFactory",
    "OrderDiscountFactory",
    "OrderFactory",
    "OrderLineFactory",
    "ShippingEventTypeFactory",
    "ShippingEventFactory",
]


class BillingAddressFactory(factory.django.DjangoModelFactory):

    first_name = "John"
    last_name = "Doe"
    line1 = "Streetname"
    line2 = "1a"
    line4 = "City"
    postcode = "1000AA"

    class Meta:
        model = get_model("order", "BillingAddress")


class ShippingAddressFactory(factory.django.DjangoModelFactory):

    first_name = "John"
    last_name = "Doe"
    line1 = "Streetname"
    line2 = "1a"
    line4 = "City"
    postcode = "1000 AA"
    phone_number = "+12125555555"

    class Meta:
        model = get_model("order", "ShippingAddress")


class OrderDiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_model("order", "OrderDiscount")


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_model("order", "Order")

    if hasattr(settings, "INITIAL_ORDER_STATUS"):
        status = settings.INITIAL_ORDER_STATUS

    site_id = getattr(settings, "SITE_ID", None)
    number = factory.LazyAttribute(lambda o: "%d" % (100000 + o.basket.pk))
    basket = factory.SubFactory("apps.webshop.tests.factories.BasketFactory")

    shipping_code = "shipping"
    shipping_incl_tax = D("4.95")
    shipping_excl_tax = factory.LazyAttribute(
        lambda o: tax_subtract(o.shipping_incl_tax)
    )

    total_incl_tax = factory.LazyAttribute(lambda o: o.basket.total_incl_tax)
    total_excl_tax = factory.LazyAttribute(lambda o: o.basket.total_excl_tax)

    guest_email = factory.LazyAttribute(
        lambda o: (
            "%s.%s@example.com"
            % (o.billing_address.first_name[0], o.billing_address.last_name)
        ).lower()
    )

    shipping_address = factory.SubFactory(ShippingAddressFactory)
    billing_address = factory.SubFactory(BillingAddressFactory)

    @factory.post_generation
    def create_line_models(obj, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            if not obj.basket.all_lines().exists():
                product = factories.ProductFactory(stockrecords=None)
                factories.StockRecordFactory(
                    product=product, price_currency=settings.DEFAULT_CURRENCY
                )
                obj.basket.add_product(product)
            for line in obj.basket.all_lines():
                OrderCreator().create_line_models(obj, line)


class OrderLineFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory("apps.webshop.tests.factories.ProductFactory")
    partner_sku = factory.LazyAttribute(lambda x: x.product.upc)
    stockrecord = factory.LazyAttribute(lambda s: s.product.stockrecords.first())
    quantity = 1

    line_price_incl_tax = factory.LazyAttribute(
        lambda obj: tax_add(obj.stockrecord.price) * obj.quantity
    )
    line_price_excl_tax = factory.LazyAttribute(
        lambda obj: obj.stockrecord.price * obj.quantity
    )

    line_price_before_discounts_incl_tax = factory.SelfAttribute(".line_price_incl_tax")
    line_price_before_discounts_excl_tax = factory.SelfAttribute(".line_price_excl_tax")

    unit_price_incl_tax = factory.LazyAttribute(
        lambda obj: tax_add(obj.stockrecord.price)
    )
    unit_price_excl_tax = factory.LazyAttribute(lambda obj: obj.stockrecord.price)

    class Meta:
        model = get_model("order", "Line")


class ShippingEventTypeFactory(factory.django.DjangoModelFactory):
    name = "Test event"
    code = factory.LazyAttribute(lambda o: slugify(o.name).replace("-", "_"))

    class Meta:
        model = get_model("order", "ShippingEventType")
        django_get_or_create = ("code",)


class ShippingEventFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
    event_type = factory.SubFactory(ShippingEventTypeFactory)

    class Meta:
        model = get_model("order", "ShippingEvent")
