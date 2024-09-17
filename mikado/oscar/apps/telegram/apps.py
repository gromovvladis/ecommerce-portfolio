
from django.urls import path
from oscar.core.loading import get_class
from oscar.core.application import OscarConfig

class TelegramConfig(OscarConfig):
    label = "telegram"
    name = "oscar.apps.telegram"
    verbose_name = "Телеграм"

    namespace = "telegram"

    # pylint: disable=attribute-defined-outside-init, W0611, W0201
    # def ready(self):
    #     self.shipping_charge_view = get_class("shipping.views", "AddShippingCharge")


    # def get_urls(self):
    #     urls = [
    #         path("api/shipping-charge/", self.shipping_charge_view.as_view(), name="charge"),
    #     ]
    #     return self.post_process_urls(urls)


