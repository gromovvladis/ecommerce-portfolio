from haystack.query import SearchQuerySet

from django import http
from django.template.response import TemplateResponse
from django.template.loader import render_to_string

from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny

from oscar.core.loading import get_class
from oscar.apps.search.signals import user_search

SearchForm = get_class("search.forms", "SearchForm")
BaseSearchView = get_class("search.views.base", "BaseSearchView")


class FacetedSearchView(BaseSearchView):
    form_class = SearchForm
    template_name = "oscar/search/results.html"
    context_object_name = "results"

    def dispatch(self, request, *args, **kwargs):
        # Raise a signal for other apps to hook into for analytics
        user_search.send(
            sender=self,
            session=self.request.session,
            user=self.request.user,
            query=self.request.GET.get("q"),
        )

        result = super().dispatch(request, *args, **kwargs)
        return http.JsonResponse({"results": result}, status=202)

    def form_valid(self, form):
        self.queryset = form.search()
        context = self.get_context_data(
            **{
                self.form_name: form,
                "query": form.cleaned_data.get(self.search_field),
                "object_list": self.queryset,
            }
        )
        return render_to_string(
            "oscar/search/results.html", context, request=self.request
        )


class SearchView(BaseSearchView):
    form_class = SearchForm
    template_name = "oscar/search/search.html"

    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, self.template_name)


class SuggestionsView(APIView, BaseSearchView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        dfuery_string = request.POST.get("q", "")
        sqs = SearchQuerySet().auto_query(
            query_string=request.POST.get("q", ""), fieldname="name"
        )[:20]

        products = []
        for prd in sqs:
            if prd.structure in ["parent", "standalone"]:
                products.append(prd._get_object())

        context = {
            "query": request.POST.get("q", ""),
            "object_list": products,
        }

        user_search.send(
            sender=self,
            session=self.request.session,
            user=self.request.user,
            query=dfuery_string,
        )

        res = render_to_string(
            "oscar/search/results.html", context, request=self.request
        )
        return http.JsonResponse({"results": res}, status=200)
