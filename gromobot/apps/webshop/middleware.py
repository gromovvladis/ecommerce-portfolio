from collections import namedtuple
from urllib.parse import urlparse

from core.loading import get_class, get_model
from django.conf import settings
from django.core.signing import BadSignature, Signer
from django.utils.functional import SimpleLazyObject, empty

Applicator = get_class("webshop.offer.applicator", "Applicator")
Selector = get_class("webshop.store.strategy", "Selector")

selector = Selector()

Basket = get_model("basket", "basket")
store = namedtuple("store", ["id"])


class WebshopMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/dashboard"):
            return self.get_response(request)

        # Keep track of cookies that need to be deleted (which can only be done
        # when we're processing the response instance).
        request.cookies_to_delete = []

        # We lazily load the basket so use a private variable to hold the
        # cached instance.
        request._basket_cache = None
        request._store_cache = None
        request.theme = 'planet'

        # Load stock/price strategy and assign to request (it will later be
        # assigned to the basket too).
        strategy = selector.strategy(request=request, user=request.user)
        request.strategy = strategy

        def load_referral_source():
            def extract_domain(url):
                parsed_url = urlparse(url)
                return parsed_url.netloc

            if "referral_source" not in request.COOKIES:
                return extract_domain(request.META.get("HTTP_REFERER"))

        _referral_source = SimpleLazyObject(load_referral_source)
        if _referral_source:
            request._referral_source = _referral_source

        def load_store():
            if not request._store_cache:
                basket = self.get_basket(request)
                store_id = basket.store_id

                if not store_id:
                    store_id = int(request.COOKIES.get("store", settings.STORE_DEFAULT))

                request._store_cache = store(store_id)

            return request._store_cache

        def load_full_basket():
            """
            Return the basket after applying offers.
            """
            basket = self.get_basket(request)
            basket.strategy = request.strategy
            self.apply_offers_to_basket(request, basket)

            return basket

        def load_basket_hash():
            """
            Load the basket and return the basket hash

            Note that we don't apply offers or check that every line has a
            stockrecord here.
            """
            basket = self.get_basket(request)
            if basket.id:
                return self.get_basket_hash(basket.id)

        # Use Django's SimpleLazyObject to only perform the loading work
        # when the attribute is accessed.
        request.basket = SimpleLazyObject(load_full_basket)
        request.basket_hash = SimpleLazyObject(load_basket_hash)
        request.store = SimpleLazyObject(load_store)
        request._referral_source = SimpleLazyObject(load_referral_source)

        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request, response):
        # Delete any surplus cookies
        cookies_to_delete = getattr(request, "cookies_to_delete", [])
        for cookie_key in cookies_to_delete:
            response.delete_cookie(cookie_key)

        if hasattr(request, "_referral_source") and request._referral_source:
            response.set_cookie(
                "referral_source",
                request._referral_source,
                max_age=settings.BASKET_COOKIE_LIFETIME,
                secure=settings.BASKET_COOKIE_SECURE,
                httponly=True,
            )

        if not hasattr(request, "basket"):
            return response

        # If the basket was never initialized we can safely return
        if (
            isinstance(request.basket, SimpleLazyObject)
            and request.basket._wrapped is empty
        ):
            return response

        cookie_key = self.get_cookie_key(request)
        # Check if we need to set a cookie. If the cookies is already available
        # but is set in the cookies_to_delete list then we need to re-set it.
        has_basket_cookie = (
            cookie_key in request.COOKIES and cookie_key not in cookies_to_delete
        )

        # If a basket has had products added to it, but the user is anonymous
        # then we need to assign it to a cookie
        if (
            request.basket.id
            and not request.user.is_authenticated
            and not has_basket_cookie
        ):
            cookie = self.get_basket_hash(request.basket.id)
            response.set_cookie(
                cookie_key,
                cookie,
                max_age=settings.BASKET_COOKIE_LIFETIME,
                secure=settings.BASKET_COOKIE_SECURE,
                httponly=True,
            )
        return response

    # pylint: disable=unused-argument
    def get_cookie_key(self, request):
        """
        Returns the cookie name to use for storing a cookie basket.

        The method serves as a useful hook in multi-site scenarios where
        different baskets might be needed.
        """
        return settings.BASKET_COOKIE_OPEN

    def process_template_response(self, request, response):
        if hasattr(response, "context_data"):
            if response.context_data is None:
                response.context_data = {}
            if "basket" not in response.context_data:
                response.context_data["basket"] = request.basket
            else:
                # Occasionally, a view will want to pass an alternative basket
                # to be rendered.  This can happen as part of checkout
                # processes where the submitted basket is frozen when the
                # customer is redirected to another site (eg PayPal).  When the
                # customer returns and we want to show the order preview
                # template, we need to ensure that the frozen basket gets
                # rendered (not request.basket).  We still keep a reference to
                # the request basket (just in case).
                response.context_data["request_basket"] = request.basket
        return response

    # Helper methods

    def get_basket(self, request):
        """
        Return the open basket for this request
        """
        # pylint: disable=protected-access
        if request._basket_cache is not None:
            return request._basket_cache

        # num_items_merged = 0
        manager = Basket.open
        cookie_key = self.get_cookie_key(request)
        cookie_basket = self.get_cookie_basket(cookie_key, request, manager)

        if hasattr(request, "user") and request.user.is_authenticated:
            # Signed-in user: if they have a cookie basket too, it means
            # that they have just signed in and we need to merge their cookie
            # basket into their user basket, then delete the cookie.
            try:
                basket, _ = manager.get_or_create(owner=request.user)
            except Basket.MultipleObjectsReturned:
                # Not sure quite how we end up here with multiple baskets.
                # We merge them and create a fresh one
                old_baskets = list(manager.filter(owner=request.user))
                basket = old_baskets[0]
                for other_basket in old_baskets[1:]:
                    self.merge_baskets(basket, other_basket)
                    # count number of items that have been merged
                    # num_items_merged += other_basket.num_items

            # Assign user onto basket to prevent further SQL queries when
            # basket.owner is accessed.
            basket.owner = request.user

            if cookie_basket:
                # count number of items in the basket
                # num_items_merged += cookie_basket.num_items
                self.merge_baskets(basket, cookie_basket)
                request.cookies_to_delete.append(cookie_key)

        elif cookie_basket:
            # Anonymous user with a basket tied to the cookie
            basket = cookie_basket
        else:
            # Anonymous user with no basket - instantiate a new basket
            # instance.  No need to save yet.
            basket = Basket()

        # Cache basket instance for the during of this request
        request._basket_cache = basket

        return basket

    def merge_baskets(self, master, slave):
        """
        Merge one basket into another.

        This is its own method to allow it to be overridden
        """
        master.merge(slave, add_quantities=False)

    # pylint: disable=unused-argument
    def get_cookie_basket(self, cookie_key, request, manager):
        """
        Looks for a basket which is referenced by a cookie.

        If a cookie key is found with no matching basket, then we add
        it to the list to be deleted.
        """
        basket = None
        if cookie_key in request.COOKIES:
            basket_hash = request.COOKIES[cookie_key]
            try:
                basket_id = Signer().unsign(basket_hash)
                basket = Basket.objects.get(
                    pk=basket_id, owner=None, status=Basket.OPEN
                )
            except (BadSignature, Basket.DoesNotExist):
                request.cookies_to_delete.append(cookie_key)
        return basket

    def apply_offers_to_basket(self, request, basket):
        if not basket.is_empty:
            Applicator().apply(basket, request.user, request)

    def get_basket_hash(self, basket_id):
        return Signer().sign(basket_id)
