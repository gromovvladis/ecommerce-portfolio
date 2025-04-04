# pylint: disable=unused-argument
from decimal import Decimal as D

from apps.webshop.order.signals import order_placed
from core.loading import get_class, get_model
from django.conf import settings
from django.db import transaction

from . import exceptions

Dispatcher = get_class("webshop.communication.utils", "Dispatcher")

Order = get_model("order", "Order")
Line = get_model("order", "Line")
OrderDiscount = get_model("order", "OrderDiscount")
OrderLineDiscount = get_model("order", "OrderLineDiscount")
CommunicationEvent = get_model("order", "CommunicationEvent")
CommunicationEventType = get_model("communication", "CommunicationEventType")
Surcharge = get_model("order", "Surcharge")


class OrderNumberGenerator(object):
    """
    Simple object for generating order numbers.

    We need this as the order number is often required for payment
    which takes place before the order model has been created.
    """

    def order_number(self, basket):
        """
        Return an order number for a given basket
        """
        return 100000 + basket.id


class OrderCreator(object):
    """
    Places the order by writing out the various models
    """

    def place_order(
        self,
        basket,
        total,
        order_time,
        shipping_method,
        shipping_charge,
        user=None,
        shipping_address=None,
        order_number=None,
        status=None,
        request=None,
        surcharges=None,
        **kwargs
    ):
        """
        Placing an order involves creating all the relevant models based on the
        basket and session data.
        """
        if basket.is_empty:
            raise ValueError("Пустая корзина не может быть подтверждена.")
        if not order_number:
            generator = OrderNumberGenerator()
            order_number = generator.order_number(basket)
        if not status and hasattr(settings, "INITIAL_ORDER_STATUS"):
            status = getattr(settings, "INITIAL_ORDER_STATUS")

        if Order._default_manager.filter(number=order_number).exists():
            raise ValueError("Уже есть заказ с номером %s" % order_number)

        with transaction.atomic():
            kwargs["surcharges"] = surcharges
            # Ok - everything seems to be in order, let's place the order
            order = self.create_order_model(
                user,
                basket,
                shipping_address,
                shipping_method,
                shipping_charge,
                total,
                order_time,
                order_number,
                status,
                request,
                **kwargs
            )
            for voucher in basket.vouchers.select_for_update():
                if not voucher.is_active():  # basket ignores inactive vouchers
                    basket.vouchers.remove(voucher)
                else:
                    available_to_user, msg = voucher.is_available_to_user(user=user)
                    if not available_to_user:
                        raise ValueError(msg)

            # Record any discounts associated with this order
            for application in basket.offer_applications:
                # Trigger any deferred benefits from offers and capture the
                # resulting message
                application["message"] = application["offer"].apply_deferred_benefit(
                    basket, order, application
                )
                # Record offer application results
                if application["result"].affects_shipping:
                    # Skip zero shipping discounts
                    shipping_discount = shipping_method.discount(basket)
                    if shipping_discount <= D("0.00"):
                        continue
                    # If a shipping offer, we need to grab the actual discount off
                    # the shipping method instance, which should be wrapped in an
                    # OfferDiscount instance.
                    application["discount"] = shipping_discount
                self.create_discount_model(order, application)
                self.record_discount(application)

            for voucher in basket.vouchers.all():
                self.record_voucher_usage(order, voucher, user)

            for line in basket.all_lines():
                self.create_line_models(order, line)
                self.update_stock_records(line)

        # Send signal for analytics to pick up
        order_placed.send(sender=self, order=order, user=user)

        return order

    def create_order_model(
        self,
        user,
        basket,
        shipping_address,
        shipping_method,
        shipping_charge,
        total,
        order_time,
        order_number,
        status,
        request=None,
        surcharges=None,
        **extra_order_fields
    ):
        """Create an order model."""
        order_data = {
            "basket": basket,
            "store": basket.store,
            "number": order_number,
            "currency": total.currency,
            "total": total.money,
            "order_time": order_time,
            "shipping": shipping_charge.money,
            "shipping_method": shipping_method.name,
        }
        if shipping_address:
            order_data["shipping_address"] = shipping_address
        if user and user.is_authenticated:
            order_data["user_id"] = user.id
        if status:
            order_data["status"] = status
        if extra_order_fields:
            order_data.update(extra_order_fields)
        if "site" not in order_data:
            order_data["site"] = self.get_referral_source(request)
        order = Order(**order_data)
        order.save()
        if surcharges is not None:
            for charge in surcharges:
                Surcharge.objects.create(
                    order=order,
                    name=charge.surcharge.name,
                    code=charge.surcharge.code,
                    money=charge.price.money,
                    tax_code=charge.price.tax_code,
                )

        return order

    def get_referral_source(self, request):
        return request.COOKIES.get("referral_source", "mikado-sushi.ru")

    def create_line_models(self, order, basket_line, extra_line_fields=None):
        """
        Create the batch line model.

        You can set extra fields by passing a dictionary as the
        extra_line_fields value
        """
        product = basket_line.product
        stockrecord = basket_line.stockrecord
        if not stockrecord:
            raise exceptions.UnableToPlaceOrder(
                "Basket line #%d has no stockrecord" % basket_line.id
            )

        store = stockrecord.store
        line_data = {
            "order": order,
            # Store details
            "store": store,
            "store_name": store.name,
            "stockrecord": stockrecord,
            # Product details
            "product": product,
            "name": basket_line.get_full_name(),
            "article": product.article,
            "quantity": basket_line.quantity,
            # Price details
            "line_price": basket_line.line_price_incl_discounts,
            "line_price_before_discounts": basket_line.line_price,
            # Reporting details
            "unit_price": basket_line.unit_price,
            "tax_code": basket_line.tax_code,
        }
        extra_line_fields = extra_line_fields or {}
        if hasattr(settings, "INITIAL_LINE_STATUS"):
            if not (extra_line_fields and "status" in extra_line_fields):
                extra_line_fields["status"] = getattr(settings, "INITIAL_LINE_STATUS")
        if extra_line_fields:
            line_data.update(extra_line_fields)

        order_line = Line._default_manager.create(**line_data)
        self.create_line_price_models(order, order_line, basket_line)
        self.create_line_attributes(order, order_line, basket_line)
        self.create_line_additionals(order, order_line, basket_line)
        self.create_line_discount_models(order, order_line, basket_line)
        self.create_additional_line_models(order, order_line, basket_line)

        return order_line

    def update_stock_records(self, line):
        """
        Update any relevant stock records for this order line
        """
        if line.product.get_product_class().track_stock:
            line.stockrecord.allocate(line.quantity)

    def create_line_discount_models(self, order, order_line, basket_line):
        for discount in basket_line.discounts:
            order_discount = order.discounts.filter(offer_id=discount.offer.id).first()
            # If we are unable to find the discount we do not care, the total amount is still saved on the discount model,
            # these models are only created so we know how much discount was given per line for each offer
            if order_discount:
                order_line.discounts.create(
                    order_discount=order_discount,
                    amount=discount.amount,
                )

    def create_additional_line_models(self, order, order_line, basket_line):
        """
        Empty method designed to be overridden.

        Some applications require additional information about lines, this
        method provides a clean place to create additional models that
        relate to a given line.
        """
        return

    def create_line_price_models(self, order, order_line, basket_line):
        """
        Creates the batch line price models
        """
        breakdown = basket_line.get_price_breakdown()
        for price, quantity in breakdown:
            order_line.prices.create(
                order=order,
                quantity=quantity,
                price=price,
                tax_code=basket_line.tax_code,
            )

    # pylint: disable=unused-argument
    def create_line_attributes(self, order, order_line, basket_line):
        """
        Creates the batch line attributes.
        """
        for attr in basket_line.attributes.all():
            if attr.option:
                order_line.attributes.create(
                    option=attr.option, type=attr.option.code, value=attr.value
                )

    # pylint: disable=unused-argument
    def create_line_additionals(self, order, order_line, basket_line):
        """
        Creates the batch line attributes.
        """
        for attr in basket_line.attributes.all():
            if attr.additional:
                order_line.attributes.create(
                    additional=attr.additional,
                    type=attr.additional.article,
                    value=attr.value,
                )

    def create_discount_model(self, order, discount):
        """
        Create an order discount model for each offer application attached to
        the basket.
        """
        order_discount = OrderDiscount(
            order=order,
            message=discount["message"] or "",
            offer_id=discount["offer"].id,
            frequency=discount["freq"],
            amount=discount["discount"],
        )
        result = discount["result"]
        if result.affects_shipping:
            order_discount.category = OrderDiscount.SHIPPING
        elif result.affects_post_order:
            order_discount.category = OrderDiscount.DEFERRED
        voucher = discount.get("voucher", None)
        if voucher:
            order_discount.voucher_id = voucher.id
            order_discount.voucher_code = voucher.code
        order_discount.save()

    def record_discount(self, discount):
        discount["offer"].record_usage(discount)
        if "voucher" in discount and discount["voucher"]:
            discount["voucher"].record_discount(discount)

    def record_voucher_usage(self, order, voucher, user):
        """
        Updates the models that care about this voucher.
        """
        voucher.record_usage(order, user)


