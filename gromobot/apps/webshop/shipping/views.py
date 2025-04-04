import json
from datetime import datetime, timedelta

from core.loading import get_class, get_model
from django import http
from django.conf import settings
from django.db.models import F, Sum
from django.utils.timezone import now
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .utils import pickup_now

ZonesUtils = get_class("webshop.shipping.zones", "ZonesUtils")
Map = get_class("webshop.shipping.maps", "Map")

ShippingZona = get_model("shipping", "ShippingZona")
Order = get_model("order", "Order")

_dir = settings.STATIC_PRIVATE_ROOT


class OrderNowView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]
    map = Map()

    def post(self, request, *args, **kwargs):

        shipping_method = request.POST.get("shipping_method")
        basket = request.basket

        if shipping_method == "zona-shipping":
            coords = request.POST.get("coords").split(",")
            address = request.POST.get("address")
            zona_id = request.POST.get("zonaId")
            result = self.shipping(coords, address, zona_id, basket)
        else:
            result = self.pickup(basket)

        return http.JsonResponse(result, status=200)

    def pickup(self, basket):
        current_time = now()
        new_order_time = pickup_now(basket)
        before_order = new_order_time - current_time

        if before_order < timedelta(hours=2):
            minutes = before_order.total_seconds() // 60
            shipping_time_text = f"Самовывоз через {int(minutes)} мин."
        elif new_order_time.date() == current_time.date():
            shipping_time_text = (
                f"Самовывоз сегодня в {new_order_time.strftime('%H:%M')}"
            )
        elif new_order_time.date() == (current_time + timedelta(days=1)).date():
            shipping_time_text = (
                f"Самовывоз завтра в {new_order_time.strftime('%H:%M')}"
            )
        else:
            shipping_time_text = (
                f"Самовывоз {new_order_time.strftime('%d.%m.%Y в %H:%M')}"
            )

        return {
            "timeUTC": new_order_time.isoformat(),
            "shipping_time_text": shipping_time_text,
        }

    def shipping(self, coords, address, zona_id, basket):
        if not address and not any(item.strip() != "" for item in coords):
            return {"error": "Укажите адрес"}

        if not coords:
            geoObject = self.geoobject(address=address)
            coords = self.coords(geoObject)

        if not address:
            geoObject = self.geoobject(coords=coords)
            address = self.address(geoObject)

        if not address or not any(item.strip() != "" for item in coords):
            return {"error": "Адрес не найден"}

        zones_utils = ZonesUtils()

        if not zona_id:
            zona_id = zones_utils.get_zona_id(coords)

        if not zona_id or zona_id == "0":
            return {"error": "Адрес вне зоны доставки"}

        if not zones_utils.is_zona_available(zona_id):
            return {
                "coords": coords,
                "address": address,
                "error": "Временно не доставляем",
                "shipping_time_text": "Доставка по данному адресу временно не осуществляется",  # Доставим через Х мин.
            }

        min_order = zones_utils.min_order_for_zona(zona_id)

        if not self.is_working_time():
            return {
                "coords": coords,
                "address": address,
                "zonaId": zona_id,
                "order_minutes": "С 9:00",  # время выполнения заказов в минутах
                "min_order": min_order,
                "shipping_time_text": "Заказ возможен на отложенное время",
            }

        order_minutes = self.rote_time(coords, zona_id, basket)
        shipping_time_text = "Доставим через %s мин." % order_minutes
        time_utc = format(
            datetime.today() + timedelta(minutes=order_minutes),
            "%d.%m.%Y %H:%M",
        )

        return {
            "coords": coords,  # строка типа 56.34535,92.34536
            "address": address,  # Строкак типа Ленина 112, Красноярск
            "zonaId": zona_id,  # Номер зоны доставки для shipping charge
            "timeUTC": time_utc,  # время в дормате 11.04.2024 11:55 для времени заказа
            "order_minutes": "~ %s мин."
            % order_minutes,  # время выполнения заказов в минутах
            "min_order": min_order,  # сумма минимального заказа для разных зон
            "shipping_time_text": shipping_time_text,  # Доставим через Х мин.
        }

    # ===================
    #  Yandex / 2Gis Maps
    # ===================

    def geoobject(self, address=None, coords=None):
        """Получает геобъект по адресу или координатам"""
        geoObject = self.map.geocode(address, coords)
        return geoObject

    def coords(self, geoObject):
        """Получает координы обекта по геобъекту"""
        coordinates = self.map.coordinates(geoObject)
        return coordinates

    def address(self, geoObject):
        """Получает адрес по геобъекту"""
        address = self.map.address(geoObject)
        return address

    # ===================
    #  Timers
    # ===================

    def rote_time(self, coords, zona_id, basket):
        """Получает координы обекта, до которого нужно простроить маршрут.
        Маршрут строим от точки, которая будет задана в корзине у стокрекорд партнера
        Возвращает инфорамию о поездке (растояние, время)"""

        coock_time = self.coockingTime(basket)

        # if not rote_time:
        try:
            line = basket.lines.first()
            store = line.stockrecord.store
            store_address = store.address
            start_point = [store_address.coords_long, store_address.coords_lat]
        except Exception:
            start_point = [56.050918, 92.904378]

        end_points = []
        end_points.append(coords)
        rote_time = self.map.route_time(start_point, end_points)

        return rote_time + coock_time

    def coocking_time(self, basket):
        basket_lines = basket.lines.prefetch_related("product").all()
        order_minutes = basket_lines.annotate(
            total_cooking_time=F("product__cooking_time") * F("quantity")
        ).aggregate(cooking_time_sum=Sum("total_cooking_time"))["cooking_time_sum"]
        return timedelta(minutes=order_minutes)


class OrderLaterView(APIView):
    """
    Время доставки к определенному времени
    """

    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def get(self, request, *args, **kwargs):
        current_time = datetime.today()
        start_time = request.basket.store.start_worktime
        end_time = request.basket.store.end_worktime

        pickup_time = pickup_now(request.basket) + timedelta(hours=1)

        if pickup_time.hour > end_time.hour or pickup_time.hour < start_time.hour:
            pickup_time = datetime.combine(
                pickup_time.date() + timedelta(days=1), start_time
            )

        data = {
            "minHours": start_time.hour,
            "maxHours": end_time.hour,
            "minDate": format(
                pickup_time,
                "%Y-%m-%dT%H:%M",
            ),
            "maxDate": format(
                current_time.replace(minute=59, hour=22) + timedelta(days=14),
                "%Y-%m-%dT%H:%M",
            ),
        }
        return http.JsonResponse({"datapicker": data}, status=200)


class ShippingZonesGeoJsonView(APIView):
    """
    Return the 'shipping all zones json'.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        json_file = json.loads(
            open(
                _dir + "/js/webshop/shipping/geojson/shipping_zones.geojson", "rb"
            ).read()
        )
        return http.JsonResponse(json_file, status=202)
