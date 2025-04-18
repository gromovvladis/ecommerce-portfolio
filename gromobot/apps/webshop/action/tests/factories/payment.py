import factory
from core.loading import get_model

__all__ = [
    "SourceTypeFactory",
    "SourceFactory",
    "TransactionFactory",
]


class SourceTypeFactory(factory.django.DjangoModelFactory):
    name = "Creditcard"
    code = "creditcard"

    class Meta:
        model = get_model("payment", "SourceType")


class SourceFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory("apps.webshop.tests.factories.OrderFactory")
    source_type = factory.SubFactory(SourceTypeFactory)

    class Meta:
        model = get_model("payment", "Source")


class TransactionFactory(factory.django.DjangoModelFactory):
    amount = factory.LazyAttribute(lambda obj: obj.source.order.total_incl_tax)
    reference = factory.LazyAttribute(lambda obj: obj.source.order.number)
    source = factory.SubFactory(SourceFactory)
    status = "authorised"

    class Meta:
        model = get_model("payment", "Transaction")
