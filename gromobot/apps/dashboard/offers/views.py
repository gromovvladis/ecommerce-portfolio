from core.loading import get_class, get_classes, get_model
from core.views import sort_queryset
from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DeleteView, ListView
from django_tables2 import SingleTableView

ConditionalOfferTable = get_class("dashboard.offers.tables", "ConditionalOfferTable")
OfferWizardStepView = get_class("dashboard.offers.wizard_views", "OfferWizardStepView")
OrderDiscountCSVFormatter = get_class(
    "dashboard.offers.reports", "OrderDiscountCSVFormatter"
)
(
    MetaDataForm,
    ConditionForm,
    BenefitForm,
    RestrictionsForm,
    OfferSearchForm,
) = get_classes(
    "dashboard.offers.forms",
    [
        "MetaDataForm",
        "ConditionForm",
        "BenefitForm",
        "RestrictionsForm",
        "OfferSearchForm",
    ],
)

ConditionalOffer = get_model("offer", "ConditionalOffer")
Condition = get_model("offer", "Condition")
Range = get_model("offer", "Range")
Product = get_model("catalogue", "Product")
OrderDiscount = get_model("order", "OrderDiscount")
Benefit = get_model("offer", "Benefit")


# pylint: disable=attribute-defined-outside-init
class OfferListView(SingleTableView):
    template_name = "dashboard/offers/offer_list.html"
    form_class = OfferSearchForm
    table_class = ConditionalOfferTable
    context_table_name = "offers"

    def get_table(self, **kwargs):
        table = super().get_table(**kwargs)
        if self.form.is_valid() and any(self.form.cleaned_data.values()):
            table.caption = "Результаты поиска: %s" % self.object_list.count()

        return table

    def get_table_pagination(self, table):
        return dict(per_page=settings.DASHBOARD_ITEMS_PER_PAGE)

    def get_queryset(self):
        self.search_filters = []
        qs = ConditionalOffer._default_manager.annotate(
            voucher_count=Count("vouchers")
        ).select_related("benefit", "condition")
        qs = sort_queryset(
            qs,
            self.request,
            [
                "name",
                "offer_type",
                "start_datetime",
                "end_datetime",
                "num_applications",
                "total_discount",
            ],
        )

        self.form = self.form_class(self.request.GET)
        # This form is exactly the same as the other one, apart from having
        # fields with different IDs, so that they are unique within the page
        # (non-unique field IDs also break Select2)
        self.advanced_form = self.form_class(self.request.GET, auto_id="id_advanced_%s")
        if not all([self.form.is_valid(), self.advanced_form.is_valid()]):
            return qs

        name = self.form.cleaned_data["name"]
        offer_type = self.form.cleaned_data["offer_type"]
        is_active = self.form.cleaned_data["is_active"]
        has_vouchers = self.form.cleaned_data["has_vouchers"]
        voucher_code = self.form.cleaned_data["voucher_code"]

        if name:
            qs = qs.filter(name__icontains=name)
            self.search_filters.append(
                (
                    f"Имя соответствует {name}",
                    (("name", name),),
                )
            )
        if is_active is not None:
            now = timezone.now()
            if is_active:
                qs = qs.filter(
                    (Q(start_datetime__lte=now) | Q(start_datetime__isnull=True))
                    & (Q(end_datetime__gte=now) | Q(end_datetime__isnull=True)),
                    status=ConditionalOffer.OPEN,
                )
                self.search_filters.append(
                    (
                        "Активен",
                        (("is_active", is_active),),
                    )
                )
            else:
                qs = qs.filter(
                    Q(start_datetime__gt=now)
                    | Q(end_datetime__lt=now)
                    | Q(status=ConditionalOffer.SUSPENDED)
                )
                self.search_filters.append(
                    (
                        "Неактивен",
                        (("is_active", is_active),),
                    )
                )
        if offer_type:
            qs = qs.filter(offer_type=offer_type)
            self.search_filters.append(
                (
                    'Тип товара "%s"' % dict(ConditionalOffer.TYPE_CHOICES)[offer_type],
                    (("offer_type", offer_type),),
                )
            )
        if has_vouchers is not None:
            qs = qs.filter(vouchers__isnull=not has_vouchers).distinct()
            self.search_filters.append(
                (
                    "Есть промокод" if has_vouchers else "Нет промокода",
                    (("has_vouchers", has_vouchers),),
                )
            )
        if voucher_code:
            qs = qs.filter(vouchers__code__icontains=voucher_code).distinct()
            self.search_filters.append(
                (
                    'Промокод соответствует коду: "%s"' % voucher_code,
                    (("voucher_code", voucher_code),),
                )
            )

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form"] = self.form
        ctx["advanced_form"] = self.advanced_form
        ctx["search_filters"] = self.search_filters
        return ctx