class OrderDispatcher:
    """
    Dispatcher to send concrete order related emails.
    """

    # Event codes
    ORDER_PLACED_EVENT_CODE = "ORDER_PLACED"

    def __init__(self, logger=None, mail_connection=None):
        self.dispatcher = Dispatcher(logger=logger, mail_connection=mail_connection)

    def dispatch_order_messages(
        self, order, messages, event_code, attachments=None, **kwargs
    ):
        """
        Dispatch order-related messages to the customer.
        """
        self.dispatcher.logger.info(
            "Order #%s - sending %s messages", order.number, event_code
        )
        if order.is_anonymous:
            email = kwargs.get("email_address")
            dispatched_messages = self.dispatcher.dispatch_anonymous_messages(
                email, messages, attachments
            )
        else:
            dispatched_messages = self.dispatcher.dispatch_user_messages(
                order.user, messages, attachments
            )

        try:
            event_type = CommunicationEventType.objects.get(code=event_code)
        except CommunicationEventType.DoesNotExist:
            event_type = None

        self.create_communication_event(order, event_type, dispatched_messages)

    def create_communication_event(self, order, event_type, dispatched_messages):
        """
        Create order communications event for audit.
        """
        if dispatched_messages and event_type is not None:
            CommunicationEvent._default_manager.create(
                order=order, event_type=event_type
            )

    def send_order_placed_email_for_user(self, order, extra_context, attachments=None):
        event_code = self.ORDER_PLACED_EVENT_CODE
        messages = self.dispatcher.get_messages(event_code, extra_context)
        self.dispatch_order_messages(
            order, messages, event_code, attachments=attachments
        )
