from core.utils import safe_referrer
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.encoding import smart_str
from django.views.generic.base import View


class PostActionMixin:
    """
    Simple mixin to forward POST request that contain a key 'action'
    onto a method of form "do_{action}".

    This only works with DetailView
    """

    def post(self, request, *args, **kwargs):
        if "action" in self.request.POST:
            model = self.get_object()
            # The do_* method is required to do what it needs to with the model
            # it is passed, and then to assign the HTTP response to
            # self.response.
            method_name = "do_%s" % self.request.POST["action"].lower()
            if hasattr(self, method_name):
                getattr(self, method_name)(model)
                return self.response
            else:
                messages.error(request, "Неверная отправка формы.")
                return self.get(request, *args, **kwargs)

        # There may be no fallback implementation at super().post
        try:
            return super().post(request, *args, **kwargs)
        except AttributeError:
            messages.error(request, "Неверная отправка формы.")
            return self.get(request, *args, **kwargs)


class NotifEditMixin:
    """
    Mixin for views that have a bulk editing facility.  This is normally in the
    form of tabular data where each row has a checkbox.  The UI allows a number
    of rows to be selected and then some 'action' to be performed on them.
    """

    action_param = "action"

    # Permitted methods that can be used to act on the selected objects
    actions = None
    checkbox_object_name = None

    def get_error_url(self, request):
        return safe_referrer(request, ".")

    def get_success_url(self, request):
        return safe_referrer(request, ".")

    def post(self, request, *args, **kwargs):
        # Dynamic dispatch pattern - we forward POST requests onto a method
        # designated by the 'action' parameter.  The action has to be in a
        # whitelist to avoid security issues.
        action = request.POST.get("data-behaviours").lower()
        if not action or action not in self.actions:
            messages.error(self.request, "Недопустимое действие.")
            return redirect(self.get_error_url(request))

        id = request.POST.get("data-notification")
        if not id:
            messages.error(
                self.request,
                "Вам нужно выбрать несколько %s." % id,
            )
            return redirect(self.get_error_url(request))

        object = self.get_object(id)
        return getattr(self, action)(request, object)


class BulkEditMixin:
    """
    Mixin for views that have a bulk editing facility.  This is normally in the
    form of tabular data where each row has a checkbox.  The UI allows a number
    of rows to be selected and then some 'action' to be performed on them.
    """

    action_param = "action"

    # Permitted methods that can be used to act on the selected objects
    actions = None
    checkbox_object_name = None

    def get_checkbox_object_name(self):
        if self.checkbox_object_name:
            return self.checkbox_object_name
        return smart_str(self.model._meta.object_name.lower())

    def get_error_url(self, request):
        return safe_referrer(request, ".")

    def get_success_url(self, request):
        return safe_referrer(request, ".")

    def post(self, request, *args, **kwargs):
        # Dynamic dispatch pattern - we forward POST requests onto a method
        # designated by the 'action' parameter.  The action has to be in a
        # whitelist to avoid security issues.
        action = request.POST.get(self.action_param, "").lower()
        if not self.actions or action not in self.actions:
            messages.error(self.request, "Неверное действие.")
            return redirect(self.get_error_url(request))

        ids = request.POST.getlist("selected_%s" % self.get_checkbox_object_name())
        ids = list(map(int, ids))
        if not ids:
            messages.error(
                self.request,
                ("Вам нужно выбрать несколько %s.") % self.get_checkbox_object_name(),
            )
            return redirect(self.get_error_url(request))

        objects = self.get_objects(ids)
        return getattr(self, action)(request, objects)

    def get_objects(self, ids):
        object_dict = self.get_object_dict(ids)
        # Rearrange back into the original order
        return [object_dict[id] for id in ids if id in object_dict]

    def get_object_dict(self, ids):
        return self.get_queryset().in_bulk(ids)


class ObjectLookupView(View):
    """Base view for json lookup for objects"""

    def get_queryset(self):
        return self.model.objects.all()  # pylint: disable=E1101

    def format_object(self, obj):
        return {
            "id": obj.pk,
            "text": str(obj),
        }

    def initial_filter(self, qs, value):
        return qs.filter(pk__in=value.split(","))

    # pylint: disable=unused-argument
    def lookup_filter(self, qs, term):
        return qs

    def product_filter(self, qs, product_id, class_id):
        return qs

    def paginate(self, qs, page, page_limit):
        total = qs.count()

        start = (page - 1) * page_limit
        stop = start + page_limit

        qs = qs[start:stop]

        return qs, (page_limit * page < total)

    def get_args(self):
        GET = self.request.GET
        return (
            GET.get("initial", None),
            GET.get("q", None),
            GET.get("product_id", None),
            GET.get("class_id", None),
            int(GET.get("page", 1)),
            int(GET.get("page_limit", 30)),
        )

    # pylint: disable=W0201
    def get(self, request):
        self.request = request
        qs = self.get_queryset()

        initial, q, product_id, class_id, page, page_limit = self.get_args()

        if product_id or class_id:
            qs = self.product_filter(qs, product_id, class_id)

        if initial:
            qs = self.initial_filter(qs, initial)
            more = False
        else:
            if q:
                qs = self.lookup_filter(qs, q)

            qs, more = self.paginate(qs, page, page_limit)

        return JsonResponse(
            {
                "results": [self.format_object(obj) for obj in qs],
                "pagination": {"more": more},
            }
        )
