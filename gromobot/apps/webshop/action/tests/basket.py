from decimal import Decimal as D

from core.loading import get_class

from . import factories

Default = get_class("webshop.store.strategy", "Default")


def add_product(basket, price=None, quantity=1, product=None):
    """
    Helper to add a product to the basket.
    """
    has_strategy = False
    try:
        has_strategy = hasattr(basket, "strategy")
    except RuntimeError:
        pass
    if not has_strategy:
        basket.strategy = Default()
    if price is None:
        price = D("1")
    if product and product.has_stockrecords:
        record = product.stockrecords.first()
    else:
        record = factories.create_stockrecord(
            product=product, price=price, num_in_stock=quantity + 1
        )
    basket.add_product(record.product, quantity)


def add_products(basket, args):
    """
    Helper to add a series of products to the passed basket
    """
    for price, quantity in args:
        add_product(basket, price, quantity)
