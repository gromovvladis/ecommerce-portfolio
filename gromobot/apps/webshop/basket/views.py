from apps.webshop.basket.signals import basket_addition
from core.loading import get_class, get_classes, get_model
from core.utils import is_ajax, safe_referrer
from django import http, shortcuts
from django.contrib.sessions.serializers import JSONSerializer
from django.http import QueryDict
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import FormView, View
from extra_views import ModelFormSetView

PageTitleMixin, ThemeMixin = get_classes(
    "webshop.mixins", ["PageTitleMixin", "ThemeMixin"]
)
Applicator = get_class("webshop.offer.applicator", "Applicator")
BasketLineFormSet = get_class("webshop.basket.formsets", "BasketLineFormSet")
Repository = get_class("webshop.shipping.repository", "Repository")
OrderTotalCalculator = get_class("webshop.checkout.calculators", "OrderTotalCalculator")
BasketMessageGenerator = get_class("webshop.basket.utils", "BasketMessageGenerator")
SurchargeApplicator = get_class("webshop.checkout.applicator", "SurchargeApplicator")
BasketLineForm, AddToBasketForm = get_classes(
    "webshop.basket.forms",
    ("BasketLineForm", "AddToBasketForm"),
)

Basket = get_model("basket", "Basket")
Line = get_model("basket", "Line")
Product = get_model("catalogue", "Product")


