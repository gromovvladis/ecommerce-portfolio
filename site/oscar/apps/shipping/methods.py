from decimal import Decimal as D
from oscar.apps.address.models import UserAddress, ShippingAddress
from oscar.core import prices
from oscar.core.loading import get_class, get_model

DeliveryZona = get_model("delivery", "DeliveryZona")
ZonesUtils = get_class("delivery.zones", "ZonesUtils")


class Base(object):
    """
    Shipping method interface class

    This is the superclass to the classes in this module. This allows
    using all shipping methods interchangeably (aka polymorphism).

    The interface is all properties.
    """

    #: Used to store this method in the session.  Each shipping method should
    #:  have a unique code.
    code = "__default__"

    default_selected = False

    #: The name of the shipping method, shown to the customer during checkout
    name = "Default shipping"

    #: A more detailed description of the shipping method shown to the customer
    #:  during checkout.  Can contain HTML.
    description = ""

    #: Whether the charge includes a discount
    is_discounted = False

    def calculate(self, basket, address=None):
        """
        Return the shipping charge for the given basket
        """
        raise NotImplementedError

    # pylint: disable=unused-argument
    def discount(self, basket):
        """
        Return the discount on the standard shipping charge
        """
        # The regular shipping methods don't add a default discount.
        # For offers and vouchers, the discount will be provided
        # by a wrapper that Repository.apply_shipping_offer() adds.
        return D("0.00")


class Free(Base):
    """
    This shipping method specifies that shipping is free.
    """

    def __init__(self, default_selected=False):
        self.default_selected = default_selected

    code = "free-shipping"
    name = "Бесплатная доставка"

    def calculate(self, basket, address=None):
        """"Returns the shipping charges and minimum order price"""
        # If the charge is free then tax must be free (musn't it?) and so we
        # immediately set the tax to zero
        return prices.Price(currency=basket.currency, money=D("0.00")), prices.Price(currency=basket.currency, money=D("0.00"))


class NoShippingRequired(Free):
    """
    This shipping method indicates that shipping costs a fixed price and
    requires no special calculation.
    """
    code = "self-pick-up"
    name = "Самовывоз"

    # Charges can be either declared by subclassing and overriding the
    # class attributes or by passing them to the constructor
    pickup_discount = None

    def __init__(self, pickup_discount=0, default_selected=False):
        if pickup_discount is not None:
            self.pickup_discount = pickup_discount
        self.default_selected = default_selected

    def calculate(self, basket, address=None):
        """"Returns the shipping charges and minimum order price"""

        discount = basket.total * self.pickup_discount / 100
        return prices.Price(currency=basket.currency, money=-discount), prices.Price(currency=basket.currency, money=D("0"))


class FixedPrice(Base):
    """
    This shipping method indicates that shipping costs a fixed price and
    requires no special calculation.
    """

    code = "fixed-price-shipping"
    name = "Доставка с фиксированной ценой"

    # Charges can be either declared by subclassing and overriding the
    # class attributes or by passing them to the constructor
    charge = None

    def __init__(self, charge=None, default_selected=False):
        if charge is not None:
            self.charge = charge
        self.default_selected = default_selected

    def calculate(self, basket, address=None):
        """"Returns the shipping charges and minimum order price"""
        return prices.Price(currency=basket.currency, money=self.charge), prices.Price(currency=basket.currency, money=D("700.00"))


class ZonaBasedShipping(Base):
    """
    This shipping method indicates that shipping costs a fixed price and
    requires no special calculation.
    """

    code = "zona-shipping"
    name = "Доставка"

    def __init__(self, default_selected=False):
        self.default_selected = default_selected


    def calculate(self, basket, address):
        """"Returns the shipping charges and minimum order price"""
        zona_id = 0
        shipping_charge = D("0.0")
        min_order = D("700.0")

        zones = ZonesUtils.available_zones()

        if isinstance(address, ShippingAddress) or isinstance(address, UserAddress):
            zona_id = ZonesUtils.zona_id([address.coords_lat, address.coords_long], zones)
        else:
            zona_id = int(address)

        if zona_id > 0:
            shipping_charge = self.zona_charge(zona_id, zones)
            min_order = self.min_order(zona_id, zones)

        return prices.Price(currency=basket.currency, money=shipping_charge), prices.Price(currency=basket.currency, money=min_order)
        
    def zona_charge(self, zona_id, zones):
        charge = 0
        try:
            zona = zones.get(number=zona_id)
            charge = zona.delivery_price
        except Exception:
            return 0
        
        return charge
    

    def min_order(self, zona_id, zones):
        amount = 700
        try:
            zona = zones.get(number=zona_id)
            amount = zona.order_price
        except Exception:
            return 700
        
        return amount
    

# pylint: disable=abstract-method
class OfferDiscount(Base):
    """
    Wrapper class that applies a discount to an existing shipping
    method's charges.
    """

    is_discounted = True

    def __init__(self, method, offer, default_selected=False):
        self.method = method
        self.offer = offer
        self.default_selected = default_selected

    # Forwarded properties

    @property
    def code(self):
        """
        Returns the :py:attr:`code <oscar.apps.shipping.methods.Base.code>` of the wrapped shipping method.
        """
        return self.method.code

    @property
    def name(self):
        """
        Returns the :py:attr:`name <oscar.apps.shipping.methods.Base.name>` of the wrapped shipping method.
        """
        return self.method.name

    @property
    def discount_name(self):
        """
        Returns the :py:attr:`name <oscar.apps.offer.models.BaseOfferMixin.name>` of the applied Offer.
        """
        return self.offer.name

    @property
    def description(self):
        """
        Returns the :py:attr:`description <.Base.description>` of the wrapped shipping method.
        """
        return self.method.description

    def calculate_excl_discount(self, basket, zonaId):
        """
        Returns the shipping charge for the given basket without
        discount applied.
        """
        return self.method.calculate(basket, zonaId)