class OfferMetaDataView(OfferWizardStepView):
    step_name = "metadata"
    form_class = MetaDataForm
    template_name = "dashboard/offers/metadata_form.html"
    url_name = "dashboard:offer-metadata"
    success_url_name = "dashboard:offer-benefit"

    def get_instance(self):
        return self.offer

    def get_title(self):
        return "Название, описание и тип"


class OfferBenefitView(OfferWizardStepView):
    step_name = "benefit"
    form_class = BenefitForm
    template_name = "dashboard/offers/benefit_form.html"
    url_name = "dashboard:offer-benefit"
    success_url_name = "dashboard:offer-condition"
    previous_view = OfferMetaDataView

    def get_instance(self):
        return self.offer.benefit

    def get_title(self):
        # This is referred to as the 'incentive' within the dashboard.
        return "Стимул"


class OfferConditionView(OfferWizardStepView):
    step_name = "condition"
    form_class = ConditionForm
    template_name = "dashboard/offers/condition_form.html"
    url_name = "dashboard:offer-condition"
    success_url_name = "dashboard:offer-restrictions"
    previous_view = OfferBenefitView

    def get_instance(self):
        return self.offer.condition


class OfferRestrictionsView(OfferWizardStepView):
    step_name = "restrictions"
    form_class = RestrictionsForm
    template_name = "dashboard/offers/restrictions_form.html"
    previous_view = OfferConditionView
    url_name = "dashboard:offer-restrictions"

    def form_valid(self, form):
        offer = form.save(commit=False)
        return self.save_offer(offer)

    def get_instance(self):
        return self.offer

    def get_title(self):
        return "Ограничения"


class OfferDeleteView(DeleteView):
    model = ConditionalOffer
    template_name = "dashboard/offers/offer_delete.html"
    context_object_name = "offer"

    def dispatch(self, request, *args, **kwargs):
        offer = self.get_object()
        if offer.vouchers.exists():
            messages.warning(
                request,
                "Это предложение можно удалить только в том случае, если к нему не прикреплены ваучеры.",
            )
            return redirect("dashboard:offer-detail", pk=offer.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Предложение удалено!")
        return reverse("dashboard:offer-list")


class OfferDetailView(ListView):
    # Slightly odd, but we treat the offer detail view as a list view so the
    # order discounts can be browsed.
    model = OrderDiscount
    template_name = "dashboard/offers/offer_detail.html"
    context_object_name = "order_discounts"
    paginate_by = settings.DASHBOARD_ITEMS_PER_PAGE

    # pylint: disable=attribute-defined-outside-init
    def dispatch(self, request, *args, **kwargs):
        self.offer = get_object_or_404(ConditionalOffer, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "suspend" in request.POST:
            return self.suspend()
        elif "unsuspend" in request.POST:
            return self.unsuspend()

    def suspend(self):
        if self.offer.is_suspended:
            messages.error(self.request, "Предложение уже приостановлено.")
        else:
            self.offer.suspend()
            messages.success(self.request, "Предложение приостановлено.")
        return HttpResponseRedirect(
            reverse("dashboard:offer-detail", kwargs={"pk": self.offer.pk})
        )

    def unsuspend(self):
        if not self.offer.is_suspended:
            messages.error(
                self.request,
                "Предложение не может быть восстановлено, поскольку в настоящее время оно не приостановлено.",
            )
        else:
            self.offer.unsuspend()
            messages.success(self.request, "Предложение восстановлено.")
        return HttpResponseRedirect(
            reverse("dashboard:offer-detail", kwargs={"pk": self.offer.pk})
        )

    def get_queryset(self):
        return self.model.objects.filter(offer_id=self.offer.pk).select_related("order")

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["offer"] = self.offer
        return ctx

    def render_to_response(self, context, *args, **kwargs):
        if self.request.GET.get("format") == "csv":
            formatter = OrderDiscountCSVFormatter()
            return formatter.generate_response(self.get_queryset(), offer=self.offer)
        return super().render_to_response(context, *args, **kwargs)