class BasketView(PageTitleMixin, ThemeMixin, ModelFormSetView):
    model = Line
    basket_model = Basket
    formset_class = BasketLineFormSet
    form_class = BasketLineForm
    page_title = "Корзина"
    template_name = "basket/basket.html"
    factory_kwargs = {"extra": 0, "can_delete": True}

    def dispatch(self, request, *args, **kwargs):
        self.check_lines()
        return super().dispatch(request, *args, **kwargs)

    def check_lines(self):
        if not is_ajax(self.request):
            updated = any(
                self._update_or_remove_line(line)
                for line in self.request.basket._all_lines()
            )

            if updated:
                self.request.basket.reset_offer_applications()
                Applicator().apply(self.request.basket, self.request.user, self.request)

    def _update_or_remove_line(self, line):
        if line.quantity == 0:
            line.delete()
            return True

        return line.check_availability()

    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs["strategy"] = self.request.strategy
        return kwargs

    def get_queryset(self):
        """
        Return list of :py:class:`Line <apps.webshop.basket.models.Line>`
        instances associated with the current basket.
        """
        return self.request.basket._all_lines()

    def get_upsell_messages(self, basket):
        offers = Applicator().get_offers(basket, self.request.user, self.request)
        applied_offers = set(basket.offer_applications.offers.values())
        return [
            {"message": offer.get_upsell_message(basket), "offer": offer}
            for offer in offers
            if offer.is_condition_partially_satisfied(basket)
            and offer not in applied_offers
            and offer.is_available()
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Shipping information is included to give an idea of the total order
        # cost.  It is also important for PayPal Express where the customer
        # gets redirected away from the basket page and needs to see what the
        # estimated order total is beforehand.
        context["upsell_messages"] = self.get_upsell_messages(self.request.basket)
        context["order_total"] = OrderTotalCalculator().calculate(self.request.basket)

        return context

    def get_success_url(self):
        return safe_referrer(self.request, "basket:summary")

    def formset_valid(self, formset):
        if is_ajax(self.request):
            self.object_list = formset.save()
            self.request.basket = Basket.objects.get(id=self.request.basket.id)
            self.request.basket.strategy = self.request.strategy
            Applicator().apply(self.request.basket, self.request.user, self.request)
            new_totals = render_to_string(
                "basket/partials/basket_totals.html",
                {
                    "basket": self.request.basket,
                    "order_total": {
                        "currency": self.request.basket.currency,
                        "money": self.request.basket.total,
                    },
                },
                request=self.request,
            )
            return http.JsonResponse(
                {
                    "new_totals": new_totals,
                    "new_nums": self.request.basket.num_items,
                },
                status=202,
            )

        return super().formset_valid(formset)

    def formset_invalid(self, formset):
        if any(formset._should_delete_form(form) for form in formset.forms):
            self.remove_deleted_forms(formset)
            if all(
                form.is_valid() or formset._should_delete_form(form)
                for form in formset.forms
            ):
                return self.formset_valid(formset)

        if is_ajax(self.request):
            return http.JsonResponse({"errors": formset.errors}, status=404)

        return super().formset_invalid(formset)

    def remove_deleted_forms(self, formset):
        """
        Removes forms marked for deletion, from the formset, as well as deletes
        their model instance objects; and modifies the formset's request data,
        to match the state of the data in the database, for the remaining forms.

        This is useful for redisplaying a formset containing other invalid
        forms, after deleting one of the forms from it.
        """
        form_data = {}
        form_index = 0
        for form in formset.forms:
            # Delete forms marked for deletion, and retain the request data
            # for the other forms
            if formset._should_delete_form(form):
                if form.instance.id is not None:
                    form.instance.delete()
            else:
                old_form_prefix = form.prefix
                new_form_prefix = formset.add_prefix(form_index)
                for field_name in form.fields:
                    form.prefix = old_form_prefix
                    old_prefixed_field_name = form.add_prefix(field_name)
                    form.prefix = new_form_prefix
                    new_prefixed_field_name = form.add_prefix(field_name)
                    try:
                        form_data[new_prefixed_field_name] = formset.data[
                            old_prefixed_field_name
                        ]
                    except KeyError:
                        pass
                form_index += 1
        for field_name in formset.management_form.fields:
            prefixed_field_name = formset.management_form.add_prefix(field_name)
            if field_name in ["INITIAL_FORMS", "TOTAL_FORMS"]:
                form_data[prefixed_field_name] = str(form_index)
            else:
                form_data[prefixed_field_name] = formset.data[prefixed_field_name]

        query_dict = QueryDict(mutable=True)
        query_dict.update(form_data)
        formset.data = query_dict
        # Clear cached values, so that they are recomputed using the modified
        # request data
        del formset.management_form
        del formset.forms
        # Clean the formset's modified request data
        formset.full_clean()


class EmptyBasketView(View):
    def post(self, request, *args, **kwargs):
        basket = request.basket
        url = reverse("basket:summary")
        # Если корзина пуста или не существует, сразу возвращаем ошибку
        if not basket.id:
            return http.JsonResponse({"url": url}, status=404)
        try:
            basket.flush()
        except Exception:
            return http.JsonResponse({"url": url}, status=500)

        return http.JsonResponse({"url": url}, status=200)


class GetUpsellMessages(View):
    def get_upsell_messages(self, basket):
        # Получаем предложения
        offers = Applicator().get_offers(basket, self.request.user, self.request)
        applied_offers = set(basket.offer_applications.offers.values())

        # Собираем только те предложения, которые удовлетворяют условиям
        return [
            {"message": offer.get_upsell_message(basket), "offer": offer}
            for offer in offers
            if offer.is_condition_partially_satisfied(basket)
            and offer not in applied_offers
        ]

    def get(self, request, *args, **kwargs):
        # Формируем ответ с использованием шаблона
        upsell_messages = render_to_string(
            "basket/partials/upsell_messages.html",
            {"upsell_messages": self.get_upsell_messages(request.basket)},
            request=self.request,
        )
        return http.JsonResponse({"upsell_messages": upsell_messages}, status=202)


class BasketAddView(FormView):
    """
    Handles the add-to-basket submissions, which are triggered from various
    parts of the site. The add-to-basket form is loaded into templates using
    a templatetag from :py:mod:`templatetags.basket_tags`.
    """

    form_class = AddToBasketForm
    product_model = Product
    add_signal = basket_addition
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        # pylint: disable=W0201
        self.product = shortcuts.get_object_or_404(
            self.product_model, slug=kwargs["slug"]
        )
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "basket": self.request.basket,
                "store_id": self.request.store.id,
                "product": self.product,
            }
        )
        return kwargs

    def _prepare_errors(self, form):
        """Helper method to prepare error messages."""
        return " ".join(
            error.as_text().replace("* ", "")
            for error in form.errors.values()
            if error.as_text().startswith("* ")
        )

    def form_invalid(self, form):
        # Serialize POST data to avoid security vulnerabilities
        serialized_data = JSONSerializer().dumps(self.request.POST)
        self.request.session[f"add_to_basket_form_post_data_{self.product.pk}"] = (
            serialized_data.decode("latin-1")
        )
        return http.JsonResponse({"errors": self._prepare_errors(form)}, status=404)

    def form_valid(self, form):
        # Add product to the basket
        self.request.basket.add_product(
            form.product, 1, form.cleaned_options(), form.cleaned_additionals()
        )

        # Send signal for basket addition
        self.add_signal.send(
            sender=self,
            product=form.product,
            user=self.request.user,
            request=self.request,
        )

        super().form_valid(form)

        return http.JsonResponse({"cart_nums": form.basket.num_items}, status=200)

    def get_success_url(self):
        post_url = self.request.POST.get("next")
        if post_url and url_has_allowed_host_and_scheme(
            post_url, self.request.get_host()
        ):
            return post_url
        return safe_referrer(self.request, "basket:summary")
