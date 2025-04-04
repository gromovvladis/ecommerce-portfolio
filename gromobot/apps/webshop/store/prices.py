class Base(object):
    """
    The interface that any pricing policy must support
    """

    #: Whether any prices exist
    exists = False

    #: Price
    money = None

    old_price = None

    #: Price to use for offer calculations
    @property
    def effective_price(self):
        return self.money

    # Code used to store the vat rate reference
    tax_code = None

    #: Retail price
    retail = None

    #: Price currency (3 char code)
    currency = None

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)


class Unavailable(Base):
    """
    This should be used as a pricing policy when a product is unavailable and
    no prices are known.
    """


class FixedPrice(Base):
    """
    This should be used for when the price of a product is known in advance.

    It can work for when tax isn't known (like in the US).

    Note that this price class uses the tax-exclusive price for offers, even if
    the tax is known.
    """

    exists = True

    def __init__(self, currency, money, old_price=None, min_price=None, tax_code=None):
        super().__init__()
        self.currency = currency
        self.money = money
        self.old_price = old_price
        self.tax_code = tax_code
