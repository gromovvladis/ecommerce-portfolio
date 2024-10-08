# pylint: disable=attribute-defined-outside-init
from django import http
from django.conf import settings
from oscar.core.compat import get_user_model
from oscar.core.loading import get_class, get_model
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication


User = get_user_model()
Partner = get_model("partner", "Partner")
PartnerSelectForm = get_class("partner.forms", "PartnerSelectForm")

partner_default = settings.PARTNER_DEFAULT

class PartnerSelectModalView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    template_name = "oscar/partner/partner_modal.html"
    form_class = PartnerSelectForm

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        partner_modal_content = render_to_string(self.template_name, context, request=request)

        response = http.JsonResponse({
            "partner_modal": partner_modal_content,
        }, status=200)
        
        # Получаем данные о партнере из куки и корзины
        cookie_partner = request.COOKIES.get('partner')
        basket_partner = getattr(request.basket, 'partner_id', None)
        basket_partner = str(basket_partner) if basket_partner is not None else None

        if basket_partner and basket_partner != cookie_partner:
            # Устанавливаем партнера из корзины, если данные не совпадают с куки
            response.set_cookie("partner", basket_partner)
        elif not cookie_partner and not basket_partner:
            # Если данные о партнере отсутствуют в куки и корзине, устанавливаем по умолчанию
            response.set_cookie("partner", partner_default)

        # Возвращаем JSON-ответ с данными
        return response


    def get_context_data(self, *args, **kwargs):
        return {
            "partner_form": self.get_partner_form(*args, **kwargs)
        }

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        if form.is_valid():
            partner_id = form.cleaned_data["partner_id"]
            if request.basket:
                if request.basket.partner_id != int(partner_id):
                    request.basket.change_basket_partner(partner_id)
                    response = http.JsonResponse({"refresh": True, "status": 200}, status=200)
                else:
                    response = http.JsonResponse({"refresh": False, "status": 200}, status=200)
           
            response.set_cookie('partner', partner_id)
            return response

        return http.JsonResponse({"error": "Ошибка выбора точки продажи", "status": 400}, status=404)


    def get_partner_form(self, *args, **kwargs):
        return self.form_class(**self.get_form_class_kwargs(*args, **kwargs))

    def get_form_class_kwargs(self, *args, **kwargs):
        partner_id = self.request.basket.partner_id or self.request.COOKIES.get('partner_id') or partner_default
        kwargs["initial"] = {
            "partner_id": partner_id,
        }
        return kwargs